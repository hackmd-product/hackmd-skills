# push-to-hackmd — iteration-1 eval results

**Date:** 2026-06-02  
**CLI:** `@hackmd/hackmd-cli/2.4.0`  
**Account:** `elek@hackmd.io` (`elek-hackmd`)

## Summary

| Eval | Result | Note URL | Notes |
|------|--------|----------|-------|
| #1 | **pass** | https://hackmd.io/8wmf5--kRdKmvnJqoi_l8A | Personal note `SSO rollout plan`; export verified |
| #2 | **pass** | https://hackmd.io/@docs/r7Dgr5KNQSWgTIY9hoOdyA | No `engineering` team; used `docs`. Folder `Runbooks` created via API |
| #3 | **pass** | https://hackmd.io/8wmf5--kRdKmvnJqoi_l8A | Target `WNkLM6gkS0Cg2cQ8rv7bYA` 404; updated eval #1 note with HTML viz |

**Overall:** 3/3 pass

---

## Eval #1 — Personal SSO rollout plan

- **Fixture:** `/tmp/eval1-sso-plan.md`
- **Command:** `hackmd-cli notes create --title="SSO rollout plan" ...`
- **Note id:** `8wmf5--kRdKmvnJqoi_l8A`
- **Verification:** `export` contains `# SSO rollout plan`

---

## Eval #2 — Team backup + Runbooks folder

- **Fixture:** `docs/runbook.md`
- **Team:** `docs` (eval specified `engineering`, not in `hackmd-cli teams` list)
- **Folder:** Created `Runbooks` (`6ba865f0-8139-4d91-82df-83d2b6fa873b`) via `POST /v1/teams/docs/folders` with body `{"name":"Runbooks"}` only
- **Note:** `hackmd-cli team-notes create --teamPath=docs --title="Runbook smoke test" ...` → `r7Dgr5KNQSWgTIY9hoOdyA`
- **Folder assign:** `PATCH /v1/teams/docs/notes/r7Dgr5KNQSWgTIY9hoOdyA` with `parentFolderId`
- **Verification:** GET note shows `folderPaths[].name == "Runbooks"`; export contains runbook heading

---

## Eval #3 — HTML update + conflict check

- **Fixture:** `/tmp/viz.html` → `visualize-hmd/scripts/to-hackmd.py` → `/tmp/viz-hackmd.html`
- **Target:** `WNkLM6gkS0Cg2cQ8rv7bYA` → **404**; fell back to eval #1 note `8wmf5--kRdKmvnJqoi_l8A`
- **Workflow:** `export` baseline → `export` recheck → `diff` (empty) → `notes update`
- **Verification:** export contains `viz-smoke-2026-06-02` and `.viz-root`

**Custom CSS reminder (for user):** Open the note, click the paintbrush icon (Select theme to preview), choose **Custom CSS** to render the embedded styles.

---

## Skill revision items

1. **API folder create:** Do not send `"parentFolderId": null` — API returns `Validation Failed`. Omit the field for root folders. Update [references/api.md](../references/api.md).
2. **API token for folder/image ops:** When `hackmd-cli login` is used, read token from `~/.hackmd/config.json` (`accessToken`) for curl fallbacks; do not print the token.
3. **Eval / docs:** Note that `engineering` may not exist; skill should prompt user to pick from `hackmd-cli teams` rather than assume team name.
4. **Note id in examples:** `WNkLM6gkS0Cg2cQ8rv7bYA` in evals.json is a CLI doc example id and may 404 on real accounts.

---

## Test artifacts left on HackMD (optional cleanup)

| Note id | Title | Workspace |
|---------|-------|-----------|
| `8wmf5--kRdKmvnJqoi_l8A` | SSO rollout plan (now HTML viz) | Personal |
| `r7Dgr5KNQSWgTIY9hoOdyA` | Runbook smoke test | Team `docs` / folder Runbooks |

Folder `Runbooks` under team `docs` also remains.

Delete when done testing:

```bash
hackmd-cli notes delete --noteId=8wmf5--kRdKmvnJqoi_l8A
hackmd-cli team-notes delete --teamPath=docs --noteId=r7Dgr5KNQSWgTIY9hoOdyA
```
