---
name: liftr-section
description: Step-by-step guide for creating Shopify sections in the LIFTR theme. Covers Liquid file structure (3-wrapper pattern, Liquid Head subsections, CSS/JS embedding), LIFTR component markup (Consumer-Klasse, skeleton, NAV buttons), Schema configuration (standard settings, blocks, presets vs default, visible_if, enabled_on/disabled_on), and HTML wrapper hierarchy (padding-global → container → component). Use whenever creating a new section, modifying section schema, adding settings or blocks to an existing section, embedding LIFTR Web Components in a section, debugging section structure, or reviewing section code. This is the procedural counterpart to liftr-css-system (which handles CSS architecture). For block internals see liftr-block. For locale entries see liftr-i18n. For schema UX see liftr-merchant-ux.
---

# LIFTR Section Guide

**Output:** 2 files per section — `sections/[name].liquid` + `assets/section.[name].css`

---

## Workflow

```
1. Gather requirements (schema questionnaire)
2. Write Liquid file (3-wrapper structure)
3. Write CSS file (→ liftr-css-system skill)
4. Create locale entries (→ liftr-i18n skill)
```

---

## Liquid File Structure

Every section follows a 3-wrapper structure:

```
LIQUID HEAD — Variables & Logic        {%- liquid %} block
SECTION HEADER — CSS & JS             Asset loading + {% style %}
HTML OUTPUT                            Markup
{% schema %}                           JSON configuration
```

### Wrapper 1: LIQUID HEAD

Contains ALL logic. No rendering except side effects.

```liquid
{% comment %} ================================================================
   LIQUID HEAD — Variables & Logic
   ================================================================ {% endcomment %}

{%- liquid

  # ============================================================================
  # IDS
  # ============================================================================

  assign id_anchor = section.settings.anchor_link | handleize

  # ============================================================================
  # SETTINGS
  # ============================================================================

  assign color   = section.settings.color
  assign design  = section.settings.design
  assign layout  = section.settings.layout
  assign padding = section.settings.padding

  # ============================================================================
  # GUARDS
  # ============================================================================

  assign has_heading = false
  if section.settings.content_heading != blank
    assign has_heading = true
  endif

  assign has_blocks = false
  if section.blocks.size > 0
    assign has_blocks = true
  endif

  # ============================================================================
  # CSS
  # ============================================================================

  assign css_color   = color   | prepend: 'color-scheme-'
  assign css_design  = design  | prepend: 'is-'
  assign css_layout  = layout  | prepend: 'is-'
  assign css_padding = padding

  # ============================================================================
  # TRANSLATIONS
  # ============================================================================

  assign t_section_name = 'sections.[name].name' | t

  # ============================================================================
  # SIDE EFFECTS
  # ============================================================================

  # Sections do NOT use custom-colors (only blocks do).
  # Side effects here: render snippets that produce {% style %} output.

-%}
```

**Subsection rules:**

| Subsection | Contains | Notes |
|------------|----------|-------|
| IDS | Anchor link, dynamic IDs | `handleize` for URL-safe IDs |
| SETTINGS | Direct assigns from `section.settings.*` | 1:1 mapping, no logic |
| GUARDS | Boolean flags via if/endif | No comparisons in assign! |
| CSS | Derived class strings | `prepend: 'is-'`, `prepend: 'color-scheme-'` |
| TRANSLATIONS | `| t` calls | Cache translation results |
| SIDE EFFECTS | `render` calls that produce output | custom-colors, other snippets |

**Critical Liquid rule:** Inside `{%- liquid %}`, comparisons in `assign` are NOT allowed:

```liquid
# ❌ WRONG — will silently fail
assign has_image = section.settings.image != blank

# ✅ CORRECT — explicit if/endif
assign has_image = false
if section.settings.image != blank
  assign has_image = true
endif
```

### Wrapper 2: SECTION HEADER

Loads CSS, JS, and scoped variables. Order: dependencies first, then section-specific.

```liquid
{% comment %} ================================================================
   SECTION HEADER — CSS & JS
   ================================================================ {% endcomment %}

{%- comment -%} CSS Dependencies {%- endcomment -%}
{{ 'snippet.[dependency].css' | asset_url | stylesheet_tag }}
{{ 'ui.[plugin].css'          | asset_url | stylesheet_tag }}
{{ 'section.[name].css'       | asset_url | stylesheet_tag }}

{%- comment -%} JS Dependencies {%- endcomment -%}
<script type="module" src="{{ 'ui.[plugin].js' | asset_url }}"></script>

{%- comment -%} Scoped Variables (only for dynamic/range settings) {%- endcomment -%}
{% style %}
  #shopify-section-{{ section.id }} {
    --[name]--[property]: {{ section.settings.[setting] }}rem;
  }
{% endstyle %}
```

**Rules:**

- CSS via `stylesheet_tag` (Shopify handles caching/dedup)
- JS always `type="module"` — no exceptions
- `{% style %}` only for values that come from range/dynamic settings. Static values belong in the CSS file.
- Load order: snippet CSS → ui CSS → section CSS → JS → `{% style %}`

### Wrapper 3: HTML OUTPUT

```liquid
{% comment %} ================================================================
   HTML OUTPUT
   ================================================================ {% endcomment %}

<div class="padding-global {{ css_color }} {{ css_design }}" id="{{ id_anchor }}">
  <div class="container-large {{ css_padding }}">
    <div class="[name]_component {{ css_layout }}">

      {% if has_heading %}
        <div class="[name]_header">
          <h2 class="heading-style-h2">
            {{ section.settings.content_heading }}
          </h2>
        </div>
      {% endif %}

      {% if has_blocks %}
        <div class="[name]_body">
          {% for block in section.blocks %}
            <div class="[name]_item" {{ block.shopify_attributes }}>
              {%- comment -%} Block content {%- endcomment -%}
            </div>
          {% endfor %}
        </div>
      {% endif %}

    </div>
  </div>
</div>
```

**HTML wrapper hierarchy:**

```
padding-global          → Color scheme, design modifier, anchor ID
  container-*           → Max-width, container query context, section padding
    [name]_component    → Layout modifier, grid/flex, component logic
```

| Element | Carries | Why |
|---------|---------|-----|
| `padding-global` | `css_color`, `css_design`, `id_anchor` | Color scheme scope, background variant |
| `container-*` | `css_padding` | CQ context, section padding utility |
| `_component` | `css_layout` | Internal layout control |

**Container sizes:** `container-small` (48rem), `container-medium` (64rem), `container-large` (85rem), `container-full` (100%). For full list → liftr-css-system (Container Classes).

**block.shopify_attributes:** Required on every block wrapper — enables editor highlighting and selection.

### Sections with LIFTR Components

When a section uses a LIFTR Web Component, the Custom Element gets a **Consumer-Klasse** for CSS Settings:

```liquid
<div class="container-large {{ css_padding }}">
  <div class="featured-products_component {{ css_layout }}">

    <liftr-slider class="featured-products_slider"
      liftr-axis="x" liftr-state="loading" liftr-skeleton="true">

      <div liftr-role="slider-viewport">
        {%- for product in collection.products -%}
          <div liftr-role="slider-item">
            {% render 'product-card', product: product %}
          </div>
        {%- endfor -%}
      </div>

      <button liftr-role="nav-prev" aria-label="{{ 'components.nav.prev' | t }}">
        {% render 'icon', name: 'angle-left' %}
      </button>
      <button liftr-role="nav-next" aria-label="{{ 'components.nav.next' | t }}">
        {% render 'icon', name: 'angle-right' %}
      </button>

    </liftr-slider>
  </div>
</div>
```

**Consumer-Klasse naming:** `{context}_{module}` — e.g. `featured-products_slider`, `store_accordion`, `aside-cart_recommendations`. The Consumer-Klasse lives directly on the Custom Element. CSS Settings target it via compound selector: `liftr-slider.featured-products_slider { }`.

**Key rules:**
- Custom element (`<liftr-slider>`) is the component — no `liftr-component` attribute
- Roles are space-separated: `liftr-role="slider-item nav-dot"`
- `liftr-state="loading"` + `liftr-skeleton="true"` only for modules that need FOUC prevention (→ liftr-css-system FOUC section)
- NAV buttons need `aria-label` with translation key
- Container class on parent wrapper, never on the Custom Element itself

---

## Schema

### Standard Settings

Every section includes these settings (no header needed — they come first):

```json
{
  "type": "color_scheme",
  "id": "color",
  "label": "t:global.label.color_scheme"
},
{
  "type": "select",
  "id": "design",
  "label": "t:global.label.design",
  "options": [
    { "value": "plain", "label": "t:global.value.design.plain" },
    { "value": "full",  "label": "t:global.value.design.full" },
    { "value": "card",  "label": "t:global.value.design.card" }
  ],
  "default": "card"
},
{
  "type": "select",
  "id": "layout",
  "label": "t:global.label.layout",
  "options": [],
  "default": ""
},
{
  "type": "select",
  "id": "padding",
  "label": "t:global.label.padding",
  "options": [
    { "value": "padding-section-small",  "label": "t:global.value.size.small" },
    { "value": "padding-section-medium", "label": "t:global.value.size.medium" },
    { "value": "padding-section-large",  "label": "t:global.value.size.large" }
  ],
  "default": "padding-section-medium"
}
```

Notes:
- `color`: Always present. Uses Shopify's native color_scheme picker.
- `design`: plain (transparent bg), full (full-width bg), card (with margin + border-radius). Omit if section has only one visual variant.
- `layout`: Section-specific options (stacked/paired, grid/list). Omit if only one layout.
- `padding`: Always present. Maps directly to utility classes.
- Sections do NOT have `color_mode` or custom-colors. Custom color overrides are a block-level concern.

### Settings Order

```
Design-Basis (no header)     color → design → layout → padding
────────────────────────────────────────────────────────────
Header: "Content"            heading, text, image, button_url, button_label
────────────────────────────────────────────────────────────
Header: "[Topic]"            Section-specific groups (e.g. "Slider", "Filter")
────────────────────────────────────────────────────────────
Header: "Advanced"           anchor_link, hide_*, editor_view
```

**Header rule:** Set a header when there is a logical/thematic distinction between settings groups. No minimum count required.

### Content Settings

Under header "Content":

```json
{
  "type": "header",
  "content": "t:global.header.content"
},
{
  "type": "text",
  "id": "content_heading",
  "label": "t:global.label.heading",
  "default": "t:sections.[name].settings.content_heading.default"
},
{
  "type": "richtext",
  "id": "content_text",
  "label": "t:global.label.text"
}
```

**Content defaults must be section-specific and inspiring:**

| ❌ Generic | ✅ Section-specific |
|---|---|
| "Your heading" | "Designed for everyday adventures" |
| "Button" | "Shop the collection" |
| "FAQ" | "Got questions? We've got answers" |
| "Heading" | "What our customers say" |

### Advanced Settings

Always last:

```json
{
  "type": "header",
  "content": "t:global.header.advanced"
},
{
  "type": "text",
  "id": "anchor_link",
  "label": "t:global.label.anchor_id",
  "info": "t:global.info.anchor_id"
}
```

### Blocks in Schema

Define block types, but block internals are documented in the `liftr-block` skill.

```json
"blocks": [
  {
    "type": "text",
    "name": "t:sections.[name].blocks.text.name",
    "settings": []
  },
  {
    "type": "image",
    "name": "t:sections.[name].blocks.image.name",
    "limit": 1,
    "settings": []
  },
  { "type": "@app" }
]
```

**Rules:**
- Order blocks by frequency (most common first)
- `@app` always last
- `@theme` for recommended blocks in the block picker
- `max_blocks` only when less than 50 is desired
- Block `limit` when a type should appear at most N times

### Presets vs Default

```
Merchant adds section via "Add Section" picker?
  → YES: presets (dynamisch, removable)

Section rendered via {% section 'name' %} in theme.liquid?
  → YES: default (static, not removable)
  → Also: add manually to section group JSON
```

| | presets | default |
|---|---|---|
| In "Add Section" picker | ✅ | ❌ |
| Merchant can remove | ✅ | ❌ |
| Typical use | hero, faqs, testimonials | header-main, footer-main, cart-drawer |

**Preset structure:**

```json
"presets": [
  {
    "name": "t:sections.[name].name",
    "category": "t:preset_categories.[category]",
    "blocks": [
      { "type": "text" },
      { "type": "image" }
    ]
  }
]
```

One preset = section name (DRY). Multiple presets only when the section has fundamentally different configurations.

Preset blocks should show a functional example — not empty, not maxed out.

### Conditional Settings (visible_if)

Settings that depend on other settings:

```json
{
  "type": "range",
  "id": "columns",
  "label": "t:sections.[name].settings.columns.label",
  "min": 2,
  "max": 4,
  "default": 3,
  "visible_if": "{{ section.settings.layout == 'grid' }}"
}
```

Primarily used in blocks for custom-colors (Auto/Custom pattern). In sections, use sparingly for layout-dependent settings.

### Placement (enabled_on / disabled_on)

Use ONE — never both:

```json
"enabled_on": {
  "templates": ["*"],
  "groups": ["footer"]
}
```

```json
"disabled_on": {
  "templates": ["password", "gift_card"],
  "groups": ["header", "overlay"]
}
```

**Decision:** Few allowed locations → `enabled_on`. Few excluded locations → `disabled_on`.

#### Section Groups Reference

| Group | ID | Description |
|-------|-----|-------------|
| Header | `header` | Top area, announcement bars |
| Footer | `footer` | Bottom area, footer nav |
| Aside | `aside` | Sidebars, drawers |
| Overlay | `overlay` | Modals, popups |
| Main | *(no group)* | Standard content (default) |

#### Templates Reference

| Template | ID | Notes |
|----------|-----|-------|
| Homepage | `index` | |
| Page | `page` | |
| Product | `product` | |
| Collection | `collection` | |
| Blog | `blog` | Blog listing |
| Article | `article` | Blog post |
| Cart | `cart` | |
| Search | `search` | |
| Customers | `customers/*` | Account pages (wildcard) |
| 404 | `404` | |
| Password | `password` | Store locked |
| Gift Card | `gift_card` | |

### Full Schema Skeleton

```json
{% schema %}
{
  "name": "t:sections.[name].name",
  "tag": "section",
  "class": "section_[name]",
  "limit": 1,
  "settings": [
    { "type": "color_scheme", "id": "color", "label": "t:global.label.color_scheme" },
    { "type": "select", "id": "design", ... },
    { "type": "select", "id": "padding", ... },

    { "type": "header", "content": "t:global.header.content" },
    { "type": "text", "id": "content_heading", ... },

    { "type": "header", "content": "t:global.header.advanced" },
    { "type": "text", "id": "anchor_link", ... }
  ],
  "blocks": [
    { "type": "@app" }
  ],
  "presets": [
    { "name": "t:sections.[name].name" }
  ]
}
{% endschema %}
```

---

## Schema UX

For schema UX principles (10-second rule, header grouping, info texts, default values, native input types, opt-in/opt-out, empty states) → liftr-merchant-ux skill.

---

## Docblock

Every section file starts with:

```liquid
{% comment %}
  ============================================================================
  SECTION: [name]
  ============================================================================
  Description: [Brief description]
  
  Blocks:
    - [block-name]: [Description]
  
  Dependencies:
    - CSS: section.[name].css
    - Snippets: [if any]
    - Plugins: [if any]
  
  CSS Variables:
    --[name]--[property]: [Description] → [Fallback]
  
  I18N Required:
    - sections.[name].name
    - sections.[name].settings.*
    - sections.[name].blocks.*
  ============================================================================
{% endcomment %}
```

---

## Checklist

### Before Writing Code

- [ ] Schema questionnaire completed (settings, blocks, presets, placement)?
- [ ] Layout options defined?
- [ ] LIFTR plugins identified?
- [ ] Locale keys planned?

### Liquid

- [ ] 3-wrapper structure (LIQUID HEAD → SECTION HEADER → HTML OUTPUT)?
- [ ] All 6 subsections in Liquid Head?
- [ ] Guards use if/endif (no comparisons in assign)?
- [ ] CSS/JS loaded in correct order (dependencies → section)?
- [ ] JS loaded as `type="module"`?
- [ ] `{% style %}` only for dynamic/range settings?

### Schema

- [ ] `name` with translation key?
- [ ] `tag` = "section"?
- [ ] `class` = "section_[name]"?
- [ ] Standard settings present (color, design, padding)?
- [ ] Settings order: Design-Basis → Content → [Topic] → Advanced?
- [ ] Content defaults section-specific and inspiring?
- [ ] `@app` last in blocks array?
- [ ] presets OR default (not both)?
- [ ] enabled_on OR disabled_on (not both)?
- [ ] visible_if for layout-dependent settings?

### HTML

- [ ] Wrapper hierarchy: padding-global → container → component?
- [ ] `padding-global` carries color scheme + design modifier?
- [ ] `container-*` carries padding utility?
- [ ] `_component` carries layout modifier?
- [ ] `block.shopify_attributes` on every block wrapper?
- [ ] Anchor ID on padding-global?

### LIFTR Components (if used)

- [ ] Consumer-Klasse on Custom Element (`{context}_{module}`)?
- [ ] CSS Settings via compound selector in section CSS?
- [ ] Skeleton attributes on modules that need FOUC prevention?
- [ ] NAV buttons with `aria-label` translation keys?
- [ ] Container class on parent, not on Custom Element?
