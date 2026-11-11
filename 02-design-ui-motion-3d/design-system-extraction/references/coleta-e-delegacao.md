# Coleta de evidência e delegação (referência de site público)

Use quando o pedido é extrair o design system de 1+ sites públicos para estudo (`design_system/refs/<marca>/`). Em vez de pedir ao subagente que descubra tudo, o agente principal junta a evidência e delega só a geração do HTML.

## 1. Evidência em `design_system/refs/<marca>/` (agente principal)

1. `curl -sL -A "Mozilla/5.0 ... Chrome/130 ..."` na home (`index.html`) e nos assets listados por `grep -o '<link[^>]*stylesheet[^>]*>'` e `<script src>` (CSS, `fonts.css`, JS de comportamento). Anotar o framework (Next/Tailwind, Shopify etc.) pelos caminhos e pelo cabeçalho do CSS.
2. Estilos computados via `browser_exec`, em desktop 1440x900 e mobile 390x844 (`Emulation.setDeviceMetricsOverride`, `mobile=True` no 390): rolar a página em passos de 600px para disparar reveal/lazy, voltar ao topo, e deduplicar por (tag + fontFamily, fontSize, fontWeight, lineHeight, letterSpacing, color, backgroundColor, borderRadius, boxShadow, transition) com contagem. Gravar `computed-desktop.json` / `computed-mobile.json` + `rootVars` (custom properties de `:root`/`html`/`body`, ignorando `--tw-*`) + `bodyBg`, e `hero-<viewport>.png`. Sempre `clearDeviceMetricsOverride` no fim.
3. Tudo dentro da pasta da marca. Não tocar em nada fora dela, exceto registrar a decisão no `docs/decisoes.md` do projeto.

## 2. Delegar a geração (um subagente por marca, em paralelo)

Briefing inclui: caminhos da evidência; obrigação de carregar esta skill e `references/prompt-sites.md`; escopo (home pública, 2 viewports; sem app autenticado/checkout); referência ≠ adoção; "não invente" (o que não existe vira "não observado"); gerar cópia do CSS com URLs absolutas (`url(/_next/` → `url(https://dominio/_next/`) mantendo o original intacto; cabeçalho no HTML com URL, data, viewports, escopo e tokens com procedência (CSS vs computed); estilo inline só se inevitável e declarado; validação com screenshot desktop+mobile e comparação com o hero original salvos na pasta; entrega com caminho, tokens, lista de "não observado" e o que não validou.

Fonte comercial (ex.: PP Neue Montreal): documentar nome/pesos e dizer no HTML que não pode ser reutilizada sem licença; não inventar substituto como se fosse extraído.

## 3. Revisão independente (agente principal, antes de repassar)

- `find . -mmin -N -not -path './design_system/*'` — só o `docs/decisoes.md` pode ter mudado fora.
- Contar estilos inline: `grep -o 'style="[^"]*"' | sort | uniq -c` (ignorar `font-style="normal"` de SVG).
- Conferir cada cor e tamanho afirmado contra `computed-*.json` (script Python com `in json.dumps(els)`). Tamanhos que só existem em outro breakpoint (ex.: título 36px só no mobile) aparecem no CSS/computed-mobile, não no desktop: conferir nos dois antes de chamar de erro.
- Abrir cada `design-system.html` por `python3 -m http.server <porta> --bind 127.0.0.1 --directory <pasta>` no `browser_exec`: `document.fonts` com status `loaded`, `scrollWidth <= innerWidth`, seções presentes. Matar o servidor no `finally`.

## Pitfalls

- **Aba em segundo plano congela animação de entrada.** Se `document.visibilityState === 'hidden'`, o print sai com texto apagado ou véu cinza (reveal parado em meio). Antes de chamar de defeito, ler `getComputedStyle().opacity` da cadeia de ancestrais e `color`; opacidade efetiva 1 = arquivo ok. Para ver a animação de fato, abrir no Chrome do usuário.
- `querySelector('#1')` é seletor inválido (id começando com dígito): usar `[id="1"]`.
- `Input.dispatchMouseEvent` pode estourar timeout na aba oculta e derrubar o lote; separar medições de hover das demais e usar `try/finally` para matar os servidores HTTP.
- Subagente que deixa `http.server` rodando: ele morre com o filho. Relançar na própria sessão se for preciso.
- Apagar os `revisao-*.png` temporários de revisão; manter só os `validacao-*` do subagente.
- `design_system/` é material de estudo (vários MB por marca): excluir do deploy.
