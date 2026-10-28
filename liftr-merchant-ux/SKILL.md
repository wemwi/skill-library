---
name: liftr-merchant-ux
description: Merchant-focused UX quality for Shopify theme editor schemas. Covers 10-second rule, settings order, header grouping (min 3 rule, flowchart), info text types, default value philosophy (inspiring copy, length limits), preset rules (DRY naming, categories), limits, conditional settings (visible_if), native input types, empty states (snippet + CSS specs), editor CSS, opt-in vs opt-out patterns. Use whenever creating/modifying section or block schemas, reviewing schema UX, writing defaults, choosing opt-in/opt-out, implementing empty states, or adding info texts. UX counterpart to liftr-section (technical structure) and liftr-block (block internals). Triggers on schema UX, settings order, header grouping, info text, defaults, presets, empty states, opt-in/opt-out, merchant experience, editor usability.
---

# LIFTR Merchant UX

**Perspective:** The Theme Editor is used by **merchants**, not developers. Every schema decision must pass the **10-second rule** — a merchant finds any setting in 10 seconds.

> For technical schema structure (Liquid, wrappers, file structure) → liftr-section skill
> For block internals (theme blocks, panels, nested blocks) → liftr-block skill
> For locale entries → liftr-i18n skill

---

## Table of Contents

1. [Principles](#1-principles)
2. [Settings Order](#2-settings-order)
3. [Header Grouping](#3-header-grouping)
4. [Info Texts](#4-info-texts)
5. [Default Values](#5-default-values)
6. [Blocks UX](#6-blocks-ux)
7. [Presets](#7-presets)
8. [Limits](#8-limits)
9. [Conditional Settings](#9-conditional-settings)
10. [Native Input Types](#10-native-input-types)
11. [Opt-in vs Opt-out](#11-opt-in-vs-opt-out)
12. [Empty States](#12-empty-states)
13. [Editor CSS](#13-editor-css)
14. [Setting Types Reference](#14-setting-types-reference)
15. [Checklist](#15-checklist)

---

## 1. Principles

| Principle | Meaning |
|-----------|---------|
| **10-second rule** | Merchant finds any setting in 10 seconds |
| **Most important first** | Design & content top, power-user options bottom |
| **Consistency** | Same order and structure across ALL sections |
| **Less is more** | Fewer groups > more groups |
| **Self-explaining** | Labels so clear that info texts are rarely needed |

**Target audience rules:**
- No technical terms (no "DOM", "Viewport", "Container")
- No abbreviations without context
- Understandable without documentation

---

## 2. Settings Order

### Standard Order for Sections

```
┌──────────────────────────────────────────┐
│  1. DESIGN BASIS (no header)             │
│     color → color_mode → [overrides]     │
│     → design → layout → padding → size   │
├──────────────────────────────────────────┤
│  2. CONTENT (Header: "Content")          │
│     heading, text, image, button         │
├──────────────────────────────────────────┤
│  3. FEATURE-SPECIFIC (own header)        │
│     e.g. Accordion, Source, Filter       │
├──────────────────────────────────────────┤
│  4. ADVANCED (Header: "Advanced")        │
│     editor_view, hide_*, custom IDs      │
└──────────────────────────────────────────┘
```

**Design Basis** — always first, **never** gets a header:

| Setting | ID | When |
|---------|-----|------|
| Color scheme | `color` | Always |
| Color mode | `color_mode` | With color override (Auto/Custom) |
| Design | `design` | For plain/full/card variants |
| Layout | `layout` | For different arrangements |
| Padding | `padding` | Configurable spacing |
| Size | `size` | S/M/L variants |

**Content** — grouped under Header "Content":

| Setting | ID | Order |
|---------|-----|-------|
| Heading | `content_heading` | 1 |
| Text | `content_text` | 2 |
| Image | `content_image` | 3 |
| Button URL | `content_button_url` | 4 |
| Button Label | `content_button_label` | 5 |

**Advanced** — grouped under Header "Advanced", always last:
`editor_view`, `hide_*`, `anchor_link`, technical IDs

### Block Settings Order

```
1. Identification (heading, title, name)
2. Content (text, image, link)
3. Appearance (color, style, size)
4. Advanced (position, visibility)
```

---

## 3. Header Grouping

### Rule 1: Minimum 3 settings per group
No header for fewer than 3 related settings. Merge into adjacent group instead.

### Rule 2: Standard headers

| Header | Translation Key | When |
|--------|-----------------|------|
| Content | `t:global.headers.content` | Editable content |
| Advanced | `t:global.headers.advanced` | Power-user options |
| Button | `t:global.headers.button` | Only with 3+ button settings |
| Highlight | `t:global.headers.highlight` | Highlight/badge config |
| Image settings | `t:global.headers.image_settings` | Only with 3+ image settings |

### Rule 3: Feature header only with complexity
Own header only when feature has **3+ settings AND own logic** (e.g. Accordion settings).

### Rule 4: Never header for Design Basis
The first settings (color, design, layout, padding) never get a header.

### Decision Flowchart

```
Does this settings group need a header?
    │
    ▼
Is it Design Basis (color, design, layout, padding)?
    │
  Yes → NO header
  No  ↓
    │
Are there 3+ related settings?
    │
  No  → NO header, merge into previous group
  Yes ↓
    │
Does it have its own logic/feature?
    │
  No  → NO header, use standard group (Content/Advanced)
  Yes → SET header
```

---

## 4. Info Texts

### Rule 1: Info only for non-obvious settings

| Setting | Info needed? | Why |
|---------|-------------|-----|
| `heading` | ❌ | Self-explaining |
| `image` | ❌ | Self-explaining |
| `color` | ❌ | Visual picker |
| `accordion_exclusive` | ✅ | Behavior not obvious |
| `source` | ✅ | Auto vs Custom needs explanation |
| `hide_distance` | ✅ | Dependency on plugin |

### Rule 2: Three info types

| Type | Purpose | Example |
|------|---------|---------|
| **A: Dependency** | Prerequisite | "Requires Distance plugin" |
| **B: Behavior** | Explain effect | "Closes other panels when opening" |
| **C: Format** | Recommendation | "16:9 for text, 9:16 for quote" |

### Rule 3: Never info for...
- Self-explaining labels (Heading, Text, Link, Button)
- Standard patterns (Color, Design, Layout, Padding)
- When label is sufficient ("Show highlight" needs no info)
- Repetition of label (❌ `label: "Menu"`, `info: "Select a menu"`)

### Rule 4: Info style

| ✅ Good | ❌ Bad |
|---------|--------|
| Max 10 words | Long explanatory sentences |
| Active: "Closes other panels" | Passive: "Other panels will be closed" |
| Concrete: "Requires Live plugin" | Vague: "This needs another feature" |
| Outcome: "Opens in sidebar" | Process: "When clicked, this will..." |

---

## 5. Default Values

### Rule 1: Default = most common use
`padding: "medium"` not `"none"`. Always the safest/most common option.

### Rule 2: Content defaults from translations
```json
// ✅ Translation for defaults
{ "id": "heading", "default": "t:sections.faqs.settings.heading.default" }

// ❌ Hardcoded text
{ "id": "heading", "default": "Frequently Asked Questions" }
```

### Rule 3: Boolean defaults
- `true` → Core feature, standard UX (e.g. "Show prices")
- `false` → Optional, specialized (e.g. "Enable zoom")

### Rule 4: Select defaults
Always safest/most common: `color_mode: "auto"`, `size: "medium"`.

### Rule 5: Content defaults are section-specific and inspiring

Default texts are **not placeholders** but **examples of good e-commerce copy**. They show the merchant how the section should feel.

**Forbidden:**

| ❌ Never use | Why |
|---|---|
| "Your heading" / "Deine Überschrift" | Generic, no example |
| Lorem Ipsum | No context |
| "Heading" / "Button" | Meta-description, not content |
| Brand-specific ("Nike Air Max") | Not exchangeable |

**Good examples:**

| Section | Setting | ❌ Generic | ✅ Inspiring |
|---------|---------|---|---|
| Hero | heading | "Welcome" | "Designed for everyday adventures" |
| Hero | button_label | "Learn more" | "Shop the collection" |
| FAQs | heading | "FAQ" | "Got questions? We've got answers" |
| Newsletter | heading | "Newsletter" | "Stay in the loop" |
| Store Locator | heading | "Locations" | "Find us near you" |

**Content length limits:**

| Setting type | Length |
|---|---|
| `pre_heading` | 3–5 words |
| `heading` | 3–7 words |
| `button_label` | 2–3 words |
| `text` / `description` | 1–2 short sentences |

Language: Defaults in **English** (en.default.schema.json). German translation follows same principle — vivid and section-specific.

---

## 6. Blocks UX

**Order by frequency** — most common block types first, `@app` always last.

**Private blocks** use `_` prefix — not shown in "Add block" picker:
```json
{ "type": "_aside-menu-header" }  // Private
{ "type": "nav_link" }            // Public
```

**Block settings** follow the same rules as section settings (order, headers, info texts, defaults).

---

## 7. Presets

### Rule 1: One preset = section name (DRY)
```json
// ✅ DRY: Reuse section name
"presets": [{ "name": "t:sections.faqs.name", "category": "t:preset_categories.support" }]

// ❌ Unnecessary duplication
"presets": [{ "name": "t:sections.faqs.presets.default.name" }]
```

### Rule 2: Multiple presets = descriptive names
Only when section has fundamentally different configurations:

| Situation | Example |
|-----------|---------|
| Different layouts | Hero: "Hero banner", "Hero split" |
| Different use cases | Contact: "Contact simple", "Contact with map" |

Naming: "Hero banner" ✅ — "Hero - Variant 1" ❌

### Rule 3: Functional examples
Presets show how the section looks — not empty, not maxed out:
```json
"blocks": [
  { "type": "faq", "settings": { "question": "...", "answer": "..." } },
  { "type": "faq", "settings": { "question": "...", "answer": "..." } },
  { "type": "faq", "settings": { "question": "...", "answer": "..." } }
]
```

### Rule 4: Categories

| Category | Sections |
|-----------|----------|
| `header` | Header elements |
| `promotion` | USP, Banner, Marquee |
| `storytelling` | Hero, About, Team |
| `social_proof` | Testimonials, Reviews, Logos |
| `shopping` | Products, Collections, Cart |
| `support` | FAQs, Contact, Store Locator |

---

## 8. Limits

### Section `limit`
- `1` → Unique sections (Header, Footer, Cart)
- `2–3` → Sections that make sense multiple times
- No limit → Unbounded sections

### `max_blocks`
- `3–6` → When more breaks design (Stories, Quick Links)
- `9–12` → Reasonable upper limit (FAQs, Testimonials)
- `16+` → Only when truly needed (Navigation, Large Grids)

**Rule:** Every limit must be justified (e.g. `6` → fits 2×3 grid). No arbitrary numbers.

---

## 9. Conditional Settings

### Rule 1: Use `visible_if` sparingly
Only when setting is **truly irrelevant** for certain options and hiding **reduces confusion**.

```json
// ✅ Width only relevant in stacked layout
{ "id": "width", "visible_if": "{{ section.settings.layout == 'is-stacked' }}" }
```

### Rule 2: No nested conditions
```json
// ❌ Too complex
{ "visible_if": "{{ section.settings.layout == 'stacked' and section.settings.show_image == true }}" }

// ✅ Simple condition
{ "visible_if": "{{ section.settings.layout == 'stacked' }}" }
```

### Rule 3: Grouped visibility
When multiple settings appear/disappear together, apply same `visible_if` to header + all settings in the group.

---

## 10. Native Input Types

Prefer Shopify's native types over generic `select`:

| Instead of select with... | Use | Benefit |
|---------------------------|-----|---------|
| left / center / right | `text_alignment` | Visual icon picker |
| Color options | `color` or `color_scheme` | Native color picker |
| true / false | `checkbox` | Clear toggle |
| Font options | `font_picker` | Shopify font library |

**Benefits:** Visual pickers, no translation keys needed, native UX, less code, future-proof.

---

## 11. Opt-in vs Opt-out

For boolean settings controlling features:

| | Opt-out (default: active) | Opt-in (default: inactive) |
|---|---|---|
| **Default** | `true` / visible | `false` / hidden |
| **Prefix** | `hide_*`, `disable_*` | `show_*`, `enable_*` |
| **Merchant action** | Activate to remove | Activate to add |

### When Opt-out
- Core feature of the section/block
- Majority of merchants want it (>70%)
- Removal is a conscious design decision
- "Completeness" is the expected default

### When Opt-in
- Specialized/niche feature
- Performance cost (extra API calls, JS load)
- Only for certain use cases
- Potentially disruptive if active unintentionally
- Experimental features

### Examples

| Setting | Pattern | Reason |
|---------|---------|--------|
| Filter in sidebar | `hide_*` (opt-out) | Core function |
| Debug output | `show_*` (opt-in) | Developer only |
| Animations | `disable_*` (opt-out) | Standard UX |
| Video autoplay | `enable_*` (opt-in) | Performance, disruptive |
| Product ratings | `hide_*` (opt-out) | Social proof is standard |
| Schema markup | `enable_*` (opt-in) | Technical SEO feature |

**Consistency:** Within a section/block, stay consistent. Don't mix `hide_price` and `show_vendor`.

---

## 12. Empty States

Empty states show the merchant in the editor that content is needed. **Only visible in editor** (`request.design_mode`), never in frontend.

### When to show?
- Block needs content to function → ✅ (Accordion without items)
- Section renders without content → ❌ (Hero without heading)
- Metafield/resource not found → ✅ (FAQs metafield empty)

### Snippet: `editor.empty-state.liquid`

```liquid
{% render 'editor.empty-state', message: 'blocks.accordion.empty_state.custom' %}
{% render 'editor.empty-state', message: 'sections.store_list.empty_state.no_stores', context: collection.title %}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | String | Yes | Translation key |
| `context` | Object | No | Interpolation for translation |

### Translation key pattern
```
t:blocks.[name].empty_state.custom     → "Add [items] to get started"
t:blocks.[name].empty_state.auto       → "No [data] found in metafield"
t:sections.[name].empty_state.default  → "Add blocks to this section"
```

### CSS specs

| Property | Value |
|----------|-------|
| Border | `2px dashed` (20% text-color) |
| Background | 5% text-color |
| Border-radius | `var(--border-radius--medium)` |
| Min-height | `8rem` |
| Padding | `var(--space--large)` |
| Text-color | 50% text-color |
| Text-align | `center` |

**CSS class:** `.editor-empty-state` (single class, unified design)

### Liquid pattern
```liquid
{%- if has_content -%}
  {% content_for "blocks" %}
{%- else -%}
  {% render 'editor.empty-state', message: 'blocks.accordion.empty_state.custom' %}
{%- endif -%}
```

---

## 13. Editor CSS

Editor-specific styles live in `assets/editor.css`, loaded only in design mode:

```liquid
{% if request.design_mode %}
  {{ 'editor.css' | asset_url | stylesheet_tag }}
{% endif %}
```

**Layer:** `@layer editor` — comes after all other layers (`base → components → sections → states → editor`).

**Result:** 0 bytes for customers, browser-cached for editor sessions, own layer prevents specificity conflicts.

**Contains:** `.editor-empty-state`, `.is-editor` visibility overrides for sidebars/hidden elements.

---

## 14. Setting Types Reference

### Text & Content
`text`, `textarea`, `richtext`, `inline_richtext`, `html`, `liquid`

### Media
`image_picker`, `video`, `video_url` (accept: youtube, vimeo)

### Links & Actions
`url`, `link_list`

### Shopify Resources
`product`, `product_list` (limit), `collection`, `collection_list` (limit), `blog`, `article`, `page`, `metaobject` (metaobject_type)

### Appearance
`color`, `color_background`, `color_scheme`, `font_picker`

### Numbers
`number`, `range` (min, max, step, unit)

### Selection
`select` (options), `radio` (options), `checkbox`

### UI Elements
`header` (content), `paragraph` (content)

### Conditional
`visible_if: "{{ section.settings.x == 'y' }}"`

---

## 15. Checklist

### Settings Structure
- [ ] Design Basis at top (no header)?
- [ ] Content under "Content" header?
- [ ] Advanced at end under "Advanced" header?
- [ ] Every group has 3+ settings?
- [ ] No unnecessary headers?

### Native Input Types
- [ ] `text_alignment` instead of select for alignment?
- [ ] `color` / `color_scheme` instead of color options?
- [ ] `checkbox` instead of select for true/false?

### Info Texts
- [ ] Info only for non-obvious settings?
- [ ] Max 10 words?
- [ ] No repetition of label?
- [ ] Dependencies documented?

### Defaults
- [ ] Default = most common use?
- [ ] Content defaults from translation keys?
- [ ] Content defaults section-specific and inspiring (not generic)?
- [ ] No placeholder texts ("Your heading", "Button", Lorem Ipsum)?
- [ ] Default length within limits (heading 3–7 words, button 2–3)?
- [ ] Boolean defaults correct (opt-in vs opt-out)?

### Blocks
- [ ] Ordered by frequency?
- [ ] `@app` last?
- [ ] Private blocks with `_` prefix?

### Presets
- [ ] One preset = section name (DRY)?
- [ ] Multiple presets → descriptive names?
- [ ] Preset shows functional example with blocks?
- [ ] Correct category?

### Empty States
- [ ] Only when content is needed for function?
- [ ] `editor.empty-state` snippet used?
- [ ] Translation key defined?
- [ ] Text is short and action-oriented?

### Translation Keys
- [ ] All labels use `t:` syntax?
- [ ] Global labels from `t:global.labels.*`?
- [ ] Global headers from `t:global.headers.*`?
- [ ] Section-specific keys in `t:sections.[name].*`?
