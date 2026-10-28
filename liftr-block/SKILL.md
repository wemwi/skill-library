---
name: liftr-block
description: Guide for creating Shopify blocks in the LIFTR theme — both Section Blocks (inline in section schema) and Theme Blocks (own file in /blocks/). Covers the decision between block types, Liquid file structure, Schema configuration (tag null, nested blocks, presets, dynamic titles), HTML attribute order, Panel Pattern (sidebar/popup/sheet get own color scheme), and Parent Override via CSS inheritance. Use whenever creating a new block, converting a section block to theme block, adding nested blocks, implementing panel overlays, or reviewing block code. For CSS architecture see liftr-css-system. For custom-colors mechanics see custom-colors skill. For locale entries see liftr-i18n.
---

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
- Block settings follow the same rules as section settings (→ liftr-section skill)
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
- Most blocks use shared CSS from `core.components.css` — only add own file if block has substantial CSS (>50 lines)

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

Block settings follow the same order as section settings. Key difference: blocks have `color_mode` + custom-colors (sections don't).

```
Design-Basis (no header)      design, layout, size (if applicable)
────────────────────────────────────────────────────────────────────
Header: "Appearance"           color_mode, [color overrides via visible_if]
────────────────────────────────────────────────────────────────────
Header: "Content"              heading, text, image, button
```

**Appearance pattern (Auto/Custom colors):**

```json
{
  "type": "header",
  "content": "t:global.header.appearance"
},
{
  "type": "select",
  "id": "color_mode",
  "label": "t:global.label.color_mode",
  "options": [
    { "value": "auto", "label": "t:global.value.color_mode.auto" },
    { "value": "custom", "label": "t:global.value.color_mode.custom" }
  ],
  "default": "auto"
},
{
  "type": "color",
  "id": "background",
  "label": "t:color_scheme.background",
  "visible_if": "{{ block.settings.color_mode == 'custom' }}"
},
{
  "type": "color",
  "id": "text",
  "label": "t:color_scheme.text",
  "visible_if": "{{ block.settings.color_mode == 'custom' }}"
},
{
  "type": "color",
  "id": "accent",
  "label": "t:color_scheme.accent",
  "visible_if": "{{ block.settings.color_mode == 'custom' }}"
}
```

For the full custom-colors mechanism → `custom-colors` skill.

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
    "category": "t:preset_categories.[category]",
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
    {
      "type": "select",
      "id": "color_mode",
      "label": "t:global.label.color_mode",
      "options": [
        { "value": "auto", "label": "t:global.value.color_mode.auto" },
        { "value": "custom", "label": "t:global.value.color_mode.custom" }
      ],
      "default": "auto"
    },
    {
      "type": "color",
      "id": "background",
      "label": "t:color_scheme.background",
      "visible_if": "{{ block.settings.color_mode == 'custom' }}"
    }
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

Sections set variables via `{% style %}` + `#shopify-section-{{ section.id }}`. Blocks consume via Inline Fallback. This uses CSS inheritance — appropriate here because these are merchant-set contextual values, not LIFTR Settings.

```liquid
{% comment %} Section sets variable {% endcomment %}
{% style %}
  #shopify-section-{{ section.id }} {
    --story-link--width: {{ section.settings.width }}rem;
  }
{% endstyle %}
```

```css
/* Block consumes with Inline Fallback */
.story-link_component {
  width: var(--story-link--width, 6rem);
}
```

**This is different from LIFTR Settings** (which are declared directly on Consumer-Klasse). Parent → Block inheritance is for merchant-configured values that flow down the DOM tree — the same pattern as color scheme inheritance.

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
    - CSS: components.css (or snippet.[name].css)
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
