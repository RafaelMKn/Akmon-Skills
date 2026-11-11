---
name: linux-memory-swap-tuning
description: "Use when tuning Linux swap, zram, zswap or memory pressure."
version: 1.0.0
metadata:
  hermes:
    tags: [linux, memory, swap, zram, zswap, psi, fedora]
    category: linux
---

# Linux memory / swap / zram tuning

Change swap or zram settings only with a valid baseline, a rehearsed way back, and a backup of the current state. Root-owned, boot-time changes are not undone by closing the session.

## Workflow

1. **Read the project's spec/decisions first** (e.g. `docs/spec-tecnica.md`, `docs/decisoes.md` in the work folder). Stages, gates and non-goals defined there beat generic advice.

2. **Inventory current state, read-only, and compare with the spec's inventory.** Drop-ins can live in four places; check all: `/etc/systemd/zram-generator.conf{,.d}`, `/run/systemd/...`, `/usr/local/lib/systemd/...`, `/usr/lib/systemd/...`. Also read:

   ```bash
   free -h; swapon --show; zramctl
   cat /sys/block/zram0/comp_algorithm /sys/block/zram0/backing_dev
   cat /sys/module/zswap/parameters/enabled
   sysctl vm.swappiness vm.page-cluster
   cat /proc/pressure/memory /proc/cmdline
   tuned-adm active; systemctl is-active systemd-oomd tuned
   ```

   Fedora default: `zram-generator` vendor config `zram-size = min(ram, 8192)`, `lzo-rle`. An algorithm change goes in a drop-in under `/etc/systemd/zram-generator.conf.d/` and only takes effect at the next boot (or by restarting `systemd-zram-setup@zram0`, which recreates the device and swaps out its contents — do not do that under memory pressure).

3. **Baseline (stage 0) must be taken under the load that causes the symptom.** Sample every ~5 s for ~30 min, read-only: PSI some/full (`avg10`, cumulative `total`), `MemAvailable`, `SwapFree`, zram `mm_stat` (orig, compr, mem_used_total), `pswpin/pswpout/pgmajfault/oom_kill` from `/proc/vmstat`, CPU split, plus controls (swappiness, TuneD profile). Record freeze moments with timestamps and the workload (apps/counts only, no content or URLs). A run on an idle machine (PSI ~0, CPU ~1%, swap I/O near zero) proves nothing — call it inconclusive and repeat under real load instead of using it as a "healthy" reference.

4. **Summarize from the CSV with code** (min/mean/max, deltas of cumulative counters between first and last sample), never by eye. Compression ratio = `orig/compr` (payload) vs `orig/mem_used_total` (physical).

5. **Gate before writing the drop-in:**
   - the user can actually reach a console/rescue/live environment, and the recovery steps exist outside the laptop (phone, password manager, paper) — ask; if they cannot, write the guide and defer the change;
   - a backup of current zram/TuneD state exists (root-owned write: the user types the `pkexec` password, never the agent);
   - the backup of user data is verified, but a boot rehearsal not done stays listed as an open limit.

6. **Apply one variable at a time** (algorithm first; size, swappiness, zswap/writeback later), then compare against the baseline under the same load. Rollback = remove the drop-in and reboot.

## Pitfalls

- Do not run a long collector in the foreground — start it in the background with completion notice, and test it for 15 s first to catch schema/permission errors.
- A background `bash` may print "cannot set terminal process group"; that is noise, check the exit code and the output files.
- `sudo -n` may need a password: never try to bypass; ask the user to run the privileged step.
- Writing `/etc/...` from the agent is a root change — confirm scope; write the recovery guide with the exact filename to remove before creating that file.
