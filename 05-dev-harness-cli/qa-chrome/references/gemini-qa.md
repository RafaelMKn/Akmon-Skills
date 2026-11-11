# Briefing padrão — Gemini 3.8 Flash high

Antes de delegar, conferir a rota efetiva; nome/esforço no prompt não configuram runtime. Preencher o briefing com valores observados, nunca deixar placeholders no envio.

## Conteúdo obrigatório do briefing
- PT-BR; repo, worktree novo, pasta de artefatos fora do repo, portas e nomes de recursos exclusivos.
- Alvo/ref/SHA/base/base_sha completos e fonte do inventário; critérios, diff e instruções do projeto.
- Preparar E EXECUTAR: suítes reais e navegador isolado headless, não somente emitir relatório.
- Gate antes de qualquer script: destinos locais/sintéticos/sandbox comprovados, env novo sem segredo, integrações reais desligadas. Proibido usar banco/stack de terceiros.
- Ler comandos nos arquivos do projeto; rodar por terminal com logs e exit code real; sem mexer em código de produto.
- Playwright com trace em todas as execuções, relatório estruturado e capturas de estados-chave; registrar comandos e artefatos. Se houver simulação de API, identificar expressamente.
- Para cada critério: cenário/asserção → arquivo:linha → comando → resultado → evidência; não preencher lacunas com inspeção ou texto plausível.
- Marcar resultados do filho como não verificados pelo principal até auditoria. Nenhum arquivo de relatório autoriza encerrar a tarefa.
- Devolver run_dir, SHAs completos, URLs e prova de alvo servido, runtime observado, logs, traces, capturas, comandos de reprodução crítica, falhas/lacunas, recursos e stop_commands seguros.
- Sem Chrome pessoal, extensão Claude, publicação, push, merge, deploy, alteração de produção ou remoção automática.

## Prova exigida pelo coordenador
Conferir asserções e artefatos e reexecutar cenários críticos no mesmo SHA. Separar claramente evidência de execução independente de auto-relato. Registrar unidade, UI/API simulada e integração/backend real em seções distintas. Não aceitar como prova suficiente só log escrito, `.last-run.json`, captura sem contexto ou resumo do filho.
