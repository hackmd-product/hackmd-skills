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

Turns the current conversation context — plans, trade-offs, decisions, phases, grilling outcomes — into a polished HTML/CSS visualization, then publishes it to HackMD.

## Trigger phrases

"visualize", "visualize with HTML/CSS", "show in HTML", "show me with a webpage", or any equivalent request to render the current discussion visually.

## Step 1 — Analyze context

Identify what to visualize from the current conversation:

- **Architecture decisions**: two or more competing options with explicit or implicit trade-offs
- **Phased plan**: sequential stages with meaningful boundaries between them
- **Decision tree / crux**: a single difficult concept or constraint that everything else hinges on
- **Topic overview**: when there's no active plan, summarize the discussion as a structured brief

Extract the "crux" — the hardest, most consequential tension or insight — and make sure the layout makes it legible at a glance.

## Step 2 — Design the layout

Choose the dominant layout pattern based on what you found:

| Pattern | When to use |
|---|---|
| **Trade-off map** (two lanes + divider) | Two competing options, clear pros/cons |
| **Phase runway** (4–6 cards in a row) | Sequential stages, each with its own character |
| **Decision grid** (2×N or 3×N cards) | Multiple independent decisions, no natural order |
| **Brief** (hero + section blocks) | General topic overview with sub-sections |

Compose sections. Each section should carry one idea. Sections can be mixed: e.g., a brief with a trade-off map embedded in one section.

## Step 3 — Write the standalone HTML

Write a full standalone HTML file to `/tmp/viz.html`. Include `<!DOCTYPE html>`, `<html>`, `<head>` (with Google Fonts `<link>`), and `<body>`. This file previews correctly in any browser and is the source of truth before the build step.

**CSS principles** (see [reference.md](reference.md) for full token set and patterns):
- Typography: `clamp()` for headings, tight `letter-spacing` (−0.03 to −0.065em) for display sizes
- Cards: `border-radius: var(--radius)`, `border: 1px solid var(--border)`, `background: var(--bg-surface)`
- Picked/active state: tint border and background with `--primary` at low opacity
- Labels: `font-size: 12px; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; color: var(--primary)`
- Use `<details><summary>` for progressive disclosure of dense reference material

**CSS should show, not adorn.** Every visual treatment should make a distinction legible:
- Tint a card to signal "picked"
- Use a green badge for "confirmed", amber for "risk", red for "blocker"
- Draw a phase boundary with a connecting element, not just whitespace

**Element safety notes** (enforced by the build script, but useful to know):
- Avoid `<main>` — stripped by HackMD's sanitizer; build script replaces it with `<div>`
- `<div>`, `<section>`, `<article>`, `<header>`, `<nav>`, `<aside>`, `<details>`, `<summary>` are safe
- No JavaScript (stripped regardless)

## Step 4 — Build HackMD-compatible output

Run the build script to produce `/tmp/viz-hackmd.html`:

```bash
python3 /path/to/visualize-hmd/scripts/to-hackmd.py \
  /tmp/viz.html \
  /tmp/viz-hackmd.html
```

What the script does:
1. Strips outer `<html>` / `<head>` / `<body>` tags
2. Extracts `<style>`, dedents CSS to column 0, prepends Google Fonts `@import` and `.markdown-body { max-width: none !important; padding: 0 !important; }`
3. Rewrites `body {}` → `.viz-root {}`, removes `html {}`, rewrites bare `a {}` → `.viz-root a {}`
4. Removes all blank lines from the HTML body (prevents Type 6 HTML block termination — see below)
5. Strips leading whitespace from all HTML lines (prevents 4-space code-block triggering)
6. Replaces `<main …>` / `</main>` with `<div …>` / `</div>`
7. Wraps body in `<div class="viz-root">…</div>`

## Step 5 — Publish to HackMD

Choose one of three channels:

### CLI

```bash
# Create
hackmd-cli notes create \
  --title="Visualization — <topic>" \
  --readPermission=owner \
  --writePermission=owner \
  --content="$(cat /tmp/viz-hackmd.html)"

# Update existing
hackmd-cli notes update \
  --noteId=<noteId> \
  --content="$(cat /tmp/viz-hackmd.html)"
```

### REST API

```bash
# Create
curl -s -X POST https://api.hackmd.io/v1/notes \
  -H "Authorization: Bearer $HACKMD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Visualization — <topic>\",\"content\":$(jq -Rs . < /tmp/viz-hackmd.html),\"readPermission\":\"owner\",\"writePermission\":\"owner\"}"

# Update existing
curl -s -X PATCH https://api.hackmd.io/v1/notes/<noteId> \
  -H "Authorization: Bearer $HACKMD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"content\":$(jq -Rs . < /tmp/viz-hackmd.html)}"
```

### MCP

```
hackmd_create_note(
  title="Visualization — <topic>",
  content=<contents of /tmp/viz-hackmd.html>,
  readPermission="owner",
  writePermission="owner"
)
```

After creation, report the URL to the user: `https://hackmd.io/<noteId>`

## Step 6 — Remind user to enable Custom CSS preview

HTML/CSS visualizations embed styles in `<style>` blocks. HackMD applies those styles only when **Custom CSS** preview is enabled.

After returning the note URL, **always** remind the user:

> Open the note, click the **paintbrush icon** in the toolbar (tooltip: "Select theme to preview"), and choose **Custom CSS** to see the visualization styled correctly.

Without this step, the note renders as unstyled markup. Do not skip this reminder for HTML visualizations.

---

## Why blank lines break HackMD rendering

HackMD uses markdown-it (CommonMark). HTML block parsing rules:

| Block type | Examples | Ends at |
|---|---|---|
| Type 1 | `<style>`, `<script>`, `<pre>` | Closing tag — blank lines **OK** inside |
| Type 6 | `<div>`, `<section>`, `<header>`, … | **Blank line** — terminates the block |

A blank line inside a `<div>` ends the HTML block. Content after the blank line is re-parsed as Markdown. If that content has 4+ spaces of indentation, it becomes a code block. This is why the build script removes all blank lines from the body HTML.

---

## What good looks like

- A 300-line Markdown plan becomes 6–10 decision cards, each with a label, heading, context, and 2–3 lines of consequence
- Trade-offs are spatially separated — reader can scan the layout and immediately understand the tension
- The crux gets the most visual weight: largest type, highest contrast, or most prominent position
- Progressive disclosure (`<details>`) hides supporting detail so the primary read is clean
- The whole artifact fits one screen at 1200px wide without scrolling past the hero

## Antipatterns

- Do not generate decorative sections that restate what the cards already say
- Do not use more than 3 accent colors in a single artifact
- Do not omit the crux — if the context has a hard trade-off, make it visible
- Do not add JavaScript even as a fallback

---

## Design system

See [reference.md](reference.md) for the full token set, spacing scale, and layout patterns.
