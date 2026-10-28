---
name: liftr-i18n
description: Translation and internationalization system for the LIFTR Shopify theme. Covers the two-system architecture (Schema texts for editor vs Theme texts for frontend), key formula ({namespace}.{context}.{type}.{id}), consumer-based frontend namespaces, file ordering, pluralization (CLDR), HTML keys, ARIA-label conventions, validation, and deprecation. Use whenever creating locale entries for new sections/blocks/snippets, adding translation keys, reviewing i18n compliance, debugging missing translations, or planning key structure for new features.
---

# LIFTR i18n Guide

---

## Two Systems

Shopify separates translations into two categories. Never mix them.

| System | File | Purpose | Access |
|--------|------|---------|--------|
| **Schema** | `*.schema.json` | Theme Editor UI (labels, infos, options) | `t:sections.hero.name` |
| **Theme** | `*.json` | Frontend (buttons, notifications, aria) | `{{ 'key' \| t }}` |

| Goes in Schema | Goes in Theme |
|---|---|
| Section/Block `name` | `aria-label` values |
| Setting `label`, `info`, `default` | Button labels in frontend |
| Select `options` | Notifications, badges, status |
| Preset `name`, `category` | All `{{ 'key' \| t }}` calls |
| Header `content` | Interpolated UI texts |

### Files

```
/locales/
  en.default.json          → Theme texts (frontend) - English
  en.default.schema.json   → Schema texts (editor) - English
  de.json                  → Theme texts (frontend) - German
  de.schema.json           → Schema texts (editor) - German
```

### Limits

Max 3400 translations per locale file. Max 1000 characters per value.

---

## Two Architectures

Schema and Theme follow **different** namespace architectures. This is intentional — the systems have different constraints and different consumers.

| | Schema (Editor) | Theme (Frontend) |
|---|---|---|
| **Architecture** | Flat per namespace, DRY via `global` | Consumer-based (strict) |
| **Namespace rule** | 4 namespaces (see below) | Which file calls `\| t`? → namespace |
| **DRY** | Yes — `global` for 2+ consumers | No — duplication allowed, `global` is closed list |

---

## Key Formula

All keys follow one formula:

```
{namespace}.{context}.{type}.{id}
```

For `global` and `theme_settings` (no context):

```
{namespace}.{type}.{id}
```

`name` is always a direct key on context, never inside a type object:

```
{namespace}.{context}.name
```

### Examples

```
Schema:    sections.faqs.label.content_button_label
           ^^^^^^^^ ^^^^ ^^^^^ ^^^^^^^^^^^^^^^^^^^^
           ns       ctx  type  id (= setting ID)

Schema:    theme_settings.label.favicon
           ^^^^^^^^^^^^^^ ^^^^^ ^^^^^^^
           ns (no ctx)    type  id

Frontend:  sections.faqs.button.submit
           ^^^^^^^^ ^^^^ ^^^^^^ ^^^^^^
           ns       ctx  type   id

Frontend:  snippets.store.label.badge_featured
           ^^^^^^^^ ^^^^^ ^^^^^ ^^^^^^^^^^^^^^
           ns       ctx   type  id
```

---

## Key Ordering

### Namespace Order

**Schema:**

| # | Namespace |
|---|-----------|
| 1 | `theme_settings` |
| 2 | `global` |
| 3 | `sections` |
| 4 | `blocks` |

**Theme** (consumer-based order):

| # | Namespace |
|---|-----------|
| 1 | `global` |
| 2 | `components` |
| 3 | `sections` |
| 4 | `blocks` |
| 5 | `snippets` |

### Type Order (system-specific, but fixed)

Within each context object, types appear in this fixed order:

**Schema:** `name` → `label` → `info` → `default` → `option` → `placeholder` → `header` → `content` → `blocks` → `presets` → Direct Keys (alphabetical: `category`, `color`, `icon`)

**Theme:** `name` → `label` → `button` → `notification` → `aria` → Direct Keys (alphabetical: `day`, `live`, `tag`, `url`, ...)

### Within a Type: Alphabetical

Keys inside any type object are sorted alphabetically. No exceptions — this includes option values (`option.size` sorts `large`, `medium`, `small`, not `small`, `medium`, `large`).

```jsonc
// [x] Alphabetical within type
"label": {
  "anchor_id": "Anchor ID",
  "color_mode": "Color mode",
  "color_scheme": "Color scheme"
}

// [!] Random order
"label": {
  "color_scheme": "Color scheme",
  "anchor_id": "Anchor ID",
  "color_mode": "Color mode"
}
```

### Contexts: Alphabetical by Name

Within `sections`, `blocks`, `snippets`, or `components` — contexts are sorted alphabetically by their key name.

---

## Schema Namespaces

Schema architecture uses 4 namespaces. Namespace names are our convention (not Shopify-enforced — Shopify only requires `t:category.group.description` format). DRY applies — shared keys live in `global`.

### Namespace Reference

| Namespace | Contains |
|-----------|----------|
| `theme_settings` | Theme Settings groups — flat, no sub-contexts |
| `global` | Shared labels, headers, infos, options (2+ consumers) + Direct Keys: `icon`, `color`, `category` |
| `sections.[name]` | Section-specific: name, labels, infos, defaults, options, headers, presets |
| `blocks.[name]` | Block-specific: name, labels, infos, defaults, options, headers |

### DRY Rule (Schema only)

If a key is used by 2+ sections or blocks → `global`. Don't duplicate.

Exception: Filter/sort labels that appear in multiple list-type sections (product list, store list) are duplicated in each section — no shared domain namespace.

```
t:global.label.color_scheme        → "Color scheme"
t:global.label.heading             → "Heading"
t:global.label.text                → "Text"
t:global.label.design              → "Design"
t:global.label.layout              → "Layout"
t:global.label.padding             → "Padding"
t:global.label.color_mode          → "Color mode"
t:global.label.anchor_id           → "Anchor ID"
t:global.header.content            → "Content"
t:global.header.appearance         → "Appearance"
t:global.header.advanced           → "Advanced"
t:global.option.size.large         → "L"
t:global.option.size.medium        → "M"
t:global.option.size.small         → "S"
t:global.option.color_mode.auto    → "Auto"
t:global.option.color_mode.custom  → "Custom"
t:global.info.anchor_id            → "Used for anchor links"
```

### Schema Key Patterns

**Theme Settings** (`theme_settings` has no sub-contexts — all flat):

```
t:theme_settings.label.[setting_id]
t:theme_settings.info.[setting_id]
t:theme_settings.default.[setting_id]
t:theme_settings.option.[setting_id].[value]
t:theme_settings.placeholder.[setting_id]
t:theme_settings.header.[header_id]
```

**Section:**

```
t:sections.[name].name
t:sections.[name].label.[setting_id]
t:sections.[name].info.[setting_id]
t:sections.[name].default.[setting_id]
t:sections.[name].option.[setting_id].[value]
t:sections.[name].placeholder.[setting_id]
t:sections.[name].header.[header_id]
t:sections.[name].blocks.[block].name
t:sections.[name].blocks.[block].label.[setting_id]
t:sections.[name].presets.default.name
```

**Section Blocks vs. Theme Blocks:**

| Block type | Key path | Deciding factor |
|------------|----------|-----------------|
| **Section Block** (embedded, no own file) | `sections.[section].blocks.[type].*` | Block defined inline in section schema |
| **Theme Block** (own file in `/blocks/`) | `blocks.[name].*` | Block has its own `.liquid` file |

The decision follows from file existence, not from content.

**Theme Block:**

```
t:blocks.[name].name
t:blocks.[name].label.[setting_id]
t:blocks.[name].info.[setting_id]
t:blocks.[name].default.[setting_id]
t:blocks.[name].option.[setting_id].[value]
t:blocks.[name].header.[header_id]
```

**Global (typed keys):**

```
t:global.label.[id]
t:global.info.[id]
t:global.option.[id].[value]
t:global.header.[id]
```

**Global (Direct Keys):**

```
t:global.icon.[icon_id]            → flat lookup, no types (e.g. "Shopping bag")
t:global.color.[role_id]           → color scheme role labels (e.g. "Background")
t:global.category.[category_id]    → preset category labels (e.g. "Header")
```

### Anti-Pattern: Settings Wrapper

Don't nest settings as individual objects with their own `label`/`info` sub-keys. Flatten to types.

```
[!] t:sections.[name].settings.[setting_id].label
[x] t:sections.[name].label.[setting_id]
```

---

## Theme Namespaces (Frontend)

Theme architecture is **strictly consumer-based**. The rule is mechanical:

**Which file calls `| t` or which JS module reads the key? → That is the namespace.**

No domain namespaces. No thematic grouping.

### Decision Flowchart

```
Is it on the global closed list? (→ see below)
  → global

Is it a LIFTR Web Component UI text (prev/next/expand/collapse)?
  → components.[module]

Is it called by a section (.liquid in /sections/)?
  → sections.[name]

Is it called by a block (.liquid in /blocks/)?
  → blocks.[name]

Is it called by a snippet (.liquid in /snippets/)?
  → snippets.[name]

Is it called by a JS module with no Liquid counterpart?
  → components.[module]
```

**Zero ambiguity.** The caller determines the namespace. If a text is called by `store.liquid` → `snippets.store`. If a text is called by a JS module with no Liquid file → `components.[module]`. Shared status texts (opening hours) live in `global.live`. Editor-only texts also live at their consumer — the section/block/snippet that renders them. Period.

### Namespace Reference

| Namespace | Rule | Contains |
|-----------|------|----------|
| `global` | Closed list (see below) | Universal UI primitives + tag + data structures |
| `components.[module]` | JS module owns the key | Web Component texts, JS-only translations |
| `sections.[name]` | Section `.liquid` file owns the key | Section frontend texts |
| `blocks.[name]` | Block `.liquid` file owns the key | Block frontend texts |
| `snippets.[name]` | Snippet `.liquid` file owns the key | Snippet frontend texts |

### DRY Policy (Frontend)

**Duplication is allowed.** If `store.liquid` and `store-summary` block both need "Öffnungszeiten", both get their own key. The cost is ~1 extra key. The benefit is zero namespace ambiguity.

**Exception:** `global` exists for truly universal UI primitives that appear across 5+ unrelated files. `global` is a **closed list** — new entries require explicit justification.

### `global` — The Closed List

`global` contains exactly three categories. Nothing else.

**1. UI Primitives** — universal button/label/notification/aria texts:

```
global.button:        back, cancel, clear, close, load_more, refresh,
                      save, search, submit
global.label:         loading, or
global.notification:  error, success
global.aria:          close, home, menu, new_window, notifications
```

**2. Tag** — product tag lookup table (static, no interpolation, 2+ consumers):

```
global.tag.prefix:    form, origin, vein, effect, tier, trait, promo, status
global.tag.form:      powder, capsules, extract, ...
global.tag.effect:    energy, relax, focus, ...
global.tag.status:    new, bestseller, low_stock, ...
```

**3. Data Structures** — non-translatable patterns and shared status texts:

```
global.time_units:    min, h, d, minutes (one/other), hours (one/other)
global.day:           monday, tuesday, ..., sunday
global.live:          open, open_now, open_at, closed, closed_at, ...
global.url:           google_maps, facebook, instagram, whatsapp, tiktok
```

**Adding to `global`:** Only if the text is (a) context-independent (makes sense without any domain context) AND (b) used by 5+ unrelated consumers. If in doubt → duplicate at the consumer. Budget is not a concern (current usage ~11% of 3400 limit).

### Where former domain keys go

| Old namespace | New home | Rule |
|---------------|----------|------|
| `shop.button.add_to_cart` | `snippets.product.button.add_to_cart` | product.liquid calls `\| t` |
| `shop.label.stock_available` | `sections.product.label.stock_available` | section calls `\| t` |
| `shop.notification.item_added` | `components.shop.notification.item_added` | JS module fires notification |
| `list.store.label.sort_distance` | `components.list.label.sort_distance` | liftr-list JS reads it |
| `list.product.label.filter_stock` | `components.list.label.filter_stock` | liftr-list JS reads it |
| `live.label.open_now` | `global.live.open_now` | Shared status, 2+ consumers, Direct Key |
| `location.label.filter_postal_label` | `components.location.label.filter_postal_label` | liftr-location JS reads it |
| `tags.*` | `global.tag.*` | 2+ consumers, static lookup |

---

## Types

### Schema Types

| Type | Purpose | Shopify attribute |
|------|---------|-------------------|
| `label` | Setting label | `"label"` |
| `info` | Setting help text | `"info"` |
| `default` | Setting default value | `"default"` |
| `option` | Select option values | `"options"` |
| `placeholder` | Input placeholder | `"placeholder"` |
| `header` | Section/block header | `"content"` (header type) |
| `content` | Paragraph content | `"content"` (paragraph type) |

### Theme Types

| Type | Purpose | Example |
|------|---------|---------|
| `label` | Visible text (badges, status, empty states) | `snippets.store.label.badge_featured` |
| `button` | Interactive controls | `global.button.close` |
| `notification` | Feedback messages | `components.shop.notification.item_added` |
| `aria` | Screen reader labels | `global.aria.new_window` |

### Direct Keys

Direct Keys sit on the context object without a type wrapper.

**Rule:** Only for Shopify-mandated positions (`name`) or data structures that don't fit any type. Never create new Direct Keys without explicit justification.

| Key | Reason |
|-----|--------|
| `name` | Shopify-mandated position for section/block/component identifier |
| `icon` | Schema: static icon lookup table (flat, no types) |
| `color` | Schema: color scheme role labels (flat, no types) |
| `category` | Schema: preset category labels (flat, no types) |
| `time_units` | Data structure (not a label, button, notification, or aria) |
| `day` | Data structure — weekday names for live status system |
| `live` | Shared status texts — opening/closing states used by 2+ consumers |
| `url` | URL data structure for regional adaptability |
| `tag` | Static lookup table (not a label, button, notification, or aria) |

---

## ARIA-Label Convention

### LIFTR Components: Combined Pattern

```liquid
aria-label="{{ 'sections.hero.name' | t }} ({{ 'components.slider.name' | t }})"
```

Output: "Hero (Slider)"

### Section/Block Regions

```liquid
aria-label="{{ 'sections.faqs.name' | t }}"
```

### Required Component Keys

Every LIFTR component needs in theme locale:

```
components.[module].name           → "Slider", "Accordion", etc.
components.[module].button.prev    → "Previous" (if applicable)
components.[module].button.next    → "Next" (if applicable)
```

---

## Pluralization

Use CLDR `one`/`other` with `count` parameter:

```json
{
  "snippets": {
    "city": {
      "label": {
        "store_count": {
          "one": "{{ count }} store",
          "other": "{{ count }} stores"
        }
      }
    }
  }
}
```

```liquid
{{ 'snippets.city.label.store_count' | t: count: city.stores.size }}
```

Rules:
- Key ID ends with `_count`
- Always provide both `one` and `other` (even if identical in German)
- Use `| t: count: variable` — never manual if/else
- No `_singular`/`_plural` suffixes (deprecated)

---

## HTML Keys

Keys containing HTML must end with `_html`:

```json
{
  "sections": {
    "newsletter": {
      "label": {
        "consent_html": "I agree to the <a href=\"/policies/privacy\">privacy policy</a>"
      }
    }
  }
}
```

Exception: Schema `richtext` defaults — Shopify handles HTML automatically.

---

## Interpolation

### Liquid (Theme texts)

Double braces: `{{ variable }}`

```json
{ "greeting": "Hello {{ name }}, you have {{ count }} items" }
```

```liquid
{{ 'global.label.greeting' | t: name: customer.first_name, count: cart.item_count }}
```

### JavaScript (LIFTR framework)

Single braces: `{ variable }`

```json
{ "distance": "{ value } km away" }
```

### No-interpolation keys

`global.tag` and `global.icon` never use interpolation — they are static lookup tables.

---

## Validation

### Key Parity

Every key in `en.default.json` must exist in `de.json` and vice versa. Same for `en.default.schema.json` / `de.schema.json`. Missing keys = translation bug.

**Audit:** Compare JSON key paths of both files per system. Any key present in one but absent in the other is a parity violation.

### Orphaned Keys

A key exists in a locale file but is never referenced in the theme codebase.

**Audit:** Extract all key paths from JSON. Search for each key across `/sections`, `/blocks`, `/snippets`, `/layout`, `/templates`. Keys with zero references are orphaned and should be removed.

Exceptions: Keys referenced only by JavaScript (LIFTR framework) won't appear in Liquid files — cross-check with JS project.

### Key Count

Monitor total keys per file. Shopify limit is 3400 per locale file (enforced on secondary languages). Current usage ~11% — budget is not a constraint.

---

## Deprecation

No alias system. Clean cut in one commit.

**Process:**
1. Create new key in all 4 locale files
2. Update all references in theme code (Liquid, Schema `t:` paths, JS)
3. Delete old key from all 4 locale files
4. Commit together — no transition period

**Rule:** All 4 files always move in sync. Never rename in `en` without renaming in `de`.

---

## New Section/Block Checklist

When creating a new section or block, these locale entries are needed:

### Schema (*.schema.json)

- [ ] `sections.[name].name` or `blocks.[name].name` (→ Direct Keys)
- [ ] `label` for every custom setting (→ reuse Schema Standard Global Keys)
- [ ] `info` for non-obvious settings
- [ ] `default` for content settings (section-specific, inspiring)
- [ ] `option` for custom select values (→ reuse `global.option.*`)
- [ ] `header` for custom headers (→ reuse `global.header.*`)
- [ ] `blocks.[type].name` for section blocks (→ Section Blocks vs. Theme Blocks)
- [ ] `presets.default.name` (usually = section name)

### Theme (*.json)

- [ ] Namespace = consumer file (→ Theme Namespaces)
- [ ] `label` for frontend UI text (empty states, badges, status)
- [ ] `button` labels for frontend buttons
- [ ] `notification` for feedback messages
- [ ] `aria` labels if section has interactive regions (→ ARIA-Label Convention)

### General

- [ ] No hardcoded strings in Liquid — everything via `| t` or `t:`
- [ ] No frontend texts in schema files
- [ ] No schema texts in theme files
- [ ] Schema: shared keys reused via `global` (→ Schema DRY Rule)
- [ ] Theme: keys live at their consumer, duplication allowed (→ Theme DRY Policy)
- [ ] Key Ordering followed: namespace order, type order, alphabetical (→ Key Ordering)
- [ ] Pluralization uses CLDR `one`/`other` with `_count` suffix (→ Pluralization)
- [ ] HTML keys end with `_html` (→ HTML Keys)
- [ ] ARIA labels use combined pattern for LIFTR components (→ ARIA-Label Convention)
- [ ] Both `en` and `de` translations provided (→ Validation: Key Parity)
- [ ] Key count per file under 3400 (→ Validation: Key Count)
