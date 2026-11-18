---
name: cursor-editor-settings
description: "Altera as configurações do usuário do editor Cursor (settings.json do perfil de usuário), preservando o resto do arquivo; use quando o usuário pedir fonte, tamanho de tab, formatar ao salvar, salvamento automático, tema, quebra de linha, minimapa, números de linha, cursor, rolagem suave ou qualquer valor do settings.json do editor."
license: MIT
metadata: { author: "Akmon contributors" }
---

# Configurações do editor Cursor (`settings.json`)

Altera o `settings.json` do **perfil de usuário** do editor, sem tocar no que não foi pedido.

## Quando usar

Ajustes de aparência, edição, arquivos, terminal e atalhos: fonte, tab, formatação ao salvar, autosave, tema, ícones, quebra de linha, minimapa, números de linha, colchetes, cursor, rolagem suave.

**Não use** para:

- Configuração de **workspace** (`.vscode/settings.json`): só vale para o projeto. Avise o usuário antes e não grave no arquivo de usuário.
- **Atribuição de commits** do agente da IDE: fica na interface (configurações do produto, seção do agente). Para a CLI, ver `cursor-cli-config`.

## Pré-condições

- Chave e valor, ou o efeito desejado ("letra maior").
- Sistema operacional (para achar o arquivo).
- O arquivo existe e é JSON válido (comentários são permitidos). Se não existir, pergunte antes de criar.

## Caminho do arquivo

| Sistema | Caminho |
|---|---|
| macOS | `~/Library/Application Support/Cursor/User/settings.json` |
| Linux | `~/.config/Cursor/User/settings.json` |
| Windows | `%APPDATA%\Cursor\User\settings.json` |

**Confirme que o arquivo existe antes de gravar** (por exemplo `ls` no caminho). Se não puder confirmar, não grave: informe o caminho provável e peça confirmação.

## Passo a passo

1. Determine o caminho pelo sistema operacional (pergunte se não souber).
2. Leia o arquivo inteiro.
3. Faça o parse aceitando comentários de linha e de bloco; ao regravar, mantenha os comentários que for possível.
4. Localize a chave; se não existir, adicione. Sem chave clara no pedido, use a tabela abaixo.
5. Altere **só** a chave pedida.
6. Valide o JSON resultante **antes** de gravar. Inválido? Não grave e informe.
7. Grave com indentação de 2 espaços.
8. Diga se é preciso recarregar a janela ou reiniciar: algumas configurações valem na hora, outras não.

## Pedidos comuns

| Pedido | Chave |
|---|---|
| tamanho da letra | `editor.fontSize` |
| tamanho de tab | `editor.tabSize` |
| formatar ao salvar | `editor.formatOnSave` |
| quebra de linha | `editor.wordWrap` |
| tema de cor | `workbench.colorTheme` (ex.: `"Default Dark Modern"`) |
| minimapa | `editor.minimap.enabled` |
| salvamento automático | `files.autoSave` |
| números de linha | `editor.lineNumbers` |
| colchetes coloridos | `editor.bracketPairColorization.enabled` |
| estilo do cursor | `editor.cursorStyle` |
| rolagem suave | `editor.smoothScrolling` |

Outras chaves usuais: `workbench.iconTheme`, `workbench.sideBar.location`, `files.exclude`, `files.associations`, `terminal.integrated.fontSize`. O produto tem chaves próprias com prefixos `cursor.` e `aipopup.`.

## Resposta ao usuário

Chave, valor anterior, valor novo e se precisa recarregar. Sucesso = o arquivo reabre sem erro de JSON e a configuração surte efeito após o recarregamento.

> ⚠️ Verificar na doc oficial: os caminhos acima foram confirmados por guias e fóruns da comunidade do Cursor, **não** por uma página oficial de documentação (que não os lista). A pasta do produto é `Cursor`, o mesmo nome dos outros caminhos `~/.cursor/`; ainda assim, confirme no sistema do usuário. Também não verificados: quais chaves exigem recarregar a janela e o nome exato da seção de atribuição na interface.
