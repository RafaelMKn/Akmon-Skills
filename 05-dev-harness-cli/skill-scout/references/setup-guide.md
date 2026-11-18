# Requisitos e solução de problemas

## Requisitos

- **Python 3.10 ou superior** (o script usa anotações como `X | None`). `python3 --version`.
- **GitHub CLI `gh` 2.0 ou superior**, autenticado, para busca de código e atualização do índice: `gh auth login`.
- Nada mais: o script não depende de `curl` nem de pacotes externos.

Verificação rápida: `python3 scripts/search_skills.py --check --no-interactive`.

## Testes

`python3 scripts/test_search_skills.py` (offline; não acessa a rede nem o seu `~/.skills`).

## Problemas comuns

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| `gh: não encontrado` | GitHub CLI ausente | instale o `gh` pelo gerenciador de pacotes do sistema; sem ele, só a API pública (limite baixo) |
| `gh autenticado: não` | sem login | `gh auth login` |
| `GitHub respondeu HTTP 403/429` | limite de requisições | autentique o `gh`; espere e tente de novo |
| `A busca de código do GitHub exige o gh` | busca de código precisa de autenticação | instale e autentique o `gh` |
| `Índice inválido: ...` | `skill-index.json` fora do esquema | corrija o campo apontado (ver `skill-index.schema.json`) |
| `Host '...' não está na lista padrão` | fonte fora de github.com | só avance com aprovação específica do usuário (`--allow-host`) |
| Erros de SSL / certificado | proxy corporativo ou certificados desatualizados | atualize os certificados do sistema; configure o proxy do `gh`; não desative a verificação de certificado |
| `já existe; nada foi alterado` | destino ocupado | remova a pasta antiga se o usuário quiser reinstalar |

## Dados

- `references/skill-index.json`: índice (vazio na distribuição; monte com `--add-source` e `--update`).
- `references/starred-skills.json`: favoritos, `{ "starred": [], "lastUpdated": "..." }`.
- Instalação padrão em `~/.skills`.
