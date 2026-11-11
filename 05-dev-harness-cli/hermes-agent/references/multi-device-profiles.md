# Independent Hermes installations and shared profiles

Use when the user wants similar agents on separate computers without an always-on primary computer. Official feature reference: https://hermes-agent.nousresearch.com/docs/user-guide/profile-distributions . Check current CLI help and docs before using version-dependent flags.

## 1. Resolve the continuity requirement

Separate these questions instead of treating all of them as folder synchronization:

| Requirement | Mechanism |
| --- | --- |
| Same running conversation from different screens | Authenticated connection to the same runtime; the host must stay available. |
| Independent operation with similar rules and tools | Private Git profile distribution; each machine has its own runtime and user data. |
| Same initial knowledge of the owner | Optional reviewed memory seed, copied once without overwriting existing memory. |
| Same project contents | Separate project Git repositories and explicit handling of uncommitted files and project secrets. |

If independent operation is required, ask about exact conversation continuity only if it changes the solution. Once fresh conversations are accepted, stop pushing shared-history infrastructure.

## 2. Discover the source without exposing credentials

1. Resolve the active profile home; do not assume the root `~/.hermes` is the active profile.
2. Inspect `hermes profile install --help`, `hermes profile update --help`, configuration key structure, skill/plugin roots and symlinks.
3. Read workspace rules before inventorying a project's `.env`.
4. List only paths, variable names and optionally populated/empty status. Do not print values, config credential subtrees, raw auth stores or URLs containing credentials.
5. Distinguish a populated credential from a working credential: the inventory does not validate authentication.

Keep the inventory scoped. The Hermes `.env`, a workspace `.env` used by its skills, and a tool-specific `.env` are different files with different destinations. Do not merge client/project secrets into the Hermes environment for convenience. Label example files, backups and locks as noncanonical rather than treating them as active credentials.

OAuth, Composio, GitHub CLI, SSH, browser sessions and vault access may not live in `.env`. List them separately and prefer a fresh login or per-device key. For a named profile, target its own `.env`, not the root profile's file.

## 3. Build a curated staging repository

Create a separate directory, not a Git repository inside the live Hermes home. Authenticate and verify the destination owner, then create the remote explicitly private and read back its visibility.

Typical distribution layout:

```text
distribution.yaml
SOUL.md
config.yaml
skills/
plugins/                 # reviewed code, not credential/runtime stores
memory-seed/             # optional; intentionally outside distribution-owned paths
docs/credenciais-manuais.md
.env.EXAMPLE
.gitignore
```

Declare explicit `distribution_owned` paths in the manifest. Keep memory-seed and documentation outside the installed payload unless the installer genuinely needs them. The installer excludes user data; Git itself does not enforce those installer exclusions.

- Exclude real `.env`, OAuth/auth stores, private keys, state databases/WAL/SHM, logs, sessions, backups, locks and caches before the first commit.
- Do not ship cron jobs, messaging gateway channels, pairing state or machine services by default; a second installation can duplicate actions or compete for the same channel.
- Derive portable configuration from an allowlist. Remove machine paths, local MCP launchers, channel routing and broad local permission grants. Document every behavioral difference from the source.
- Write only the staged distribution's config file. Change a live installation through `hermes config set`, never by rewriting its YAML.
- Materialize reviewed skill symlinks as actual files: the distribution installer rejects symlinks. Detect traversal cycles.
- Preserve required scripts, templates, fonts and assets. A text-only filename allowlist can silently break otherwise copied skills; review omissions and restore safe dependencies.
- Do not rewrite identifiers or Markdown whitespace just to make copied upstream material pass a cosmetic diff check.
- Record platform assumptions in the README. WSL and native Windows have separate data roots; a profile installed in WSL does not automatically appear in a native Desktop backend.

## 4. Scan content before the first commit

Use a real secret scanner against the working directory, not only Git history:

```bash
gitleaks dir /path/to/staging --redact=100 --report-format json --report-path /safe/local/report.json
```

Use the current release's help for flags. If fetching a scanner binary, resolve its official release and keep it in scratch rather than adding it to the distribution.

Also compare staged text against known local credential values in-process without printing them. Collect sensitive scalar fields precisely: marking an entire auth/config container sensitive can misclassify provider names and model IDs as secrets.

Review findings individually. A filename or object-storage key in an example can match a generic API-key rule; add an exception only for the verified literal pattern and exact path. Do not suppress an entire directory or all findings from a generic rule. A private repository is not a substitute for a clean scan.

Inspect staged filenames and contents before committing, and rescan after documentation or asset changes. Report the checks actually executed, not a guarantee that no secret can exist.

## 5. Exercise installation and preservation in isolation

Test with both `HOME` and `HERMES_HOME` pointing to a fresh scratch home. Setting only `HERMES_HOME` to a child of the real Hermes root may still anchor named profiles to that real root. Assert the resolved destination is inside scratch before proceeding.

Run the real CLI install against the local distribution, using a disposable profile name:

```bash
hermes profile install /path/to/staging --name portable-agent -y
```

Check expected skill/plugin counts and absence of symlinks. Then add explicit synthetic sentinel files for local `.env`, memory, session data and a local config edit; hash them, run the real update command, and compare hashes:

```bash
hermes profile update portable-agent -y
```

Assert that no cron jobs were shipped and that optional memory-seed was not auto-installed. Use synthetic sentinels only as test fixtures, never as fabricated production results.

`profile update` preserves local user data and normally preserves `config.yaml`; do not promise that updating the distribution synchronizes model/config changes automatically. Avoid `--force-config` without backup and comparison. Also note that updating a named profile does not modify the source machine's `default` profile.

A passing local install/update test proves packaging and preservation, not Windows execution, provider login or functioning client integrations. Keep those destination checks explicitly pending.

## 6. Publish and explain the update lifecycle

Obtain an independent review, address blockers, then push and read back remote visibility, branch head and expected files. A created empty repository or local commit is not a published distribution. If review is still running, report preparation rather than completion.

Installer workflow, after Hermes and Git authentication exist on the destination:

```bash
hermes profile install github.com/OWNER/REPO --name portable-agent
hermes -p portable-agent model
hermes -p portable-agent
hermes profile update portable-agent
```

The installed profile has no `.git`. Keep a separate authoring clone, pull before editing, copy only reviewed changes into it, scan, commit and push. Explain that editing a local skill does not publish it automatically; concurrent changes require Git reconciliation, not forced overwrites.

Copy optional initial memories only when the destination files are absent, and do not keep overwriting memories as part of normal updates. Keep independent histories independent unless the user explicitly requests a separate history-transfer design.
