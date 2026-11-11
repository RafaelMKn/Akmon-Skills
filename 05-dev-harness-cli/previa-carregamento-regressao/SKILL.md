---
name: previa-carregamento-regressao
description: Use ao testar prévias de carregamento HTML e React.
---

# Regressão de prévias de carregamento

- Bloqueie módulos JavaScript com promessa controlada em `page.route` para capturar a prévia HTML; confira que a montagem React desconecta o nó inicial.
- Retenha a resposta de autenticação ou vínculo para alcançar a prévia React deterministicamente. Libere as promessas no `finally`.
- Compare `getBoundingClientRect()` de banda, abas, filtro e cada métrica em HTML, React e tela carregada; confira contagens, anexe as medidas e reporte a maior diferença por caixa.
- Meça `document.documentElement.scrollWidth` em 320px no HTML e no React. Liste elementos com retângulo direito fora da viewport, distinguindo descendentes corretamente cortados por `overflow:hidden`.
- Use `minmax(0,1fr)` para eliminar o tamanho mínimo intrínseco das grades; limite descrições e barras. Confira especificidade e ordem: regras posteriores podem restaurar `max-width:62ch` e causar overflow.
- Não use `legend` para imitar um rótulo interno: ele fica no contorno do `fieldset`. Coloque o rótulo no fluxo e compare o retângulo externo do cartão.
- Confira largura positiva das barras em contêiner flex: um span vazio sem largura pode desaparecer mesmo com a caixa pai correta.
- Prove cobertura removendo o span de coluna da métrica principal, divergindo token inline, removendo texto de carregamento e introduzindo largura excessiva. Restaure cada mutação com contexto que inclua o seletor inteiro: `span 1` pode ser legítimo em media queries.
- Grave capturas no diretório de saída do Playwright por padrão e permita sobrescrita via variável de ambiente. Não versione caminho absoluto do operador no spec.
