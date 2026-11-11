# Versionar fluxo n8n em git e automatizar deploy

Quando existe repositório de fluxos (snapshots em `workflows/*.json`) e alguém pede "CI/CD",
"deploy automático" ou "push na main atualiza a instância". Leia antes de escrever qualquer
pipeline que escreva em n8n.

## A pergunta que decide tudo: o repositório é arquivo ou fonte de deploy?

Repositório de fluxo nasce quase sempre como **arquivo**: snapshot sanitizado para versionamento,
auditoria e histórico. Usá-lo como **fonte de deploy** é uma mudança de natureza, não um passo
seguinte — e costuma estar escrito no próprio `README.md` do repositório ("blocos de credenciais
removidos", "não está pronto para importação sem reconexão").

Antes de construir pipeline, leia o README do repositório e conte os blocos `credentials` nos
JSONs versionados. Zero credenciais = arquivo. Tratar arquivo como fonte de deploy é o erro que
esta página existe para impedir.

## Semântica do `PUT /api/v1/workflows/{id}` — medida, não suposta

- **`PUT` substitui o array `nodes` inteiro; não mescla.** Nó enviado sem bloco `credentials` tem
  o vínculo **apagado** na instância (`{'PG': {...}}` vira `{'PG': None}`). Deployar JSON
  sanitizado desconecta todas as credenciais de uma vez, e reconectar é trabalho manual na UI, nó
  por nó.
- **`PUT` preserva `active: true` e aplica imediatamente.** Fluxo ativo continua ativo já com o
  conteúdo novo. Não existe janela de revisão: merge vira mudança em produção no mesmo segundo.
- Exportar da instância **não** garante que os IDs de credencial sobrevivem ao caminho de volta —
  eles sobrevivem ao `get-workflow`, mas qualquer etapa de sanitização os remove.

### Prove a semântica destrutiva antes de automatizá-la

Antes de montar automação em cima de um verbo que escreve, teste o verbo numa **instância
descartável** (`<instancia>`) com workflow throwaway: crie, leia o estado, aplique a operação exatamente
como o pipeline aplicaria, releia, e **delete os workflows de teste conferindo que não sobrou
nenhum**. Cinco minutos de teste substituem uma discussão inteira sobre o que a API "deveria" fazer,
e o resultado vira evidência citável na decisão. Documentação de API não descreve efeito colateral
em campo omitido; medição descreve.

Nunca faça esse teste na instância do cliente, mesmo com fluxo de nome óbvio de teste.

## Arquitetura que funciona: CI valida e detecta drift, deploy fica manual

Sentido seguro do automatismo é **instância → repositório**, não o contrário:

| Job | Gatilho | Usa segredo? | Faz |
|---|---|---|---|
| validação | PR que toca `workflows/**` | não | JSON válido, zero `credentials`, zero segredo em claro, forma canônica |
| drift | agendado + manual | sim (leitura) | compara instância com repo; **abre PR**, nunca faz push na main |
| deploy | manual, fora do CI | sim (escrita) | dry-run por padrão, exige `--confirm` |

O motor do detector de drift deve rodar **local** também (`--instance <PREFIXO>`), porque pôr chave
de API de produção como Secret do GitHub é decisão de segurança do dono da conta, e o runner pode
nem alcançar a instância (restrição de IP em host próprio). Job agendado sem os Secrets configurados
sai **neutro com aviso**, não vermelho — job que falha por design todo dia é ruído que ninguém lê.

## Sanitização e rehidratação

Duas funções inversas, em scripts separados:

- **sanitize** (instância → repo): remove todo bloco `credentials` e os campos voláteis que poluem
  diff sem significar mudança — `updatedAt`, `createdAt`, `versionId`, `versionCounter`,
  `triggerCount`, `shared`, `meta`, `isArchived`, `pinData`, `staticData`. Saída determinística
  (`indent=2, sort_keys=True, ensure_ascii=False`): rodar duas vezes no mesmo input tem que dar
  byte-idêntico, senão o detector de drift acusa mudança onde não houve.
- **rehydrate** (repo → deploy): reinjeta os vínculos a partir de um mapa vindo de Secret/env.

**Mapeie credencial por TIPO de credencial, não por nome de nó.** Nome de nó muda com refactor e o
mapa quebra em silêncio; o tipo (`supabaseApi`, `postgres`, `redis`, `openAiApi`, `httpHeaderAuth`)
é estável, e num projeto típico cada tipo tem uma credencial só — dezenas de vínculos colapsam em
poucas entradas. Levante o mapa real dos snapshots **não sanitizados** e conte os vínculos por tipo;
esse número é o gabarito da verificação.

O rehydrate deve **falhar duro** (exit != 0) listando os nós órfãos quando algum nó que exigia
credencial ficou sem. Deploy parcial deixa o fluxo pior que antes de começar.

ID de credencial não é segredo, mas não vai para repositório: versione
`cred-map.example.json` com valores obviamente falsos e resolva o mapa real em tempo de deploy.

## Gates de PR que valem a pena

- parse de todo `workflows/*.json`;
- **zero blocos `credentials`** — protege a decisão de manter o repo sanitizado;
- **zero segredo em claro** (chave, token, telefone, e-mail), com os marcadores de redação já
  existentes na lista branca, senão o gate vira falso positivo permanente;
- **canonicidade**: re-rodar o sanitize no arquivo do repo tem que dar byte-idêntico, o que impede
  commit de JSON fora da forma canônica;
- resumo do job com tabela arquivo / nome / id / nº de nós / `active`.

Esses gates não precisam de Secret nenhum — rodam em runner limpo, inclusive em fork.

### O gate de canonicidade reprova os arquivos que já estão no repositório

Espere isso e avise antes: os JSONs versionados normalmente **não** estão na forma canônica (mantém
`updatedAt`/`createdAt`, ordenação de chaves diferente), então o gate falha no primeiro PR que tocar
`workflows/**`. Antes de chamar de bug, prove que a diferença é apenas de forma: compare os dois
lados ignorando ordem de chave e campos voláteis; se a única divergência de conteúdo for um campo
que o sanitize remove por lista branca (`description: null`, por exemplo), são semanticamente
idênticos e o gate está **certo** em reprovar.

Não normalize os arquivos no mesmo PR do CI: o diff fica enorme, se mistura com a revisão do
pipeline e atropela qualquer alteração recém-mergeada nos mesmos arquivos. Normalização é PR próprio,
feito de preferência conferindo contra a instância. Declare no corpo do PR que o gate vai falhar até
lá, e que isso é sinal correto — senão a próxima sessão "conserta" o gate afrouxando a regra.

### Calibre os dois lados do drift na mesma forma

O detector tem que passar **o arquivo do repositório pelo mesmo sanitizador** aplicado ao lado vivo
antes de comparar. Sem isso, repo cru (com `updatedAt`) contra instância sanitizada dá divergência
em 100% dos fluxos e o drift real de conteúdo fica invisível no meio do ruído. Isso não maquia o
problema de canonicidade, que continua sendo reportado pelo gate — só garante que o drift relatado é
sobre nós, conexões e settings.

Teste o motor com três fixtures locais, que rodam sem rede e sem instância de pé: instância idêntica ao
repo (não deve acusar), instância com um nó removido (deve acusar), e só `updatedAt`/`versionId`
alterados (**não** deve acusar). O terceiro caso é o que pega descalibração. Fixture local é também o
único caminho de verificação quando a instância está fora do ar — use, e diga no relato que a prova
contra a instância real ficou pendente, em vez de declarar o detector validado.

## Compare repo com instância antes de propor qualquer pipeline

O diagnóstico mais provável é que o repositório está **atrasado**. Compare `updatedAt` e contagem
de nós, fluxo a fluxo, antes de escrever uma linha de YAML:

- repo mais velho que a instância significa que um deploy automático **reverteria** trabalho já
  aplicado em produção — inclusive mudanças que dependeram de migration já rodada;
- divergência de contagem de nós entre live e repo é sinal de edição feita direto na UI, que
  ninguém trouxe de volta;
- a comparação em si já justifica o detector de drift, que é o entregável de valor real quando o
  deploy automático cai.

O GET de instância lenta (self-hosted) chega a 60–120s por fluxo e ocasionalmente devolve corpo
vazio: implemente retry e timeout generoso, e **não conclua que um fluxo sumiu** por causa de uma
resposta vazia.

## Verificação do próprio pipeline

Antes de abrir o PR, execute — e cole a saída real no corpo dele:

- **sanitize determinístico:** duas rodadas no mesmo input, byte-idêntico;
- **rehydrate completo:** contagem de vínculos por tipo batendo com o gabarito dos snapshots não
  sanitizados, nos quatro fluxos, não só no maior;
- **ida e volta:** `sanitize(rehydrate(x)) == x` byte a byte;
- **gate de segurança com teste negativo:** rode o validador contra um arquivo **rehidratado** (com
  credenciais e telefones reais) e exija `exit != 0`. Gate que nunca viu um caso ruim não está
  provado, e o rehidratado é o caso ruim que você já tem em mãos;
- **sintaxe dos YAML:** não precisa ficar sem prova só porque `pyyaml` não é stdlib — `js-yaml` via
  Node valida e mostra `on`, `jobs` e contagem de steps. Só declare "não validado" depois de tentar.

## Delegar a construção

Esse pipeline é trabalho de implementação: escreva a spec com o contexto já medido (semântica do
`PUT`, mapa de credenciais por tipo, tabela de divergência repo × instância) e delegue a escrita.
Na spec, marque explicitamente o que **já foi decidido** para o filho não re-decidir, dê permissão
de **leitura apenas** na instância de cliente, e exija verificação executada de verdade: ida e volta
`sanitize(rehydrate(x)) == x`, contagem de vínculos reinjetados batendo com o gabarito, e o detector
**encontrando o drift já conhecido**. Detector que não acha drift conhecido está errado, não
aprovado.

### Filho que morre no meio deixa trabalho em disco — colha antes de redelegar

Implementação longa consome cota: um filho de ~50 minutos pode cair por rate limit do provedor e
voltar como `status=failed` com resumo vazio. Isso **não** significa que nada foi feito — ele pode
ter commitado e feito push de quase tudo. Antes de reabrir a tarefa, inspecione o alvo: `git log` da
branch, `git status`, arquivos novos, e se a branch já está no remoto.

O diff **pendente, não commitado**, costuma ser a parte mais valiosa: leia antes de descartar,
porque é onde está a correção que o filho descobriu medindo. E o que ele quase sempre não termina é
a **verificação**, último passo do briefing e primeira vítima da interrupção — rodar a bateria eu
mesmo é mais rápido que redelegar, são comandos determinísticos, e me dá em primeira mão a
evidência que eu ia ter que conferir de qualquer jeito.

Quando a entrega tem muitos artefatos independentes, fatie em duas ou três delegações menores com
handle verificável em cada uma: perder um pedaço custa menos que perder tudo.
