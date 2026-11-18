---
name: cursor-hooks
description: "Cria e edita hooks do Cursor (hooks.json mais scripts ou verificações em prompt) que auditam, bloqueiam, reescrevem entradas ou injetam contexto em eventos do agente; use quando o usuário pedir um hook, mencionar hooks.json ou quiser automatizar algo ao redor de um evento (formatar após editar, barrar comando perigoso, auditar chamadas MCP)."
license: MIT
metadata: { author: "Akmon contributors" }
---

# Hooks do Cursor

Um hook é um comando (ou um prompt de verificação) que o Cursor executa antes ou depois de um evento do agente. Ele pode **permitir, bloquear, pedir confirmação, reescrever a entrada de uma ferramenta ou acrescentar contexto**. Esta skill deve **criar ou alterar os arquivos**, não apenas descrever o formato.

## Quando usar

- Pedido para criar/editar um hook, um `hooks.json` ou um script de hook.
- Automação em torno de um evento do agente.
- Pergunta sobre quais eventos existem ou qual usar.

## Informações necessárias

Pergunte apenas o que não der para inferir:

1. **Objetivo** do hook.
2. **Escopo:** projeto (compartilhado no repositório) ou usuário (todos os projetos).
3. **Evento**, comportamento desejado, tipo (`command` ou `prompt`), filtro (`matcher`) e política de falha (aberta ou fechada).

Pré-condições do script:

- Shebang válido e permissão de execução.
- Todo executável chamado precisa estar no `PATH` de quem roda o hook. Não presuma `jq`, `python3` ou `node`: verifique com `command -v`.

## Passo a passo

1. Reúna os dados que faltam.
2. Escolha o local:
   - Projeto: `.cursor/hooks.json` e `.cursor/hooks/` (caminhos relativos à **raiz do projeto**, ex.: `.cursor/hooks/formatar.sh`).
   - Usuário: `~/.cursor/hooks.json` e `~/.cursor/hooks/` (caminhos relativos a `~/.cursor/`, ex.: `./hooks/formatar.sh`).
   - Prefira projeto quando o comportamento deve ir para o repositório.
3. Escolha o **evento mais específico** para o objetivo (tabela abaixo).
4. Crie ou atualize o `hooks.json`. Se já existir, preserve hooks não relacionados e altere só o necessário.
5. Comece **sem matcher** ou com um simples. Só endureça depois de confirmar que o hook dispara. Filtro complexo? Filtre dentro do script.
6. Crie o script na pasta de hooks do mesmo escopo: leia o JSON da entrada padrão, execute a lógica e devolva JSON na saída padrão, usando **só os campos permitidos** pelo evento.
7. Torne o script executável (`chmod +x`).
8. Verifique dependências com `command -v`.
9. **Teste com o evento real** (rodar um comando de shell, salvar um arquivo, etc.).
10. Confira a execução na aba **Hooks** em **Customize** ou no canal de saída **Hooks**. Se o hook não aparecer, revise primeiro a sintaxe do JSON e do matcher; remova o matcher para isolar.

O arquivo é recarregado ao salvar. Se não carregar, reinicie o Cursor.

## Estrutura do `hooks.json`

```json
{
  "version": 1,
  "hooks": {
    "beforeShellExecution": [
      { "command": ".cursor/hooks/barra-rm.sh", "matcher": "rm\\s+-rf", "timeout": 10, "failClosed": true }
    ]
  }
}
```

| Campo | Significado |
|---|---|
| `version` | obrigatório, inteiro positivo; use `1` |
| `command` | caminho ou comando de shell |
| `type` | `"command"` (padrão) ou `"prompt"` |
| `prompt` | texto do prompt quando `type` é `"prompt"` (a entrada JSON entra no lugar de `$ARGUMENTS`) |
| `model` | modelo opcional para hooks de prompt |
| `timeout` | segundos |
| `matcher` | expressão regular estilo JavaScript (`\s`, não `[[:space:]]`); vazio ou `"*"` casa tudo |
| `failClosed` | `true` bloqueia a ação se o hook falhar, estourar o tempo ou devolver JSON inválido |
| `loop_limit` | só para `stop`/`subagentStop`; padrão 5 |

## Eventos

| Grupo | Eventos |
|---|---|
| Sessão | `sessionStart`, `sessionEnd` |
| Ferramentas | `preToolUse`, `postToolUse`, `postToolUseFailure` |
| Subagentes | `subagentStart`, `subagentStop` |
| Shell | `beforeShellExecution`, `afterShellExecution` |
| MCP | `beforeMCPExecution`, `afterMCPExecution` |
| Arquivos | `beforeReadFile`, `afterFileEdit` |
| Prompt e contexto | `beforeSubmitPrompt`, `preCompact` |
| Fim de resposta | `stop`, `afterAgentResponse`, `afterAgentThought` |
| Tab | `beforeTabFileRead`, `afterTabFileEdit` |
| Aplicativo | `workspaceOpen` |

## O que casa o `matcher`

| Evento | Casa com |
|---|---|
| `preToolUse`, `postToolUse`, `postToolUseFailure` | tipo da ferramenta (`Shell`, `Read`, `Write`, `Task`, `MCP: ...`) |
| `subagentStart`, `subagentStop` | tipo do subagente (`generalPurpose`, `explore`, `shell`) |
| `beforeShellExecution`, `afterShellExecution` | texto completo do comando |
| `beforeReadFile` | `Read` ou `TabRead` |
| `afterFileEdit` | `Write` ou `TabWrite` |
| `beforeSubmitPrompt` | `UserPromptSubmit` |

## Saída (JSON no stdout): use somente estes campos

| Evento | Campos |
|---|---|
| `preToolUse` | `permission`, `user_message`, `agent_message`, `updated_input` |
| `postToolUse` | `additional_context`; em ferramentas MCP também `updated_mcp_tool_output` |
| `postToolUseFailure` | `additional_context` |
| `subagentStart` | `permission`, `user_message` |
| `subagentStop`, `stop` | `followup_message` |
| `beforeShellExecution`, `beforeMCPExecution` | `permission`, `user_message`, `agent_message` |
| `beforeReadFile` | `permission`, `user_message` |
| `beforeTabFileRead` | `permission` |
| `beforeSubmitPrompt` | `continue`, `user_message` |
| `preCompact` | `user_message` |
| `sessionStart` | `env`, `additional_context` |
| `workspaceOpen` | `pluginPaths` |
| demais (`after*`, `sessionEnd`) | sem campos de saída |

`permission` aceita `allow`, `deny` e `ask`. Nuances: em `preToolUse`, `ask` é aceito mas não é aplicado; em `subagentStart`, `ask` vale como `deny`.

> ⚠️ Verificar na doc oficial: o comportamento de `ask` em `preToolUse` e `subagentStart` pode mudar entre versões.

## Códigos de saída do script

- `0`: sucesso (a saída JSON é usada). Em hooks de permissão, JSON inválido bloqueia a ação.
- `2`: bloqueia a ação (equivale a `permission: "deny"`).
- Outro valor: o hook falha e a ação segue (falha aberta), exceto com `failClosed: true`.

Um ponto de partida seguro está em `templates/hook-exemplo.sh`.

## Resposta ao usuário

Informe: local, evento, matcher (ou ausência), política de falha e **o que foi testado**. Se não foi possível testar, diga isso: não declare sucesso sem o teste.

> ⚠️ Verificar na doc oficial: a lista de eventos e de campos muda entre versões do Cursor. Confirme em `https://cursor.com/docs/hooks` se o evento que o usuário quer não estiver na tabela.
