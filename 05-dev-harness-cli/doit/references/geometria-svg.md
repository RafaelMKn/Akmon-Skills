# Homologação de gráficos SVG responsivos

## Procedimento

1. Extraia do guia aprovado os invariantes: espaço mínimo dos eixos, região que não pode ser coberta, unidades e comportamento de ponteiro. Uma correção de corte não autoriza sobrepor colunas.
2. Separe projeção pura (escala, coordenadas, índices e rótulos) da medição DOM. Teste extremos puros antes de ampliar a matriz de navegador: série vazia, um item, zeros e série densa.
3. Meça o texto renderizado com `getBBox()` ou `getComputedTextLength()`, usando a fonte efetiva. Dimensione a margem pelo maior entre mínimo responsivo, destaque selecionado com padding e maior marca do eixo com respiro. A seleção zero não pode encolher a margem a ponto de cortar a escala de um período com pico grande.
4. Faça a primeira medição antes da pintura; se houver SSR, use efeito isomórfico. Recalcule após carregamento da fonte e redimensionamento. Inclua nas dependências a representação das marcas, não apenas a leitura selecionada: trocar dados ou métrica pode manter a leitura em zero e mudar toda a escala.
5. No navegador, espere a fonte e confira geometricamente TODAS as marcas, unidade, datas e destaque: limites dentro do SVG, texto dentro do retângulo e destaque fora da região proibida. Cubra valor grande selecionado e, principalmente, valor pequeno/zero selecionado no mesmo período de pico grande.
6. Cubra troca de métrica e troca de dados mantendo a mesma leitura selecionada, sem remontar o componente. Confirme identidade do elemento para não deixar uma remontagem mascarar dependência ausente.
7. Prove sensibilidade: execute o teste contra a geometria anterior e depois remova deliberadamente a dependência das marcas; ambos devem falhar antes de restaurar a versão correta. Capture o estado final estreito e largo para inspeção visual.

## Interação

- Distinga hover do mouse de arrasto touch/caneta pressionado. Capture o ponteiro no início, libere em término/cancelamento e limpe estado ao perder captura; movimento touch sem pressão não deve selecionar.
- Preserve a rolagem vertical quando o contrato pede seleção horizontal (`touch-action: pan-y`). Teste arrasto horizontal e gesto vertical separadamente; um clique sintético não comprova o arrasto.

## Custo da matriz

- Meça primeiro um cenário de cada família antes de multiplicar casos. Quando autorizado reduzir combinações, preserve extremos de quantidade em todas as larguras e quantidades intermediárias nas larguras extremas; registre a matriz e os critérios cobertos.
- Colete geometria em lote com `locator.evaluate` e faça comparações numéricas locais com `node:assert` quando não houver condição assíncrona a esperar. Preserve limites e tolerâncias; trocar a mecânica da asserção não autoriza apagar checagens ou aumentar timeout para esconder lentidão.
