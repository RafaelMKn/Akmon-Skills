#!/usr/bin/env bash
# Exemplo de hook "beforeShellExecution": bloqueia `rm` recursivo em caminhos críticos
# (/, /home, /etc, /usr, ~, $HOME...) e pede confirmação para `git push --force`.
# Copie para .cursor/hooks/ e aponte o "command" do hooks.json para este arquivo.
# Entrada: JSON no stdin. Saída: JSON no stdout (campos: permission, user_message, agent_message).
# Entrada inválida: sai com código 2 (bloqueia), para não liberar comando que não foi analisado.
# Exemplo didático: não substitui sandbox nem revisão; um comando ofuscado pode escapar da análise.
set -euo pipefail

if ! command -v python3 >/dev/null 2>&1; then
  # Sem python3 não dá para analisar a entrada; falha aberta (código != 0 e != 2).
  echo "hook-exemplo: python3 não encontrado" >&2
  exit 1
fi

python3 -c '
import json, re, shlex, sys

try:
    dados = json.load(sys.stdin)
    comando = str(dados.get("command", ""))
except (json.JSONDecodeError, AttributeError) as erro:
    print(f"hook-exemplo: entrada JSON inválida ({erro}); bloqueando por segurança", file=sys.stderr)
    sys.exit(2)

CRITICOS = {"/", "/*", "/home", "/root", "/etc", "/usr", "/var", "/bin", "/boot", "/lib", "/opt", "~", "~/", "$HOME", "${HOME}"}

def rm_perigoso(cmd: str) -> bool:
    try:
        partes = shlex.split(cmd, posix=True)
    except ValueError:
        return bool(re.search(r"\brm\b", cmd))  # não deu para analisar: trata como perigoso
    for i, p in enumerate(partes):
        if p.rsplit("/", 1)[-1] != "rm":
            continue
        args = partes[i + 1:]
        recursivo = any(a in ("-r", "-R", "--recursive") or (a.startswith("-") and not a.startswith("--") and set("rR") & set(a)) for a in args)
        alvos = [a.rstrip("/") or "/" for a in args if not a.startswith("-")]
        if recursivo and any(a in CRITICOS or a + "/" in CRITICOS for a in alvos):
            return True
    return False

if rm_perigoso(comando):
    print(json.dumps({
        "permission": "deny",
        "user_message": "Comando bloqueado pelo hook: rm recursivo em caminho crítico.",
        "agent_message": "Não execute rm recursivo em /, /home, ~ ou pastas de sistema. Use um caminho específico.",
    }))
elif re.search(r"\bgit\s+push\b.*(--force\b|-f\b)", comando):
    print(json.dumps({
        "permission": "ask",
        "user_message": "Push forçado: confirme antes de continuar.",
    }))
else:
    print(json.dumps({"permission": "allow"}))
'
