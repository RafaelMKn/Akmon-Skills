# IDE Antigravity

> ⚠️ Verificar na doc oficial: esta página de apoio vem da especificação funcional. As páginas consultadas confirmam que existe uma IDE autônoma e extensões para vários editores, mas não detalham os atalhos abaixo. Confirme em `https://antigravity.google/docs/ide/extensions` antes de afirmar.

## Base

A IDE é baseada no VS Code.

## Três modos de IA

1. **Autocomplete passivo** (Tab).
2. **Comando inline**: `Ctrl+I` (Linux e Windows) ou `⌘I` (macOS).
3. **Chat/agente** na barra lateral, com modo de planejamento.

## Recursos do Tab

Supercomplete, "Tab to Jump" e "Tab to Import".

## Controles

| Ação | Tecla |
|---|---|
| Aceitar sugestão | `Tab` |
| Cancelar | `Esc` |
| Aceitar palavra por palavra | `Ctrl+→` ou `⌘+→` |

## Integrações de editor

- Code lenses acima de símbolos.
- Sobreposição de diff.
- Correção automática a partir de diagnósticos.

## Customizações do workspace

Ficam em `<raiz>/.agents/`. Para criar regras, skills, plugins, hooks ou MCP, use `antigravity-personalizacao`. As skills ativas aparecem no menu **Customizations** do painel lateral do agente; os servidores MCP em **…** > **MCP Servers**.
