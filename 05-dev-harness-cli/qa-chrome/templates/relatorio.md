# Relatório QA — <run_id>

Alvo: <label> `<ref>` SHA `<sha>` (base `<branch>` @ `<base_sha>`)
Aprovação do checklist não autoriza merge/deploy nem prova cobertura total.

## Suítes automatizadas (Hermes)
| Comando | Exit | Log | Observação |
|---|---|---|---|

## Runtime observado
Provider, modelo e esforço efetivos; não confundir configuração com probe executado.

## Reprodução independente pelo principal
Comandos, SHA, saídas e exit codes; separar auto-relatos ainda não auditados.

## Cenários — categoria de prova explícita
Separar unidade, UI com API simulada e integração/backend real. Incluir traces/capturas efetivamente abertos; arquivo existente não equivale a auditoria.
| ID | Resultado | Observado | Evidência (verificada?) | Esperado vs obtido | Reprodução | Intervenção do usuário |
|---|---|---|---|---|---|---|

## Pendências e ação necessária do usuário

## Ambiente mantido
URLs, processos/containers, worktrees, bancos de QA, logs, comandos de encerramento (específicos).

Gerar a base com `scripts/qa_artifacts.py report --run-dir <dir>`; complementar à mão sem inventar resultados.
