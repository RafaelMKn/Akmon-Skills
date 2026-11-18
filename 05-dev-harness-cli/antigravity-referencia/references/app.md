# Aplicativo Antigravity 2.0 (desktop)

## Barra lateral

Nova conversa, projetos, tarefas agendadas, **Skills & Customizations** (**Customizations**), configurações.

> ⚠️ Verificar na doc oficial: os nomes exatos dos itens da barra lateral variam entre versões.

## Canvas (caixa de conversa)

- `/` abre os comandos de barra.
- `@` menciona arquivos e pastas, conversas anteriores, sessões de terminal, regras e servidores ou ferramentas MCP.
- Upload por arrastar ou colar.

## Permissões (confirmado na documentação)

Em **Settings > General > Global Permissions > Permission Preset**:

| Preset | Sandbox do terminal | Comandos | Arquivos | MCP e web |
|---|---|---|---|---|
| Request Review | desligado | sempre pergunta | só workspace | pergunta |
| Default (padrão) | ligado | permitidos no sandbox; pergunta fora | workspace + temporários | pergunta |
| Auto | ligado | permitidos no sandbox; checagem automática fora | workspace + temporários | pergunta |
| Turbo | desligado | permitidos sem restrição | sistema de arquivos inteiro | permitido |

- Default cai para Request Review se o sandbox não estiver disponível.
- Auto não existe em contas business ou enterprise.

### Listas Allow / Deny / Ask

- Tipos de ação: `read_file`, `write_file`, `read_url`, `execute_url`, `download_url`, `command`, `mcp`.
- Precedência: **Deny > Ask > Allow**.
- Regras de comando casam por prefixo literal; use o prefixo `regex:` para expressão regular.
- O curinga `*` casa tudo no espaço daquela ação.
- Domínios liberados para `read_url` também alimentam a lista de rede de saída do sandbox. `execute_url` e `download_url` têm concessões próprias.

### Global e por projeto

- Global: **Settings > General > Global Permissions**.
- Por projeto: **Settings > Projects**. Projetos novos começam em "Inherit Global"; "Use Global Settings" remove a sobrescrita.

> ⚠️ Verificar na doc oficial: a especificação cita nomes de política como `always-proceed`, `request-review`, `strict`, `proceed-in-sandbox` para o app. A documentação consultada os usa para o `toolPermission` da **CLI**; o modo de revisão de artefatos (**Artifact review**) não teve seus valores descritos.

## Painel auxiliar

Subagentes, tarefas em segundo plano, artefatos, arquivos alterados e terminais.

## Link

`https://antigravity.google/docs/permissions`
