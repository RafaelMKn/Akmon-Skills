# Plugins do Antigravity

Plugin é um pacote que reúne skills, servidores MCP, hooks, regras e agentes.

## Onde ficam

- Projeto: `.agents/plugins/<nome>/` (ativo só naquele projeto).
- Máquina: `~/.gemini/config/plugins/<nome>/` (ativo em todos os workspaces).

## Estrutura

```
plugins/<nome>/
├── plugin.json          # manifesto (também aceito: .antigravity-plugin/plugin.json)
├── mcp_config.json      # servidores MCP do plugin (opcional)
├── hooks.json           # hooks do plugin (opcional)
├── rules/AGENTS.md      # regras (opcional)
└── skills/              # skills (opcional)
```

## Manifesto (`plugin.json`)

- `name`: texto em minúsculas com hífens. Obrigatório para CLI e Marketplace; para pasta local, o padrão é o nome da pasta. Também serve de prefixo dos servidores MCP do plugin (`<nome>_<servidor>`).
- `disabled`: booleano, padrão `false`. Se `true`, o plugin nasce desligado na primeira instalação. A escolha posterior do usuário prevalece.
- Outros campos vistos na documentação de exemplo: `displayName`, `version`, `description`, `logo`, `suggestedPrompts`.
- Se existir `.antigravity-plugin/plugin.json`, ele tem prioridade sobre o `plugin.json` da raiz.

## Variáveis e diretório de trabalho

- `${PLUGIN_ROOT}`: caminho de instalação, somente leitura (`~/.gemini/config/plugins/<nome>`).
- `${PLUGIN_DATA}`: pasta gravável fora do workspace.
- Comandos de hook do plugin rodam com a raiz do plugin como diretório de trabalho.

## Ligar e desligar

- Shell: `agy plugin enable <nome>` e `agy plugin disable <nome>`.
- Dentro da CLI: `/plugin enable <nome>` e `/plugin disable <nome>`.
- App: menu ⋮ em **Customizations > Installed**.
- Um plugin com variáveis de configuração obrigatórias fica desligado até ser configurado.

> ⚠️ Verificar na doc oficial: a especificação cita o estado gravado em um `config.json` do usuário (chave `plugins`, campo `enabled`). Essa chave e o caminho do arquivo não aparecem nas páginas consultadas.
