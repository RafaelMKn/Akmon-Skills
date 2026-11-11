# Estados de interface desenhados sobre o DOM real (skeleton, vazio, erro)

Use para propôr ou validar como uma tela fica enquanto carrega, sem dados ou com erro, num app
que já roda localmente. Desenhar o skeleton do zero produz blocos genéricos que não lembram a tela;
o usuário espera ver as caixas específicas da tela real, em cinza ou branco.

## Procedimento

1. Suba o app real (dev server) com dados de exemplo e faça login pelo navegador headless.
2. Inspecione a árvore da tela alvo e anote quais elementos são caixas (fundo, sombra ou borda) e
   o tamanho de cada uma. É isso que vira o mapa do skeleton.
3. Capture a tela normal (`0-normal.png`) na largura de referência.
4. Para cada variante, recarregue, injete um `<style>` com os tokens do projeto e reescreva o DOM
   no próprio navegador. Não edite o repositório.
   - Texto vira barra: envolva cada nó de texto não vazio em `<span>` com `color: transparent`,
     fundo de token neutro e `box-decoration-break: clone`. A barra fica com o comprimento real da
     linha.
   - Valores curtos (números, contadores) precisam de `min-width`, ou viram pontinhos.
   - Controles (botões, inputs) viram blocos sólidos. Esconda os filhos, o placeholder e o
     `::-webkit-calendar-picker-indicator`, senão o ícone do campo de data vaza.
   - Abas e links de navegação: transforme só o texto deles, não o elemento inteiro, ou viram
     tijolos.
   - Desligue `transition` e `animation` antes da captura.
5. Variantes úteis para a escolha: (1) cartões brancos com barras cinza dentro; (2) cada cartão
   como bloco cinza sólido; (3) moldura real (abas, títulos, rótulos) com só os dados vindos do
   backend em cinza.
6. Confira cada captura com visão: texto real vazado, ícone visível, barra minúscula. Corrija o
   seletor e gere de novo.
7. Monte um HTML de quadro (grade 2×2: normal + variantes, legenda de uma linha cada) na mesma
   pasta das PNGs. Abra em headless e confira se todas as imagens carregaram
   (`naturalWidth > 0`) e se não há requisição falha.

## Da variante escolhida à implementação

1. Versione as duas PNGs (escolhida e tela normal) junto da spec e cite-as nela como referência;
   o implementador precisa ver o alvo, não ler a descrição dele.
2. Na spec, troque a descrição genérica pela anatomia medida no passo 2 (caixa, largura, altura,
   grade) e acrescente um critério geométrico verificável: Playwright mede as caixas do estado novo
   e as da tela carregada, na mesma largura, e exige diferença pequena (ex.: ≤ 8px em x, y, largura
   e altura). Sem esse critério, "parecido" vira opinião.
3. Reutilize as classes reais de layout da tela no componente do estado (posição e quebra
   responsiva batem por construção) e crie classes próprias só para as barras.
4. Exija `document.documentElement.scrollWidth <= 320` em 320px: barras com largura fixa copiada do
   desktop estouram a tela estreita mesmo quando a grade real já quebra.
5. Antes de delegar, faça grep nos testes de navegador pelas classes reaproveitadas e pelo texto
   exato do contêiner de status (`toHaveText` no `role=status`, `toHaveCount(0)` de uma classe do
   painel): o estado novo passa a carregar essas classes e textos, e esses testes caem. Inclua
   esses arquivos na lista permitida, com o ajuste descrito (seletor que distingue o estado,
   `toContainText`).

## Armadilhas

- Script Node que importa a lib de navegador do projeto (`@playwright/test`) resolve módulos
  pelo caminho do arquivo. Rode uma cópia temporária dentro do repo, apague em seguida e confira
  `git status`. Guarde o original fora do repo, com os artefatos.
- Saia da tela com a estrutura da tela real e junte uma ressalva: se a estrutura depende de algo
  ainda não resolvido durante o carregamento (papel, permissão, rota inicial), a variante fiel é
  fiel a um só caso. Diga isso ao entregar.
- Antes de capturar, conecte-se pela ferramenta que mantém sessão estável. Se a aba do navegador
  interativo se perder, gere as capturas pelo Playwright headless.
