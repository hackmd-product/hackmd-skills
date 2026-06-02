---
name: visualize-hmd
description: >-
  Generate an HTML/CSS visualization of the currently discussed plan, topic,
  architecture decisions, or trade-offs, then publish it to HackMD (My workspace).
  Runs a build step that converts standalone HTML to HackMD-compatible markup
  before publishing via CLI, API, or MCP.
  Use when the user says "visualize", "visualize with HTML/CSS", "show in HTML",
  "show me with a webpage", or any equivalent request to render a plan visually
  and publish to HackMD.
---

# Visualize — HackMD

Turns conversation context into HTML/CSS, builds HackMD-safe markup, publishes to HackMD.

**Scope:** User wants a **generated visualization** from the discussion. If they already have a file to upload, use `push-to-hackmd` instead.

**Paths:** In a monorepo checkout, set `SKILL_DIR` to this folder (e.g. `hackmd-skills/visualize-hmd`). Scripts live under `$SKILL_DIR/scripts/`.

---

## For agents (workflow)

### Step 1 — Analyze context

Identify: architecture trade-offs, phased plan, decision crux, or topic overview. Extract the **crux** (hardest tension) — it gets the most visual weight.

### Step 2 — Layout selection (decision tree)

```
Exactly 2 competing options with clear pros/cons?
  → Trade-off map
4–6 sequential phases with distinct boundaries?
  → Phase runway
3+ independent decisions, no natural order?
  → Decision grid
Otherwise / mixed / overview only?
  → Brief (hero + sections); may embed another pattern in one section
Multiple patterns apply?
  → Pick the one that makes the crux most visible
```

| Pattern | When to use |
|---------|-------------|
| **Trade-off map** | Two lanes + divider |
| **Phase runway** | 4–6 cards in a row |
| **Decision grid** | 2×N or 3×N cards |
| **Brief** | General overview |

Use HTML fragments and tokens from [reference.md](reference.md) — do not invent new CSS class names.

### Step 3 — Write standalone HTML

Write `/tmp/viz.html` with `<!DOCTYPE html>`, `<html>`, `<head>` (Google Fonts `<link>`), `<body>`. No JavaScript. Avoid `<main>` (build script rewrites to `<div>`).

### Step 4 — Build HackMD output

```bash
SKILL_DIR="<path-to>/visualize-hmd"
python3 "$SKILL_DIR/scripts/to-hackmd.py" --strict /tmp/viz.html /tmp/viz-hackmd.html
```

Check `$?` — non-zero means conversion failed; do not publish.

**One-shot create (optional):**

```bash
VIZ_TITLE="Visualization — <topic>" "$SKILL_DIR/scripts/publish-viz.sh" /tmp/viz.html /tmp/viz-hackmd.html
```

### Step 5 — Publish channel selection

```
hackmd-cli in PATH and hackmd-cli whoami succeeds?
  yes → CLI (preferred)
else HACKMD_API_TOKEN set?
  yes → REST API (see push-to-hackmd / shared/references/api.md)
else HackMD MCP available?
  yes → MCP create_note
else → stop; instruct user to hackmd-cli login or set token
```

**Create vs update:**

| User intent | Action |
|-------------|--------|
| "visualize" (default) | **Create** new note |
| "update" / provides note URL or id | Resolve id → export baseline → replace body via [../../shared/scripts/safe-sync.sh](../../shared/scripts/safe-sync.sh) |
| Same title already exists | Warn; ask before overwrite |

For updates, follow [../../shared/README.md](../../shared/README.md).

### Step 6 — Custom CSS + size

- Append or confirm reminder: `<!-- Enable Custom CSS preview: paintbrush → Custom CSS -->`
- Tell the user to enable **Custom CSS** in the toolbar (required for `<style>` to apply).
- If built output **> 500 KB**, warn; suggest more `<details>` or split notes.

### Failure modes

| Failure | Recovery |
|---------|----------|
| `to-hackmd.py --strict` fails | Fix HTML (blank lines in body, `<main>`, unscoped `body{}`); rebuild |
| Publish fails | Do not claim success; report CLI/API error |
| User sees unstyled note | Custom CSS not enabled — repeat step 6 |

---

## For manual users

See [README.md](README.md) and [reference.md](reference.md) for design tokens, patterns, and CLI examples.

---

## Why blank lines break HackMD rendering

HackMD uses markdown-it (CommonMark). Type 6 HTML blocks (`<div>`, etc.) **end at a blank line**. The build script removes blank lines inside the body and strips 4-space indentation so content is not parsed as code blocks.

---

## Antipatterns

- Decorative sections that repeat card content
- More than 3 accent colors
- Omitting the crux when a hard trade-off exists
- JavaScript (stripped by HackMD)

---

## Related skills

- [../push-to-hackmd/SKILL.md](../push-to-hackmd/SKILL.md) — generic publish / backup
- [../agentic-work-log/SKILL.md](../agentic-work-log/SKILL.md) — link new viz URL in work log callout when useful
- [../shared/README.md](../shared/README.md) — safe update contract

## Design system

See [reference.md](reference.md).
