// Teste em tempo real (relógio de verdade) de UI temporizada/hover via Chrome headless + CDP.
// Uso: node cdp-realtime-probe.mjs <url> '<expr JS que retorna string de estado>' [hoverSelector] [scrollSelector] [shotPrefix]
// Ex.:  node cdp-realtime-probe.mjs file:///.../index.html \
//         "(() => { const t=[...document.querySelectorAll('[role=tab]')].find(b=>b.ariaSelected==='true'); return t.textContent })()" \
//         '#cap-panel' '#agente' /tmp/abas
// - scrollSelector: rola a seção para a viewport com scroll INSTANTÂNEO (html com
//   scroll-behavior:smooth faz scrollIntoView/scrollTo não andar a tempo e o mouse cai no vazio).
// - Lê o estado 4x a cada 2 s; se hoverSelector vier, leva o mouse até o centro dele em passos
//   (dispara pointerenter de verdade), lê antes/depois de 3 s (deve ficar igual = pausado),
//   tira o mouse e lê de novo (deve andar).
// - shotPrefix: salva <prefix>-rest.png e <prefix>-hover.png para olhar com visão.
// Headless reporta matchMedia('(hover: hover)') = false mesmo com Emulation.setEmulatedMedia;
// componente que decide hover por matchMedia nunca reage aqui — decidir por evento
// (pointerType === 'mouse') e usar '(pointer: coarse)' só para o fallback de toque.
import { spawn } from 'node:child_process';
import fs from 'node:fs';

const [url, stateExpr, hoverSel, scrollSel, shotPrefix] = process.argv.slice(2);
const PORT = 9333;
const chrome = spawn('google-chrome', ['--headless=new', '--no-sandbox', '--hide-scrollbars', `--remote-debugging-port=${PORT}`, 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let ws;
for (let i = 0; i < 40 && !ws; i++) {
  try {
    const list = await (await fetch(`http://127.0.0.1:${PORT}/json`)).json();
    const page = list.find(x => x.type === 'page');
    if (page) ws = new WebSocket(page.webSocketDebuggerUrl);
  } catch {}
  if (!ws) await sleep(250);
}
await new Promise(r => ws.addEventListener('open', r, { once: true }));
let id = 0;
const pending = new Map();
ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m.result); pending.delete(m.id); } });
const send = (method, params = {}) => new Promise(r => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async expr => (await send('Runtime.evaluate', { expression: expr, returnByValue: true })).result.value;
const shot = async name => { if (!shotPrefix) return; const r = await send('Page.captureScreenshot', { format: 'png' }); fs.writeFileSync(`${shotPrefix}-${name}.png`, Buffer.from(r.data, 'base64')); };

await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url });
await sleep(1500);
if (scrollSel) {
  await ev(`document.documentElement.style.scrollBehavior='auto'; window.scrollTo(0, document.querySelector(${JSON.stringify(scrollSel)}).getBoundingClientRect().top + scrollY + 40)`);
  await sleep(600);
}
await shot('rest');
for (let s = 0; s < 4; s++) { console.log(`t+${s * 2}s`, await ev(stateExpr)); await sleep(2000); }
if (hoverSel) {
  const [x, y] = await ev(`(() => { const r=document.querySelector(${JSON.stringify(hoverSel)}).getBoundingClientRect(); return [r.x+r.width/2, r.y+r.height/2]; })()`);
  for (let k = 1; k <= 8; k++) { await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: 10 + (x - 10) * k / 8, y: 10 + (y - 10) * k / 8 }); await sleep(30); }
  console.log('under mouse:', await ev(`(() => { const e=document.elementFromPoint(${x}, ${y}); return e ? e.tagName + '.' + e.className : 'null (fora da viewport?)'; })()`));
  console.log('hover on', await ev(stateExpr));
  await sleep(1200);
  await shot('hover');
  await sleep(1800);
  console.log('hover +3s', await ev(stateExpr));
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: 5, y: 5 });
  await sleep(2000);
  console.log('hover off +2s', await ev(stateExpr));
}
ws.close();
chrome.kill();
