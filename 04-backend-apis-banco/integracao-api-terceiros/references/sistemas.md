# Particularidades por sistema

## Clinicorp — contrato público, sem homologação autenticada

- Swagger oficial: `https://api.clinicorp.com/api-docs/`. A OpenAPI está embutida em `swagger-ui-init.js`, na propriedade `swaggerDoc`; parseie o JSON em vez de adivinhar um endpoint de spec.
- Autenticação: o esquema tem nome `bearerAuth`, mas declara `type: http`, `scheme: basic`. Username é o ID do usuário API; password é o Token API. Confira o contrato vigente antes de usar.
- Busca consultiva: `GET /patient/get` usa `subscriber_id`, `PatientId` e `Phone` (capitalização literal). A descrição de `Phone` aceita formatos com/sem DDI e pontuação; isso não prova unicidade da pessoa.
- Agenda: `GET /appointment/list` requer `from`/`to`; `subscriber_id` seleciona o assinante em contas de grupo e `businessId` filtra a clínica. Omitir o filtro pode consultar todas as clínicas do assinante. Não confunda o ID interno do tenant com o filtro do provedor.
- Orçamentos: `GET /estimates/list` requer `subscriber_id`, `from`/`to`, com intervalo máximo documentado de 31 dias; `clinic_id` filtra a unidade. `GET /estimates/get` usa `treatment_id`.
- `Status=APPROVED` e `ApprovedDate` são candidatos documentais à mensuração de fechamento, não prova de pagamento. Comparecimento exige mapear os status reais retornados para a clínica; confirmação de agendamento não prova presença.
- **Nunca tratar todo GET como seguro:** `GET /appointment/change_status` é mutação. Restrinja os probes aos endpoints consultivos aprovados.
- A documentação consultada não forneceu uma cota de requisições. Obtenha limite contratual do fornecedor e faça coleta funcional com volume autorizado; não descubra quota saturando uma API clínica em produção.
- Esses pontos descrevem documentação pública; não equivalem a validação de credenciais, consulta a pacientes nem homologação do tenant.

## si9 Sistemas

- Spec: `https://apiv2.si9sistemas.com.br/api-prd/q/openapi?format=json` (Swagger em `/docs/#/`).
- Base: `https://apiv2.si9sistemas.com.br/api-prd`. A antiga `api.si9sistemas.com.br/imobilsi9-api`
  com `/oauth/token` é a coleção Postman obsoleta.
- Auth: header `X-Api-Key: Bearer <token>`, **com** a palavra Bearer. Sem ela, ou usando
  `Authorization`, dá 401. O token já carrega o tenant e é gerado no painel (Conexões → API Si9).
- Permissões por token: `LIST_LEADS` (GET /lead), `CADASTRAR_LEADS` (POST /lead e
  /lead/{id}/contacts), `LIST_IMOVEIS` (/property). Se faltar, 403.
- `POST /lead`: obrigatórios `name`, `classification` (high/medium/low/future) e `source`.
  `phones: [{phoneNumber, phoneType: comercial|residential}]`, `emails: ["..."]`, `interestedIn:
  buy|rent`.
- **Telefone só com dígitos** (`45999999999`). Com `+`, espaço ou parênteses a API devolve 500
  `Range [0, 2) out of bounds for length 1` e não cria nada.
- **Normalização de 9º dígito obrigatória para celular BR:** a busca de upsert da Si9 compara a string exata do telefone (`phoneNumber`). Enviar celular com 10 dígitos (DDD + 8 dígitos) quando o cadastro no Si9 já existia com 11 dígitos (ou vice-versa) falha no casamento e cria um lead duplicado com novo ID. Normalize no fluxo para 11 dígitos antes de disparar.
- Upsert por telefone/e-mail: cada reenvio concatena `observation` e soma um contato no histórico.
- **Reconversão x falso duplicado:** quando um lead já existente reconverte com o mesmo telefone/e-mail, o Si9 reaproveita o ID, mas reseta o status para `"novo"` e atualiza `lastContact`. Isso reativa a notificação/roleta dos corretores e gera a falsa percepção de duplicidade na operação, quando é reengajamento legítimo.
- **Sem logs ou auditoria na API:** a Si9 não expõe endpoints de logs, auditoria ou monitoramento de tráfego, nem tela de histórico no painel web. Todo diagnóstico de falhas, rejeições ou duplicidades deve ser feito a partir dos dados de execução gravados na origem (n8n runData / respostas HTTP).
- Atribui o lead a um corretor automaticamente. Não existe DELETE: lead de teste é excluído pelo
  painel da imobiliária.
- Use `GET /lead?phone=` antes da escrita e depois do webhook para comprovar o cadastro.
  Trate o retorno efetivo: a busca pode devolver `[]` quando não há correspondência e uma lista
  de leads quando há, apesar de a spec descrever um objeto único. Não presuma `.get("id")` na raiz.
- Compare o POST com o GET ao verificar contatos: o POST retorna `phones` e `emails`, enquanto
  a busca pode retornar `cellNumber`, `phoneNumber` e `email` nulos e omitir os arrays. Confira
  ID, nome e marcador da observação no GET; use a saída do nó HTTP para comprovar os arrays
  aceitos. Não classifique campos nulos da busca como perda de telefone/e-mail sem outra evidência.
- A spec pública v2 consultada não expõe pipeline/funil nem etapa: o schema `Lead` não tem esses campos e os paths cobrem apenas leads, contatos e imóveis. Não adicione `pipelineId`/`stageId` por suposição. Para direcionamento a funil/etapa, verifique configuração no painel do si9 ou obtenha contrato documentado do suporte.
