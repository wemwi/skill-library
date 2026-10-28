# LIFTR Block Guide

---

## Decision: Section Block vs. Theme Block

```
Will the block be used in 2+ different sections?
  → YES: Theme Block (/blocks/[name].liquid)

Does the block need to contain other blocks (nested)?
  → YES: Theme Block (only theme blocks support nesting)

Otherwise?
  → Section Block (inline in section schema)
```

| | Section Block | Theme Block |
|---|---|---|
| File | Inline in section schema | Own file: `/blocks/[name].liquid` |
| Reuse | One section only | Multiple sections |
| Rendering | `{% for block in section.blocks %}` | `{% content_for "blocks" %}` |
| Settings | In section schema under `"blocks"` | In block's own schema |
| Presets | None (section has presets) | Own presets possible |
| Nested blocks | Not possible | Possible via `blocks` attribute |

| Scenario | Recommendation |
|----------|----------------|
| Story-Link in Header + Footer + Sidebar | Theme Block |
| FAQ-Item only in FAQ-Section | Section Block |
| Testimonial in multiple slider sections | Theme Block |
| Hero-Slide only in Hero-Section | Section Block |
| Product-Card everywhere | Theme Block |
| Slide with nested Text + Button | Theme Block |

---

## Section Block

Section blocks live inline in the section schema. The section renders them via `{% for block in section.blocks %}`.

### Schema (inside section file)

```json
"blocks": [
  {
    "type": "faq-item",
    "name": "t:sections.[section].blocks.faq-item.name",
    "limit": 10,
    "settings": [
      {
        "type": "text",
        "id": "heading",
        "label": "t:global.label.heading"
      },
      {
        "type": "richtext",
        "id": "content",
        "label": "t:global.label.text"
      }
    ]
  },
  { "type": "@app" }
]
```

### Rendering

```liquid
{% for block in section.blocks %}
  <div class="[section]_item" {{ block.shopify_attributes }}>
    {% if block.type == 'faq-item' %}
      <h3>{{ block.settings.heading }}</h3>
      {{ block.settings.content }}
    {% endif %}
  </div>
{% endfor %}
```

**Rules:**
- `block.shopify_attributes` is mandatory on every block wrapper (editor highlighting)
- Block settings follow the same rules as section settings (→ `section.md`)
- `@app` always last in the blocks array

---

## Theme Block

Theme blocks have their own file in `/blocks/`. They render themselves — the parent section just calls `{% content_for "blocks" %}`.

### File Structure

```
/blocks/[name].liquid

  Docblock
  LIQUID HEAD (Settings, Guards, CSS, Side Effects)
  SECTION HEADER (CSS & JS — if needed)
  HTML OUTPUT
  {% schema %}
```

Same wrapper structure as sections, but typically shorter. SECTION HEADER only present when the block loads its own CSS or JS.

### Liquid Head

```liquid
{%- liquid

  # ============================================================================
  # SETTINGS
  # ============================================================================

  assign design = block.settings.design | default: 'default'

  # ============================================================================
  # GUARDS
  # ============================================================================

  assign has_content = false
  if block.settings.content != blank
    assign has_content = true
  endif

  assign has_nested_blocks = false
  if block.blocks.size > 0
    assign has_nested_blocks = true
  endif

  assign is_custom = false
  if block.settings.color_mode == 'custom'
    assign is_custom = true
  endif

  # ============================================================================
  # CSS
  # ============================================================================

  assign css_design = design | prepend: 'is-'

  # ============================================================================
  # SIDE EFFECTS
  # ============================================================================

  if is_custom
    render 'custom-colors', scope: 'block', name: '[name]', id: block.id, background: block.settings.background, text: block.settings.text, accent: block.settings.accent
  endif

-%}
```

**Differences from section Liquid Head:**
- Uses `block.settings.*` instead of `section.settings.*`
- Uses `block.id` instead of `section.id`
- Uses `block.blocks` for nested blocks
- No IDS subsection (no anchor links on blocks)
- No TRANSLATIONS subsection (blocks rarely cache translations)

### Section Header (CSS & JS)

Only present when the block loads own assets:

```liquid
{% comment %} ================================================================
   SECTION HEADER — CSS & JS
   ================================================================ {% endcomment %}

{{ 'snippet.[name].css' | asset_url | stylesheet_tag }}
<script type="module" src="{{ 'ui.[plugin].js' | asset_url }}"></script>
```

**Rules:**
- CSS via `stylesheet_tag` (Shopify handles dedup)
- JS always `type="module"`
- Most blocks use shared CSS from `core.components-critical.css` (above the fold) or `core.components.css` (deferred) — only add an own `block.[name].css` / `snippet.[name].css` if the block has substantial CSS (>50 lines)

### HTML Output

```liquid
<div id="{{ block.id }}" class="[name]_component {{ css_design }}" {{ block.shopify_attributes }}>

  {% if has_content %}
    <div class="[name]_content">
      {{ block.settings.content }}
    </div>
  {% endif %}

  {% if has_nested_blocks %}
    <div class="[name]_blocks">
      {% content_for "blocks" %}
    </div>
  {% endif %}

</div>
```

---

## Theme Block Schema

### Required Attributes

```json
{% schema %}
{
  "name": "t:blocks.[name].name",
  "tag": null,
  "settings": [],
  "blocks": [],
  "presets": [
    {
      "name": "t:blocks.[name].name"
    }
  ]
}
{% endschema %}
```

**`tag` is always `null`.** No Shopify wrapper — full DOM control. Never use `"tag": "div"`.

### Settings

Block settings follow the same order as section settings (→ `merchant-ux.md`). Blocks usually add
`color_mode` + color overrides — they belong to the Design-Basis (no header), directly after `color`:

```
Design-Basis (no header)      [color] → color_mode → [color overrides via visible_if] → design → layout → size
────────────────────────────────────────────────────────────────────
Header: "Content"              heading, text, image, button
```

Schema pattern for Auto/Custom colors, guard and render call → `custom-colors.md`.

### Nested Blocks

Theme blocks can accept child blocks:

```json
"blocks": [
  { "type": "text" },
  { "type": "button" },
  { "type": "image" },
  { "type": "@app" }
]
```

Render children: `{% content_for "blocks" %}` — not a for-loop.

Maximum recommended nesting: 3 levels. Deeper nesting creates UX confusion in the editor.

### Presets

```json
"presets": [
  {
    "name": "t:blocks.[name].name",
    "category": "t:global.category.[category]",
    "settings": {
      "design": "card"
    },
    "blocks": [
      { "type": "text", "settings": { "text": "Welcome" } }
    ]
  }
]
```

One preset = block name (DRY). Preset should show a functional example with pre-filled content.

### Dynamic Block Titles

Shopify uses settings with these IDs as block title in the editor sidebar (priority order):

1. `heading`
2. `title`
3. `text`

Use `heading` as the standard ID for block titles.

### Section Integration

Register theme blocks in the section schema by type name:

```json
"blocks": [
  { "type": "story-link" },
  { "type": "testimonial" },
  { "type": "@app" }
]
```

Shopify recognizes theme blocks automatically (file exists in `/blocks/`). No `@theme` wrapper needed.

---

## Panel Pattern

Panels are independent visual surfaces. **Sidebar, Popup, and Sheet always get their own `color_scheme` + `color_mode`.**

### Which UI elements are panels?

| Panel (own color scheme) | Not a panel (inherits) |
|---|---|
| Sidebar (filter, menu) | Dropdown (small, temporary) |
| Popup / Modal | Tooltip |
| Bottom Sheet | Accordion content |

### Panel as Block File

```json
{
  "settings": [
    {
      "type": "color_scheme",
      "id": "color",
      "label": "t:global.label.color_scheme"
    },
    { "type": "select", "id": "color_mode", "...": "Auto/Custom pattern → custom-colors.md" }
  ]
}
```

```liquid
<div class="filter-panel_component color-scheme-{{ block.settings.color }}">
  ...
</div>
```

### Panel Embedded in Section

When panel settings live in the section schema (no own block file), use `panel_` prefix:

```json
{ "id": "color", "type": "color_scheme" },
{ "id": "panel_color", "type": "color_scheme" },
{ "id": "panel_color_mode", ... },
{ "id": "panel_background", "visible_if": "{{ section.settings.panel_color_mode == 'custom' }}" }
```

---

## Parent Override (Section → Block)

Merchant-set section values (`{% style %}` on `#shopify-section-{{ section.id }}`) that blocks consume
with Inline Fallback → `css-system.md` (liftr-foundation), "Parent Override".

---

## Docblock

```liquid
{% comment %}
  ============================================================================
  BLOCK: [name]  /  THEME BLOCK: [name]
  ============================================================================
  Description: [Brief description]
  
  Usage:
    Section Block – only in [section-name].
    Theme Block – used in [section-1], [section-2].
  
  CSS API:
    --[name]--background   → color-scheme--card
    --[name]--text         → color-scheme--text
  
  Dependencies:
    - CSS: core.components-critical.css / core.components.css (or block.[name].css)
    - Snippets: custom-colors
    - Plugins: [if any]
  ============================================================================
{% endcomment %}
```

---

## Checklist

### Section Block

- [ ] Settings inline in section schema?
- [ ] `block.shopify_attributes` on wrapper?
- [ ] `@app` last in blocks array?
- [ ] Block type switching handled in for-loop?

### Theme Block

- [ ] File in `/blocks/[name].liquid`?
- [ ] `"tag": null` in schema?
- [ ] Attribute order: id → class → liftr-* → aria-* → shopify_attributes?
- [ ] `id="{{ block.id }}"` on root element?
- [ ] Presets defined with functional example?
- [ ] `heading` used as setting ID for dynamic block title?

### Nested Blocks

- [ ] `blocks` attribute in schema lists allowed child types?
- [ ] `{% content_for "blocks" %}` for rendering children?
- [ ] Nesting depth ≤ 3 levels?

### Color Override

- [ ] `color_mode` setting (Auto/Custom)?
- [ ] Color settings with `visible_if` on color_mode?
- [ ] `render 'custom-colors', scope: 'block'` in side effects?
- [ ] Only rendered when `is_custom` is true?

### Panel Block

- [ ] Is it a sidebar, popup, or sheet?
- [ ] Has own `color_scheme` setting (type: color_scheme, id: color)?
- [ ] Has own `color_mode` setting?
- [ ] `color-scheme-{{ block.settings.color }}` class on panel container?
- [ ] If section-embedded: `panel_` prefix on all panel settings?
