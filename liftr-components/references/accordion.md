# liftr-accordion — Implementation Guide

**Element:** `<liftr-accordion>`
**Files:** `ui.accordion.js`, `ui.accordion.css`
**Category:** UI Module (Web Component)

---

## 1. CSS Ownership — What Exists Where

### `core.critical.liquid` (@layer base) — Section 7

FOUC prevention rules. These rules **already exist** and must NOT be duplicated:

```css
/* Before defined OR loading: hide all panels */
liftr-accordion:not(:defined) [liftr-role~="accordion-panel"],
liftr-accordion[liftr-state~="loading"] [liftr-role~="accordion-panel"] {
  display: none !important;
}

/* After defined: aria-hidden controls visibility */
liftr-accordion [liftr-role~="accordion-panel"][aria-hidden="true"] { display: none !important; }
liftr-accordion [liftr-role~="accordion-panel"][aria-hidden="false"] { display: block !important; }

/* Disabled: show all panels */
liftr-accordion[liftr-state~="disabled"] [liftr-role~="accordion-panel"] { display: block !important; }

/* Hide toggle icons until ready */
liftr-accordion:not(:defined) [liftr-role~="accordion-toggle"]::after,
liftr-accordion[liftr-state~="loading"] [liftr-role~="accordion-toggle"]::after { display: none !important; }

/* Sheet mode: hide inline accordion panels (content portaled into sheet dialog) */
liftr-accordion[liftr-settings~="mode-sheet"] [liftr-role~="accordion-panel"] {
  display: none !important;
}

/* Sheet mode: show when portaled into panel_module */
liftr-accordion[liftr-settings~="mode-sheet"] .panel_module > [liftr-role~="accordion-panel"] {
  display: block !important;
}
```

### `ui.accordion.css` (@layer modules)

All component-level styles. These rules **already exist**:

```css
/* Root display */
liftr-accordion { display: block; }

/* Disabled: no pointer events on toggles */
liftr-accordion[liftr-state~="disabled"] [liftr-role~="accordion-toggle"] { pointer-events: none; }

/* Toggle layout (flex with gap for icon) */
liftr-accordion[liftr-settings]:not([liftr-settings~="icon-none"]) [liftr-role~="accordion-toggle"] {
  display: flex; justify-content: space-between; align-items: center;
}

/* Icon base (::after pseudo-element with mask-image) */
liftr-accordion[liftr-settings]:not([liftr-settings~="icon-none"]) [liftr-role~="accordion-toggle"]::after {
  content: ''; background-color: currentColor;
  mask-size: contain; mask-repeat: no-repeat; mask-position: center;
  transition: transform var(--transition--fast) var(--ease--out);
}

/* Icon types: angle, plus, chevron, arrow, bell */
/* Icon sizes: xsmall, small, regular, medium, large */
/* Reduced motion: transition: none on icon */

/* Sheet mode: icon never rotates (no open/close state, acts as "opens sheet" indicator) */
liftr-accordion[liftr-settings~="mode-sheet"] [liftr-role~="accordion-toggle"]::after {
  transform: none !important;
}
```

### Section CSS (@layer sections)

Section CSS only handles:
- Layout of the `.accordion_component` wrapper (flex, gap, max-width)
- Visual design of `.accordion_item` (background, border-radius, shadow)
- Toggle/panel styling (padding, font-size, colors)
- Design variants (`.is-card`, `.is-line`)
- Color overrides via `--accordion--*` custom properties (Section 5)

Section CSS must **NOT** touch:
- Toggle icon rendering (owned by `ui.accordion.css`)
- Panel visibility logic (owned by `core.critical.liquid`)
- Disabled state behavior (owned by `ui.accordion.css`)
- ARIA-driven display (owned by `core.critical.liquid`)
- Sheet panel open/close animations (owned by `ui.panel.css`)

---

## 2. FOUC & Loading

FOUC is covered by the `core.critical.liquid` §7 rules above (`:not(:defined)` hides all panels,
`aria-hidden` takes over after mount). No skeleton needed (rule → `css-system.md`, liftr-foundation).
`liftr-state="loading"` is optional: it keeps panels and toggle icons hidden until `MIN_LOADING` (900 ms)
has passed; the theme's `blocks/accordion.liquid` does not set it.

---

## 3. liftr-accordion

### Module Constants

```javascript
const ROLES = Object.freeze({
  ITEM:   'accordion-item',
  TOGGLE: 'accordion-toggle',
  PANEL:  'accordion-panel'
});

const STATES = Object.freeze({
  DISABLED: 'disabled',
  OPEN:     'open',
  CLOSED:   'closed'
});

const EVENTS = Object.freeze({
  OPENED:           'opened',
  CLOSED:           'closed',
  ENABLED:          'enabled',
  DISABLED:         'disabled',
  SETTINGS_CHANGED: 'settings-changed',
  KEYBOARD:         'keyboard'
});

const SETTINGS = Object.freeze({
  MODE_CLOSED:    'mode-closed',
  MODE_HIGHLIGHT: 'mode-highlight',
  MODE_SHEET:     'mode-sheet',
  ICON_NONE:      'icon-none',
  ICON_ANGLE:     'icon-angle',
  ICON_PLUS:      'icon-plus',
  ICON_CHEVRON:   'icon-chevron',
  ICON_ARROW:     'icon-arrow',
  ICON_BELL:      'icon-bell',
  SIZE_XSMALL:    'size-xsmall',
  SIZE_SMALL:     'size-small',
  SIZE_REGULAR:   'size-regular',
  SIZE_MEDIUM:    'size-medium',
  SIZE_LARGE:     'size-large'
});
```

No PROPERTIES (JS does not set CSS variables).

LISTEN (sheet mode dependency — NOT exported):
```javascript
const LISTEN = Object.freeze({
  PANEL_CLOSED: 'liftr:panel:closed'
});
```

Dynamic import: Sheet mode lazy-loads `ui.panel.js` ROLES via `await import('ui.panel')` on first sheet mode activation. No static dependency on panel module.

### CSS Settings (Responsive)

The accordion reads CSS custom properties via `watchSettings()`:

```javascript
const CSS_SCHEMA = Object.freeze({
  mode:      { type: 'string', default: 'closed' },
  exclusive: { type: 'bool', default: true },
  icon:      { type: 'string', default: 'angle' },
  size:      { type: 'string', default: 'regular' }
});
```

CSS properties (on the consumer element `liftr-accordion.{context}_accordion`):

| Property | Type | Default | Values |
|----------|------|---------|--------|
| `--accordion-enabled` | bool | `true` | `true`, `false` |
| `--accordion-mode` | string | `closed` | `closed`, `highlight`, `sheet` |
| `--accordion-exclusive` | bool | `true` | `true`, `false` |
| `--accordion-icon` | string | `angle` | `none`, `angle`, `plus`, `chevron`, `arrow`, `bell` |
| `--accordion-size` | string | `regular` | `xsmall`, `small`, `regular`, `medium`, `large` |

Example responsive setup (container class on a parent wrapper, unnamed CQ → `css-system.md`, liftr-foundation):

```html
<div class="container-large">
  <div class="faqs_component">
    <liftr-accordion class="faqs_accordion">
      ...
    </liftr-accordion>
  </div>
</div>
```

```css
liftr-accordion.faqs_accordion {
  --accordion-enabled: true;
  --accordion-mode: closed;
  --accordion-exclusive: true;
  --accordion-icon: angle;
  --accordion-size: regular;
}

@container (max-width: 48rem) {
  liftr-accordion.faqs_accordion {
    --accordion-icon: plus;
    --accordion-size: small;
  }
}
```

Sheet mode responsive setup (filter panels, as in `core.components.css` → `panel-accordion_component`):

```css
/* Why @media, not @container: the bottom sheet is viewport UX — a CQ would also
   trigger in narrow desktop sidebars. */
@media (max-width: 48rem) {
  liftr-accordion.panel-accordion_component {
    --accordion-mode: sheet;
  }
}
```

The sheet panels are created by `ui.accordion.js` (`#createSheet`), which sets `--panel-mode: sheet`
inline on each created `<liftr-panel>` — no section CSS rule is needed for them.

### Settings Output (liftr-settings)

When enabled, the module writes a combined token string to `liftr-settings`:

```html
<!-- Closed mode with angle icon at regular size -->
<liftr-accordion liftr-settings="mode-closed icon-angle size-regular">

<!-- Highlight mode with no icon (size omitted when icon-none) -->
<liftr-accordion liftr-settings="mode-highlight icon-none">

<!-- Sheet mode with plus icon (panels open as bottom sheets on mobile) -->
<liftr-accordion liftr-settings="mode-sheet icon-plus size-regular">
```

CSS selectors use `[liftr-settings~="..."]` for token matching:

```css
liftr-accordion[liftr-settings~="icon-angle"] [liftr-role~="accordion-toggle"]::after {
  mask-image: var(--icon--angle);
}
```

When disabled, `liftr-settings` is removed entirely.

### Modes

| Mode | Behavior |
|------|----------|
| `closed` | All panels closed by default. User toggles individually. Hash linking supported. |
| `highlight` | First panel forced open. Used for "featured answer" pattern. |
| `sheet` | Toggle opens content as bottom sheet (via `<liftr-panel>`). No inline ARIA. Used for mobile filter panels. |

### Sheet Mode — Architecture

Sheet mode creates `<liftr-panel>` elements on demand when a toggle is clicked:

1. **First click** on toggle → `#createSheet(index)` creates `<liftr-panel>` inside the accordion-item
2. Accordion-panel is **portaled** from its inline position into the sheet's `.panel_module`
3. Panel opens via Public API (`panel.open()`)
4. On close → content portaled **back** to original position
5. Panel persists in DOM for reuse on subsequent opens

**Critical invariant:** Portaled content never leaves its `<liftr-list-filter>` ancestor, preserving scoped `this.roleAll()` queries.

**DOM during sheet open:**
```
<liftr-accordion liftr-settings="mode-sheet icon-plus size-regular">
  <liftr-list-filter liftr-role="accordion-item">
    <fieldset>
      <button liftr-role="accordion-toggle">Title</button>
      <!-- placeholder comment marks original position -->
      <liftr-panel liftr-id="filter-sheet-0">
        <dialog class="panel_component">
          <div liftr-role="panel-drag"></div>
          <header class="panel_header">...</header>
          <div class="panel_module">
            <!-- accordion-panel portaled here -->
            <liftr-scroll liftr-role="accordion-panel">
              <input liftr-role="filter-input"> <!-- still child of liftr-list-filter -->
            </liftr-scroll>
          </div>
          <footer class="panel_footer">
            <button liftr-role="panel-close">Speichern</button>
          </footer>
        </dialog>
      </liftr-panel>
    </fieldset>
  </liftr-list-filter>
</liftr-accordion>
```

**Dependencies:** Panel ROLES are lazy-loaded via `await import('ui.panel')` when sheet mode activates. No static import — panel module only loaded when needed.

**Mode transitions:**
- `closed` → `sheet`: Close all inline panels, remove ARIA, start panel:closed listener, preload panel ROLES
- `sheet` → `closed`: Close active sheet, destroy all panels, restore ARIA, apply initial open logic
- `sheet` → disabled: Close active sheet, destroy all panels, remove settings

### Exclusive vs Non-Exclusive

| `exclusive: true` (default) | `exclusive: false` |
|-----------------------------|---------------------|
| Only one panel open at a time | Multiple panels can be open |
| Opening one closes others | Independent toggle per item |

### Initial Open

Priority order for which panel opens on mount:

1. **URL hash** — `#item-id` matches an item's `id` attribute
2. **`config.initialOpen`** — numeric index from settings.modules.accordion
3. **None** — all panels closed

Only applies in `closed` mode. In `highlight` mode, first panel always opens. In `sheet` mode, no initial open (all panels hidden inline).

### Events

| Event | Detail | When |
|-------|--------|------|
| `liftr:accordion:opened` | `{ index, hash, animated }` | Inline panel opens |
| `liftr:accordion:opened` | `{ index, mode: 'sheet' }` | Sheet panel opens |
| `liftr:accordion:closed` | `{ index, animated }` | Inline panel closes |
| `liftr:accordion:closed` | `{ index, mode: 'sheet' }` | Sheet panel closes |
| `liftr:accordion:enabled` | `{ enabled: true }` | CSS Settings enables |
| `liftr:accordion:disabled` | `{ enabled: false }` | CSS Settings disables |
| `liftr:accordion:settings-changed` | `{ mode, icon, size, exclusive }` | CSS Settings change |
| `liftr:accordion:keyboard` | `{ key, fromIndex }` | Keyboard navigation |
| `liftr:accordion:mounted` | `{ element }` | Automatic (LiftrModule) |
| `liftr:accordion:unmounted` | `{ element }` | Automatic (LiftrModule) |

**Note:** Sheet mode events include `mode: 'sheet'` in detail. Consumers can distinguish inline vs sheet open/close.

### Public API

| Method/Getter | Returns | Description |
|---------------|---------|-------------|
| `open(index)` | void | Open item by index |
| `close(index)` | void | Close item by index |
| `toggle(index)` | void | Toggle item by index |
| `closeAll()` | void | Close all items |
| `isOpen(index)` | boolean | Check if item is open |
| `length` | number | Number of items |
| `openIndex` | number | First open index (-1 if none) |
| `openIndices` | number[] | All open indices |

All methods are guarded — safe to call before mount or when disabled.

### ARIA

The module manages full ARIA automatically:

| Element | Attributes |
|---------|-----------|
| Toggle (`<button>`) | `aria-expanded`, `aria-controls` |
| Panel | `role="region"`, `aria-hidden`, `aria-labelledby` |

When disabled, all ARIA attributes are removed (panels become static content).
When in sheet mode, all ARIA attributes are removed (panel dialog provides its own accessibility).

IDs are auto-generated via `ensureId()` if not present on toggle/panel.

### Keyboard Navigation

| Key | Action |
|-----|--------|
| `ArrowDown` | Focus next toggle |
| `ArrowUp` | Focus previous toggle |
| `Home` | Focus first toggle |
| `End` | Focus last toggle |
| `Enter`/`Space` | Toggle current (native button behavior) |

Focus wraps around (last → first, first → last).

### Hash Linking

Items with an `id` attribute support deep linking:

```html
<div liftr-role="accordion-item" id="shipping-info">
  <button liftr-role="accordion-toggle">Shipping</button>
  <div liftr-role="accordion-panel">...</div>
</div>
```

- URL `#shipping-info` → opens that panel on mount
- Opening a panel → updates URL hash via `history.replaceState()`
- `hashchange` event → opens matching panel

### Nesting Support

Accordions can be nested. The ownership check (`#belongsToAccordion`) ensures each accordion only manages its own direct items, not items belonging to a nested `<liftr-accordion>`.

---

## 4. Required HTML Structure

```html
<div class="{context}_component">
  <liftr-accordion
    class="{context}_accordion"
    liftr-id="my-faq"
  >
    <div liftr-role="accordion-item" id="item-1">
      <button liftr-role="accordion-toggle">Question 1</button>
      <div liftr-role="accordion-panel">
        <p>Answer 1</p>
      </div>
    </div>

    <div liftr-role="accordion-item" id="item-2">
      <button liftr-role="accordion-toggle">Question 2</button>
      <div liftr-role="accordion-panel">
        <p>Answer 2</p>
      </div>
    </div>
  </liftr-accordion>
</div>
```

### Required Elements

| Role | Element | Required | Notes |
|------|---------|----------|-------|
| `accordion-item` | `<div>` | Yes (1+) | Wraps each toggle+panel pair |
| `accordion-toggle` | `<button>` | Yes | Must be `<button>`, not `<div>` or `<a>` |
| `accordion-panel` | `<div>` | Yes | Content container |

### Optional Attributes

| Attribute | On | Purpose |
|-----------|-----|---------|
| `liftr-id` | Root | External JS targeting |
| `id` | Item | Hash linking (`#item-id`) |
| `liftr-state="loading"` | Root | Optional: hide panels until `MIN_LOADING` (Section 2) |

---

## 5. Section CSS — Design Extension

### Color Override API

Public variables consumed by `core.components.css` (`.accordion_item`, `.accordion_toggle`, `.accordion_panel`):

```css
.faqs_component {
  --accordion--card: var(--color-scheme--card);     /* Item background */
  --accordion--text: var(--color-scheme--text);     /* Text color */
  --accordion--accent: var(--color-scheme--accent); /* Toggle hover */
}
```

### Layout Override API

```css
liftr-accordion.faqs_accordion {
  --accordion--max-width: var(--faqs--max-width, 48rem);       /* .accordion_component max width */
  --accordion--toggle-font-size: var(--font-size--large);      /* Toggle text */
  --accordion--panel-font-size: var(--font-size--medium);      /* Panel text */
}
```

Toggle/panel padding is internal (`--_padding-toggle`, `--_padding-panel`) and set by the item variant — not overridable from outside.

### Design Variants

Variants in `core.components.css`:

| Variant | Class | Description |
|---------|-------|-------------|
| Card | `.accordion_item.is-card` | Item with background, border + shadow |
| Line | `.accordion_item.is-line` / `.accordion_component.is-line` | Items separated by border-bottom, no background; component gap 0 |

```html
<!-- Theme block: blocks/accordion.liquid -->
<liftr-accordion class="accordion_component" liftr-id="accordion-{{ block.id }}">
  <div liftr-role="accordion-item" class="accordion_item is-card">...</div>
</liftr-accordion>
```

---

## 6. Complete Example

### HTML (Liquid)

```liquid
<div class="faqs_component">
  <liftr-accordion
    class="accordion_component faqs_accordion"
    liftr-id="product-faq"
  >
    {% for block in section.blocks %}
      <div
        liftr-role="accordion-item"
        class="accordion_item is-card"
        id="faq-{{ block.id }}"
      >
        <button
          liftr-role="accordion-toggle"
          class="accordion_toggle"
        >
          {{ block.settings.question }}
        </button>
        <div
          liftr-role="accordion-panel"
          class="accordion_panel"
        >
          {{ block.settings.answer }}
        </div>
      </div>
    {% endfor %}
  </liftr-accordion>
</div>
```

### CSS (Section)

```css
/* section.faqs.css — wrapper .container-large provides the container */
liftr-accordion.faqs_accordion {
  --accordion-enabled: true;
  --accordion-mode: closed;
  --accordion-exclusive: true;
  --accordion-icon: angle;
  --accordion-size: regular;
  --accordion--max-width: var(--faqs--max-width, 48rem);
}

@container (max-width: 48rem) {
  liftr-accordion.faqs_accordion {
    --accordion-size: small;
  }
}
```

### Settings JSON (optional)

```json
{
  "modules": {
    "accordion": {
      "initialOpen": 0
    }
  }
}
```

---

## 7. Icon System

Icons are rendered via `::after` pseudo-element on the toggle button using CSS `mask-image`. The icon type and size are controlled by `liftr-settings` tokens.

### Available Icons

| Token | Variable | Open State |
|-------|----------|------------|
| `icon-angle` | `--icon--angle` | Rotates 90° |
| `icon-plus` | `--icon--plus` | Rotates 45° (becomes ×) |
| `icon-chevron` | `--icon--chevron` | Rotates 90° |
| `icon-arrow` | `--icon--arrow` | Rotates 90° |
| `icon-bell` | `--icon--bell` | Swaps to `--icon--bell-slash` |
| `icon-none` | — | No icon rendered |

### Available Sizes

| Token | Icon Size Variable | Gap |
|-------|--------------------|-----|
| `size-xsmall` | `--icon-size--xsmall` | `--space--xxsmall` |
| `size-small` | `--icon-size--small` | `--space--xsmall` |
| `size-regular` | `--icon-size--regular` | `--space--small` |
| `size-medium` | `--icon-size--medium` | `--space--small` |
| `size-large` | `--icon-size--large` | `--space--medium` |

When `icon-none` is set, the size token is omitted from `liftr-settings`.

---

## 8. Enable/Disable Flow

```
CSS: --accordion-enabled: true
  → watchSettings detects enabled
  → state.remove('disabled')
  → ARIA applied to all items (closed/highlight) or removed (sheet)
  → liftr-settings token string written
  → initial open logic runs (closed/highlight only)
  → sheet mode: preload panel ROLES, start panel:closed listener
  → emit liftr:accordion:enabled

CSS: --accordion-enabled: false
  → watchSettings detects disabled
  → sheet mode: close active sheet, destroy all panels, stop listener
  → state.clear() → state.add('disabled')
  → ARIA removed from all items
  → liftr-settings removed
  → toggle pointer-events: none (CSS)
  → all panels visible (core.critical.liquid)
  → emit liftr:accordion:disabled

CSS: --accordion-mode: closed → sheet (responsive breakpoint)
  → close all inline panels
  → remove ARIA from all items
  → start panel:closed listener, preload panel ROLES
  → liftr-settings updated to mode-sheet

CSS: --accordion-mode: sheet → closed (responsive breakpoint)
  → close active sheet, portal content back
  → destroy all sheet panels
  → stop panel:closed listener
  → apply ARIA to all items
  → apply initial open logic
  → liftr-settings updated to mode-closed
```

This allows the accordion to become a static content block on certain viewports.

---

## 9. Checklist

### HTML

- [ ] Root is `<liftr-accordion>` (no skeleton needed)
- [ ] Each item: `<div liftr-role="accordion-item">`
- [ ] Each toggle: `<button liftr-role="accordion-toggle">` (must be `<button>`)
- [ ] Each panel: `<div liftr-role="accordion-panel">`
- [ ] Optional: `id` on items for hash linking
- [ ] Parent wrapper carries a container class (`container-*`)
- [ ] Root: consumer class `.{context}_accordion` for CSS Settings

### CSS Settings

- [ ] `--accordion-enabled` on `liftr-accordion.{context}_accordion`
- [ ] `--accordion-mode` set (closed, highlight, or sheet)
- [ ] `--accordion-exclusive` set if non-exclusive needed
- [ ] `--accordion-icon` set (default: angle)
- [ ] `--accordion-size` set if non-regular needed
- [ ] Responsive changes via unnamed `@container (max-width: …)` (sheet mode: `@media`)
- [ ] Sheet mode: core.critical.liquid has both hide + show-in-panel rules

### Section CSS

- [ ] Only visual styling (colors, spacing, typography)
- [ ] Uses `--accordion--*` override properties where available
- [ ] Does NOT touch icon rendering
- [ ] Does NOT touch panel visibility
- [ ] Does NOT touch disabled behavior

---

## 10. Common Mistakes

**1. Toggle is not a `<button>`**
```html
<!-- WRONG -->
<div liftr-role="accordion-toggle">Question</div>
<a liftr-role="accordion-toggle">Question</a>

<!-- CORRECT -->
<button liftr-role="accordion-toggle">Question</button>
```
Module throws an error if toggle is not `<button>`.

**2. Panel visibility in section CSS**
```css
/* WRONG — fights with core.critical.liquid */
.accordion_panel { display: none; }
[aria-expanded="true"] + .accordion_panel { display: block; }

/* CORRECT — core.critical.liquid handles visibility via aria-hidden */
/* Section CSS only styles the panel content */
.accordion_panel { font-size: var(--font-size--medium); }
```

**3. Icon styles in section CSS**
```css
/* WRONG — duplicates ui.accordion.css */
.accordion_toggle::after { content: ''; mask-image: ...; }

/* CORRECT — icon is fully managed by liftr-settings tokens */
/* Only override color if needed: */
.accordion_toggle::after { color: var(--color-scheme--accent); }
```

**4. Missing container on a parent**
```html
<!-- WRONG — no container ancestor, @container rules never match -->
<div class="faqs_component"><liftr-accordion class="faqs_accordion">…</liftr-accordion></div>

<!-- CORRECT — container class on a parent wrapper, never on the Custom Element -->
<div class="container-large"><div class="faqs_component"><liftr-accordion class="faqs_accordion">…</liftr-accordion></div></div>
```

**5. Using liftr-id for CSS Settings**
```css
/* WRONG */
[liftr-id="product-faq"] { --accordion-mode: closed; }

/* CORRECT */
liftr-accordion.product-faq_accordion { --accordion-mode: closed; }
```

**6. Adding skeleton attributes**
```html
<!-- UNNECESSARY — a bare liftr-skeleton matches nothing, and the panels are already FOUC-safe -->
<liftr-accordion liftr-state="loading" liftr-skeleton>

<!-- CORRECT -->
<liftr-accordion class="faqs_accordion">
```

**7. Nesting without unique context classes**
```html
<!-- WRONG — nested accordion inherits parent CSS Settings -->
<liftr-accordion class="faq_accordion">
  <liftr-accordion class="faq_accordion">  <!-- Same class! -->

<!-- CORRECT — unique context per level -->
<liftr-accordion class="faq_accordion">
  <liftr-accordion class="sub-faq_accordion">
```

**8. Sheet mode: styling the created sheet panels' mode in section CSS**
```css
/* UNNECESSARY — ui.accordion.js (#createSheet) sets --panel-mode: sheet inline
   on every sheet panel it creates; a CSS rule here has no effect */
.filter-group_component > fieldset > liftr-panel { --panel-mode: sheet; }

/* CORRECT — switch the accordion itself */
@media (max-width: 48rem) {
  liftr-accordion.panel-accordion_component { --accordion-mode: sheet; }
}
```

**9. Sheet mode: missing core.critical.liquid show rule**
```css
/* WRONG — only the hide rule, content invisible inside sheet */
liftr-accordion[liftr-settings~="mode-sheet"] [liftr-role~="accordion-panel"] {
  display: none !important;
}

/* CORRECT — both hide + show for portaled content */
liftr-accordion[liftr-settings~="mode-sheet"] [liftr-role~="accordion-panel"] {
  display: none !important;
}
liftr-accordion[liftr-settings~="mode-sheet"] .panel_module > [liftr-role~="accordion-panel"] {
  display: block !important;
}
```

**10. Sheet mode: querying panel ROLES with string literals**
```javascript
/* WRONG — hardcoded foreign module role */
querySelector('[liftr-role~="panel-close"]');

/* CORRECT — dynamic import, use constants */
const { ROLES: PR } = await import('ui.panel');
querySelector(`[${ATTRIBUTES.ROLE}~="${PR.CLOSE}"]`);
```
