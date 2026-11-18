---
name: cursor-sdk-guia
description: "Orienta integrações com o SDK TypeScript do Cursor (@cursor/sdk) para rodar agentes em scripts, CI, ações do GitHub, serviços e bots: padrão de chamada, runtime local ou cloud, erros, streaming, cancelamento e MCP; use quando o usuário citar @cursor/sdk, Agent.create, Agent.prompt, Agent.resume, run.stream ou CursorAgentError, ou quiser rodar agentes do Cursor por código."
license: MIT
metadata: { author: "Akmon contributors" }
---

# SDK TypeScript do Cursor (`@cursor/sdk`)

Ajuda a construir integrações que rodam agentes do Cursor **fora da IDE**. A API muda com frequência: consulte `https://cursor.com/docs/api/sdk/typescript` e `Cursor.models.list()` em vez de responder de memória.

## Quando usar

- O usuário cita o SDK, `@cursor/sdk` ou nomes da API (`Agent.create`, `Agent.prompt`, `Agent.resume`, `agent.send`, `run.stream`, `CursorAgentError`).
- Quer rodar agentes por código, em CI, ação do GitHub, serviço ou bot.
- Precisa escolher entre runtime **local** e **cloud**, configurar MCP, tratar streaming, cancelamento ou erros.
- Quer migrar da API REST `/v1/agents` para o SDK.

## Entradas e pré-condições

- Objetivo e onde roda (máquina do usuário, CI, servidor).
- Runtime: local ou cloud. Se a escolha muda o código e não está clara, pergunte.
- Chave de API: `apiKey` explícito ou `CURSOR_API_KEY`. **Nunca escreva a chave no código nem a mostre em respostas.**
- Local: repositório/pasta de trabalho. Cloud: lista de repositórios.
- Node.js 22.13 ou superior (fonte: https://cursor.com/docs/api/sdk/typescript).

## Passo a passo

1. Se o usuário já escolheu o SDK, vá direto à implementação, sem justificativas de venda.
2. Se o problema cabe no SDK mas ele não o citou, faça **uma** pergunta curta sobre o runtime e espere.
3. Escolha **um** padrão de chamada (abaixo) e não misture.
4. **Runtime explícito:** `local: { cwd }` ou `cloud: { repos: [...] }`. Omitir os dois faz o SDK usar local sem aviso.
5. Passe `apiKey` explicitamente em código compartilhado.
6. **Modelo:** obrigatório antes do primeiro `send()` no local; opcional no cloud (o servidor escolhe). Liste com `Cursor.models.list()` antes de fixar um `id`.
7. Toda criação/retomada de agente em `try/finally`, liberando o agente.
8. Chame `wait()` no run, **mesmo com streaming**, para obter o resultado final.
9. Antes de `cancel()` ou `conversation()`, confira `run.supports("cancel")` / `run.supports("conversation")` para o runtime em uso.
10. Separe os dois tipos de falha: **falhou ao iniciar** (exceção do SDK) × **falhou durante a execução** (`result.status === "error"`).
11. Registre `run.id` e `agent.agentId` logo depois do envio, antes do streaming.
12. Ao monitorar ou listar agentes, não confunda ID de agente com ID de run.
13. Se o usuário quiser painel ou visualização, sugira uma skill de canvas (dependência externa, não incluída aqui).

## Padrões de chamada

| Padrão | Quando | Descarte |
|---|---|---|
| `Agent.prompt(texto, opções)` | uma chamada, sem streaming nem continuação | automático |
| `Agent.create(opções)` + `agent.send(texto)` | vários turnos, streaming, cancelamento | `await agent[Symbol.asyncDispose]()` ou `await using` (exige suporte no `tsconfig`) |
| `Agent.resume(id, opções)` | retomar em outro processo | igual ao anterior |

Em `Agent.resume`, o runtime é inferido pelo ID: prefixo `bc-` é cloud; o resto é local. Servidores MCP passados em linha **não persistem**: repasse-os no `resume`.

## Opções principais

- `apiKey`.
- `model: { id }` (e `params`). Descubra valores válidos com `Cursor.models.list()`. Identificadores como `auto-smart` aparecem nos exemplos da documentação; confira a lista antes de usar.
- `local: { cwd, settingSources }`: `settingSources` aceita valores como `"project"`, `"user"` e `"plugins"`. Sem efeito em cloud.
- `cloud: { repos: [{ url, startingRef }], autoCreatePR, skipReviewerRequest }`: `skipReviewerRequest` (padrão `false`) evita pedir revisão ao usuário, útil em CI. `repos` vazio permite agente sem repositório.
- `mcpServers`: servidores MCP em linha; também aceitos em `send()`.

## Objetos e métodos

- Agente: `agent.agentId`, `agent.send(...)`, `agent[Symbol.asyncDispose]()`, `agent.close()`.
- Run: `run.id`, `run.stream()` (gerador assíncrono de eventos; eventos do tipo `assistant` trazem `message.content` com blocos `type: "text"`), `run.wait()` (resultado final com `status` e `result`), `run.cancel()`, `run.conversation()`, `run.supports(op)`, `run.unsupportedReason(op)`. Operações: `stream`, `wait`, `cancel`, `conversation`.
- Consulta: `Agent.get(id)`, `Agent.getRun(runId, opções)` (no cloud exige `agentId`), `Agent.list(opções)` (devolve `{ items, nextCursor? }`), `Agent.listRuns(agentId)`.
- Modelos: `Cursor.models.list()`.
- `run.status`: `running`, `finished`, `error`, `cancelled`.

## Erros e códigos de saída

Veja `references/erros.md`. Resumo: erros do SDK (`CursorAgentError` é alias de `CursorSdkError`) têm `isRetryable`; falha de execução vem em `result.status`.

Convenção sugerida para scripts: `0` só para `finished`; `1` para erro do SDK; `2` para `status === "error"`; `3` para `cancelled`.

## Esqueleto (escrito para esta skill)

```ts
import { Agent, Cursor } from "@cursor/sdk";

const apiKey = process.env.CURSOR_API_KEY;
if (!apiKey) throw new Error("Defina CURSOR_API_KEY");

const agent = await Agent.create({
  apiKey,
  model: { id: process.env.CURSOR_MODEL_ID ?? "" }, // valor vindo de Cursor.models.list()
  local: { cwd: process.cwd() },
});
try {
  const run = await agent.send("Liste os TODOs do repositório");
  console.error("agente", agent.agentId, "run", run.id);
  for await (const evento of run.stream()) {
    if (evento.type === "assistant") {
      for (const bloco of evento.message.content) if (bloco.type === "text") process.stdout.write(bloco.text);
    }
  }
  const resultado = await run.wait();
  process.exitCode = resultado.status === "finished" ? 0 : resultado.status === "error" ? 2 : 3;
} finally {
  await agent[Symbol.asyncDispose]();
}
```

## Resposta ao usuário

Padrão escolhido, runtime, e **o que não foi executado** (por exemplo, sem chave real para testar). Sucesso = o script roda do início ao fim com chave real; sem chave, o usuário é avisado de que o teste não foi feito.

> ⚠️ Verificar na doc oficial: (1) o **valor padrão de `model`** não é declarado na documentação; os exemplos usam `composer-2.5` e `auto-smart`, e a especificação interna citava `composer-2`: não fixe valores, consulte `Cursor.models.list()`. (2) O nome do produto na API é **Cursor** (`Cursor.models.list()`); o nome "Codex" que aparecia em alguns textos de origem não consta na documentação oficial. (3) `settingSources: "all"` (da especificação) não foi confirmado; a doc cita `"project"`, `"user"`, `"plugins"`. (4) MCP em cloud somente via HTTP acessível pela rede: não confirmado. (5) Comportamento de `Agent.getRun` e `stream()` em runs desanexados: pode não suportar streaming nem conversa. (6) Chaves de administrador de time ainda não são suportadas; chaves de usuário e de conta de serviço funcionam.
