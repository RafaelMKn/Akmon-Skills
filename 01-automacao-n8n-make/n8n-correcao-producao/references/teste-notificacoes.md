# Teste controlado de notificações WhatsApp

## Procedimento

1. Leia o nó live de envio e identifique host, instância remetente, autenticação, destinatário e ações anteriores. Não reproduza o webhook completo se ele cadastra lead, grava CRM ou notifica grupo antes do ponto que precisa ser testado.
2. Confirme um destinatário autorizado. Para “meu número”, procure documentação ou contato previamente identificado; se houver registros conflitantes, confirme o número encontrado antes de enviar. Não deduza identidade apenas por um telefone válido.
3. Defina a camada testada: chamada direta ao provedor verifica o transporte; executar o caminho n8n verifica também credencial, expressão e roteamento. Escolha o menor teste autorizado e relate essa limitação explicitamente.
4. Envie uma única mensagem com marcador `[TESTE]`, explicando que não é lead real. Preserve o remetente do sistema que está sob teste, mas não use essa autorização para enviar comunicação pessoal em nome do usuário: “pelo meu WhatsApp” exige uma sessão cujo remetente seja o dele.
5. Grave imediatamente HTTP, ID da mensagem, horário e status inicial em evidência sanitizada. Se ocorrer timeout ou resposta ambígua, procure a mensagem antes de tentar de novo: o provedor pode ter enviado apesar de a resposta não ter chegado.
6. Releia a mensagem pelo ID exato. Na Evolution v2, o caminho exercitado é `POST /chat/findMessages/<instância>` com `{"where":{"key":{"id":"<ID>"}},"page":1,"offset":10}`; essa operação consulta, não envia. Confira o ID, `key.fromMe`, o texto e que o destino não é grupo. Confirme o contrato na versão instalada antes de reutilizar.
7. Relate a prova em camadas: HTTP de sucesso significa aceitação; consulta por ID significa registro persistido; `PENDING` ou status ausente não significa entrega. Confirmação do destinatário prova recebimento daquela mensagem, não recuperação contínua nem execução dos dois workflows.
8. Atualize o relatório existente com a confirmação recebida e deixe explícito o que falta para o fluxo completo. Não mantenha “recebimento pendente” após o destinatário confirmar, nem feche o incidente só com teste direto do provedor.
9. Ao limpar, remova exports e evidências temporárias que contenham dados pessoais ou headers. Preserve os backups de rollback e o relatório sanitizado; não apague credenciais que os fluxos já referenciam.

## Confirmar entrada enviada pelo usuário

1. Consulte `list-executions --workflow-id <ID> --limit 5` no workflow esperado e no legado quando houver cutover. Depois use `get-execution <EXEC_ID> --include-data` para conferir o conteúdo real; uma execução recente pode ser Schedule Trigger, não a mensagem procurada.
2. Extraia somente texto, instância, `key.fromMe`, ID da execução, horário com fuso, nomes dos nós executados e erro do último nó. Não imprima o payload inteiro da Evolution: `messageContextInfo`, `messageSecret`, headers e identificadores não necessários não ajudam o diagnóstico e expõem dados.
3. Compare mensagem e direção com o envio relatado. Informe separadamente: chegou ao webhook, passou pelo gate, chamou agente e executou envio. `status: success` com término em Switch não comprova atendimento: o Switch pode encerrar com todas as saídas vazias.
4. Se terminar em Switch sem saída, leia as regras do JSON usado naquela execução, o telefone normalizado a montante e os arrays de `runData[<Switch>].data.main`. Compare os operadores e cada saída; regra `startsWith` com dois prefixos e sem fallback é allowlist, não prova de que pontuação ou conteúdo foram bloqueados.
5. Para alteração autorizada de allowlist, preserve o resto do grafo e sincronize ordem das regras com `connections[<Switch>].main`. Remover uma regra desloca os índices das saídas. Teste localmente contatos preservados, adicionados, removidos e desconhecidos; só a próxima mensagem natural prova o caminho em produção.
6. Preserve os dígitos fornecidos para novos contatos. Remova apenas a apresentação visual necessária ao prefixo; não acrescente nono dígito por plausibilidade. Se houver conflito entre telefone informado e JID observado, reporte antes de alterar a autorização.
7. Após a próxima mensagem, confirme se ultrapassou o gate. Se falhar no nó seguinte, relate que a correção de roteamento foi comprovada e nomeie o novo bloqueio, sem declarar o atendimento resolvido. Erro genérico de conexão sugere investigar host/rede/credencial, mas não prova sozinho qual deles é a causa.

## Critério de pronto

Exija execução natural posterior ao patch para homologar o workflow. Quando o teste foi direto na Evolution, registre apenas que o transporte foi testado; uma chave usada em uma chamada direta não prova que a credencial recém-vinculada no n8n será resolvida corretamente.

## Fronteira entre fluxo e provedor

Investigue erros internos no source da versão realmente instalada antes de propor alteração de número, sufixo JID, retry ou troca de remetente. Uma consulta de número bem-sucedida agora comprova o estado atual, não explica uma indisponibilidade histórica. Não aplique workaround sem reproduzir a causa; os logs do serviço são a próxima evidência quando o erro aponta para estado interno da sessão.
