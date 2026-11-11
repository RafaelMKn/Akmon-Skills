// Build de preview que abre direto por file:// (sem servidor): bundle IIFE, sem type=module/crossorigin.
// Uso: copie para a raiz do projeto Vite (precisa resolver 'vite'), rode `node .preview-build.mjs <outDir>` e apague.
import { build } from 'vite';
import fs from 'node:fs';
import path from 'node:path';

const outDir = process.argv[2];
if (!outDir) { console.error('uso: node build-file-preview.mjs <outDir>'); process.exit(1); }
await build({
  base: './',
  logLevel: 'warn',
  build: {
    outDir,
    emptyOutDir: true,
    modulePreload: false,
    rollupOptions: { output: { format: 'iife', inlineDynamicImports: true } },
  },
});
const f = path.join(outDir, 'index.html');
const original = fs.readFileSync(f, 'utf8');
const scripts = [...original.matchAll(/<script type="module" crossorigin src="([^"]+)"><\/script>/g)].map(m => m[1]);
let html = original.replace(/<script type="module" crossorigin src="[^"]+"><\/script>/g, '').replace(/ crossorigin/g, '');
// Script no fim do body para o #root existir quando o IIFE rodar.
for (const s of scripts) html = html.replace('</body>', `<script src="${s}"></script>\n</body>`);
fs.writeFileSync(f, html);
console.log('ok', scripts);
