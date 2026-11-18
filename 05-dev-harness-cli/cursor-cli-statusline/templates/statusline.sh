#!/usr/bin/env bash
# Exemplo de status line para a CLI do Cursor.
# Mostra: modelo | uso de contexto | pasta. Lê o JSON da sessão no stdin.
# Teste: echo '{"model":{"display_name":"Modelo X"},"context_window":{"used_percentage":42},"cwd":"/tmp/projeto"}' | ./statusline.sh
set -u

if ! command -v jq >/dev/null 2>&1; then
  echo "statusline: instale o jq"
  exit 0
fi

entrada="$(cat)"

modelo="$(printf '%s' "$entrada" | jq -r '.model.display_name // "modelo?"' 2>/dev/null || echo 'modelo?')"
uso="$(printf '%s' "$entrada" | jq -r '(.context_window.used_percentage // 0) | floor' 2>/dev/null || echo 0)"
pasta="$(printf '%s' "$entrada" | jq -r '.workspace.current_dir // .cwd // ""' 2>/dev/null || echo '')"
pasta="${pasta##*/}"

# Barra simples de 10 posições
cheios=$(( uso / 10 )); [ "$cheios" -gt 10 ] && cheios=10
barra=""
for i in 1 2 3 4 5 6 7 8 9 10; do
  if [ "$i" -le "$cheios" ]; then barra+="█"; else barra+="░"; fi
done

cor=$'\033[32m'
[ "$uso" -ge 70 ] && cor=$'\033[33m'
[ "$uso" -ge 90 ] && cor=$'\033[31m'
reset=$'\033[0m'

printf '%s | %s%s %s%%%s | %s\n' "$modelo" "$cor" "$barra" "$uso" "$reset" "${pasta:-.}"
