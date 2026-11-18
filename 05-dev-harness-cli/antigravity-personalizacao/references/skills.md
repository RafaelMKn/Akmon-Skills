# Skills no Antigravity

Uma skill é uma pasta com um `SKILL.md` e arquivos opcionais.

## Onde ficam

- **Projeto:** `<raiz>/.agents/skills/<pasta-da-skill>/`. O produto também lê `.agents/skills/` de cada pasta-pai até a raiz do repositório. O nome antigo `.agent/skills` continua aceito.
- **Máquina:** `~/.gemini/config/skills/<pasta-da-skill>/` (o caminho legado `~/.gemini/antigravity/skills/` também é aceito na IDE).
- **Só CLI:** além dos anteriores, lê `~/.gemini/antigravity-cli/skills/`, `~/.gemini/skills/` e as skills de plugins em `~/.gemini/config/plugins/<plugin>/skills/`.

## Frontmatter

- `description` (obrigatória): o que a skill faz e quando usar. É com ela que o agente decide ativar.
- `name` (opcional): identificador em minúsculas com hífens; se faltar, vale o nome da pasta. Recomenda-se sempre preencher.

## Pastas opcionais

| Pasta | Uso |
|---|---|
| `scripts/` | Utilitários executáveis. O agente deve rodá-los com `--help` em vez de ler o código-fonte. |
| `examples/` | Implementações de referência. |
| `resources/` | Modelos, esquemas, dados. |
| `references/` | Documentação longa carregada sob demanda. |

> ⚠️ Verificar na doc oficial: `references/` aparece na especificação funcional, mas a página de skills consultada lista apenas `scripts/`, `examples/` e `resources/`.

## Carregamento progressivo

1. **Descoberta:** a cada turno o agente vê nome e descrição de todas as skills.
2. **Ativação:** se a tarefa combina, ele lê o `SKILL.md` inteiro.
3. **Execução:** segue as instruções.

O usuário pode chamar uma skill digitando `/<nome-da-skill>` no app; na CLI cada skill vira um comando de barra (use `/skills reload` ou abra uma conversa nova depois de adicionar uma).

## Boas práticas

- Descrição específica, com os termos que o usuário realmente usa.
- Corpo objetivo; detalhes longos em arquivos de apoio.
- Caminhos dentro do `SKILL.md` são relativos à pasta da skill.
