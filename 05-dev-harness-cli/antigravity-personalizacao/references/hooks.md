# Hooks do Antigravity

Hooks executam um comando seu em momentos do ciclo do agente. São **síncronos** e só aceitam `type: "command"`.

## Onde ficam

| Cliente | Projeto | Máquina |
|---|---|---|
| App, CLI, IDE | `.agents/hooks.json` | `~/.gemini/config/hooks.json` |

Plugins podem trazer o próprio `hooks.json`. A CLI **não** lê hooks de `~/.gemini/antigravity-cli/settings.json`. Para inspecionar na CLI use `/hooks`.

## Estrutura

Cada chave de topo é o nome do hook:

```json
{
  "bloqueia-rm": {
    "enabled": true,
    "PreToolUse": [
      {
        "matcher": "run_command",
        "hooks": [{ "type": "command", "command": "./verifica.sh", "timeout": 10 }]
      }
    ]
  }
}
```

- `enabled`: padrão `true`.
- Eventos: `SessionStart`, `PreToolUse`, `PostToolUse`, `PreInvocation`, `PostInvocation`, `Stop`.
- `PreToolUse` e `PostToolUse` usam grupos com `matcher` e a lista `hooks`. Os demais eventos usam a lista de handlers diretamente.
- Handler: `type` (só `"command"`), `command` (obrigatório), `timeout` em segundos (padrão 30).
- O comando roda no shell do sistema; o diretório de trabalho é o da pasta que contém o `hooks.json`.

## Matcher

Vale só para `PreToolUse` e `PostToolUse`. É expressão regular aplicada ao **nome da ferramenta**: `""` ou `"*"` casa tudo; `"run_command"` casa só essa; `"a|b"` casa qualquer uma; `"browser_.*"` casa por prefixo. Nos demais eventos é ignorado.

## Entrada (JSON no stdin, chaves em camelCase)

Comuns: `conversationId`, `workspacePaths`, `transcriptPath`, `artifactDirectoryPath`, `modelName`, `lastUserInput`.

| Evento | Campos extras |
|---|---|
| `PreToolUse` | `toolCall` (`name`, `args`), `stepIdx` |
| `PostToolUse` | `toolCall`, `stepIdx`, `error` (opcional) |
| `PreInvocation`, `PostInvocation` | `invocationNum`, `initialNumSteps` |
| `Stop` | `executionNum`, `terminationReason`, `error` (opcional), `fullyIdle` |

## Saída (JSON no stdout)

| Evento | Campos |
|---|---|
| `SessionStart` | `injectSteps` (opcional) |
| `PreToolUse` | `decision` (obrigatório: `allow`, `auto_approve`, `deny`, `ask`, `force_ask`, `deny_unless_prior_grant`), `reason`, `overwrite` (mescla rasa nos argumentos da ferramenta), `permissionOverrides` |
| `PostToolUse` | `{}` |
| `PreInvocation` | `injectSteps`, `terminationBehavior` (`terminate` ou vazio) |
| `PostInvocation` | `injectSteps`, `terminationBehavior` (`force_continue`, `terminate` ou vazio) |
| `Stop` | `decision` (`continue` mantém o agente rodando; qualquer outro valor permite parar), `reason` |

`injectSteps`: cada item contém um de `systemMessage`, `userMessage`, `ephemeralMessage`, `errorMessage`.

> ⚠️ Verificar na doc oficial: nomes de eventos e de ferramentas variam com a versão. Confirme em `https://antigravity.google/docs/hooks`.
