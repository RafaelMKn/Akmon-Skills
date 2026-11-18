# Ferramental de Desenvolvimento, CLI & Harness

> Skills para engenharia de software (TDD, debugging sistemático, code review, spike), gestão de PRs/GitHub, orquestração de harnesses (Claude Code, Codex, OpenCode, Hermes) e infraestrutura.

Total de skills nesta categoria: **64**

| Skill | Descrição |
|---|---|
| **[`agent-session-handoff`](agent-session-handoff/SKILL.md)** | Use when forwarding instructions to a live agent session. |
| **[`antigravity-personalizacao`](antigravity-personalizacao/SKILL.md)** | Orienta e cria customizações do agente Antigravity (regras, skills, plugins, hooks e servidores MCP), indicando onde cada arquivo fica, qual vence em caso de conflito e como registrar pastas fora do padrão; use quando o usuário pedir para criar, mover ou entender essas customizações no projeto ou na máquina. |
| **[`antigravity-referencia`](antigravity-referencia/SKILL.md)** | Responde dúvidas de uso do Antigravity (CLI agy, IDE, aplicativo 2.0 e SDK Python) combinando um mapa offline com a documentação oficial; use quando o usuário perguntar como usar, configurar ou ajustar permissões dessas superfícies. Para criar regras, skills, plugins, hooks ou MCP, use antigravity-personalizacao. |
| **[`auditoria-infra-hospedagem`](auditoria-infra-hospedagem/SKILL.md)** | Use when auditing a hosting account: cost, waste, DNS. |
| **[`babysit`](babysit/SKILL.md)** | Keep a PR merge-ready by triaging comments, resolving clear conflicts, and fixing CI in a loop. |
| **[`blocked-page-recovery`](blocked-page-recovery/SKILL.md)** | Use when a fetch fails: 403/429, paywall, WAF, bot wall. |
| **[`chromium-print-regression`](chromium-print-regression/SKILL.md)** | Use when testing CSS print with real Chromium PDFs. |
| **[`claude-code`](claude-code/SKILL.md)** | Delegate coding to Claude Code CLI (features, PRs). |
| **[`codebase-inspection`](codebase-inspection/SKILL.md)** | Inspect codebases w/ pygount: LOC, languages, ratios. |
| **[`codex`](codex/SKILL.md)** | Delegate coding to OpenAI Codex CLI (features, PRs). |
| **[`cursor-hooks`](cursor-hooks/SKILL.md)** | Cria e edita hooks do Cursor (hooks.json mais scripts ou verificações em prompt) que auditam, bloqueiam, reescrevem entradas ou injetam contexto em eventos do agente; use quando o usuário pedir um hook, mencionar hooks.json ou quiser automatizar algo ao redor de um evento (formatar após editar, barrar comando perigoso, auditar chamadas MCP). |
| **[`cursor-rules`](cursor-rules/SKILL.md)** | Cria regras persistentes do Cursor em arquivos .mdc dentro de .cursor/rules/, escolhendo entre regra sempre ativa, por tipo de arquivo (globs) ou aplicada pelo agente conforme o contexto; use quando o usuário pedir para registrar uma convenção, padrão de código ou instrução permanente, ou mencionar .cursor/rules, .mdc ou AGENTS.md. |
| **[`cursor-skill-authoring`](cursor-skill-authoring/SKILL.md)** | Guia a criação de skills de agente para o Cursor (pasta com SKILL.md, frontmatter, descrição, corpo e arquivos de apoio); use quando o usuário quiser criar uma skill, transformar um fluxo recorrente em skill, entender o formato do frontmatter ou decidir onde guardar uma skill pessoal ou de projeto. |
| **[`delegated-cli-runtime`](delegated-cli-runtime/SKILL.md)** | Use when integrating a structured external agent CLI. |
| **[`dogfood`](dogfood/SKILL.md)** | Exploratory QA of web apps: find bugs, evidence, reports. |
| **[`doit`](doit/SKILL.md)** | Use when told /doit: implement approved doc via subagents. |
| **[`domain-modeling`](domain-modeling/SKILL.md)** | Build and sharpen a project's domain model. Use when discussing codebase terminology, writing or editing a CONTEXT.md, or recording or editing an ADR. |
| **[`akmon`](akmon/SKILL.md)** | **Skill padrão editável**, ativa em toda requisição: escolhe e roda a skill ideal. Adaptável: a IA do usuário poda o mapa para só as skills instaladas. |
| **[`external-agent-runtime-integration`](external-agent-runtime-integration/SKILL.md)** | Use when integrating an external agent CLI runtime. |
| **[`github`](github/SKILL.md)** | GitHub via gh CLI: PRs, issues, reviews, repos, auth. |
| **[`grill-with-docs`](grill-with-docs/SKILL.md)** | A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go. |
| **[`grilling`](grilling/SKILL.md)** | Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases. |
| **[`guia-contexto-projeto`](guia-contexto-projeto/SKILL.md)** | Use ao fazer guia de contexto, spec técnica ou tasks de v1. |
| **[`hermes-agent`](hermes-agent/SKILL.md)** | Use, configure, theme, extend, and orchestrate Hermes Agent. |
| **[`hermes-agent-skill-authoring`](hermes-agent-skill-authoring/SKILL.md)** | Author in-repo SKILL.md files: frontmatter and structure. |
| **[`hermes-context-tuning`](hermes-context-tuning/SKILL.md)** | Use when Hermes is slow, costly, or context-heavy. |
| **[`hermes-roteamento-modelos`](hermes-roteamento-modelos/SKILL.md)** | Use when changing Hermes models, effort or fallback. |
| **[`hermes-voz`](hermes-voz/SKILL.md)** | Use when setting up or debugging Hermes voice and wake. |
| **[`ia-quota-monitor`](ia-quota-monitor/SKILL.md)** | Monitor, consultar e gerenciar cotas e limites de taxa de IA (Claude Code, OpenAI Codex e Google Antigravity/Gemini) no Linux e KDE Plasma. |
| **[`impeccable`](impeccable/SKILL.md)** | Use when the user wants to design, redesign, shape, critique, audit, polish, clarify, distill, harden, optimize, adapt, animate, colorize, extract, or otherwise improve a frontend interface. Covers websites, landing pages, dashboards, product UI, app shells, components, forms, settings, onboarding, and empty states. Handles UX review, visual hierarchy, information architecture, cognitive load, accessibility, performance, responsive behavior, theming, anti-patterns, typography, fonts, spacing, layout, alignment, color, motion, micro-interactions, UX copy, error states, edge cases, i18n, and reusable design systems or tokens. Also use for bland designs that need to become bolder or more delightful, loud designs that should become quieter, live browser iteration on UI elements, or ambitious visual effects that should feel technically extraordinary. Not for backend-only or non-UI tasks. |
| **[`incident-forensics`](incident-forensics/SKILL.md)** | Reconstrói quando, como e o tamanho real de um incidente. |
| **[`infra-vps-producao`](infra-vps-producao/SKILL.md)** | Use when operating a production VPS: Docker, Traefik, DNS. |
| **[`inspecting-hermes-desktop-dom`](inspecting-hermes-desktop-dom/SKILL.md)** | Read the live Hermes desktop DOM/CSS over CDP. |
| **[`last30days-skill`](last30days-skill/skills/last30days/SKILL.md)** | Research what people actually say about any topic in the last 30 days. Pulls posts and engagement from Reddit, X, YouTube, TikTok, Hacker News, Polymarket, GitHub, and the web. |
| **[`limpeza-workspace-dev`](limpeza-workspace-dev/SKILL.md)** | Use ao limpar pasta dev: worktrees, backups, clones. |
| **[`linux-app-management`](linux-app-management/SKILL.md)** | Use ao gerenciar apps e backups no Linux. |
| **[`linux-audio-pipewire`](linux-audio-pipewire/SKILL.md)** | Corrige áudio no Linux — PipeWire, mic, Bluetooth, ganho. |
| **[`linux-desktop-customization`](linux-desktop-customization/SKILL.md)** | Use when customizing Linux desktop themes and panels. |
| **[`linux-memory-swap-tuning`](linux-memory-swap-tuning/SKILL.md)** | Use when tuning Linux swap, zram, zswap or memory pressure. |
| **[`linux-power-management`](linux-power-management/SKILL.md)** | Use when diagnosing Linux power, heat, fan, or CPU. |
| **[`loop`](loop/SKILL.md)** | Run a prompt or skill on a recurring local interval using monitored background shell output. Use for /loop, polling status, recurring fixed-interval tasks, dynamic self-paced loops, local cron-like loops, or waking an agent periodically. Do not use for one-off tasks. |
| **[`maintaining-custom-forks`](maintaining-custom-forks/SKILL.md)** | Use when maintaining a production fork with custom code. |
| **[`cursor-migracao-para-skills`](cursor-migracao-para-skills/SKILL.md)** | Converte regras do Cursor aplicadas pelo agente (.mdc sem globs e sem alwaysApply) e comandos de barra (.md) para skills (SKILL.md em pasta própria), preservando o corpo do texto e trocando só o frontmatter; use quando o usuário quiser migrar regras ou comandos para skills ou unificá-los na pasta de skills. |
| **[`migrate-workflows`](migrate-workflows/SKILL.md)** | Automatically migrate legacy workflows to modern skills across global and workspace configurations. Scans for existing workflows, creates target SKILL.md files, and safely archives old workflow files. |
| **[`node-inspect-debugger`](node-inspect-debugger/SKILL.md)** | Debug Node.js via --inspect + Chrome DevTools Protocol CLI. |
| **[`opencode`](opencode/SKILL.md)** | Delegate coding to OpenCode CLI (features, PR review). |
| **[`permissioned-github`](permissioned-github/SKILL.md)** | Guidelines for interacting with GitHub and request permissions from the user when commands fail due to restrictions in the agent environment. |
| **[`previa-carregamento-regressao`](previa-carregamento-regressao/SKILL.md)** | Use ao testar prévias de carregamento HTML e React. |
| **[`python-debugpy`](python-debugpy/SKILL.md)** | Debug Python: pdb REPL + debugpy remote (DAP). |
| **[`qa-chrome`](qa-chrome/SKILL.md)** | Use ao testar PRs com navegador e provas auditáveis. |
| **[`requesting-code-review`](requesting-code-review/SKILL.md)** | Pre-commit review: security scan, quality gates, auto-fix. |
| **[`cursor-sdk-guia`](cursor-sdk-guia/SKILL.md)** | Orienta integrações com o SDK TypeScript do Cursor (@cursor/sdk) para rodar agentes em scripts, CI, ações do GitHub, serviços e bots: padrão de chamada, runtime local ou cloud, erros, streaming, cancelamento e MCP; use quando o usuário citar @cursor/sdk, Agent.create, Agent.prompt, Agent.resume, run.stream ou CursorAgentError, ou quiser rodar agentes do Cursor por código. |
| **[`sdlc-review`](sdlc-review/SKILL.md)** | Review Kanban handoffs and route verified outcomes. |
| **[`shell`](shell/SKILL.md)** | Runs the rest of a /shell request as a literal shell command. Use only when the user explicitly invokes /shell and wants the following text executed directly in the terminal. |
| **[`simplify-code`](simplify-code/SKILL.md)** | Parallel 4-agent cleanup of recent code changes. |
| **[`skill-scout`](skill-scout/SKILL.md)** | Procura, instala e gerencia skills de agente: pesquisa num índice local de fontes e, sob demanda, no GitHub e na web, e antes disso avalia se o pedido precisa mesmo de uma skill ou de outro tipo de customização (prompt, instrução, agente ou hook); use quando o usuário quiser achar, instalar, favoritar, atualizar ou listar skills, ou perguntar se deve usar skill, prompt, instrução, agente ou hook. |
| **[`spike`](spike/SKILL.md)** | Throwaway experiments to validate an idea before build. |
| **[`split-to-prs`](split-to-prs/SKILL.md)** | Split current work into small reviewable PRs. Use when the user asks to split a chat, set of changes, branch, or PR. |
| **[`cursor-cli-statusline`](cursor-cli-statusline/SKILL.md)** | Configura uma linha de status personalizada acima do prompt da CLI do Cursor (statusLine em cli-config.json, com script que lê JSON da sessão); use quando o usuário mencionar status line, statusline, barra de status ou rodapé da CLI, ou quiser mostrar modelo, uso de contexto, branch ou pasta acima do prompt. |
| **[`storage-timeout-profiling`](storage-timeout-profiling/SKILL.md)** | Use when storage-heavy tests time out. |
| **[`systematic-debugging`](systematic-debugging/SKILL.md)** | 4-phase root cause debugging: understand bugs before fixing. |
| **[`test-driven-development`](test-driven-development/SKILL.md)** | TDD: enforce RED-GREEN-REFACTOR, tests before code. |
| **[`cursor-cli-config`](cursor-cli-config/SKILL.md)** | Consulta e altera as preferências da CLI do Cursor em ~/.cursor/cli-config.json (permissões, modo de aprovação, vim, exibição, sandbox, rede, atribuição de commits), preservando as demais chaves; use quando o usuário pedir para mudar uma configuração da CLI, ajustar permissões, trocar o modo de aprovação ou falar em preferências ou config da CLI. |
| **[`cursor-editor-settings`](cursor-editor-settings/SKILL.md)** | Altera as configurações do usuário do editor Cursor (settings.json do perfil de usuário), preservando o resto do arquivo; use quando o usuário pedir fonte, tamanho de tab, formatar ao salvar, salvamento automático, tema, quebra de linha, minimapa, números de linha, cursor, rolagem suave ou qualquer valor do settings.json do editor. |

---
*Akmon Skills*
