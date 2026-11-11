---
name: akmon
description: "Use em toda requisição de trabalho (skill padrão editável). Escolhe e roda a skill ideal."
version: 0.3.0
author: <autor>, Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [roteamento, skills, catalogo, padrao, editavel]
    default: true     # padrão: ativa em toda requisição (skills.auto_load)
    editable: true    # template: adapte às skills que o usuário instalou
    related_skills: [using-n8n-mcp-skills, composio-apps]
---

# Akmon — roteador de skills (padrão da sessão)

Esta skill vem pré-carregada em toda sessão (`skills.auto_load`). Todo pedido de trabalho do operador
passa por ela: escolher **a skill ideal**, anunciar em uma linha, carregar e executar seguindo a
skill. O índice de skills do system prompt diz o que existe; esta skill resolve **qual delas** quando
há várias parecidas (20 de n8n, 3 de Composio, 2 de runtime de agente...) e em que **ordem** elas se
encadeiam. O mapa completo, com o que cada skill faz e quando chamar, está em `references/mapa.md`.

## Padrão editável (adapte ao usuário)

Skill **padrão**: ativa em toda requisição, via `skills.auto_load`. E **editável**: as tabelas abaixo
cobrem o catálogo inteiro da biblioteca, mas cada pessoa instala só parte dele. Na primeira vez, ou
quando skills forem instaladas/removidas, siga `references/adaptar-ao-usuario.md`: entender o estilo
de trabalho, escolher as skills que fazem sentido, instalar com o OK do usuário e podar este arquivo
e o mapa para citar só o que está instalado. Enquanto não adaptada, skill citada aqui que não consta
no índice de skills do system prompt **não existe** nesta instalação: não a carregue nem a invente.

## When to Use

- **Todo pedido de tarefa** (fazer, corrigir, criar, investigar, publicar, pesquisar) — sem precisar
  de palavra-chave.
- Chamada explícita: "akmon, <pedido>" ou "qual skill uso pra X?" → modo completo (abaixo).
- **Não se aplica** a conversa, pergunta factual de uma linha ou continuação de tarefa cuja skill
  já foi carregada nesta sessão — aí segue direto, sem linha de anúncio.

## Procedure

### Modo rápido (padrão, sem chamada de ferramenta extra)

1. **Classificar** o pedido por três eixos, nesta ordem:
   - **Alvo:** qual sistema/projeto/cliente. Projeto com skill própria (ex.: a skill de um projeto específico) vence skill genérica.
   - **Verbo:** criar, corrigir, revisar/auditar, investigar, operar servidor, publicar, pesquisar.
   - **Estado:** produção (cliente real) ou novo/laboratório. Produção puxa as skills com gates
     (`n8n-correcao-producao`, `infra-vps-producao`, `n8n-servidor-vps`).
2. **Escolher UMA principal** pela tabela de desambiguação e pela rota por intenção abaixo + índice do system prompt, só entre
   skills instaladas. Empate:
   a mais específica (a que cita o sistema pelo nome) vence. No máximo 2 de apoio.
3. **Anunciar em uma linha**, sem narrar:
   `Skill: <principal> (apoio: <x>) — <motivo em até 12 palavras>.`
4. **Carregar e executar:** `skill_view(name="<principal>")`; apoio só no passo que precisar. A
   skill escolhida manda a partir daqui, gates inclusos.
5. **Nenhuma serve:** `Nenhuma skill cobre isso — sigo sem skill.` e executa. Se sair procedimento
   reutilizável, propor skill no fim.

### Modo completo (dúvida real, ou chamada explícita "akmon")

1. `terminal(command="python3 <pasta-da-skill>/scripts/checar_mapa.py")` —
   `NAO MAPEADA` = skill nova: leia com `skill_view` e inclua a linha em `references/mapa.md`.
2. `skill_view(name="akmon", file_path="references/mapa.md")` e decida com o mapa.
3. Se a escolha muda o resultado e o pedido não decide ("arruma o fluxo" sem dizer criar ou
   corrigir, ou sem instância): UMA pergunta via `clarify`. Ambiguidade que não muda o resultado:
   decida sozinho.
4. Siga os passos 3–5 do modo rápido.

## Desambiguação

| Pedido | Skill | Não é |
|---|---|---|
| Criar fluxo n8n novo / mudança estrutural | `n8n-flow-builder` | `n8n-workflow-patterns` (apoio) |
| Fluxo **em produção** quebrou / alterar fluxo que roda para cliente | `n8n-correcao-producao` | `n8n-flow-builder` |
| Execução com erro, fora de contexto de produção | `n8n-flow-debugger` | `incident-forensics` |
| "Desde quando está quebrado? qual o tamanho?" | `incident-forensics` | `n8n-flow-debugger` |
| "Como estão os fluxos?" (visão geral de erros) | `radar-n8n` | `n8n-flow-debugger` |
| Revisar/dar parecer em fluxo sem mexer | `n8n-flow-reviewer` | `n8n-validation-expert` (só erro de validação) |
| Chamar ferramenta do n8n-mcp | `n8n-mcp-tools-expert` (+ `n8n-multi-instance`) | — |
| n8n sem MCP, via API/.env | `n8n-manager` | — |
| Subir/atualizar/reverter o **container** n8n no VPS | `n8n-servidor-vps` | `n8n-self-hosting` (VM nova do zero) |
| VPS de produção: Docker, Traefik, DNS | `infra-vps-producao` | `auditoria-infra-hospedagem` (custo da conta) |
| Conta real de app (Gmail, Calendar, YouTube, Slack, GitHub...) | `composio-apps` | `composio` (setup/SDK do Composio) |
| Notion: páginas, bases, API | `notion` | — |
| Notion público sem login | `notion-publico-raspagem` | `notion` |
| Implementar feature/bug (código) | skill do projeto + `esquadrao-agentes` (delegar) | `claude-code`/`codex` (CLI externo) |
| Bug de código genérico | `systematic-debugging` | `node-inspect-debugger`/`python-debugpy` |
| Conferir o que outro agente fez | `auditoria-trabalho-de-agente` | `requesting-code-review` (próprio diff) |
| Prompt de agente de IA | `prompt-engineering-agentes` | `n8n-agents` (nó AI Agent) |
| Medir se mudança no agente melhorou | `eval-set-agentes` | — |
| Vídeo motion | `motion-flux` | `remotion-video` (render), `elevenlabs-motion` (voz) |
| Landing page / site de cliente | `redesign-landing-page` | `impeccable` (ajuste pontual de UI) |
| Melhorar UI existente | `impeccable` | `claude-design` (HTML avulso) |
| Plugar CLI de agente como runtime | `delegated-cli-runtime` | `external-agent-runtime-integration` (apoio) |
| Hermes lento/caro/contexto grande | `hermes-context-tuning` | `hermes-agent` |
| Trocar modelo/effort/fallback | `hermes-roteamento-modelos` | `hermes-agent` |
| Decisão em aberto, escopo indefinido | `grilling` | `grill-with-docs` (gera ADR) |

## Rota por intenção (skills sem par parecido)

Fora da Desambiguação acima: uma linha por área, com todas as skills dela. O que cada uma faz está em
`references/mapa.md`. `scripts/checar_mapa.py` exige que toda skill instalada apareça aqui ou na tabela acima.

| Pedido | Skill |
|---|---|
| Word, planilha, PDF ou slides | `docx` (Word), `xlsx` (Excel/CSV), `pdf` (criar, ler, juntar, OCR), `powerpoint` (.pptx) |
| E-mail: triagem, rascunho, IMAP no terminal | `email-inbox-triage` (triagem e rascunhos), `himalaya` (IMAP/SMTP) |
| Google Docs/Drive/Sheets via gws CLI | `google-workspace` |
| Box, X/Twitter, mapas e rotas | `box`, `xurl` (X/Twitter), `maps` (geocoding, rotas) |
| Reunião, ata ou documento longo em ações | `meeting-action-items`, `document-to-action-items`, `teams-meeting-pipeline` (Teams) |
| Revisão semanal, notas | `weekly-review-planning`, `obsidian` |
| Monitorar preço ou concorrente | `product-price-monitor`, `competitor-news-monitor` |
| Pesquisa: tendência, paper, fonte, wiki | `last30days` (últimos 30 dias), `arxiv` (papers), `grounded-citations` (fontes verificáveis), `llm-wiki` (base markdown) |
| Página que falha (403, paywall, WAF) | `blocked-page-recovery` |
| YouTube, GIF, áudio, música | `youtube-content`, `gif-search`, `songsee` (espectrograma), `songwriting-and-ai-music` (Suno) |
| Vídeo e animação (ASCII, Manim, filme de marca) | `ascii-video`, `manim-video` (matemática/algoritmo), `motionmaxxing` (filme motion com direção de marca) |
| Diagrama, infográfico, arte generativa | `architecture-diagram` (SVG), `baoyu-infographic`, `p5js` |
| Design tokens, referência visual, HTML editorial | `design-md`, `design-system-extraction` (copiar estilo de site), `design-dna` (identidade de referência), `popular-web-designs` (54 design systems), `editorial-html-content` (portal/reportagem), `product-visual-exploration` (produto físico) |
| Animação e 3D no código web | `animated-component-libraries` (React pronto), `canvas` (IDE), `generative_ui` (widget no chat), `gsap-scrolltrigger` (scroll), `lightweight-3d-effects` (Zdog/Vanta), `lottie-animations`, `modern-web-design` (tendências), `motion-framer` (React), `react-spring-physics` (física), `react-three-fiber` (3D em React), `scroll-reveal-libraries` (AOS), `threejs-webgl` (3D sem React), `web3d-integration-patterns` (mistura de libs) |
| Texto e marca: anúncio, tom humano, nome | `ad-creative` (anúncio pago), `humanizer` (tira cara de IA), `naming` (nome de produto/marca) |
| Carreira, cliente, ideia de negócio | `carreira-e-posicionamento` (currículo/LinkedIn), `curriculo-blindado` (banca de 7 avaliadores), `relatorio-resultados-cliente`, `pauta-definicao-cliente` (reunião com cliente travado), `shark-tank` (estressar ideia) |
| Só macOS | `apple-notes`, `apple-reminders`, `findmy`, `imessage` |
| Notion fora dos casos acima | `notion-view-presentation` (enxugar visualização), `notion-reestruturacao-workspace` (reestruturar workspace) |
| n8n: Code node, binário, erro, subfluxo, entrada MCP | `n8n-code-javascript` (JS), `n8n-code-python` (Python), `n8n-code-tool` (tool de código do agente), `n8n-binary-and-data` (arquivos/binário), `n8n-error-handling` (retry, DLQ), `n8n-subworkflows`, `using-n8n-mcp-skills` (porta de entrada MCP) |
| Make, ClickUp, Airtable | `make-manager`, `clickup-api`, `airtable` |
| GoHighLevel | `ghl-prompt-flows` (prompts e workflows) |
| API de cliente, WhatsApp | `integracao-api-terceiros` (CRM/ERP de cliente), `whatsapp-baileys-local` (envio pela bancada local), `evolution-podman-local` (Evolution API local) |
| Backend: Fastify, OAuth, Prisma | `fastify-best-practices`, `oauth`, `prisma-cli`, `prisma-client-api` |
| Postgres e Supabase: orçamento, privilégio, ACL | `pg-budget-reservation-ledger` (orçamento diário), `postgres-least-privilege-api-tests` (privilégio e locks), `supabase-sql-permission-probes` (ACL) |
| QA e teste | `qa-chrome` (PR com navegador), `dogfood` (QA exploratório), `test-driven-development` (TDD), `chromium-print-regression` (CSS de impressão), `previa-carregamento-regressao` (tela de loading), `storage-timeout-profiling` (timeout de storage) |
| Código: spike, limpar, medir, domínio, GitHub | `spike` (experimento descartável), `simplify-code`, `codebase-inspection` (LOC), `domain-modeling` (CONTEXT/ADR), `github` (gh CLI), `permissioned-github` (GitHub com permissão), `babysit` (PR até merge), `split-to-prs` (dividir em PRs), `doit` (/doit), `sdlc-review` (exige kanban) |
| Agentes e CLIs: criar, controlar, cota | `openclaw-agent-creator`, `opencode` (CLI externo), `computer-use` (desktop), `create-subagent`, `agent-session-handoff` (sessão viva), `ia-quota-monitor` (cotas), `sdk` (SDK TypeScript) |
| Skills e Hermes: achar, criar, migrar, configurar | `skill-finder`, `hermes-agent-skill-authoring` (skill no repo do Hermes), `inspecting-hermes-desktop-dom`, `hermes-voz`, `maintaining-custom-forks`, `create-skill`, `create-hook`, `create-rule`, `migrate-to-skills`, `migrate-workflows`, `update-cli-config`, `update-cursor-settings`, `statusline`, `loop`, `shell` (/shell) |
| Antigravity | `agy-customizations`, `antigravity-guide` |
| Linux e pasta de projetos | `linux-power-management`, `linux-desktop-customization`, `linux-app-management`, `linux-memory-swap-tuning`, `linux-audio-pipewire`, `limpeza-workspace-dev` |
| Contexto de projeto, dados públicos, briefing | `guia-contexto-projeto`, `documentos-dados-publicos` (lote de bases oficiais) |

## Cadeias frequentes

- **Fluxo em produção quebrado:** `radar-n8n` → `incident-forensics` → `n8n-correcao-producao`.
- **Fluxo novo:** `n8n-flow-builder` → `n8n-node-configuration`/`n8n-expression-syntax` →
  `n8n-validation-expert` → `n8n-flow-reviewer`.
- **Feature de código:** skill do projeto → `esquadrao-agentes` → `delegate_task` →
  `auditoria-trabalho-de-agente`.
- **Vídeo:** `motion-flux` → `elevenlabs-motion` → `remotion-video`.

## Pitfalls

- **Esta skill é injetada em toda sessão** — cada byte aqui custa em todo turno. Detalhe novo vai
  para `references/mapa.md`, não para este arquivo.
- **Mudança aqui só vale na próxima sessão** (o auto_load é lido uma vez por sessão, para não
  quebrar o cache de prompt).
- **Fora do alcance do sistema atual:** skills de outro SO (ex.: `apple/*`, só macOS) e as que exigem toolset inativo (ex.: `sdlc-review`).
- **Não empilhar skills.** Principal + apoio sob demanda; 5 skills "por garantia" só enchem contexto.
- **O roteamento não pula gates.** Produção continua exigindo confirmação do alvo e backup.
- **Adaptar não é apagar:** não renomeie a skill nem tire `default`/`editable` do frontmatter; o
  `auto_load` a chama pelo nome. Ativar/desligar: `references/adaptar-ao-usuario.md` (fase 1).

## Verification

- Pedido de tarefa → resposta começa com `Skill: ...` ou `Nenhuma skill cobre isso`.
- A skill anunciada foi carregada com `skill_view` antes de agir.
- `checar_mapa.py` retorna `OK` (exit 0) depois de qualquer atualização do mapa ou deste arquivo: toda skill instalada está no mapa **e** na triagem (Desambiguação ou Rota por intenção).
- Depois de adaptar ao usuário: nenhuma skill citada aqui falta na instalação dele.
