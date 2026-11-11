---
name: storage-timeout-profiling
description: Use when storage-heavy tests time out.
---

# Investigar timeout com storage dublado

- Reproduza o cenário isolado e compare com a execução em suíte; um verde isolado não elimina custo algorítmico amplificado por concorrência.
- Antes de editar, meça contagem e tempo nas fronteiras de leitura, escrita e cópia profunda. Separe custo de notificações do custo de leitura; não presuma que o dublê é culpado por usar cópias.
- Procure leitura integral dentro de um laço sobre os mesmos registros: N chamadas de storage copiando N registros são custo quadrático mesmo sem trabalho elegível.
- Não otimize removendo isolamento de objetos do helper, relaxando timeout, reduzindo carga ou criando cache entre casos. Isso pode ocultar custo real e quebrar semântica.
- Para uma saída antecipada baseada em snapshot, preserve terminais com telemetria pendente e a revalidação individual quando houver trabalho. Verifique todos os escritores concorrentes antes de assumir monotonicidade de prazos.
- Escreva regressão determinística sobre a contagem de operações, acompanhada de verificações de prazo e conclusão. Evite asserção de milissegundos dependente da máquina.
- Confirme RED, GREEN e sabotagem restaurada. Execute os consumidores reais do helper e os testes de concorrência/reinício.
- Guarde sondas e logs no scratch autorizado, retire instrumentação do diff final e reporte separadamente medidas instrumentadas, duração normal e latência de produção não medida.
