# HTML de decisão: comparar ferramentas para um projeto

Use quando o usuário pede "debata, pesquise e traga em HTML" os prós de duas ferramentas (runtime de agente, SaaS, lib) e a recomendação por caso de um projeto/cliente. Superfície: **Compare** (colunas paralelas), com veredito no topo.

## Procedimento

1. **Identificar o produto exato antes de pesquisar.** Nome curto de ferramenta ("openbot", "clawbot") costuma bater em vários produtos distintos com a mesma feature. Faça 1–2 buscas e, se houver mais de um candidato plausível, pergunte via `clarify` listando-os com o fabricante/repo; comparar o produto errado invalida o HTML inteiro.
2. **Confirmar a feature que motivou a pergunta na fonte primária, com data.** Para projeto no GitHub: `gh api 'repos/<owner>/<repo>/releases?per_page=40'` e filtrar o corpo das releases por palavra-chave (skill|memor|learn…) em Python; depois `gh pr view <n> -R owner/repo --json title,body,mergedAt` e a doc de arquitetura (raw.githubusercontent). Registre: versão, data, modos/configs, maturidade ("lançado hoje", testado como).
3. **Checar licença e preço sempre.** `LICENSE` do repo + página de licença comercial + página de preços. "Código aberto" não implica uso comercial (ex.: PolyForm Noncommercial): trabalho para clientes é uso comercial e costuma ser o fator decisivo.
4. **Checar o lado já adotado com o ambiente real**, não de memória: config local (`hermes config get <seção>`), `--help` da CLI, doc oficial da feature equivalente.
5. **Ancorar no projeto.** Ler CONTEXT/PRODUCT/spec/decisões do repo e citar os IDs de decisão (Q4, Q13…) que a troca reabriria. A recomendação por caso usa os componentes reais do projeto (crons, agentes, interface), não categorias genéricas.
6. **Debater a premissa.** Se o argumento original ("ferramenta X atualiza skills sozinha") deixou de ser diferencial ou é risco no contexto (produção exige determinismo/aprovação), dizer isso no HTML e na resposta.

## Estrutura do HTML (resumido)

1. Kicker com projeto · tema · data; título; lede de 2 linhas.
2. **Veredito** em caixa no topo (decisão + 1 frase de porquê).
3. "O debate em duas frases": premissa corrigida × o que de fato decide.
4. Tabela da feature lado a lado (como funciona, controle, manutenção, maturidade).
5. Dois cards de **pontos positivos**, cada um com bloco "Contra" curto — equilíbrio é obrigatório, o usuário pediu prós dos dois lados.
6. Recomendação por caso do projeto: linhas `caso | ferramenta+modo | porquê`, incluindo "não agora" quando couber.
7. **Lacunas**: o que não foi testado/verificado (obrigatório — nada de afirmação sem prova).
8. Rodapé com links das fontes primárias.

Identidade: reutilize fontes/cores de um HTML de marca já existente no repo (ver portable-html-print.md, reuso de @font-face). Verifique abrindo no navegador e inspecionando topo e meio por screenshot.

## Pitfalls

- Pedido escrito "resumido e ambíguo" pelo usuário significou "equilibrado, mostrando os dois lados" — quando um adjetivo do pedido não faz sentido literal, confirme a leitura na mesma pergunta do `clarify` do passo 1, não em outra rodada.
- Preço com promoção/gratuidade temporária: registrar a data de corte e a data da consulta no HTML; muda rápido.
- Integração cruzada (ferramenta B usa A como provider) gera efeito composto (dois mecanismos de aprendizado/memória ativos); listar como lacuna se não testado.
