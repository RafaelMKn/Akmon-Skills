# Servidores MCP no Antigravity

## Arquivos

| Escopo | Caminho |
|---|---|
| Máquina | `~/.gemini/config/mcp_config.json` |
| Projeto | `<workspace>/.agents/mcp_config.json` |
| Plugin | `<raiz-do-plugin>/mcp_config.json` (vale quando o plugin está ligado) |

A raiz do JSON tem a chave `mcpServers`, um objeto em que cada chave é o nome único do servidor.

## Servidor local (stdio)

- `command` (obrigatório): executável a iniciar.
- `args`: lista de argumentos.
- `env`: variáveis de ambiente do processo.
- `cwd`: diretório de trabalho (opcional).

## Servidor remoto

- `serverUrl` (obrigatório; `url` também funciona): endpoint HTTP ou HTTPS.
- `headers`: cabeçalhos extras, por exemplo `Authorization`.
- O transporte remoto deve ser **Streamable HTTP**. O transporte antigo HTTP+SSE e a chave `httpUrl` não são aceitos.

## Exemplo (escrito para esta skill)

```json
{
  "mcpServers": {
    "relatorios": {
      "command": "node",
      "args": ["./servidor-relatorios.js"],
      "env": { "RELATORIOS_MODO": "leitura" }
    },
    "docs-internas": {
      "serverUrl": "https://mcp.exemplo.internal/docs"
    }
  }
}
```

## Segredos

Não grave tokens no arquivo versionado. Use variáveis de ambiente e referencie-as no processo, ou deixe o arquivo no escopo de máquina.

## Onde conferir

- App: **Customizations > Installed > MCP Servers**.
- CLI: `/mcp` (MCP Manager).
- IDE: menu **…** do painel lateral do agente > **MCP Servers**.
