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

When using API fallbacks after `hackmd-cli login`, read the token from `~/.hackmd/config.json` (`accessToken`) into `HACKMD_API_TOKEN` in the shell — do not print it.

---

## 3. Determine where to store content

Clarify when not obvious:

| Question | Options |
|----------|---------|
| Workspace | **Personal** (`hackmd-cli notes`) vs **team** (`--teamPath`, from `hackmd-cli teams` — confirm path exists; do not assume a team name) |
| Note | **New** vs **update existing** (user provides URL, note id, or title to match in list) |
| Folder | Optional; API only — list/create via `/folders` or `/teams/{teampath}/folders` |
| Permissions | Default `--readPermission=owner --writePermission=owner` unless user asks otherwise |

Resolve **note id** for updates:

- User gives `https://hackmd.io/...` → extract id or short id; use `team-notes --output=json` if needed.
- Match by title in `hackmd-cli notes` / `team-notes` output.

Record chosen `noteId`, `teamPath` (if any), and `parentFolderId` (if folder used).

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

If a **folder** is required, create the note via API with `parentFolderId`, or `PATCH` after create — see [references/api.md](references/api.md).

Capture returned **note id** from CLI table output.

### Update (existing note) — avoid overwriting remote edits

1. **Baseline**: `hackmd-cli export --noteId=<id> > /tmp/hackmd-baseline.md`
2. Apply local/content changes to a working file.
3. **Recheck**: `hackmd-cli export --noteId=<id> > /tmp/hackmd-recheck.md`
4. `diff /tmp/hackmd-baseline.md /tmp/hackmd-recheck.md`
   - **No diff** → safe to push.
   - **Has diff** → remote changed; merge remote into your working copy, then push (never blind overwrite).
5. **Push**:
   - Personal: `hackmd-cli notes update --noteId=<id> --content="$(cat /path/to/working.md)"`
   - Team: `hackmd-cli team-notes update --teamPath=<team> --noteId=<id> --content="$(cat /path/to/working.md)"`

`team-notes update` requires the **internal note id**, not the public short id.

### Images (optional)

After the note exists, upload local images via API `POST /v1/notes/{noteId}/images`, then insert returned `data.link` into the markdown. Details: [references/api.md](references/api.md).

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

Team endpoints: `/v1/teams/{teampath}/notes` — see [references/api.md](references/api.md).

### Finish

Return to the user:

- Note URL: `https://hackmd.io/<noteId>` (or permalink from API if present)
- Workspace (personal / team name)
- Whether the note was created or updated
- For HTML visualizations: Custom CSS preview reminder

---

## Edge cases

- **Very large content**: Prefer `cat file | hackmd-cli notes create` over inline shell quoting.
- **Binary assets**: Not inlined in notes; upload images via API or host elsewhere and link.
- **No token and user declines install**: Stop with links to join + API authorization docs; do not guess credentials.
- **Conflict on update**: Show a short summary of remote vs local diff; ask how to merge if unclear.

## Related skills

- Rich HTML visualization pipeline: `visualize-hmd`
- Reading HackMD notes: workspace rule `hackmd-cli.mdc` (export before edit, diff before push)

## References

- [references/api.md](references/api.md) — folders, team routes, image upload, swagger paths
- [HackMD API swagger](https://api.hackmd.io/v1/docs/swagger.json)
- [hackmd-cli](https://github.com/hackmdio/hackmd-cli)
