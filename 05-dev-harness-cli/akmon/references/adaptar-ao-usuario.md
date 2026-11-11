# Adaptar o akmon ao usuário

Receita para a **IA do usuário** montar a instalação dele: entrevistar, escolher quais skills da
biblioteca fazem sentido, instalar com permissão, decidir se o `akmon` roda em toda requisição e
podar o `akmon` para citar só o que foi instalado.

O `akmon` é um roteador: escolhe qual skill rodar e anuncia a escolha em uma linha. Ele é entregue
como **template editável**. O mapa e as tabelas cobrem o catálogo inteiro, mas cada pessoa instala só
uma parte. Esta receita ajusta o template ao que a pessoa de fato usa.

A receita vale para qualquer harness que leia skills no formato `SKILL.md`. Os mais usados são
**Claude Code, Codex e Antigravity**, e o texto trata os três como caso principal. O **Hermes** é o
harness em que a biblioteca rende mais (carregamento automático por configuração, subagentes,
orquestração), por isso aparece com uma nota própria onde isso muda o procedimento.

Rode quando: a biblioteca é usada pela primeira vez, o usuário pede "adapte o akmon", ou uma skill é
instalada ou removida depois (nesse caso, só as fases 2 a 7).

## Regras (valem em todas as fases)

- **Nada sem permissão.** Instalar, remover ou editar skill, e criar ou editar arquivo de
  configuração ou de instruções do harness (`CLAUDE.md`, `AGENTS.md`, `config.yaml`...) só com o OK
  do usuário, depois de mostrar o caminho exato e o conteúdo. A única edição que a receita autoriza
  por conta própria é a poda do `akmon` (fase 6), e depois de mostrar o diff.
- **Não invente dado do usuário.** Resposta que não veio vira "não informado", não palpite.
- **Não renomeie o `akmon`** nem tire `default` e `editable` do frontmatter: o carregamento
  automático chama a skill pelo nome.
- **Mantenha o `SKILL.md` do `akmon` pequeno.** Ele pode ser injetado em todo turno; detalhe vai
  para `references/mapa.md`.
- **Caminho que esta receita não lista, não presuma.** Se o harness do usuário não está na tabela da
  fase 3, leia a documentação dele ou pergunte.
- Responda no idioma do usuário.

## 0. Preparar

1. **Identifique o harness** em que você está rodando (Claude Code, Codex, Antigravity, Hermes,
   OpenClaw...). Se não tiver certeza, pergunte. Se o usuário usa mais de um, anote todos: as fases 3
   a 5 se repetem para cada um.
2. **Obtenha a biblioteca.** Se o repositório já está clonado na máquina, use essa pasta. Senão,
   clone só para leitura em diretório temporário (peça permissão se o harness exigir):
   `git clone --depth 1 https://github.com/RafaelMKn/skills-library.git <tmp>/skills-library`.
   Daqui em diante, `<biblioteca>` é essa pasta.
3. **Leia o catálogo:** `<biblioteca>/README.md` (tabela por bancada) e
   `<biblioteca>/05-dev-harness-cli/akmon/references/mapa.md`.
4. **Veja o que já está instalado** nos diretórios de skills do harness (fase 3) e liste os nomes.
   Skill já instalada não se reinstala por cima sem avisar.

## 1. Entrevista (estilo grill-me)

Objetivo: saber o bastante para classificar cada bancada da biblioteca em recomendada, opcional ou
fora. Conduza assim:

- **Uma pergunta por vez.** Espere a resposta antes da próxima.
- **Cada pergunta vem com a sua recomendação**, baseada no que você já leu, para o usuário só
  confirmar ou corrigir. Exemplo: "Vi `n8n` no seu `package.json` e um `AGENTS.md` falando de
  clientes. Meu palpite: você roda n8n em produção para cliente. Confere?"
- **Explore antes de perguntar.** O que dá para responder lendo (memória do harness, `AGENTS.md` ou
  `CLAUDE.md` do projeto, arquivos de dependência, pastas de skills já instaladas, conversas
  recentes), leia em vez de perguntar.
- **Siga o ramo.** Resposta abre pergunta nova (usa n8n: é instância própria? tem o MCP do n8n? é
  produção?) ou fecha um ramo inteiro (não faz vídeo: não pergunte de motion).
- **Pergunta que não mudaria nenhuma escolha de skill não se faz.**
- Se o usuário disser "tanto faz" ou "não sei", registre como "não informado" e siga com a
  recomendação mais conservadora (opcional, não recomendada).

Roteiro de ramos, na ordem. Cada linha é um ponto de partida, não um questionário fixo:

| Ramo | O que descobrir | Bancada que isso decide |
|---|---|---|
| Áreas de trabalho | O que faz no dia a dia: automação, código, design, vídeo, agentes de IA, documentos, pesquisa | todas |
| Automação | n8n, Make ou nenhum; instância própria; MCP configurado; sistema em produção de cliente | `01-automacao-n8n-make` |
| Visual | Vídeo ou motion, site e landing, UI, 3D e animação web, criativos de anúncio | `02-design-ui-motion-3d` |
| Agentes | Constrói agentes, escreve prompts, mede qualidade com eval | `03-agentes-ia-prompts` |
| Backend | Stack (Fastify, Prisma, Postgres, Supabase...), integra API de terceiros | `04-backend-apis-banco` |
| Dev e harness | Escreve código, usa GitHub, delega a subagentes, quais harnesses usa | `05-dev-harness-cli` |
| Escritório | Word, Excel, PDF, slides, e-mail, Google Workspace, pesquisa, notas | `06-produtividade-pesquisa-docs` |
| Ambiente | Sistema operacional e harness (decide o que roda e onde instala) | todas |
| Limites | O que o agente pode fazer sozinho e o que não pode tocar | regras de autonomia |

Ao terminar, resuma o perfil em **5 linhas** e peça confirmação. É esse perfil que justifica cada
skill escolhida na fase seguinte.

## 2. Curadoria: quais skills fazem sentido

1. Para cada bancada, classifique as skills em **recomendada**, **opcional** ou **fora**, com
   **uma linha de motivo ligada ao perfil** ("roda n8n em produção para cliente →
   `n8n-correcao-producao`"). Sem motivo no perfil, a skill não entra: skill "por garantia" só
   enche o contexto.
2. **Complete dependências.** Se escolher uma skill, traga as que ela cita em `related_skills` e as
   que as cadeias do `akmon` encadeiam (fluxo novo: builder, validação, revisão). Avise o que
   entrou só por dependência.
3. **Marque o que não roda no ambiente dele:** skill de outro sistema operacional (`apple-*` só
   macOS) ou que exige ferramenta que o harness não tem.
4. **Apresente a lista**, bancada por bancada: recomendadas e opcionais com o motivo, e só a
   contagem das que ficaram fora. Peça aprovação por bancada. O usuário pode adicionar, tirar ou
   trocar.
5. Só avance com a lista final aprovada. O `akmon` entra sempre: é o roteador.

## 3. Onde instalar (pedir permissão)

Antes de copiar qualquer coisa, pergunte **onde** instalar e espere a resposta. Duas decisões:

- **Escopo:** *usuário* (vale para todos os projetos da máquina) ou *projeto* (só esta pasta, pode ir
  para o git do time). Recomende *usuário* para skill de uso pessoal e *projeto* para skill que o
  time inteiro deve ter.
- **Harness:** o que você detectou na fase 0, ou outro se o usuário quiser instalar em mais de um.

Caminhos conferidos na documentação oficial de cada harness (nov/2026):

| Harness | Skills, escopo usuário | Skills, escopo projeto | Instrução sempre ativa, usuário | Instrução sempre ativa, projeto |
|---|---|---|---|---|
| Claude Code | `~/.claude/skills/<nome>/` | `.claude/skills/<nome>/` | `~/.claude/CLAUDE.md` | `CLAUDE.md` na raiz |
| Codex | `~/.agents/skills/<nome>/` | `.agents/skills/<nome>/` | `~/.codex/AGENTS.md` | `AGENTS.md` na raiz |
| Antigravity | `~/.gemini/config/skills/<nome>/` | `.agents/skills/<nome>/` | `~/.gemini/GEMINI.md` ou `~/.gemini/AGENTS.md` | `GEMINI.md` ou `AGENTS.md` na raiz |
| OpenClaw | `~/.agents/skills/<nome>/` ou `~/.openclaw/skills/<nome>/` | `<workspace>/skills/<nome>/` ou `<workspace>/.agents/skills/<nome>/` | `AGENTS.md` no workspace do agente (padrão `~/.openclaw/workspace/AGENTS.md`) | o mesmo `AGENTS.md` do workspace |
| Hermes | `~/.hermes/skills/<nome>/` (subpasta de categoria é opcional) | `<raiz-git>/.hermes/skills/<nome>/` ou `<raiz-git>/.agents/skills/<nome>/`, só se a raiz for confiável (`hermes skills trust`) | não usa arquivo: `skills.auto_load` (fase 5) | `.hermes.md`, `AGENTS.md` ou `CLAUDE.md` na pasta de trabalho |

Notas que mudam o procedimento:

- **`~/.agents/skills/` é compartilhada.** Codex e OpenClaw leem essa pasta direto. O Hermes a lê se
  ela estiver em `skills.external_dirs` (`hermes config set skills.external_dirs '["~/.agents/skills"]'`,
  preservando as entradas existentes). Quem usa mais de um desses harnesses instala uma vez só.
  Claude Code e Antigravity têm pasta própria (`~/.claude/skills/`, `~/.gemini/config/skills/`).
- **Antigravity:** a pasta global `~/.gemini/config/skills/` é a única lida pelo app, pela CLI e pela
  IDE; outras variantes (`~/.gemini/antigravity/skills/` etc.) valem só em parte das superfícies.
  Arquivo de regra acima de 24 KB é truncado: mantenha o bloco do `akmon` curto.
- **Hermes:** skill de projeto não carrega sem confiança explícita na raiz do repositório
  (proteção contra injeção de prompt). Arquivo de contexto é lido só na pasta de trabalho, e só um
  (`.hermes.md` vence `AGENTS.md`, que vence `CLAUDE.md`).
- **Claude Code** também lê `AGENTS.md` quando não há `CLAUDE.md`; para o bloco do `akmon`, use o
  `CLAUDE.md`.

Mostre ao usuário a lista de caminhos finais ("vou criar `~/.claude/skills/n8n-flow-builder/`,
`~/.claude/skills/akmon/`, ...") e peça o OK. Se um destino já tem pasta com o mesmo nome, pare e
pergunte: não sobrescreva.

## 4. Instalar

1. Copie a **pasta inteira** de cada skill aprovada (`SKILL.md`, `references/`, `scripts/`,
   `templates/`) de `<biblioteca>/<bancada>/<nome>/` para o destino aprovado. Skill copiada pela
   metade quebra links.
2. Instale o `akmon` junto: `<biblioteca>/05-dev-harness-cli/akmon/`.
3. Confira com `ls` que cada pasta instalada tem o `SKILL.md`.
4. Mantenha a pasta da skill com o nome dela (`skills/<nome>/`). Nenhum dos harnesses da tabela
   exige subpasta de categoria; OpenClaw e Hermes a aceitam por organização.
5. Se o harness só lê skills no início da sessão, avise que as novas valem a partir da próxima.

## 5. `akmon` em toda requisição?

Pergunte, com a recomendação e o custo:

> Quer que o `akmon` rode em **toda** requisição de trabalho? Ele escolhe a skill certa e anuncia a
> escolha em uma linha. Custo: um pouco de contexto a cada turno. Se preferir não, você o chama só
> quando quiser ("akmon, <pedido>").

Recomende **sim** se o usuário instalou muitas skills ou skills parecidas entre si (o roteador existe
para resolver "qual das duas"); recomende **não** se instalou poucas e distintas.

**Se não:** nada a configurar. Os harnesses listam nome e descrição de cada skill instalada, então a
chamada explícita funciona. Registre a decisão no relato final e siga para a fase 6.

**Se sim**, peça permissão para o arquivo exato (escopo e caminho da tabela da fase 3). O mecanismo
depende do harness:

- **Claude Code, Codex, Antigravity e OpenClaw**: acrescente **ao final** do arquivo de instruções da
  tabela da fase 3 (`CLAUDE.md`; `AGENTS.md`; `GEMINI.md` ou `AGENTS.md`; `AGENTS.md` do workspace),
  no escopo escolhido, criando-o se não existir, este bloco, sem tocar no resto:

  ```markdown
  <!-- akmon:start -->
  ## Roteador de skills (akmon)

  Em todo pedido de trabalho (fazer, corrigir, criar, investigar, publicar, pesquisar), carregue
  primeiro a skill `akmon`, anuncie a skill escolhida em uma linha e siga-a. Não se aplica a
  conversa nem a pergunta factual de uma linha.
  <!-- akmon:end -->
  ```

  Mostre o diff e só grave depois do OK. Se o bloco já existir, não duplique. Desligar: apagar o
  trecho entre os marcadores. Avise o usuário de que isto é uma instrução para a IA, não uma
  configuração do programa: a IA costuma segui-la, mas não é garantido em todo turno.
- **Hermes** (melhor aproveitamento; confirmado em `skills.auto_load` do código-fonte): a skill é pré-carregada por configuração, sem depender de a IA
  seguir uma instrução. Rode `hermes config get skills.auto_load`, acrescente `akmon` **preservando as
  entradas existentes** e grave só por comando: `hermes config set skills.auto_load '["akmon"]'` (o
  valor é exemplo; use a lista que o `get` devolveu mais `akmon`). Não edite o `config.yaml` à mão.
  Lido uma vez por sessão: vale a partir da próxima. Desligar:
  `hermes config set skills.auto_load '[]'`; sessão avulsa sem ele: `hermes --ignore-rules`.
- **Outro harness:** use o arquivo de instruções sempre ativo dele, se a documentação o confirmar;
  senão, deixe o `akmon` em chamada explícita.

No Hermes, `skills.auto_load` é do usuário (vale em todos os projetos). Para valer só num projeto,
use o arquivo de contexto do projeto com o mesmo bloco acima.

## 6. Poda do `akmon`

Rode o checador apontando para a pasta de skills onde você instalou (escopo da fase 3):

```bash
python3 <pasta-do-akmon-instalado>/scripts/checar_mapa.py <pasta-de-skills>
```

(Sem argumento, ele varre as pastas de skills que existirem entre `~/.claude/skills`,
`~/.agents/skills`, `~/.gemini/config/skills`, `~/.hermes/skills` e as de projeto, e imprime quais
usou. Com mais de um harness instalado, passe só a pasta do que está sendo podado.) A saída diz o que
ajustar:

| Saída | Ação |
|---|---|
| `ORFA NO MAPA: x` | Apague a linha de `x` em `references/mapa.md` |
| `NAO MAPEADA: x` | Leia o `SKILL.md` de `x` e acrescente a linha `\| \`x\` \| faz \| chame quando \|` na seção certa do mapa, com texto tirado da descrição real (não do nome) |
| `ORFA NO SKILL.md: x` | Edite a Desambiguação, a Rota por intenção ou as Cadeias, abaixo |
| `FORA DA TRIAGEM: x` | Acrescente `x` à linha da área dele na Rota por intenção (ou crie a linha) |

Edição do `SKILL.md` do `akmon` instalado (mostre o diff ao usuário):

1. **Desambiguação e Rota por intenção:** apague a linha cuja skill principal não está instalada
   (na Rota, tire só a skill ausente; apague a linha se a área ficar vazia). Na coluna "Não é", tire
   a menção a skill ausente. Linha com texto genérico ("skill do projeto") sem skill instalada
   correspondente: troque pela skill instalada que cumpre o papel ou remova.
2. **Cadeias frequentes:** apague a cadeia com elo ausente; se o trecho restante ainda é uma
   sequência útil, encurte em vez de apagar.
3. **Acrescente** linha de desambiguação só para pares de skills parecidas que ele instalou. Skill
   sem parecida não precisa de linha: o índice de skills do harness já a descreve.
4. **Pitfalls:** remova itens que falam de skill ausente.
5. Escreva em `references/mapa.md`, no topo, uma linha
   `Última adaptação: <data> — <perfil em 1 frase>`.

## 7. Verificação e relato

1. `checar_mapa.py` imprime `OK` e sai com código 0.
2. O `SKILL.md` do `akmon` não ficou maior que antes da poda (o ganho é justamente tirar o que não
   se usa).
3. Se o usuário ativou o `akmon` em toda requisição: em **sessão nova**, faça 2 ou 3 pedidos típicos
   dele e confira que a resposta abre com `Skill: <nome> ...` apontando para uma skill instalada,
   nunca para uma ausente. Se não ativou, teste com "akmon, <pedido típico>".
4. Relate ao usuário, em poucas linhas: skills instaladas e onde; se o `akmon` ficou em toda
   requisição e por qual arquivo ou comando; linhas removidas do `akmon`; o que ficou pendente
   (skill recomendada que ele não aprovou) e como desfazer cada mudança.

Repita as fases 2 a 7 sempre que instalar ou remover skills.
