# Regras do Antigravity

Regras são instruções em Markdown que o agente lê automaticamente.

## Onde ficam

| Escopo | Arquivos |
|---|---|
| Projeto / pasta | `AGENTS.md`, `GEMINI.md`, `.agents/AGENTS.md`, `.agents/GEMINI.md`, `.agents/rules/*.md` (a forma antiga `.agent/rules/*.md` ainda funciona) |
| Máquina (arquivo único) | `~/.gemini/AGENTS.md`, `~/.gemini/GEMINI.md`, `~/.gemini/config/AGENTS.md`, `~/.gemini/config/GEMINI.md` |
| Máquina (modular) | `~/.gemini/config/rules/*.md` |

## Como são descobertas

- O produto olha a pasta do workspace e cada pasta-pai até a raiz do repositório (a pasta com `.git`).
- Subpastas **abaixo** do workspace não são carregadas.
- As regras **se acumulam**: todas as encontradas entram juntas, uma não substitui a outra.
- Em `.agents/rules/` só são lidos os `.md` do primeiro nível. Arquivos em subpastas são ignorados, a menos que estejam registrados em `.agents/rules.json`.

> ⚠️ Verificar na doc oficial: o formato interno do `rules.json` não está descrito nas páginas consultadas.

## Frontmatter

- `AGENTS.md` e `GEMINI.md`: **sem** frontmatter, sempre ativos.
- Todo `.md` dentro de `rules/` precisa de frontmatter YAML com a chave `trigger`. Sem `trigger` válido, o arquivo é descartado em silêncio.

| `trigger` | Efeito | Chaves extras |
|---|---|---|
| `always_on` | O conteúdo inteiro entra em toda interação | nenhuma |
| `model_decision` | Entra só o caminho e a descrição; o agente lê o resto se a tarefa combinar | `description` (obrigatória) |
| `glob` | Ativa quando o agente trabalha com arquivos que casam com os padrões | `globs` (obrigatória; `glob` também é aceito) |
| `manual` | Só carrega quando o usuário menciona a regra com `@` | nenhuma; **a CLI não suporta** |

## Exemplo mínimo (escrito para esta skill)

```markdown
---
trigger: glob
globs: ["**/*.sql"]
---
# Migrações SQL
- Cada migração faz uma única mudança de esquema.
- Nomeie com data e assunto: `2026-11-17_adiciona_indice_pedidos.sql`.
```

## Dica de qualidade

Uma regra, um assunto. Regras curtas e específicas são mais fáceis de acertar o gatilho do que um arquivo único e longo.

> ⚠️ Workflows (fluxos acionados por comando) são um tópico separado na documentação; o local onde ficam não foi confirmado.
