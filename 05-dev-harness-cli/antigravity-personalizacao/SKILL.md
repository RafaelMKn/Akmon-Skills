---
name: antigravity-personalizacao
description: "Orienta e cria customizações do agente Antigravity (regras, skills, plugins, hooks e servidores MCP), indicando onde cada arquivo fica, qual vence em caso de conflito e como registrar pastas fora do padrão; use quando o usuário pedir para criar, mover ou entender essas customizações no projeto ou na máquina."
license: MIT
metadata: { author: "Akmon contributors" }
---

# Personalização do Antigravity

Guia para criar e organizar as cinco customizações do agente Antigravity: **regra, skill, plugin, hook e servidor MCP**. Esta skill decide o tipo, o local e o escopo, e grava os arquivos. Detalhes de formato ficam em `references/`.

Dúvidas gerais de uso do produto (CLI, IDE, app, SDK) pertencem à skill `antigravity-referencia`.

## Quando usar

- O usuário quer criar uma regra, skill, plugin, hook ou servidor MCP.
- Pergunta como o Antigravity carrega ou prioriza esses itens.
- Quer registrar uma pasta fora do padrão (`skills.json`, `plugins.json`).
- Quer decidir entre versionar no repositório ou deixar na máquina.

## Antes de começar

1. Descubra o **escopo**: projeto (vai para o repositório, vale para a equipe) ou máquina (vale para todos os projetos do usuário). Se não estiver claro, pergunte antes de criar qualquer arquivo.
2. Confirme que há permissão de escrita na raiz do projeto, quando o escopo for projeto.
3. Verifique se o item já existe. Nunca sobrescreva sem confirmação.

## Tabela de decisão

| O usuário quer... | Tipo | Arquivo principal | Referência |
|---|---|---|---|
| Instruções permanentes ou por contexto | Regra | `AGENTS.md`, `GEMINI.md` ou `.agents/rules/*.md` | `references/regras.md` |
| Um procedimento reutilizável que o agente ativa quando faz sentido | Skill | `skills/<nome>/SKILL.md` | `references/skills.md` |
| Empacotar skills, MCP, hooks e regras para distribuir | Plugin | `plugins/<nome>/plugin.json` | `references/plugins.md` |
| Executar um comando em eventos do agente (bloquear, auditar, injetar) | Hook | `hooks.json` | `references/hooks.md` |
| Dar ao agente ferramentas externas | MCP | `mcp_config.json` | `references/mcp.md` |
| Carregar itens de uma pasta fora do padrão | Registro | `skills.json` / `plugins.json` | `references/registro-json.md` |

Se o pedido não cabe em nenhum tipo, explique o que o produto oferece para aquele objetivo, sem inventar um formato.

## Passo a passo

1. **Classificar** o pedido pela tabela acima.
2. **Escolher o local.**
   - Projeto: pasta `.agents/` na raiz do repositório.
   - Máquina: `~/.gemini/config/`.
3. **Explicar o carregamento.** Skills entram no contexto só com nome e descrição; o conteúdo completo é lido quando a skill é ativada. Regras `always_on` entram sempre; `model_decision` entram só com descrição até o agente precisar delas.
4. **Tratar nomes repetidos.** Se dois itens têm o mesmo nome, explique qual vence (ver "Precedência").
5. **Criar ou editar** os arquivos, com JSON válido e frontmatter correto. Se algo falhar (JSON inválido, caminho inexistente, conflito sem decisão), informe o problema e **não grave**.
6. **Dizer onde conferir:**
   - App: **Customizations** na barra lateral (**Installed**, e dentro dela a seção **MCP Servers**).
   - CLI: `/skills`, `/hooks`, `/mcp` e `/plugin`.
   - IDE: menu **Customizations** do painel lateral do agente.

## Precedência (do maior para o menor)

1. Itens descobertos no projeto.
2. Itens declarados em `skills.json` / `plugins.json` do workspace.
3. Descoberta global em `~/.gemini/config/`.
4. Itens integrados ao aplicativo (casados pelo nome).
5. Itens declarados em JSON global.

> ⚠️ Verificar na doc oficial: esta ordem veio da especificação funcional e não aparece nas páginas públicas consultadas. Regras são exceção confirmada: elas se **acumulam**, nenhuma substitui a outra.

## Limites e cuidados

- Caminhos sob `~/.gemini/`, nomes de eventos e de ferramentas dependem da versão do produto. Confirme em `https://antigravity.google/docs` antes de recomendar algo específico.
- Hooks são síncronos e aceitam só `type: "command"`.
- Versionar no repositório: pasta de skills e um `.agents/skills.json` apontando para ela (ver `references/registro-json.md`).

## Resposta final ao usuário

Informe: tipo escolhido, caminho exato, escopo, precedência aplicada e onde conferir no aplicativo.
