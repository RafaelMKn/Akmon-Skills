---
name: antigravity-referencia
description: "Responde dúvidas de uso do Antigravity (CLI agy, IDE, aplicativo 2.0 e SDK Python) combinando um mapa offline com a documentação oficial; use quando o usuário perguntar como usar, configurar ou ajustar permissões dessas superfícies. Para criar regras, skills, plugins, hooks ou MCP, use antigravity-personalizacao."
license: MIT
metadata: { author: "Akmon contributors" }
---

# Referência do Antigravity

Responde perguntas sobre o produto Antigravity usando um **mapa offline** (em `references/`) e a **documentação oficial ao vivo** para tudo que for atual, específico ou ausente do mapa.

## Quando usar

Perguntas sobre como usar, configurar ou personalizar:

- a **CLI** `agy` (comandos, atalhos, flags, configuração);
- a **IDE** Antigravity (autocomplete, comando inline, chat/agente);
- o **aplicativo 2.0** (barra lateral, canvas, permissões);
- o **SDK Python** (`google-antigravity`).

Customização de regras, skills, plugins, hooks e MCP é com a skill `antigravity-personalizacao`.

## Passo a passo

1. **Identificar a superfície** (CLI, IDE, app, SDK). Se a resposta depende dela e não está clara, pergunte.
2. **Ler o resumo offline** da superfície:
   - CLI: `references/cli.md`
   - IDE: `references/ide.md`
   - App 2.0: `references/app.md`
   - SDK Python: `references/sdk.md`
3. **Buscar ao vivo** quando a pergunta for sobre novidades, versões, integrações avançadas (por exemplo Vertex AI), configuração detalhada ou algo que o resumo não cobre. Use o mapa de links abaixo.
4. **Responder** com o trecho pertinente e o link. Não invente comandos, chaves ou valores que não estejam nas fontes.
5. **Lista completa de comandos da CLI:** indique `agy --help` no terminal e `/help` dentro da interface.
6. **Declarar a origem:** diga se a resposta veio do resumo offline ou de uma página consultada agora. Sem acesso à web e com dúvida atual, diga que não foi possível confirmar e que a informação pode estar desatualizada.

## Mapa de páginas oficiais

Base: `https://antigravity.google`

| Assunto | Caminho |
|---|---|
| Início da documentação | `/docs` |
| Visão geral e produtos | `/docs/getting-started` |
| CLI: referência | `/docs/cli/reference` |
| CLI: uso e solução de problemas | `/docs/cli/using`, `/docs/cli/troubleshooting` |
| Skills | `/docs/skills` |
| Regras | `/docs/rules` |
| Hooks | `/docs/hooks` |
| Plugins | `/docs/plugins`, `/docs/build-plugins` |
| MCP | `/docs/mcp` |
| Permissões e segurança | `/docs/permissions` |
| IDE e extensões | `/docs/ide/extensions` |
| SDK | `/docs/sdk/overview` |
| Novidades | `/changelog` |
| Suporte | `/support` |

> ⚠️ Verificar na doc oficial: alguns caminhos antigos (`/docs/rules-workflows`, `/docs/sdk`) hoje apenas redirecionam. Se um link falhar, parta de `/docs`.

## Regras de honestidade

- Não cite nomes de modelo sem conferir na documentação ou com `agy models`; eles mudam.
- Valores de configuração do app (políticas e modos) podem ter mudado. Confirme ao vivo.
- O caminho de configuração da CLI depende da versão.

## Formato da resposta

1. Resposta direta, na superfície certa.
2. Link da página oficial usada.
3. Origem: "resumo offline" ou "consultado agora".
