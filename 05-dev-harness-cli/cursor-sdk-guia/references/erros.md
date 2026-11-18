# Erros do SDK e códigos de saída

## Dois tipos de falha

| Tipo | Como aparece | O que significa |
|---|---|---|
| Falha ao iniciar | exceção do SDK (`CursorAgentError`, alias de `CursorSdkError`) | a execução nunca começou (autenticação, configuração, rede) |
| Falha da execução | `result.status === "error"` depois de `wait()` | o agente rodou e falhou no meio |

Todos os erros do SDK têm a propriedade somente leitura `isRetryable`. Quando `true`, tentar de novo é seguro; é `false` para `agent_busy`.

## Subtipos e o que fazer

| Erro | Ação |
|---|---|
| `AuthenticationError` | gere uma chave nova e confirme a permissão; cheque espaços em volta, chave de outro ambiente, ou acesso do usuário ao repositório (cloud) |
| `RateLimitError` | recue com atraso exponencial; se for teto mensal, aumente o limite do plano |
| `ConfigurationError` | rode `Cursor.models.list()` para validar `id`/`params` do modelo; confira repositórios e caminhos |
| `AgentBusyError` | espere o run ativo, cancele com `run.cancel()` ou consulte `Agent.listRuns()`; tentar de novo na hora continua falhando |
| `IntegrationNotConnectedError` | abra `error.helpUrl`, reconecte o provedor e repita; registre `helpUrl` em log (a mensagem padrão não o inclui) |
| `NetworkError` | repita com recuo; guarde `error.requestId` para suporte |
| `UnsupportedRunOperationError` | cheque `run.supports(op)` ou `run.unsupportedReason(op)` antes |
| `AgentNotFoundError` | confira o ID do agente, `cwd` e `local.store` |
| `UnknownAgentError` | inspecione `error.code` e `error.cause` |

## Códigos de saída sugeridos (convenção desta skill)

| Código | Quando |
|---|---|
| 0 | `status === "finished"` |
| 1 | exceção do SDK |
| 2 | `status === "error"` |
| 3 | `status === "cancelled"` |

## Padrão de tratamento

```ts
try {
  const run = await agent.send(prompt);
  const resultado = await run.wait();
  process.exitCode = resultado.status === "finished" ? 0 : resultado.status === "error" ? 2 : 3;
} catch (e) {
  const err = e as { isRetryable?: boolean; helpUrl?: string; message?: string };
  console.error("Falha ao iniciar:", err.message, err.helpUrl ?? "");
  process.exitCode = 1;
}
```

> ⚠️ Verificar na doc oficial: a lista de subtipos pode crescer; confirme em `https://cursor.com/docs/api/sdk/typescript`.
