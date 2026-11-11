# Refinar contratos de backend sem antecipar implementação

Use ao transformar uma experiência já aprovada em especificação técnica. As alternativas abaixo são perguntas de desenho, não escolhas padrão já autorizadas.

## 1. Recon direcionado às decisões

Delegue exploração somente leitura por caminho: schema e migrations sucessivas; autorização e grants; consumidores de leitura; persistência principal e fallback; histórico e reexecução. Peça referências de arquivo e linha. Confira diretamente os pontos usados para recomendar uma mudança; um relatório de recon não prova corrida reproduzida nem estado de produção.

Trace quem cria o registro e quem consegue encontrá-lo depois. Um cadastro gerencial pode existir sem estar visível à equipe por depender de vínculo prévio. Antes de ampliar leitura, explicite quais campos serão compartilhados e quais objetos relacionados continuarão privados.

Diferencie vínculo ao cadastro corrente de snapshot documental. Renomear uma entidade pode mudar o rótulo consultado em histórico sem reescrever os documentos históricos. Pergunte qual garantia o produto exige antes de propor versionamento completo.

## 2. Entrevista em ordem de dependência

1. **Acesso e ciclo de vida:** quem lê cada campo; quem escreve; o que arquivar impede; o que acontece com operações já persistidas ou ainda em preparação.
2. **Concorrência e recuperação:** perda de atualização, comparação de versões, resposta perdida e repetição da mesma intenção versus novo cadastro deliberado. Não confundir unicidade por nome com idempotência.
3. **Busca e validação:** correspondência parcial, acentos, ordenação, paginação, normalização e compatibilidade com registros legados. Separe validar endereço de consultar endereço ou disparar enriquecimento.
4. **Retenção e autoria:** última alteração versus trilha completa; duração do registro de operação; rascunho em memória versus persistência local. Explique o que se perde ao recarregar e o que ainda pode ser recuperado.
5. **Arquitetura e aceite:** apresente contratos que realizem as decisões, testes e limites da garantia; só então peça confirmação do plano completo.

Enquanto recon estiver pendente, pergunte apenas decisões independentes dele. Não peça ao usuário para descobrir fatos consultáveis no código.

## 3. Converter decisões em contratos verificáveis

- Defina a fronteira transacional de mudanças de estado; checar elegibilidade antes de uma chamada lenta não impede mudança concorrente antes da gravação. Cubra persistência alternativa e reexecução, não apenas o caminho principal.
- Especifique chave, escopo, entrada incompatível, retenção e autorização no replay de operações. Uma operação aplicada e seu estado atual são respostas diferentes; outra pessoa pode ter alterado o registro depois.
- Distinga conflito de versão de resultado incerto de rede. Repetir uma alteração sem identificador de operação pode parecer conflito mesmo quando a primeira tentativa funcionou.
- Explique se paginação é leitura viva ou snapshot. Ordenação estável e desempate não garantem snapshot quando nomes mudam entre páginas; documente atualização e deduplicação em vez de prometer estabilidade absoluta.
- Não converta exceção SQL em código HTTP presumido. Inclua mapeamento explícito de erros no contrato e testes do transporte utilizado.
- Não invente autoria histórica para preencher metadados novos. Migração deve representar desconhecido como desconhecido.
- Em histórico dentro de um detalhe, correlacione cada resposta com a entidade selecionada e invalide consultas anteriores; cancelamento sozinho não impede uma resposta já resolvida de contaminar a próxima seleção. Diferencie vazio de falha inicial e preserve páginas carregadas quando falhar o carregamento adicional.
- Especifique o efeito de atualizar sobre paginação e expansões; reiniciar a lista e preservar a posição são experiências diferentes. Defina o tratamento de data de ordenação ausente antes de prometer recência determinística para registros legados.

## 4. Documentos gerados por IA

1. **Verifique o caminho inteiro antes de prometer completude.** Trace captura, montagem da entrada, recortes como `slice`, prompt, configuração efetiva no chamador, adaptador, validação, constraint SQL, leitura e cópia. Aumentar saída não recupera entrada descartada; um padrão compartilhado não é necessariamente o orçamento usado pelo handler.
2. **Feche a origem de cada afirmação.** Separe fatos da conversa, referência de conhecimento, metadados registrados e sugestões novas. Participante declarado não comprova presença; conhecimento do Playbook não comprova assunto discutido. Se sugestões forem permitidas, defina rótulo e fontes e impeça que virem compromisso automaticamente.
3. **Separe profundidade de tamanho obrigatório.** Defina seções vazias, cobertura esperada, limites de entrada/saída, métrica de caracteres, orçamento de tokens e comportamento em corte ou timeout. Não apresente caracteres e tokens como equivalentes nem teto de saída como garantia de caber no tempo. Use ensaio real como gate ainda pendente, não como capacidade já medida.
4. **Confronte preservação com a escrita real.** Quando o usuário pedir histórico intacto ou imutabilidade, inspecione upsert, reexecução e RPC, não só a prevenção no botão. Se o primeiro resultado vencer, autorize o replay, proteja a gravação concorrente e devolva os valores canônicos persistidos, não o texto ou horário produzidos pela tentativa perdedora. Não confunda evitar sobrescrita com evitar cobrança duplicada de modelo.
5. **Separe geração nova de leitura legada.** Regras novas de títulos e estrutura podem ser obrigatórias para gerar sem invalidar documentos antigos. Especifique formato persistido, renderização segura e cópia integral por superfície; não acrescente um botão inexistente sob o nome de correção de compatibilidade.
6. **Planeje consumidores antes de emitir código novo.** Um motivo de erro novo exige rastrear enums, constraints, RPCs, validadores, filas e listas fechadas da interface. Defina ordem de publicação e compatibilidade com versões antigas; testar apenas o produtor não prova que a lista continuará legível.

- Distinga limite de conteúdo do teto de transporte: unidades UTF-16, pontos de código, bytes UTF-8 e escapes JSON não são equivalentes. Dimensione o corpo HTTP com envelope e teste multibyte/escapes antes de prometer aceitar o limite funcional.
- Antes de trocar uma RPC de upsert para primeiro resultado vence, faça o handler devolver o registro canônico persistido e confirme a drenagem das versões antigas; caso contrário ele pode combinar ID vencedor com conteúdo não salvo. Teste também os estados intermediários do rollout.
- Confira migrations posteriores antes de concluir que enum/CHECK/RPC não reconhece um motivo: o descompasso pode estar somente nos validadores e consumidores. Reconcilie o caminho inteiro sem repetir migration já publicada.

## 5. Métricas derivadas e instrumentação

1. **Defina o que o número comprova antes de escolher o detector.** Identifique unidade, origem, relógio e agregação: horário de chegada não é duração; canal não é pessoa; áudio capturado não comprova fala transmitida ou ouvida. Confira essas fronteiras no caminho real antes de formular a rodada.
2. **Feche silêncio, sobreposição e falta de cobertura separadamente.** Pergunte se eventos simultâneos contam em ambos e se a soma precisa coincidir com o total. Distinga zero observado, medição parcial e indisponibilidade; não transforme interrupção de captura em ausência do evento.
3. **Separe coleta, persistência e exibição.** Uma métrica pode ser calculada independentemente da IA, mas exibida somente quando um documento derivado existir. Faça essa escolha explicitamente e não use a falha da geração para inventar ou descartar medições já conhecidas.
4. **Modele recuperação sem dupla contagem.** Para acumuladores, especifique snapshots absolutos, identidade da captura, revisão e política de finalização/replay. Defina o que uma queda perde desde o último checkpoint, preserve qualidade parcial e não renove retenção a cada tentativa.
5. **Não prometa conhecimento que a superfície não possui.** O navegador pode conhecer sua fila local; o painel remoto sem registro não sabe se há sincronização pendente. Use indisponibilidade sem causa presumida e defina quando a próxima consulta pode refletir o envio.
6. **Separe meta de precisão de resultado medido.** Registre tolerância absoluta/relativa, unidade, conjunto rotulado e testes negativos como critérios propostos. Preserve invariantes de privacidade também nos testes: proibir áudio persistido inclui fixtures, logs e artefatos novos, não só o banco de produção. Dependência especializada e relaxamento de CSP são decisões explícitas quando alteram restrições do projeto; compatibilidade e desempenho permanecem gates até execução real.

## 6. Fechar a spec

Registre por componente: contrato, autorização, falhas, concorrência, compatibilidade e teste correspondente. Diferencie detalhe interno a escolher com testes de decisão de produto ainda aberta; não declare entrevista concluída enquanto a segunda categoria existir.

Exija teste com duas conexões para alegar garantia de corrida; testes sequenciais verificam estados, não interleavings. Para busca e listagem, cubra mais de uma página e nomes repetidos. Para acesso, cubra chamada direta, não só botões ocultos.

Após aprovação final, remova propostas superadas e blocos de pendências resolvidas. Verifique a sequência das decisões e a coerência do estado inicial do documento. Relate quais arquivos foram escritos e quais superfícies externas continuam sem atualização; não narre teste de implementação quando a entrega foi apenas documental.
