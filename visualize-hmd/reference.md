# Visualize — Design Reference

## Full token set

```css
:root {
  /* Typography */
  --text-emphasis:    #18181b;   /* headings, strong copy */
  --text-default:     #3f3f46;   /* body text */
  --text-subtle:      #71717a;   /* captions, helper text */

  /* Surfaces */
  --bg-page:          #f4f4f5;   /* outermost background */
  --bg-surface:       #fdfdfd;   /* card face */
  --bg-soft:          #fafafa;   /* nested surface */
  --bg-muted:         #f4f4f5;   /* hover, inactive */

  /* Brand */
  --primary:          #564dff;
  --primary-strong:   #2e01a5;
  --primary-soft:     #eeedff;

  /* Semantic */
  --green:            #16a34a;
  --green-soft:       #eaf8ef;
  --amber:            #b7791f;
  --amber-soft:       #fff7e6;
  --red:              #dc2626;
  --red-soft:         #fef2f2;

  /* Structure */
  --border:           #d4d4d8;
  --radius:           18px;
  --shadow:           0 24px 70px rgb(24 24 27 / 10%);
}
```

---

## Layout patterns

### Trade-off map

Three-column grid: [option A] [divider/choice] [option B].

```html
<div class="tradeoff-map">
  <article class="option option--muted">
    <span class="label">Option A</span>
    <h3>…</h3>
    <ul>…</ul>
  </article>

  <div class="choice-pivot" aria-hidden="true">
    <span>Constraint</span>
    <strong>Pick first</strong>
  </div>

  <article class="option option--picked">
    <span class="label">Option B</span>
    <h3>…</h3>
    <ul>…</ul>
  </article>
</div>
```

```css
.tradeoff-map {
  display: grid;
  grid-template-columns: 1fr 120px 1fr;
  gap: 16px;
  align-items: stretch;
}
.option {
  padding: 24px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg-surface);
}
.option--picked {
  border-color: rgb(86 77 255 / 38%);
  background: linear-gradient(180deg, rgb(86 77 255 / 8%), transparent 60%), #fff;
}
.option--muted {
  background: linear-gradient(180deg, #fff, #f8f8f9);
}
.choice-pivot {
  align-self: center;
  display: grid;
  place-items: center;
  gap: 8px;
  padding: 18px 8px;
  border: 1px dashed rgb(86 77 255 / 45%);
  border-radius: 999px;
  color: var(--primary);
  text-align: center;
  background: var(--primary-soft);
}
```

### Phase runway

Four-column (or N-column) card strip.

```html
<div class="phase-runway">
  <article class="phase-card phase-card--zero">
    <span class="phase-index">0</span>
    <h3>Name</h3>
    <p>What happens here.</p>
    <code>key constraint</code>
  </article>
  <!-- repeat for each phase -->
</div>
```

```css
.phase-runway {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}
.phase-card {
  padding: 22px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg-surface);
}
.phase-card--zero {
  border-color: rgb(22 163 74 / 36%);
  background: linear-gradient(180deg, rgb(22 163 74 / 10%), transparent 58%), #fff;
}
.phase-index {
  display: inline-grid;
  place-items: center;
  width: 42px;
  height: 42px;
  margin-bottom: 22px;
  color: #fff;
  font-weight: 800;
  border-radius: 14px;
  background: var(--primary);
}
.phase-card--zero .phase-index { background: var(--green); }
```

### Decision grid

3-column (or 2-column) grid of cards for independent decisions.

```html
<div class="decision-grid">
  <article class="decision-card">
    <span class="decision-num">01</span>
    <h3>Decision title</h3>
    <p>Stakes and consequence.</p>
  </article>
</div>
```

```css
.decision-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
.decision-card {
  padding: 20px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg-surface);
}
.decision-num {
  display: inline-flex;
  margin-bottom: 18px;
  font-size: 13px;
  font-weight: 800;
  color: var(--primary);
}
```

### Brief hero

Hero block for topic overview. Combine with a right-side "primary bet" card.

```html
<header class="viz-hero">
  <div class="hero-grid">
    <div>
      <p class="eyebrow">Visualization · topic</p>
      <h1>Title</h1>
      <p class="hero-copy">One or two sentence summary.</p>
    </div>
    <aside class="crux-card">
      <span class="label">Crux</span>
      <strong>The hardest decision</strong>
      <p>Why it's the crux.</p>
    </aside>
  </div>
</header>
```

```css
.viz-hero {
  padding: 32px;
  border: 1px solid rgb(212 212 216 / 82%);
  border-radius: calc(var(--radius) + 8px);
  background: rgb(253 253 253 / 92%);
  box-shadow: var(--shadow);
}
.hero-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 28px;
  align-items: end;
}
h1 {
  font-size: clamp(36px, 6vw, 72px);
  line-height: 0.94;
  letter-spacing: -0.06em;
  color: var(--text-emphasis);
  margin: 0 0 20px;
}
.hero-copy {
  font-size: 18px;
  line-height: 1.75;
  color: var(--text-subtle);
}
.crux-card {
  padding: 22px;
  background: linear-gradient(135deg, rgb(86 77 255 / 11%), rgb(255 255 255 / 86%)), var(--bg-surface);
  border: 1px solid rgb(86 77 255 / 28%);
  border-radius: var(--radius);
}
.crux-card strong {
  display: block;
  margin-bottom: 12px;
  font-size: 22px;
  line-height: 1.2;
  color: var(--text-emphasis);
}
```

---

## Typography utilities

```css
.eyebrow, .label {
  display: block;
  margin-bottom: 10px;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--primary);
}

/* status badges */
.badge {
  display: inline-block;
  padding: 3px 10px;
  font-size: 11px;
  font-weight: 700;
  border-radius: 999px;
}
.badge--confirmed { background: var(--green-soft);  color: var(--green); }
.badge--risk      { background: var(--amber-soft);  color: var(--amber); }
.badge--blocker   { background: var(--red-soft);    color: var(--red); }
.badge--tbd       { background: var(--bg-muted);    color: var(--text-subtle); }
```

---

## Progressive disclosure

Use `<details><summary>` for supporting material readers may not need on first pass.

```html
<details>
  <summary>Implementation notes</summary>
  <p>Dense reference content here.</p>
</details>
```

HackMD renders `<details>` natively. Style it for consistency:

```css
details {
  padding: 12px 16px;
  background: var(--bg-muted);
  border-radius: 10px;
  margin-top: 12px;
}
details summary { cursor: pointer; font-weight: 600; }
details[open] { background: var(--bg-surface); }
```

---

## HackMD rendering constraints

**Custom CSS preview required:** After opening a published note, click the **paintbrush icon** (tooltip: "Select theme to preview") and select **Custom CSS**. HackMD does not apply embedded `<style>` blocks until this preview mode is enabled.

| Feature | Supported |
|---|---|
| `<style>` tags | ✅ (requires Custom CSS preview) |
| CSS Grid / Flexbox | ✅ |
| CSS custom properties | ✅ |
| `@import` (Google Fonts) | ✅ |
| `<details>` / `<summary>` | ✅ |
| `<script>` | ❌ stripped |
| Event handlers (`onclick`, etc.) | ❌ stripped |
| `<html>` / `<head>` / `<body>` | ❌ omit — HackMD wraps the note itself |
| External CSS `<link>` | ❌ not rendered |
| Inline SVG | ✅ (safe attributes only) |

**Selector scope**: HackMD wraps content in `.markdown-body`. Custom classes don't need prefixing unless you're overriding default prose styles (headings, links, tables).

---

## Boilerplate — minimal note structure

```html
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+TC:wght@400;500;700;800&display=swap');

:root {
  --text-emphasis: #18181b; --text-default: #3f3f46; --text-subtle: #71717a;
  --bg-page: #f4f4f5; --bg-surface: #fdfdfd; --border: #d4d4d8;
  --primary: #564dff; --primary-soft: #eeedff;
  --green: #16a34a; --green-soft: #eaf8ef;
  --radius: 18px; --shadow: 0 24px 70px rgb(24 24 27 / 10%);
}

*, *::before, *::after { box-sizing: border-box; }

.viz-shell {
  font-family: Inter, "Noto Sans TC", -apple-system, sans-serif;
  color: var(--text-default);
  padding: 8px 0 48px;
}

/* ... component styles ... */
</style>

<div class="viz-shell">
  <!-- content here -->
</div>
```

---

## HackMD publish command

```bash
# Create new note (returns noteId + userPath)
hackmd-cli notes create \
  --title="Visualization — <topic>" \
  --readPermission=owner \
  --writePermission=owner \
  --content="$(cat /tmp/viz_output.html)"

# Update existing note
hackmd-cli notes update --noteId=<id> --content="$(cat /tmp/viz_output.html)"
```

URL format after creation: `https://hackmd.io/<userPath>`
