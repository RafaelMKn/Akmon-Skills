# Portable HTML and print verification

Use for folders, flyers, and other standalone branded HTML pieces that also need PDF delivery.

## Procedure

1. Build the complete HTML with embedded CSS, original brand assets, and an explicit print page size. Keep preview controls outside the composition and hide them with `@media print` placed at the END of the stylesheet (an earlier print rule loses to a later base rule of equal specificity, so the control prints and can push content onto an extra page). Avoid exact `height:297mm` pages — rounding adds a blank page; use ~295mm with `break-before:page`. Label illustrative product data as fictitious and preserve product disclaimers.
2. If portability requires embedded fonts, fetch the font stylesheet, download each referenced font, and substitute data URLs using the font's actual MIME/format. Replace the original import by its exact full string or parse CSS; never terminate an import match at the first semicolon, because font-family weight URLs contain semicolons. A partial replacement leaves invalid CSS before `:root` and can silently discard the entire color-token rule.
   Faster when the repo already has a branded self-contained HTML: extract its `@font-face{...}` blocks with a regex (`re.findall(r'@font-face\s*{[^}]*}', html)` — data URLs contain no `}`), save to a scratch .css, and inject them into the new artifact's `<style>`; this keeps the exact brand fonts without re-downloading. Confirm in the browser with `document.fonts.check('16px <Family>')`.
3. Render with installed Chromium/Chrome. Discover the executable first. The following command shape was exercised successfully; substitute absolute paths and choose a viewport tall enough to include the whole composition:

   ```sh
   google-chrome --headless --no-sandbox --disable-gpu \
     --no-pdf-header-footer \
     --print-to-pdf=/absolute/output/folder.pdf \
     --screenshot=/absolute/output/folder.png \
     --window-size=964,1600 --timeout=15000 \
     file:///absolute/output/folder.html
   ```

   Use `--no-sandbox` only when the execution environment requires it and the local HTML is trusted; retain Chrome's sandbox otherwise.
4. Inspect the screenshot for actual brand colors, circles/underlines, typography, wrapping, and the complete footer. Successful image creation does not prove that the stylesheet parsed. A screenshot ending before the footer verifies only the viewport, not the whole piece.
5. Run `pdfinfo /absolute/output/folder.pdf` to verify page size and page count, then `pdftotext /absolute/output/folder.pdf -` to confirm the final CTA and footer survived export. A one-page brief requires `Pages: 1`; `break-inside: avoid` does not make an oversized composition fit.
6. If PDF pagination overflows, reduce unnecessary vertical spacing or content and re-export. Modest print-only scaling is possible, but calculate effective printed text size before accepting it: aggressive shrinking trades overflow for illegibility. Inspect the exported PDF itself, not just the screen screenshot.
7. After every CSS or font correction, regenerate both screenshot and PDF and repeat the checks; earlier verification no longer covers the changed artifact.
8. Deliver the HTML and PDF as native file attachments (`MEDIA:/absolute/path` in Hermes desktop), with a short statement of what was verified. Do not claim print-production readiness from a browser PDF alone; bleed, color requirements, and final physical-size readability require their own checks.
