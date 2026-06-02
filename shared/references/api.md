# HackMD API fallback

Base URL: `https://api.hackmd.io/v1`  
Auth header: `Authorization: Bearer $HACKMD_API_TOKEN`

Full spec: [swagger.json](https://api.hackmd.io/v1/docs/swagger.json)

## When to use API instead of CLI

| Need | Endpoint |
|------|----------|
| Folders (list/create/move) | `/folders`, `/teams/{teampath}/folders` |
| Place note in folder | `parentFolderId` on `POST`/`PATCH` note |
| Image upload | `POST /notes/{noteId}/images` |
| CLI not installed and user declined install | All note operations |

## Folders (personal workspace)

```bash
# List
curl -s -H "Authorization: Bearer $HACKMD_API_TOKEN" https://api.hackmd.io/v1/folders

# Create (root folder — omit parentFolderId; null is rejected)
curl -s -X POST https://api.hackmd.io/v1/folders \
  -H "Authorization: Bearer $HACKMD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Folder"}'

# Create note inside folder
curl -s -X POST https://api.hackmd.io/v1/notes \
  -H "Authorization: Bearer $HACKMD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Title\",\"content\":$(jq -Rs . < note.md),\"parentFolderId\":\"<folder-uuid>\",\"readPermission\":\"owner\",\"writePermission\":\"owner\"}"

# Move existing note into folder
curl -s -X PATCH "https://api.hackmd.io/v1/notes/<noteId>" \
  -H "Authorization: Bearer $HACKMD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"parentFolderId":"<folder-uuid>"}'
```

Team folders: replace `/folders` with `/teams/{teampath}/folders` and team notes under `/teams/{teampath}/notes`.

## Image upload

`POST /v1/notes/{noteId}/images` — `multipart/form-data`, field name `image`.

```bash
curl -s -X POST "https://api.hackmd.io/v1/notes/<noteId>/images" \
  -H "Authorization: Bearer $HACKMD_API_TOKEN" \
  -F "image=@/path/to/screenshot.png"
```

Response shape:

```json
{ "data": { "link": "https://..." } }
```

Insert in markdown: `![alt](<link>)`.

Upload requires an existing note id (create note first, then upload, then patch content if images were embedded inline).

## Team notes

```bash
# List
curl -s -H "Authorization: Bearer $HACKMD_API_TOKEN" \
  "https://api.hackmd.io/v1/teams/<teampath>/notes"

# Create
curl -s -X POST "https://api.hackmd.io/v1/teams/<teampath>/notes" \
  -H "Authorization: Bearer $HACKMD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Title\",\"content\":$(jq -Rs . < note.md)}"

# Update
curl -s -X PATCH "https://api.hackmd.io/v1/teams/<teampath>/notes/<noteId>" \
  -H "Authorization: Bearer $HACKMD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"content\":$(jq -Rs . < note.md)}"
```

## Note ids

- **API note id**: long alphanumeric (e.g. `raUuSTetT5uQbqQfLnz9lA`) — use for `export`, `update`, API paths.
- **User/team path**: short public slug in URLs — resolve via `hackmd-cli team-notes --teamPath=X --output=json` or GET note metadata.

## Permissions (common values)

- `readPermission` / `writePermission`: `owner` | `signed_in` | `guest`
- `commentPermission`: `disabled` | `forbidden` | `owners` | `signed_in_users` | `everyone`

Match CLI defaults (`owner` / `owner` / `disabled`) unless the user specifies otherwise.
