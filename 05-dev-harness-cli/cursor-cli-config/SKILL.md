---
name: cursor-cli-config
description: "Consulta e altera as preferências da CLI do Cursor em ~/.cursor/cli-config.json (permissões, modo de aprovação, vim, exibição, sandbox, rede, atribuição de commits), preservando as demais chaves; use quando o usuário pedir para mudar uma configuração da CLI, ajustar permissões, trocar o modo de aprovação ou falar em preferências ou config da CLI."
license: MIT
metadata: { author: "Akmon contributors" }
---

# Configuração da CLI do Cursor

Preferências da CLI ficam em `~/.cursor/cli-config.json` (no Windows, `%USERPROFILE%\.cursor\cli-config.json`). Esta skill lê, altera **só a chave pedida** e regrava um JSON válido.

## Quando usar

- Mudar uma configuração da CLI.
- Ajustar permissões, modo de aprovação, modo vim, exibição ou sandbox.
- "Preferências da CLI", "config da CLI".

## Pré-condições

- O arquivo existe e é JSON válido. Se não existir, **pergunte antes de criar**.
- Arquivos de configuração são JSON puro: **sem comentários**.
- Para valer só em um projeto: `.cursor/cli.json` na pasta do projeto (ver "Configuração de projeto").

## Passo a passo

1. Leia o arquivo inteiro e faça o parse. Se for inválido, **pare**, informe o erro e não grave.
2. Localize a chave pedida. Se for **estado interno** (lista abaixo), não altere: explique que o produto a gerencia.
3. Para **permissões e modo de aprovação**, confirme o efeito com o usuário antes de gravar: ampliar permissões aumenta o risco de execução sem controle. Aplique o **menor privilégio** que atenda ao pedido e registre a mudança.
4. Altere somente a chave pedida; mantenha as demais.
5. Grave JSON válido, indentação de 2 espaços.
6. Reabra o arquivo, confirme que o JSON é válido e que as outras chaves não mudaram.
7. Informe que a mudança deve ser conferida após reiniciar a CLI.

## Chaves documentadas

| Chave | Tipo / valores | Observação |
|---|---|---|
| `version` | número (atual `1`) | obrigatório |
| `permissions.allow` | lista de padrões | obrigatório; ex.: `Shell(ls)`, `Mcp(servidor, ferramenta)` |
| `permissions.deny` | lista de padrões | obrigatório |
| `editor.vimMode` | booleano; padrão `false` | obrigatório |
| `approvalMode` | `"allowlist"`, `"auto-review"`, `"unrestricted"` | `allowlist` pede aprovação para o que não está permitido; `unrestricted` aprova tudo automaticamente |
| `maxMode` | booleano | |
| `channel` | texto | canal de atualização |
| `notifications`, `hints`, `rewind`, `suggestNextPrompt` | booleanos | |
| `display.showLineNumbers`, `display.showThinkingBlocks`, `display.showStatusIndicators`, `display.showStatusLineRunningTime` | booleanos | |
| `sandbox.mode`, `sandbox.networkAccess` | texto | sobrescrevem o modo e a rede do sandbox |
| `sandbox.readBoundary` | `"system"` (padrão) ou `"workspace"` | |
| `network.useHttp1ForAgent` | booleano; padrão `false` | |
| `attribution.attributeCommitsToAgent`, `attribution.attributePRsToAgent` | booleanos; padrão `true` | |

## Estado interno (não editar)

`version` (valor gerido pela CLI), `model`, `selectedModel`, `modelParameters`, `hasChangedDefaultModel`, `privacyCache`, `authInfo`, `showSandboxIntro`, `conversationClassificationScoredConversations`. A CLI pode sobrescrever esses campos.

## Configuração de projeto

Arquivo `.cursor/cli.json` na pasta do projeto. Segundo a documentação, **somente permissões** podem ser definidas no nível do projeto; as demais configurações são globais. Esse arquivo sobrescreve valores só na sessão e não grava na configuração da home.

## Variáveis de ambiente

`CURSOR_CONFIG_DIR` muda a pasta de configuração; no Linux/BSD também vale `XDG_CONFIG_HOME`.

## Arquivo corrompido

Se a CLI não aceitar o arquivo, ele pode ser movido para algo como `.bad` e recriado pela CLI. Não faça isso sem o usuário pedir.

## Resposta ao usuário

Chave, valor anterior, valor novo, arquivo alterado e o aviso de reinício.

> ⚠️ Verificar na doc oficial (`https://cursor.com/docs/cli/reference/configuration`): as chaves `bedrock`, `webFetchDomainAllowlist`, `sandbox.networkAllowlist` e `editor.defaultBehavior`, que constavam na especificação interna, **não aparecem** na documentação consultada; só altere-as se já existirem no arquivo do usuário e avise que não foram confirmadas. Também não confirmados: valores de `channel`; efeito imediato ou só após reiniciar; o que a CLI faz se `permissions` faltar; mesclagem de vários `.cursor/cli.json` do git root até a pasta atual.
