# Shared HackMD utilities (hackmd-skills)

Cross-skill contracts and scripts. **Content skills** (`agentic-work-log`, `visualize-hmd`) generate or append body text; **transport** is centralized here and in `push-to-hackmd`.

## Role split

| Layer | Owner | Responsibility |
|-------|--------|----------------|
| Transport | `push-to-hackmd` + `shared/scripts/` | Auth, destination, safe update, API fallbacks |
| Compile | `visualize-hmd` | Standalone HTML → HackMD markup (`to-hackmd.py`) |
| Incremental log | `agentic-work-log` | Collect prompts → callout → append via safe sync |

## Safe update contract (anti-clobber)

All skills that **update** an existing note MUST follow this sequence:

1. **Baseline** — `hackmd-cli export --noteId=<id> > baseline.md` (before local edits).
2. **Local edit** — Build `working.md` (append, replace, or merge in agent memory).
3. **Recheck** — `hackmd-cli export --noteId=<id> > recheck.md`.
4. **Compare** — `diff baseline.md recheck.md`
   - **No diff** → remote unchanged since step 1; safe to push `working.md`.
   - **Has diff** → remote changed during your edit. **Do not blind overwrite.**
     - If changes are only **outside** `<!-- agent-sync:YYYY-MM-DD -->` blocks (manual edits): re-apply your append onto `recheck.md`, then push.
     - If changes touch **inside** an agent-sync block another run may have written: **abort**, show diff summary, ask the user.
5. **Push** — Use [`scripts/safe-sync.sh`](scripts/safe-sync.sh) or equivalent CLI/API update.
6. **State** — Persist local state (timestamps, note id) **only after** a successful push.

**Not transactional:** Between recheck and push, the remote can still change. For critical notes, run `safe-sync.sh` immediately before push (it rechecks again).

### Script: `safe-sync.sh`

```bash
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$REPO_ROOT/shared/scripts/safe-sync.sh" push \
  --note-id "<id>" \
  --baseline-file /tmp/baseline.md \
  --working-file /tmp/working.md \
  [--team-path "<team>"]
```

Exit codes: `0` = updated, `1` = conflict (remote changed since baseline), `2` = usage/CLI error.

## Destination resolution (ask vs infer)

**Default policy: ask-first** when ambiguous; **infer** only when the user gave an unambiguous signal.

| Signal | Action |
|--------|--------|
| URL or `--note=` / `noteId` | Resolve id (see `resolve-note.sh`); use it |
| User says "new note" / `--new-note` | Create; do not reuse config id unless user confirms |
| User names team | `hackmd-cli teams` — must exist; else fail |
| No team mentioned | Personal workspace |
| Title match for update | Exact one match; **zero or 2+** → ask user |
| Scheduled run (`AGENTIC_WORK_LOG_*`, cron) | **Never** auto-create a note; require `hackmd_note_id` in config/env |

## References

- [references/api.md](references/api.md) — folders, images, team routes (single copy for all skills)

## Related skills

- [../push-to-hackmd/SKILL.md](../push-to-hackmd/SKILL.md) — full publish workflow
- [../agentic-work-log/SKILL.md](../agentic-work-log/SKILL.md) — incremental work log
- [../visualize-hmd/SKILL.md](../visualize-hmd/SKILL.md) — HTML visualizations
