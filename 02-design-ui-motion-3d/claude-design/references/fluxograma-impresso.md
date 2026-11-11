# Fluxograma para apresentar (HTML + PDF de poucas páginas)

Use quando o pedido for um fluxograma de processo, regra de negócio ou spec para apresentar a sócio ou cliente, em tela e em PDF.

## Formato que o usuário espera

- **Fluxograma clássico:** terminal arredondado no início e no fim, caixas de passo e **losango** de pergunta no eixo central. O caminho principal (geralmente o SIM) desce. O desvio (NÃO, exceção, "vai para a equipe") sai **na horizontal** para uma caixa lateral, com o rótulo SIM/NÃO na seta. Ocupe a largura da página, não só a altura.
- **Não** faça uma pilha vertical de cartões com o ramo encostado ao lado. Isso não é lido como fluxograma e estoura em muitas páginas.
- Teto de páginas: um fluxo por página A4, cabendo inteiro, e no total o que ele pediu (tipicamente ≤ 2). Texto de mensagem (WhatsApp, e-mail) vai num balão ao lado do passo, ligado por uma linha tracejada, nunca dentro da caixa.
- Legenda curta de cores por ator (automático × equipe × nada acontece) e do losango.

## Duas audiências no mesmo arquivo

Quando o fluxo vai ao sócio e depois ao cliente, use **o mesmo desenho** com um toggle `Visão clínica / Visão técnica` (`?v=cli|tec`, persistido em localStorage):
- Na visão técnica aparecem **badges numerados** nos nós, que remetem a notas de rodapé (IDs de fluxo, colunas, crons, testes, discordâncias). As notas não entram dentro do diagrama.
- Na visão do cliente: zero IDs e zero jargão, só as regras, o que muda em relação ao combinado e o que ele precisa aprovar.
- Esconda pelo `body.v-tec` com `!important` (`body:not(.v-tec) .only-tec{display:none!important}`), nunca com `style="display:..."` inline. Display inline quebra o grid ou flex do elemento.
- Exporte um PDF por visão e rode `pdftotext cliente.pdf - | grep <ID>` para provar que o PDF do cliente não vaza ID interno.

## Como desenhar

Gere o SVG por um script Python com coordenadas explícitas: colunas fixas (esquerda, centro, direita), linhas Y fixas e helpers `node`, `edge_v`, `edge_h` e `bubble`. Isso é mais confiável que layout CSS para setas e losangos e permite reajustar texto e regerar. Salve o script ao lado do artefato (`scripts/gerar_fluxograma.py`) e guarde a versão anterior como `-v1.html` antes de refazer.

## Armadilhas de impressão (Chromium `Page.printToPDF` / `--print-to-pdf`)

- Coloque `@media print` **no fim** do `<style>`. Uma regra de print declarada antes perde para uma regra base de mesma especificidade declarada depois. Exemplo: a toolbar com `display:flex` continua impressa e empurra o conteúdo para uma página extra.
- Página com altura exata de `297mm` gera página em branco por arredondamento. Use `height:295mm` no print, `@page{size:A4;margin:0}` e `.page+.page{break-before:page}`, e exporte com `preferCSSPageSize=True`.
- Confira o overflow de cada página antes de exportar: `[...document.querySelectorAll('.page')].map(p=>[p.scrollHeight,p.clientHeight])`. Se um valor for maior que o outro, o conteúdo vaza. Depois confira `pdfinfo` (Pages) **em cada visão**, porque a técnica tem mais texto e estoura primeiro.
- Em SVG, a regra CSS de classe (`.tb{fill:...}`) vence o atributo `fill="..."`. Para texto branco em nó escuro, use `style="fill:#fff"`.
- Rasterize o PDF (`pdftoppm -r 80 -png`) e olhe as páginas reais. O screenshot da tela não prova a paginação.
