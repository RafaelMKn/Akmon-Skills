#!/usr/bin/env python3
"""Confere as skills instaladas contra o mapa e a triagem desta skill.

Confere dois arquivos: references/mapa.md (linhas `| `nome` | ... |`) e as tabelas/cadeias do
SKILL.md (linhas que começam com `|` ou contêm `→`).
Saída: 'OK' quando bate (exit 0); senão (exit 1) lista
  NAO MAPEADA        instalada e ausente do mapa;
  ORFA NO MAPA       citada no mapa e não instalada;
  ORFA NO SKILL.md   citada na triagem e não instalada;
  FORA DA TRIAGEM    instalada e sem nenhuma linha nas tabelas/cadeias do SKILL.md.
Uso: checar_mapa.py [pasta-de-skills ...]. Sem argumento, varre as pastas de skills que existirem:
  ~/.claude/skills, ~/.agents/skills, ~/.gemini/config/skills, ~/.hermes/skills (usuário)
  .claude/skills, .agents/skills (projeto, a partir do diretório atual). Somente stdlib.
"""
import os
import re
import sys
from pathlib import Path

HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
if len(sys.argv) > 1:
    PASTAS = [Path(a).expanduser() for a in sys.argv[1:]]
else:
    candidatas = [
        Path.home() / ".claude" / "skills",
        Path.home() / ".agents" / "skills",
        Path.home() / ".gemini" / "config" / "skills",
        HOME / "skills",
        Path.cwd() / ".claude" / "skills",
        Path.cwd() / ".agents" / "skills",
    ]
    PASTAS = [c for c in candidatas if c.is_dir()]
if not PASTAS:
    sys.exit("Nenhuma pasta de skills encontrada: passe o caminho como argumento.")
RAIZ = Path(__file__).resolve().parent.parent
MAPA = RAIZ / "references" / "mapa.md"
SKILL_MD = RAIZ / "SKILL.md"
IGNORAR = {RAIZ.name}
FERRAMENTAS = {"delegate_task"}  # ferramentas citadas nas cadeias, não são skills


def nome_da_skill(p: Path):
    txt = p.read_text(encoding="utf-8", errors="replace")
    if not txt.startswith("---"):
        return None
    m = re.search(r"^name:\s*['\"]?([\w.-]+)", txt, re.M)
    return m.group(1) if m else None


instaladas = set()
for pasta in PASTAS:
    for p in pasta.rglob("SKILL.md"):
        if any(part.startswith(".") for part in p.relative_to(pasta).parts):
            continue
        n = nome_da_skill(p)
        if n and n not in IGNORAR:
            instaladas.add(n)

mapeadas = set(re.findall(r"^\| `([\w.-]+)` \|", MAPA.read_text(encoding="utf-8"), re.M))

# Nomes de skill citados nas tabelas e cadeias do SKILL.md
citadas = set()
for linha in SKILL_MD.read_text(encoding="utf-8").splitlines():
    if linha.startswith("|") or "→" in linha:
        citadas |= set(re.findall(r"`([a-z0-9_][a-z0-9_.-]*)`", linha))
citadas -= IGNORAR | FERRAMENTAS

faltando = sorted(instaladas - mapeadas)
orfas = sorted(mapeadas - instaladas)
orfas_skill = sorted(citadas - instaladas)
fora = sorted(instaladas - citadas)
print("pastas: " + ", ".join(str(x) for x in PASTAS))
print(f"instaladas={len(instaladas)} mapeadas={len(mapeadas)} na_triagem={len(instaladas & citadas)}")
for n in faltando:
    print(f"NAO MAPEADA: {n}")
for n in orfas:
    print(f"ORFA NO MAPA: {n}")
for n in orfas_skill:
    print(f"ORFA NO SKILL.md: {n}")
for n in fora:
    print(f"FORA DA TRIAGEM: {n}")
if not (faltando or orfas or orfas_skill or fora):
    print("OK")
else:
    sys.exit(1)
