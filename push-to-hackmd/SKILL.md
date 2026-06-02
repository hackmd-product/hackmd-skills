---
name: push-to-hackmd
description: >-
  Sync plans, Markdown, plaintext, HTML/CSS, or local files to HackMD notes
  (personal or team workspace, optional folders). Use whenever the user says
  "push to HackMD", "save to HackMD", "backup at HackMD", "publish to HackMD",
  "upload to HackMD", or wants to back up or publish content to hackmd.io—even
  if they only mention HackMD in passing.
---

# Push to HackMD

Publish or back up content to [HackMD](https://hackmd.io). Prefer **`hackmd-cli`**; fall back to the [HackMD REST API](https://api.hackmd.io/v1/docs/swagger.json) when the CLI cannot do the operation (folders, image upload, `parentFolderId`).

## Trigger phrases

`push to HackMD`, `save to HackMD`, `backup at HackMD`, and equivalents (`publish to HackMD`, `sync to HackMD`, `put this on HackMD`).

## Workflow overview

```
Task Progress:
- [ ] 0. Resolve content to sync
- [ ] 1. Ensure hackmd-cli (or API token) is ready
- [ ] 2. Confirm HackMD auth (token / login)
- [ ] 3. Choose destination (workspace, team, folder, note)
- [ ] 4. Sync (create or update; avoid clobbering remote edits)
```

---

## 0. Determine content

Identify what the user wants on HackMD. Supported in note body: **plaintext**, **Markdown**, **HTML**, **CSS** (inline or in `<style>`). **Images**: embed as URLs, or upload via API after a note exists (see [references/api.md](references/api.md)).

| Source | How to obtain |
|--------|----------------|
| Current session | Plan, summary, or pasted text from the conversation |
| Explicit path | Read the file(s) the user named |
| Workspace default | If context is obvious (e.g. single open `*.md` / `*.html`), use it; otherwise ask |
| Multiple files | Combine with clear headings, or one note per file—confirm with user |

**HTML/CSS**: If content is standalone HTML for rich layout, consider running `visualize-hmd`’s build step (`to-hackmd.py`) when blank lines or `<main>` would break HackMD rendering. After publish, remind the user to enable **Custom CSS** preview (paintbrush → Custom CSS) on the note.

**Title**: Derive from first `#` heading, filename stem, or ask once if unclear.

---

## 1. Tooling — `hackmd-cli` first

### Check installation

```bash
command -v hackmd-cli && hackmd-cli version
```

If missing, tell the user:

- Install: `npm install -g @hackmd/hackmd-cli` ([hackmd-cli repo](https://github.com/hackmdio/hackmd-cli))
- Then re-run the check.

**Only install after explicit permission.** Run:

```bash
npm install -g @hackmd/hackmd-cli
```

(or execute [scripts/ensure-cli.sh](scripts/ensure-cli.sh) — exits 0 if already installed, installs when user has approved).

### CLI capabilities (use these before API)

| Action | Command |
|--------|---------|
| Login | `hackmd-cli login` (prompts for token) |
| Whoami | `hackmd-cli whoami` |
| List personal notes | `hackmd-cli notes` |
| List teams | `hackmd-cli teams` |
| List team notes | `hackmd-cli team-notes --teamPath=<team>` |
| Export note | `hackmd-cli export --noteId=<id>` |
| Create personal | `hackmd-cli notes create --title="..." --content="..." --readPermission=owner --writePermission=owner` |
| Update personal | `hackmd-cli notes update --noteId=<id> --content="..."` |
| Create team | `hackmd-cli team-notes create --teamPath=<team> --title="..." --content="..." ...` |
| Update team | `hackmd-cli team-notes update --teamPath=<team> --noteId=<id> --content="..."` |

Pipe large bodies: `cat file.md | hackmd-cli notes create --title="..."`.

**Short URLs / team paths**: `export` accepts API note id; for `@team/shortId`, resolve internal id via `hackmd-cli team-notes --teamPath=<team> --output=json` then export/update.

**Folders** are not in the CLI — use API (`POST /folders`, `parentFolderId` on note create/update). See [references/api.md](references/api.md).

---

## 2. Authentication

Ask: **Do you already have a HackMD API token?**

If **no**:

1. Account: [https://hackmd.io/join](https://hackmd.io/join)
2. Create token: [https://hackmd.io/@docs/api-authorization](https://hackmd.io/@docs/api-authorization)
3. Either:
   - `hackmd-cli login` and paste the token, or
   - `export HACKMD_API_TOKEN="<token>"` for API/curl fallbacks

Verify:

```bash
hackmd-cli whoami
# or
curl -s -H "Authorization: Bearer $HACKMD_API_TOKEN" https://api.hackmd.io/v1/me
```

Do not echo or log the token. If login fails, re-check token scope and expiry.

When using API fallbacks after `hackmd-cli login`, read the token from `~/.hackmd/config.json` (`accessToken`) into `HACKMD_API_TOKEN` in a **subshell** for `curl` only — **never** `echo` the token or paste it into chat.

---

## 3. Determine where to store content

**Policy: ask-first when ambiguous.** Infer only when the user gave an explicit URL, note id, or unambiguous phrase (`new note`, `update this note`, team name that exists in `hackmd-cli teams`).

### Decision tree

```
User gave hackmd.io URL or note id?
  yes → ../../shared/scripts/resolve-note.sh "<url-or-id>" → noteId (+ team:PATH on stderr if team URL)
User said "new" / "create" / no existing note implied?
  yes → create path (step 4); capture new noteId from CLI output
User said "update" / gave title to match?
  yes → list notes (personal or team):
        hackmd-cli notes --output=json | jq -r --arg t "Exact Title" '[.[] | select(.title==$t)]'
        (team: hackmd-cli team-notes --teamPath=X --output=json | jq …)
        • 0 matches → ask user
        • 1 match → use .id
        • 2+ matches → list candidates; ask user (never pick arbitrarily)
User named a team?
  yes → hackmd-cli teams — teamPath must appear; else stop with error
No team mentioned?
  → personal workspace (hackmd-cli notes)
Folder requested?
  → API only; see ../../shared/references/api.md
```

Record `noteId`, `teamPath` (if any), `parentFolderId` (if folder used).

---

## 4. Sync contents

### Create (new note)

**Personal:**

```bash
hackmd-cli notes create \
  --title="<title>" \
  --readPermission=owner \
  --writePermission=owner \
  --content="$(cat /path/to/content.md)"
```

**Team:**

```bash
hackmd-cli team-notes create \
  --teamPath=<team> \
  --title="<title>" \
  --readPermission=owner \
  --writePermission=owner \
  --content="$(cat /path/to/content.md)"
```

If a **folder** is required, create the note via API with `parentFolderId`, or `PATCH` after create — see [../../shared/references/api.md](../../shared/references/api.md).

Capture returned **note id** from CLI table output.

### Update (existing note) — avoid overwriting remote edits

Follow [../../shared/README.md](../../shared/README.md) (safe update contract). Prefer the script:

```bash
# After building /path/to/working.md from baseline + your edits:
REPO="$(cd "<skill-or-repo-root>" && pwd)"   # hackmd-skills checkout, or path to shared/
"$REPO/shared/scripts/safe-sync.sh" push \
  --note-id "<id>" \
  --baseline-file /tmp/hackmd-baseline.md \
  --working-file /path/to/working.md \
  [--team-path "<team>"]
```

Manual equivalent: export baseline → edit working copy → `safe-sync.sh push` (rechecks export before update). Exit `1` = conflict — show diff summary and **ask the user** how to merge; do not blind overwrite.

`team-notes update` requires the **internal note id**, not the public short id.

### Images (optional)

After the note exists, upload local images via API `POST /v1/notes/{noteId}/images`, then insert returned `data.link` into the markdown. Details: [../../shared/references/api.md](../../shared/references/api.md).

### API fallback

When CLI is unavailable or insufficient:

```bash
# Create
curl -s -X POST https://api.hackmd.io/v1/notes \
  -H "Authorization: Bearer $HACKMD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"<title>\",\"content\":$(jq -Rs . < file.md),\"readPermission\":\"owner\",\"writePermission\":\"owner\"}"

# Update
curl -s -X PATCH "https://api.hackmd.io/v1/notes/<noteId>" \
  -H "Authorization: Bearer $HACKMD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"content\":$(jq -Rs . < file.md)}"
```

Team endpoints: `/v1/teams/{teampath}/notes` — see [../../shared/references/api.md](../../shared/references/api.md).

### Finish

Return to the user:

- Note URL: `https://hackmd.io/<noteId>` (or permalink from API if present)
- Workspace (personal / team name)
- Whether the note was created or updated
- For HTML visualizations: Custom CSS preview reminder

---

## Edge cases

- **Very large content**: Prefer `cat file | hackmd-cli notes create` over inline shell quoting. If content **> 5 MB**, warn and confirm; if **> 50 MB**, stop (check HackMD limits).
- **HTML with `<style>`**: Suggest `visualize-hmd` + `to-hackmd.py` if layout breaks; append HTML comment: `<!-- Enable Custom CSS preview (paintbrush → Custom CSS) -->`
- **Binary assets**: Not inlined in notes; upload images via API or host elsewhere and link.
- **No token and user declines install**: Stop with links to join + API authorization docs; do not guess credentials.
- **Conflict on update**: Show a short summary of remote vs local diff; ask how to merge if unclear.

## Related skills

- Rich HTML visualization pipeline: `visualize-hmd`
- Reading HackMD notes: workspace rule `hackmd-cli.mdc` (export before edit, diff before push)

## References

- [../../shared/README.md](../../shared/README.md) — safe update contract, destination policy
- [../../shared/references/api.md](../../shared/references/api.md) — folders, team routes, image upload
- [../../shared/scripts/safe-sync.sh](../../shared/scripts/safe-sync.sh) — push with recheck
- [HackMD API swagger](https://api.hackmd.io/v1/docs/swagger.json)
- [hackmd-cli](https://github.com/hackmdio/hackmd-cli)
