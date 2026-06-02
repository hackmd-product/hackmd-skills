# visualize-hmd

An agent skill for **Claude** and **Cursor** that turns plans, trade-offs, and architecture decisions into polished HTML/CSS visualizations—and publishes them to [HackMD](https://hackmd.io).

Say *"visualize this in HTML"* or *"show me with a webpage"* during a planning session, and the agent produces a scannable brief: trade-off maps, phase runways, decision grids, or topic overviews—then ships it to your HackMD My workspace.

## What it does

| Step | Action |
|------|--------|
| 1 | Analyze conversation context and find the **crux** (the hardest tension or insight) |
| 2 | Pick a layout pattern: trade-off map, phase runway, decision grid, or brief |
| 3 | Write standalone HTML (previewable in any browser) |
| 4 | Run `to-hackmd.py` to convert markup for HackMD's renderer |
| 5 | Publish via **CLI**, **REST API**, or **MCP** |

## Why a build step?

HackMD renders note content through markdown-it (CommonMark). Standalone HTML does not paste cleanly:

| Issue | Symptom | Fix in `to-hackmd.py` |
|-------|---------|------------------------|
| Type 6 HTML blocks end at blank lines | Sections become code blocks | Remove all blank lines from body HTML |
| 4-space indentation | Indented tags render as code | Strip leading whitespace on every line |
| `<main>` stripped by sanitizer | Tag text appears on the page | Replace `<main>` with `<div>` |
| `.markdown-body` max-width | Layout squeezed to a narrow column | Override `max-width` and `padding` |
| `<link>` for fonts ignored | Missing typography | Move fonts to `@import` inside `<style>` |

The skill authors HTML in a normal standalone file; the script produces HackMD-safe output.

## Installation

This skill lives in the [hackmd-skills](https://github.com/hackmd-product/hackmd-skills) monorepo under `visualize-hmd/`. The former standalone repo [hackmd-product/visualize-hmd](https://github.com/hackmd-product/visualize-hmd) is superseded by that path.

### Cursor

```bash
git clone https://github.com/hackmd-product/hackmd-skills.git /tmp/hackmd-skills
cp -R /tmp/hackmd-skills/visualize-hmd ~/.cursor/skills/
```

Or add as a project skill:

```bash
git clone https://github.com/hackmd-product/hackmd-skills.git .cursor/skills-src/hackmd-skills
cp -R .cursor/skills-src/hackmd-skills/visualize-hmd .cursor/skills/
```

Cursor discovers skills from `SKILL.md` automatically.

### Claude Code

```bash
git clone https://github.com/hackmd-product/hackmd-skills.git /tmp/hackmd-skills
cp -R /tmp/hackmd-skills/visualize-hmd ~/.claude/skills/
```

## Usage (manual)

If you want to run the pipeline yourself:

```bash
# 1. Author standalone HTML (your design)
#    Save as viz.html with <!DOCTYPE html>, <html>, <head>, <body>

# 2. Convert for HackMD
python3 scripts/to-hackmd.py viz.html viz-hackmd.html

# 3. Publish (pick one channel)
hackmd-cli notes create \
  --title="Visualization — My Topic" \
  --readPermission=owner \
  --writePermission=owner \
  --content="$(cat viz-hackmd.html)"
```

After creation, open `https://hackmd.io/<noteId>` (My workspace).

**Enable Custom CSS preview:** Click the **paintbrush icon** in the toolbar (tooltip: "Select theme to preview") and choose **Custom CSS**. Embedded `<style>` blocks do not apply until this is on—the note will look unstyled otherwise.

### REST API

```bash
export HACKMD_API_TOKEN=your_token

curl -s -X POST https://api.hackmd.io/v1/notes \
  -H "Authorization: Bearer $HACKMD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Visualization — My Topic\",\"content\":$(jq -Rs . < viz-hackmd.html),\"readPermission\":\"owner\",\"writePermission\":\"owner\"}"
```

### MCP

Use your HackMD MCP server's note-creation tool with the contents of `viz-hackmd.html` as the note body.

## Layout patterns

| Pattern | Best for |
|---------|----------|
| **Trade-off map** | Two competing options with pros/cons |
| **Phase runway** | Sequential stages (Phase 0 → 1 → 2 → 3) |
| **Decision grid** | Independent open questions for a dev team |
| **Brief** | General topic overview with hero + sections |

See [reference.md](reference.md) for design tokens, card styles, and CSS snippets.

## Repository structure

In [hackmd-skills](https://github.com/hackmd-product/hackmd-skills):

```
hackmd-skills/visualize-hmd/
├── SKILL.md              # Agent instructions (workflow + constraints)
├── reference.md          # Design system: tokens, patterns, HackMD limits
├── scripts/
│   └── to-hackmd.py      # Standalone HTML → HackMD-compatible markup
└── README.md
```

## Requirements

- **Python 3** — for `to-hackmd.py` (stdlib only, no pip dependencies)
- **HackMD account** — for publishing
- One of:
  - [@hackmd/hackmd-cli](https://www.npmjs.com/package/@hackmd/hackmd-cli) — `hackmd-cli login` first
  - HackMD API token — for `curl` examples
  - HackMD MCP server — for agent-integrated publishing

## What good output looks like

- A long Markdown plan becomes **6–10 decision cards**, each with a label, heading, and consequence
- Trade-offs are **spatially separated**—the tension is obvious at a glance
- The **crux** gets the most visual weight (largest type, strongest contrast)
- Dense detail hides behind `<details>` so the first screen stays clean
- No JavaScript; CSS Grid / Flexbox only

## Limitations

- **No `<script>`** — HackMD strips JavaScript
- **No `<html>` / `<head>` / `<body>` in published content** — use the build script
- **Avoid `<main>`** — sanitizer removes the tag and may leak raw markup
- Prefer **`<div>`** for layout containers (not `<main>`)

## License

See repository license file (if present). Maintained by [HackMD](https://hackmd.io) product team.

## Related

- [HackMD API documentation](https://hackmd.io/c/collections/p2DGPdMRb)
- [hackmd-cli](https://www.npmjs.com/package/@hackmd/hackmd-cli)
