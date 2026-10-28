# Custom Colors

The `custom-colors` snippet (`snippets/custom-colors.liquid`) is the single mechanism for merchant color
overrides. It outputs a scoped `{% style %}` block with blank-checked CSS custom properties. This file is
the single home for the Auto/Custom schema pattern, the guard and the render call.

---

## The Chain

```
Setting ID        →  Snippet Parameter  →  CSS Variable
────────────────     ────────────────      ──────────────────────────
background        →  background          →  --{name}--background
text              →  text                →  --{name}--text
accent            →  accent              →  --{name}--accent
card              →  card                →  --{name}--card
button_primary    →  button_primary      →  --{name}--button-primary
...               →  ...                 →  ...
```

The mapping is 1:1. Setting ID = snippet parameter = CSS variable suffix (with `_` → `-` for CSS).

### All Color Suffixes

```
background  gradient  card  text  accent  link
button-primary  button-primary-text
button-secondary  button-secondary-text  border
```

These IDs are **reserved** for color overrides. Never use `text` or `background` as a setting ID for content — use `content_text`, `content_heading` etc.

---

## Three Scopes

| Scope | Selector | When |
|---|---|---|
| `section` | `#shopify-section-{id}` | Section sets own colors OR colors that inherit to child snippets |
| `block` | `#{id}` | Block sets own colors (most common) |
| `snippet` | `#shopify-section-{id} .{name}_component` | Section sets colors only for a child snippet's component (e.g. product cards) |

The `name` parameter differentiates variables: `--hero--text` vs `--product--text`. No collision even when section sets colors for a snippet inside it.

---

## How It Works

### 1. Schema: Auto/Custom Toggle

Part of the Design-Basis (no header, → `merchant-ux.md`), directly after `color`:

```json
{
  "type": "select",
  "id": "color_mode",
  "label": "t:global.label.color_mode",
  "options": [
    { "value": "auto", "label": "t:global.option.color_mode.auto" },
    { "value": "custom", "label": "t:global.option.color_mode.custom" }
  ],
  "default": "auto"
},
{
  "type": "color",
  "id": "text",
  "label": "t:global.color.text",
  "visible_if": "{{ block.settings.color_mode == 'custom' }}"
},
{
  "type": "color",
  "id": "accent",
  "label": "t:global.color.accent",
  "visible_if": "{{ block.settings.color_mode == 'custom' }}"
}
```

Only add the color settings the component consumes. In sections use `section.settings.color_mode`;
section-embedded panels use the `panel_` prefix (→ `block.md`, Panel Pattern).

### 2. Liquid: Guard + Render

```liquid
{%- liquid
  assign is_custom = false
  if block.settings.color_mode == 'custom'
    assign is_custom = true
  endif

  if is_custom
    render 'custom-colors', scope: 'block', name: 'badge', id: block.id, background: block.settings.background, text: block.settings.text
  endif
-%}
```

**Guard Contract:** Caller checks `is_custom`. Snippet handles blank checks internally.

### 3. Snippet Output

The snippet generates:

```css
#block-id {
  --badge--background: #ff6600;
  --badge--text: #ffffff;
}
```

Only non-blank values are output. Blank or `rgba(0,0,0,0)` values are skipped.

### 4. CSS: Inline Fallback

The component consumes with Inline Fallback — no declaration:

```css
.badge_component {
  background: var(--badge--background, var(--color-scheme--accent));
  color: var(--badge--text, var(--color-scheme--text));
}
```

Why no declaration → `css-system.md` (liftr-foundation), "Inline Fallback".

---

## Scope Examples

### Block (most common)

```liquid
{%- if is_custom -%}
  {%- render 'custom-colors',
    scope: 'block', name: 'highlight-badge', id: block.id,
    background: block.settings.background,
    text: block.settings.text
  -%}
{%- endif -%}
```

Output: `#{block.id} { --highlight-badge--background: ...; }`

### Section

```liquid
{%- if is_custom -%}
  {%- render 'custom-colors',
    scope: 'section', name: 'hero', id: section.id,
    background: section.settings.background,
    text: section.settings.text
  -%}
{%- endif -%}
```

Output: `#shopify-section-{id} { --hero--background: ...; }`

### Section Setting Colors for Child Snippet

```liquid
{%- if is_custom -%}
  {%- render 'custom-colors',
    scope: 'section', name: 'product-card', id: section.id,
    background: section.settings.card_background,
    text: section.settings.card_text
  -%}
{%- endif -%}
```

Output: `#shopify-section-{id} { --product-card--background: ...; }`

Variables inherit down to `.product-card_component` via CSS inheritance.

---

## Blank Handling

Shopify color picker returns `rgba(0,0,0,0)` for unset values. This is `!= blank` but visually transparent.

The snippet checks both:

```liquid
assign blank_color = 'rgba(0,0,0,0)'

if background != blank and background != blank_color
  {{ prefix }}background: {{ background }};
endif
```

**Result:** Unset colors produce no output → CSS fallback applies. This is the snippet's responsibility — callers don't need to check for `rgba(0,0,0,0)`.

---

## Rules

**Do:**
- ✅ Always use `custom-colors` snippet for merchant color overrides
- ✅ Only render when `is_custom` is true (Guard Contract)
- ✅ Use Inline Fallback on consuming elements (→ `css-system.md`, liftr-foundation)
- ✅ Pass only the color parameters the block actually uses

**Don't:**
- ✘ No manual `{% style %}` for color overrides — always use the snippet
- ✘ No `capture` blocks for building style strings
- ✘ No color variable declarations on `_component` — only consumption with fallback

---

## Forwarding (to Nested Components)

When block colors need to flow into nested shared components (Panel, Button), use CSS Forwarding in the section/block CSS:

```css
/* Section CSS — forward block colors to panel */
liftr-panel.discount_panel {
  --panel--background: var(--discount--background);
  --panel--text: var(--discount--text);
}

/* Forward to button via nearest shared parent */
.discount_body {
  --button--primary: var(--discount--button-primary);
  --button--primary-text: var(--discount--button-primary-text);
}
```

Forwarding is documented only here.

---

## Checklist

- [ ] `color_mode` setting with Auto/Custom options?
- [ ] Color settings with `visible_if` on `color_mode == 'custom'`?
- [ ] `is_custom` guard in Liquid (if/endif, not assign comparison)?
- [ ] `render 'custom-colors'` with correct scope, name, id?
- [ ] Only used color parameters passed (not all 11)?
- [ ] CSS consumers use Inline Fallback, no declaration?
- [ ] No manual `{% style %}` for color overrides?
- [ ] Forwarding in CSS for nested shared components (if applicable)?
- [ ] Color setting IDs match the reserved suffixes exactly?
