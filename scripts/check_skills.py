#!/usr/bin/env python3
"""Validador de Integridade e Estrutura de Agent Skills (CI).

Akmon-Skills — https://github.com/RafaelMKn/Akmon-Skills

Verifica:
1. Existência e validade sintática do YAML frontmatter (máx 64 KB).
2. Presença e preenchimento dos campos obrigatórios ('name' e 'description').
3. Integridade de links relativos internos (references/, scripts/, docs/).
4. Detecção de placeholders comuns esquecidos (ex: links apontando para '(url)').
"""

import argparse
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Aviso: 'pyyaml' não encontrado. Instale com 'pip install pyyaml'.", file=sys.stderr)
    yaml = None

# Expressão para checagem de links em Markdown: [texto](caminho)
LINK_REGEX = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

MAX_FRONTMATTER_BYTES = 64 * 1024  # 64 KB


def check_skill_file(skill_path: Path, repo_root: Path, strict_links: bool = False):
    errors = []
    warnings = []

    try:
        raw_bytes = skill_path.read_bytes()
    except OSError as e:
        return [f"Erro de I/O ao ler arquivo: {e}"], []

    try:
        content = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return ["Arquivo não está codificado em UTF-8 válido"], []

    # 1. Checagem de Frontmatter
    if not content.startswith("---"):
        errors.append("Frontmatter ausente (o arquivo deve começar com '---')")
        return errors, warnings

    parts = content.split("---", 2)
    if len(parts) < 3:
        errors.append("Frontmatter malformado (não fecha com '---')")
        return errors, warnings

    fm_raw = parts[1]
    if len(fm_raw.encode("utf-8")) > MAX_FRONTMATTER_BYTES:
        errors.append(f"Frontmatter excede o limite máximo de {MAX_FRONTMATTER_BYTES // 1024} KB")

    if yaml is not None:
        try:
            fm_data = yaml.safe_load(fm_raw)
            if not isinstance(fm_data, dict):
                errors.append("Frontmatter YAML precisa ser um mapeamento/dicionário chave-valor")
            else:
                # 2. Campos obrigatórios
                name = fm_data.get("name")
                if not name or not str(name).strip():
                    errors.append("Campo obrigatório 'name' ausente ou vazio no frontmatter")

                description = fm_data.get("description")
                if not description or not str(description).strip():
                    errors.append("Campo obrigatório 'description' ausente ou vazio no frontmatter")
        except (yaml.YAMLError, ValueError, TypeError) as e:
            errors.append(f"Erro de sintaxe no YAML do frontmatter: {e}")

    # 3. Checagem de Links Relativos e Placeholders
    skill_dir = skill_path.parent
    for label, link in LINK_REGEX.findall(content):
        link_clean = link.split("#")[0].strip()
        if not link_clean:
            continue

        # Ignorar links externos ou mailto
        if link_clean.startswith(("http://", "https://", "mailto:", "#", "tel:")):
            continue

        # Detectar placeholders óbvios
        if link_clean in ("url", "link", "exemplo", "TODO"):
            msg = f"Link com placeholder não preenchido: '[{label}]({link})'"
            if strict_links:
                errors.append(msg)
            else:
                warnings.append(msg)
            continue

        # Resolver caminho relativo
        target_path = (skill_dir / link_clean).resolve()
        if not target_path.exists():
            msg = f"Link relativo quebrado: '[{label}]({link})' -> destino não encontrado"
            if strict_links:
                errors.append(msg)
            else:
                warnings.append(msg)

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Validador de estrutura das Agent Skills do Akmon")
    parser.add_argument("--root", default=".", help="Diretório raiz do repositório (padrão: .)")
    parser.add_argument("--strict-links", action="store_true", help="Falhar com erro caso haja links quebrados")
    parser.add_argument("--github-summary", action="store_true", help="Gerar tabela resumo no $GITHUB_STEP_SUMMARY")
    args = parser.parse_args()

    repo_root = Path(args.root).resolve()
    if not repo_root.exists():
        print(f"Erro: Diretório {repo_root} não existe.", file=sys.stderr)
        sys.exit(2)

    # Localizar todas as skills em pastas de categorias (ex: 01-*, 02-*, etc.)
    skills_found = sorted(repo_root.glob("0*/**/SKILL.md"))
    if not skills_found:
        # Fallback para qualquer SKILL.md
        skills_found = sorted(repo_root.glob("**/SKILL.md"))

    print(f"\n🔍 Akmon Skills Validator — Iniciando auditoria em {len(skills_found)} skills...\n")

    total_errors = 0
    total_warnings = 0
    results = []

    for skill in skills_found:
        rel = skill.relative_to(repo_root)
        errs, warns = check_skill_file(skill, repo_root, strict_links=args.strict_links)
        total_errors += len(errs)
        total_warnings += len(warns)
        results.append({
            "path": str(rel),
            "errors": errs,
            "warnings": warns,
            "ok": len(errs) == 0,
        })

    # Exibição no console
    failed_skills = [r for r in results if not r["ok"]]
    warned_skills = [r for r in results if r["warnings"] and r["ok"]]

    for r in results:
        if not r["ok"]:
            print(f"❌ {r['path']}")
            for e in r["errors"]:
                print(f"   └─ [ERRO] {e}")
            for w in r["warnings"]:
                print(f"   └─ [AVISO] {w}")
        elif r["warnings"]:
            print(f"⚠️  {r['path']}")
            for w in r["warnings"]:
                print(f"   └─ [AVISO] {w}")

    print("\n" + "=" * 60)
    print("Relatório Final:")
    print(f"  • Total de Skills auditadas : {len(skills_found)}")
    print(f"  • Skills 100% conformes     : {len(skills_found) - len(failed_skills) - len(warned_skills)}")
    print(f"  • Skills com avisos         : {len(warned_skills)} ({total_warnings} avisos)")
    print(f"  • Skills com erros          : {len(failed_skills)} ({total_errors} erros)")
    print("=" * 60 + "\n")

    # Geração de resumo para GitHub Actions
    if args.github_summary and "GITHUB_STEP_SUMMARY" in os.environ:
        summary_file = os.environ["GITHUB_STEP_SUMMARY"]
        with open(summary_file, "a", encoding="utf-8") as f:
            f.write("## 🛡️ Relatório de Validação Estrutural de Skills\n\n")
            f.write(f"- **Skills auditadas:** {len(skills_found)}\n")
            f.write(f"- **Status:** {'❌ Falhas encontradas' if total_errors > 0 else '✅ Todas em conformidade'}\n\n")

            if failed_skills:
                f.write("### ❌ Skills com Erros\n\n")
                f.write("| Skill | Detalhes dos Erros |\n")
                f.write("| :--- | :--- |\n")
                for r in failed_skills:
                    err_msg = "<br>".join(r["errors"])
                    f.write(f"| `{r['path']}` | {err_msg} |\n")
                f.write("\n")

            if warned_skills:
                f.write("### ⚠️ Skills com Avisos\n\n")
                f.write("| Skill | Avisos Registrados |\n")
                f.write("| :--- | :--- |\n")
                for r in warned_skills:
                    warn_msg = "<br>".join(r["warnings"])
                    f.write(f"| `{r['path']}` | {warn_msg} |\n")
                f.write("\n")

    if total_errors > 0:
        print("💥 Validação FALHOU. Corrija os erros apontados acima antes de integrar.\n")
        sys.exit(1)

    print("✨ Validação CONCLUÍDA com sucesso!\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
