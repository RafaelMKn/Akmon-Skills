# CLI `agy`

## Básico

- Iniciar a interface: `agy`.
- Sair: `/exit` ou `/quit`; `Ctrl+D` com a caixa de prompt vazia. `Ctrl+C` interrompe a rodada atual e, sem nada rodando, pressionado duas vezes também sai.
- Ajuda de flags e subcomandos: `agy --help`. Ajuda dentro da interface: `/help`.
- Outros subcomandos citados na documentação: `agy models`, `agy agents`, `agy plugin enable|disable <nome>`.

## Comandos de barra comuns

Digite `/` na caixa de prompt para abrir o menu.

| Comando | Para quê |
|---|---|
| `/model` | escolher o modelo (persiste entre sessões) |
| `/resume` | retomar uma conversa anterior |
| `/plan` | montar um plano para revisão |
| `/permissions` | gerenciar permissões de ferramentas |
| `/config` (alias `/settings`) | abrir o editor de configurações |
| `/mcp` | gerenciar servidores MCP |
| `/skills` | ver as skills carregadas |
| `/agents` | agentes personalizados e subagentes em segundo plano |
| `/rewind` (alias `/undo`) | voltar o histórico da conversa |
| `/help` | comandos e atalhos |

## Modo não interativo

- `-p`, `--print` ou `--prompt`: executa um prompt e imprime a resposta.
- `--output-format`: `text` (padrão), `json` ou `stream-json` (só no modo print).
- `--input-format`: `text` ou `stream-json` (só no modo print).
- `--json-schema`: força saída estruturada no modo print.
- `--print-timeout`: limite de tempo no modo print.

## Outras flags

`--model`, `--mode`, `--effort`, `--agent`, `-c`/`--continue` (retoma a última conversa), `--add-dir` (repetível), `--sandbox`, `--dangerously-skip-permissions` (aprova tudo automaticamente; use com cautela).

## Configuração

- Arquivo: `~/.gemini/antigravity-cli/settings.json`. Chaves omitidas usam o padrão. Exemplos de chaves: `agentMode`, `colorScheme`, `toolPermission`.
- Permissões globais da CLI: arrays `allow`, `deny` e `ask` nesse mesmo arquivo.
- Modos de execução (`--mode` ou `agentMode`): `default`, `accept-edits`, `auto` (indisponível em contas business/enterprise).
- `toolPermission`: `request-review`, `proceed-in-sandbox`, `strict`, `always-proceed`.

## Links

- `https://antigravity.google/docs/cli/reference`
- `https://antigravity.google/docs/cli/using`
- `https://antigravity.google/docs/permissions`
