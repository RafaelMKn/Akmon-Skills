---
name: integracao-api-terceiros
description: "Use when integrating a client's CRM/ERP API."
version: 0.2.0
author: <autor>
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [api, integracao, crm, openapi, n8n, clientes]
    related_skills: [n8n-flow-builder, n8n-correcao-producao]
---

# Integração com API de terceiro (CRM/ERP de cliente)

Vale para quando um fluxo envia ou lê dados do sistema do cliente: CRM imobiliário, ERP,
plataforma de leads. O fluxo n8n em si segue `n8n-flow-builder` ou `n8n-correcao-producao`. Esta
skill cobre o contrato com a API externa.

## When to Use

- "Ta aí a doc da API, o que estávamos fazendo de errado?"
- Montar ou consertar um HTTP Request para o CRM, ERP ou plataforma de leads de um cliente.
- Erro 401, 403 ou 500 vindo de uma API externa de cliente.

## Procedure

1. **Identificar o dono do projeto.** Parte dos clientes é de agência parceira (ex.: <agencia>), não da
   <empresa>. Todo nome que vai parar no sistema do cliente (dado de teste, `source`, remetente) usa
   a agência dona. **Nunca escreva o nome da <empresa> em projeto de outra agência**, porque o cliente final
   vê esse nome.
2. **Achar a especificação real.** Doc enviada pelo cliente > coleção Postman antiga > o que já
   estava no fluxo. Postman de terceiro costuma estar defasado, e base URL, auth e formato do body
   mudam juntos.
   - URL de Swagger UI (`.../docs/#/`) não traz a spec no HTML. Rode `curl -s <url>` e procure
     `url:` dentro do `SwaggerUIBundle({...})`. Quarkus serve em `/q/openapi?format=json`.
     Chutar `swagger.json` ou `api-docs` só devolve 500.
   - Salve a spec no scratch e leia `info.description` inteira: header de auth, permissões,
     chave de deduplicação e regras de upsert costumam estar só ali, não nos paths.
3. **Comparar com o que estava sendo feito:** tabela antes × depois de base URL, auth e body. É a
   resposta para "o que estávamos fazendo de errado".
4. **Validar a credencial com endpoint comprovadamente consultivo** (ex.: busca por telefone
   inexistente). GET não garante leitura: algumas APIs expõem mutações em GET. Monte uma allowlist
   pela semântica documentada antes do probe. Leia `type`/`scheme` do security scheme; o nome
   `bearerAuth` pode rotular autenticação Basic. Teste apenas variantes fundamentadas na doc;
   o status (200 × 401 × 403) mostra qual vale e se falta permissão.
5. **Escrita em produção só com liberação explícita.** Antes, mostre que o POST grava no sistema
   real e peça o OK. Depois:
   - GET pela chave de deduplicação (telefone/e-mail) e confirmar que volta vazio. Em API com
     upsert, o POST atualizaria um registro real.
   - Registro marcado como teste: `TESTE INTEGRACAO <AGENCIA> - NAO ATENDER`,
     `source: Teste Integracao <Agencia>`, e-mail `@example.com`, telefone fictício.
   - Se der 500, isole o campo: mande o payload mínimo e reinclua um campo por vez.
6. **Verificar o caminho completo antes de relatar.** Se o pedido é testar um fluxo, dispare sua
   entrada real (ex.: webhook), não um POST direto ao CRM que contorna transformação e credenciais.
   - Envie uma única requisição e guarde um marcador único no registro de teste. HTTP 200 com
     `Workflow was started` confirma somente o aceite, não a conclusão.
   - Consulte as execuções do workflow e leia a execução com dados: confira status, nós percorridos,
     payload transformado e resposta do nó de escrita. Se a primeira listagem vier vazia, consulte
     novamente sem reenviar o webhook; a execução pode ainda estar terminando.
   - Faça GET no CRM pela chave de deduplicação ou ID e confira o marcador e os campos retornados.
     Compare com a resposta do POST quando o GET tiver representação reduzida; campo ausente ou
     nulo em uma projeção não prova perda do dado.
   - Separe cadastro comprovado de distribuição/funil/etapa: só afirme o direcionamento quando
     houver evidência da API ou do painel. Não introduza um funil específico que não veio do pedido
     nem de uma fonte consultada.
7. **Relatar:** status e ID da execução, ID do registro criado, campos comprovados, destinatário
   atribuído quando retornado, e limpeza pendente. CRM de imobiliária costuma distribuir o lead
   para um corretor real, então identifique o teste e informe quem precisa excluir pelo painel.
8. Registre as particularidades do sistema em `references/sistemas.md` (uma seção por sistema).

## Pitfalls

- **Upsert repete efeito colateral:** reenviar o mesmo lead pode concatenar observação e somar
  histórico. Deduplique o disparo no fluxo, não conte com a API.
- **Telefone formatado quebra parser de API brasileira:** normalize para só dígitos no fluxo antes
  de enviar, a menos que a spec exija outro formato e um teste comprove.
- **Variação de 9º dígito pode gerar duplicata em upsert por string:** confirme o contrato e o tipo de número antes de normalizar. Não acrescente o nono dígito cegamente a telefone fixo ou ambíguo; variantes candidatas e telefone compartilhado exigem revisão quando houver risco de vincular pessoas distintas. Regras específicas comprovadas ficam em `references/sistemas.md`.
- **API opaca sem logs exige rastreio na ponta integradora:** CRMs sem endpoint ou tela de log de integração exigem inspeção nos dados brutos de execução da ferramenta disparadora (payload enviado e corpo de erro HTTP) e checagem cruzada via GET.
- **Não faça POST repetido no mesmo registro para testar formatos:** cada tentativa vira histórico
  no CRM do cliente. Use um registro vazio novo por variação.

## Verification

- A spec foi baixada e a fonte citada (URL da spec).
- A credencial foi validada por GET, com o código de status registrado.
- A escrita foi testada com um registro de teste identificado pela agência dona, e o ID foi
  reportado junto com o caminho de limpeza.

Particularidades por sistema: `references/sistemas.md`.
