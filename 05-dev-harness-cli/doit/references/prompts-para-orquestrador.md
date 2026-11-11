# Escrever prompts /doit para outro orquestrador executar depois

Usar quando o usuário pede "escreva um prompt goal/doit em .md para cada marco" em vez de executar agora.

## Estrutura da pasta (`<repo>/docs/prompts-doit/`)

- `00-contexto-comum.md`: repo, SHA base da `main`, documentos a ler (caminhos absolutos), tabela papel→modelo, gates com comando exato (o do CI, não o padrão local), proibições,
  formato do relatório final. Cada prompt manda ler este arquivo primeiro.
- `NN-<marco>.md`: objetivo, modelos por papel, ponto de partida com fatos verificados, tarefas em ordem,
  critérios de aceite, fora do escopo, saída esperada (inclui pedido de autorização para push + PR draft).
- `ORDEM.md`: tabela prompt→marco do checklist→modelos→pré-requisito; diagrama de ondas; conflitos de
  arquivo previstos e ordem de merge; tabela de decisões (D) e ações (A) que só o usuário resolve, com o que cada
  uma bloqueia; riscos. Marcos sem prompt (mecânicos ou já feitos) listados com o motivo.

## Regras

- Marco que toca ambiente real (banco, DNS, Vercel, e-mail, IA paga) é prompt à parte, com "uma escrita por vez
  com sim explícito", filhos só leem e segredo nunca passa pelo chat. Dependente de migration/PR anterior declara
  o pré-requisito e manda parar se não estiver na main; nunca renumerar migration.
- Fato no prompt = fato que eu conferi (SHA, contagens, `git status`, teste reexecutado). Marque o que veio só de
  relatório de worker e o que não foi rodado. Antes de escrever "falta X", grep X na branch: lacuna afirmada sem
  ler o código (rate limit e link que já existiam) faz o orquestrador refazer trabalho pronto. Corrija o prompt
  e o checklist quando descobrir.
- Escolha de orquestrador que o usuário não ditou ("modelo mais potente") é minha: diga na ordem e onde trocar.
- Decisão de produto pendente vira linha D no `ORDEM.md`; não preencha com suposição (retenção, base legal, CNPJ).
- Não commitar nada no checkout do usuário sem pedido; avise que a pasta é untracked.
