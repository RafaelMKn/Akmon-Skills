#!/usr/bin/env python3
"""Confere as skills instaladas contra o mapa e a triagem desta skill.

Confere dois arquivos: references/mapa.md (linhas `| `nome` | ... |`) e as tabelas/cadeias do
SKILL.md (linhas que começam com `|` ou contêm `→`).
Saída: 'OK' quando bate (exit 0); senão (exit 1) lista
  NAO MAPEADA        instalada e ausente do mapa;
  ORFA NO MAPA       citada no mapa e não instalada;
  ORFA NO SKILL.md   citada na triagem e não instalada;
  FORA DA TRIAGEM    instalada e sem nenhuma linha nas tabelas/cadeias do SKILL.md.
Uso: checar_mapa.py [pasta-de-skills]   (padrão: ~/.hermes/skills). Somente stdlib.
"""
import os
import re
import sys
from pathlib import Path

HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
SKILLS = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else HOME / "skills"
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
for p in SKILLS.rglob("SKILL.md"):
    if any(part.startswith(".") for part in p.relative_to(SKILLS).parts):
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
