# SDK Python do Antigravity

## Instalação (confirmado)

```bash
pip install google-antigravity
```

- Requer Python 3.10 ou superior.
- Licença Apache-2.0. Repositório: `https://github.com/Google-Antigravity/antigravity-sdk-python`.
- As rodas de cada plataforma trazem um **binário de runtime**; por isso instale pelo PyPI e não rode só a partir de um clone do repositório.

## Símbolos principais

| Símbolo | Situação |
|---|---|
| `Agent` | confirmado; usado como gerenciador de contexto assíncrono (`async with`) |
| `LocalAgentConfig` | confirmado; aceita `system_instructions` e opções de Vertex (`vertex`, `project`, `location`) |
| `agent.chat(texto)` | confirmado; devolve um objeto de resposta cujo texto se obtém com `await resposta.text()` |
| `CapabilitiesConfig` | ⚠️ Verificar na doc oficial |
| `google.antigravity.utils.interactive.run_interactive_loop` | ⚠️ Verificar na doc oficial |
| propriedades `thoughts` e `tool_calls` da resposta | ⚠️ Verificar na doc oficial |
| agente somente leitura por padrão; escrita exige `CapabilitiesConfig()` | ⚠️ Verificar na doc oficial |
| resposta iterável em tokens (streaming) | ⚠️ Verificar na doc oficial; a documentação lista um exemplo de streaming sem descrever a API |

## Exemplo mínimo (escrito para esta skill)

```python
import asyncio
from google.antigravity import Agent, LocalAgentConfig

async def main():
    config = LocalAgentConfig(system_instructions="Responda em português, em poucas linhas.")
    async with Agent(config) as agent:
        resposta = await agent.chat("Resuma o que é um índice de banco de dados.")
        print(await resposta.text())

asyncio.run(main())
```

> ⚠️ Verificar na doc oficial: o caminho de importação acima segue o nome do pacote; confirme em `https://antigravity.google/docs/sdk/overview` e nos exemplos do repositório antes de entregar ao usuário.

## Links

- `https://antigravity.google/docs/sdk/overview`
- `https://antigravity.google/docs/sdk/tools`
- `https://antigravity.google/docs/sdk/mcp`
