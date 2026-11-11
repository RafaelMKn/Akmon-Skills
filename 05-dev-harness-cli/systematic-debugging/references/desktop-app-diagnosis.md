# Diagnosing a third-party desktop app (Electron / AppImage) from the outside

Use when the user shows a screenshot of an error in a closed desktop app (no repo, no debugger) — e.g. an agent hub that "does not find" a CLI that is clearly installed.

## Procedure

1. **Confirm the thing the error denies.** If it says "X not installed", run `which -a X`, `X --version` and time it (`/usr/bin/time -f %es X --version`). Version-probe timeouts are a common false "not installed".
2. **Find the running process and its version**: `ps aux | grep -i <app>`. AppImages show as `<App>-<ver>-x86_64.AppImage` plus a `.mount_*` dir with the real binary. Two versions alive at once (leftover after auto-update) is worth reporting — kill the stale one.
3. **Read the env the GUI really has**: `tr '\0' '\n' < /proc/<pid>/environ | grep PATH`. Empty/unreadable is possible; then rely on the app's own resolution logic (step 6).
4. **Logs live in `~/.config/<App>/`** (Electron userData): `logs/*/*.log`, `trace.ndjson` (IPC calls with timestamps — shows which button the user pressed and when), `update/update.log`, `*-v1.json` state files. Grep provider/agent name across all of them.
5. **Correlate time correctly**: Electron logs are UTC (`...Z`); the user is local time. Check the screenshot file mtime (`ls --time-style=full-iso`) and convert before deciding which log lines belong to the symptom. A screenshot taken after the last log line means the logs may not cover it.
6. **Read the bundled source**: `npx -y @electron/asar extract <mount>/resources/app.asar $TMPDIR/asar` (the asar is under the `.mount_*` dir of the running AppImage). Then:
   - Find the user-visible string in the i18n bundle → get its key (e.g. `error.provider.xInstallFailed`).
   - Search the key in `out/main/index.js` to land on the code path that sets it.
   - Use Python `re` with slicing, not `grep -o '.{200}...'`: minified bundles have huge lines and multibyte text, and grep context regexes silently return nothing.
7. **Explain from code, not from guesses**: state what triggers the message (which state, which button) and what the button actually does before telling the user to click it.

## Pitfalls

- When logs say the component is detected/available but the UI shows it missing, check which **host/profile/server** the UI is pointed at (multi-host apps keep a local host id and an "active server" id in separate JSON files). Report a mismatch as a hypothesis until the user confirms in the UI.
- "Retry" buttons in agent hubs often run an installer, not a re-detect. Read the handler before recommending it — reinstalling over a working user install can move config forward.
- Don't paste secrets from state files (`privateKey`, `encryptedToken`) into output; filter keys when printing JSON.

## Known app notes

- **<agente>** (agent hub, Electron): resolves `hermes` via login-shell PATH plus fallbacks (`~/.local/bin`, `~/.bun/bin`, `/usr/local/bin`, `/usr/bin`...), runs `hermes --version` with a 5–10 s timeout and parses `^Hermes Agent vX.Y.Z`. The Hermes settings "Repetir"/Download runs a pinned `install.sh` from the hermes-agent repo; message `error.provider.hermesInstallFailed` comes from that installer path, not from detection. `<AGENTE>_HERMES_PATH` overrides the path and disables the installer. Provider logs: `~/.config/<agente>/logs/providers/providers.log`; installer warnings use logger `hermes-installer`.
