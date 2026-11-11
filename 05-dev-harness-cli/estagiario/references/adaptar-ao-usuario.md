# Adaptar o estagiário ao usuário (skill padrão editável)

O `estagiario` é a skill **padrão** do harness: fica ativa em toda requisição (`skills.auto_load`) e
decide qual skill rodar. Ele é entregue como **template editável**: o mapa e as tabelas cobrem o
catálogo inteiro da biblioteca, mas cada pessoa instala só uma parte. Esta receita faz a IA do
usuário (1) escolher quais skills fazem sentido para o estilo de trabalho dele e (2) reescrever o
estagiário para citar **somente** as skills que ele de fato instalou.

Rode quando: a skill é instalada pela primeira vez, o usuário pede "adapte o estagiário", ou uma
skill é instalada/removida depois.

Regras que valem em todas as fases:

- Não invente dado do usuário. Resposta que não veio vira "não informado", não palpite.
- Não instale, remova nem edite skill sem o OK dele. Editar o estagiário é o único passo que a
  receita autoriza por conta própria, e depois de mostrar o diff.
- Não renomeie o estagiário nem tire as marcas `default` e `editable` do frontmatter: o `auto_load`
  chama pelo nome.
- Mantenha o `SKILL.md` pequeno. Ele é injetado em todo turno; detalhe vai para `references/mapa.md`.

## 1. Ativar como padrão

```bash
hermes config get skills.auto_load
```

Se `estagiario` não estiver na lista, acrescente **preservando as entradas existentes**
(a lista abaixo é exemplo; use a que o comando acima devolveu mais `estagiario`):

```bash
hermes config set skills.auto_load '["estagiario"]'
```

Edite o `config.yaml` só por `hermes config set`. O `auto_load` é lido uma vez por sessão: vale a
partir da próxima. Desligar: `hermes config set skills.auto_load '[]'`; sessão avulsa sem ele:
`hermes --ignore-rules`.

## 2. Perfil de trabalho

Antes de perguntar, leia o que já existe (memória do usuário, `AGENTS.md`/README do workspace,
conversas recentes). Depois pergunte só o que falta, em uma rodada (`clarify` ou `grilling`):

1. O que a pessoa faz no dia a dia (áreas: automação, código, design, vídeo, conteúdo, dados...).
2. Stack e ferramentas que ela usa de verdade (n8n, Make, Notion, Supabase, Docker, Figma...).
3. Trabalha com sistema em produção de cliente, ou é projeto novo/laboratório?
4. Sistema operacional e harness (Linux/macOS/Windows; Hermes, Claude Code, Codex...).
5. O que ela quer que o agente faça sozinho e o que NÃO quer que toque.

Resuma o perfil em 5 linhas e confirme. É ele que justifica cada skill escolhida na fase seguinte.

## 3. Curadoria: quais skills fazem sentido

1. Leia o catálogo: `README.md` da biblioteca (tabela por categoria) e `references/mapa.md`.
2. Classifique cada categoria em **recomendada**, **opcional** ou **fora**, com **uma linha de
   motivo ligada ao perfil** ("usa n8n em produção → `n8n-correcao-producao`"). Sem motivo
   no perfil, a skill não entra: skill "por garantia" só enche o contexto.
3. Complete dependências: se escolher uma skill, traga as que ela cita em `related_skills` e as
   cadeias do estagiário (ex.: fluxo novo → builder, validação, revisão). Avise o que ficou de fora.
4. Marque o que não roda no ambiente dele: skill de outro SO (`apple/*` só macOS) ou que exige
   toolset ausente.
5. Apresente a lista e **espere aprovação**. Ele pode adicionar, tirar ou trocar.

## 4. Instalação (pelo usuário ou com o OK dele)

Copie a pasta inteira de cada skill aprovada (SKILL.md, `references/`, `scripts/`, `templates/`)
para o diretório de skills do harness (`~/.hermes/skills/<categoria>/<nome>/` no Hermes) ou use o
comando de instalação do harness. Skill copiada pela metade (sem `references/` ou `scripts/`)
quebra links. Depois de instalar, confira com `ls` que cada pasta tem o `SKILL.md`.

## 5. Poda do estagiário

```bash
python3 <pasta-da-skill>/scripts/checar_mapa.py
```

A saída diz o que ajustar:

| Saída | Ação |
|---|---|
| `ORFA NO MAPA: x` | Apague a linha de `x` em `references/mapa.md` |
| `NAO MAPEADA: x` | Leia o `SKILL.md` de `x` e acrescente a linha `\| \`x\` \| faz \| chame quando \|` na seção certa do mapa, com texto tirado da descrição real (não do nome) |
| `ORFA NO SKILL.md: x` | Edite a Desambiguação/Cadeias, abaixo |

Edição do `SKILL.md` (mostre o diff ao usuário):

1. **Desambiguação:** apague a linha cuja skill principal não está instalada. Na coluna "Não é",
   tire a menção a skill ausente. Linha com texto genérico ("skill do seu ambiente", "skill do
   projeto") ou sem skill instalada correspondente: troque pela skill instalada que cumpre o papel
   ou remova.
2. **Cadeias frequentes:** apague a cadeia com elo ausente; se o trecho restante ainda é uma
   sequência útil, encurte em vez de apagar.
3. **Acrescente** linha de desambiguação só para pares de skills parecidas que ele instalou
   (a tabela existe para resolver "qual das duas"). Skill sem parecida não precisa de linha: o
   índice de skills do system prompt já a descreve.
4. **Pitfalls:** remova itens que falam de skill ausente.
5. Escreva em `references/mapa.md`, no topo, uma linha `Última adaptação: <data> — <perfil em 1 frase>`.

## 6. Verificação

1. `checar_mapa.py` imprime `OK` e sai com código 0.
2. `SKILL.md` não ficou maior que antes da poda (o ganho é justamente tirar o que não se usa).
3. Em **sessão nova**, faça 2 ou 3 pedidos típicos do usuário e confira que a resposta abre com
   `Skill: <nome> ...` apontando para uma skill instalada, nunca para uma ausente.
4. Relate ao usuário: skills mantidas, linhas removidas do estagiário, e o que ficou pendente
   (skill recomendada que ele ainda não instalou).

Repita as fases 3 a 6 sempre que instalar ou remover skills.
