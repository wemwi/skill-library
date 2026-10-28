---
name: liftr-accordion
description: Implementation guide for the liftr-accordion Web Component in LIFTR v4.9. Use whenever building, configuring, or debugging collapsible accordion panels, FAQ sections, expandable content areas, filter panel groups with responsive bottom sheets, or any toggle-to-reveal UI within the LIFTR ecosystem. Triggers on any mention of liftr-accordion, accordion, collapsible, expandable, FAQ, toggle panel, disclosure, expand/collapse, filter sheet, bottom sheet filter, or any grouped show/hide interaction. Also use when implementing product detail accordions, sidebar filter groups, settings panels, or any component where items open/close with ARIA, keyboard navigation, responsive enable/disable via CSS Settings, or responsive sheet mode.
---

# liftr-accordion — Implementation Guide

**Element:** `<liftr-accordion>`
**Files:** `ui.accordion.js` (v4.5.0), `components.accordion.css`
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

### `components.accordion.css` (@layer components)

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
- Color overrides via `--accordion-*` custom properties
- Sheet mode: `--panel-mode: sheet` on dynamically created `<liftr-panel>` elements

Section CSS must **NOT** touch:
- Toggle icon rendering (owned by `components.accordion.css`)
- Panel visibility logic (owned by `core.critical.liquid`)
- Disabled state behavior (owned by `components.accordion.css`)
- ARIA-driven display (owned by `core.critical.liquid`)
- Sheet panel open/close animations (owned by `ui.panel.css`)

---

## 2. No Skeleton in critical.liquid (Partial)

The accordion uses skeleton loading but has **custom FOUC prevention** in critical.liquid Section 7 instead of the generic skeleton pattern. Panels are hidden via `display: none !important` until JS takes over via `aria-hidden`.

HTML must include:
```html
<liftr-accordion liftr-state="loading" liftr-skeleton>
```

After MIN_LOADING (900ms), the `loading` state is removed automatically by LiftrModule.

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

Dynamic import: Sheet mode lazy-loads `ui.panel.js` ROLES via `await import('./ui.panel.js')` on first sheet mode activation. No static dependency on panel module.

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

CSS properties (on `.{context}_accordion` class):

| Property | Type | Default | Values |
|----------|------|---------|--------|
| `--accordion-enabled` | bool | `true` | `true`, `false` |
| `--accordion-mode` | string | `closed` | `closed`, `highlight`, `sheet` |
| `--accordion-exclusive` | bool | `true` | `true`, `false` |
| `--accordion-icon` | string | `angle` | `none`, `angle`, `plus`, `chevron`, `arrow`, `bell` |
| `--accordion-size` | string | `regular` | `xsmall`, `small`, `regular`, `medium`, `large` |

Example responsive setup:

```html
<div class="faq_component">
  <liftr-accordion class="faq_accordion" liftr-state="loading" liftr-skeleton>
    ...
  </liftr-accordion>
</div>
```

```css
.faq_component { container: faq / inline-size; }

.faq_accordion {
  --accordion-enabled: true;
  --accordion-mode: closed;
  --accordion-exclusive: true;
  --accordion-icon: angle;
  --accordion-size: regular;
}

@container faq (max-width: 48rem) {
  .faq_accordion {
    --accordion-icon: plus;
    --accordion-size: small;
  }
}
```

Sheet mode responsive setup (filter panels):

```css
.filter-panel_component { container: filter-panel / inline-size; }

.filter-panel_accordion {
  --accordion-enabled: true;
  --accordion-mode: closed;
  --accordion-exclusive: true;
  --accordion-icon: plus;
  --accordion-size: regular;
}

@container filter-panel (max-width: 48rem) {
  .filter-panel_accordion {
    --accordion-mode: sheet;
  }
}

/* Sheet panels created by JS need --panel-mode from CSS */
.filter-group_component > fieldset > liftr-panel {
  --panel-mode: sheet;
  --panel-enabled: true;
}
```

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
  mask-image: var(--icon-mask--angle);
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

**Dependencies:** Panel ROLES are lazy-loaded via `await import('./ui.panel.js')` when sheet mode activates. No static import — panel module only loaded when needed.

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
    liftr-state="loading"
    liftr-skeleton
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
| `liftr-state="loading"` | Root | Skeleton loading |
| `liftr-skeleton` | Root | Skeleton target |

---

## 5. Section CSS — Design Extension

### Color Override API

```css
.faq_accordion {
  --accordion-card: var(--color-scheme--card);     /* Item background */
  --accordion-text: var(--color-scheme--text);     /* Text color */
  --accordion-accent: var(--color-scheme--accent); /* Hover + active border */
}
```

### Layout Override API

```css
.faq_accordion {
  --accordion-max-width: 48rem;               /* Component max width */
  --accordion-toggle-font-size: var(--font-size--large);   /* Toggle text */
  --accordion-panel-font-size: var(--font-size--medium);   /* Panel text */
  --accordion-toggle-padding: var(--space--medium) var(--space--large);
  --accordion-panel-padding: 0 var(--space--large) var(--space--large);
}
```

### Design Variants

Two built-in variants via `.accordion_component`:

| Variant | Class | Description |
|---------|-------|-------------|
| Card (default) | `.is-card` | Items with background + shadow |
| Line | `.is-line` | Items separated by border-bottom, no background |

```html
<!-- Card variant -->
<div class="faq_component accordion_component is-card">
  <liftr-accordion class="faq_accordion">...</liftr-accordion>
</div>

<!-- Line variant -->
<div class="faq_component accordion_component is-line">
  <liftr-accordion class="faq_accordion">...</liftr-accordion>
</div>
```

---

## 6. Complete Example

### HTML (Liquid)

```liquid
<div class="faq_component accordion_component is-card">
  <liftr-accordion
    class="faq_accordion"
    liftr-state="loading"
    liftr-skeleton
    liftr-id="product-faq"
  >
    {% for block in section.blocks %}
      <div
        liftr-role="accordion-item"
        class="accordion_item"
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
.faq_component {
  container: faq / inline-size;
  max-width: var(--accordion-max-width, 48rem);
  margin-inline: auto;
}

.faq_accordion {
  --accordion-enabled: true;
  --accordion-mode: closed;
  --accordion-exclusive: true;
  --accordion-icon: angle;
  --accordion-size: regular;
  --accordion-accent: var(--color-scheme--accent);
}

@container faq (max-width: 48rem) {
  .faq_accordion {
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
| `icon-angle` | `--icon-mask--angle` | Rotates 90° |
| `icon-plus` | `--icon-mask--plus` | Rotates 45° (becomes ×) |
| `icon-chevron` | `--icon-mask--chevron` | Rotates 90° |
| `icon-arrow` | `--icon-mask--arrow` | Rotates 90° |
| `icon-bell` | `--icon-mask--bell` | Swaps to `--icon-mask--bell-slash` |
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
  → all panels visible (critical.liquid)
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

- [ ] Root is `<liftr-accordion>` with `liftr-state="loading"` and `liftr-skeleton`
- [ ] Each item: `<div liftr-role="accordion-item">`
- [ ] Each toggle: `<button liftr-role="accordion-toggle">` (must be `<button>`)
- [ ] Each panel: `<div liftr-role="accordion-panel">`
- [ ] Optional: `id` on items for hash linking
- [ ] Wrapper: `.{context}_component` with container query
- [ ] Root: `.{context}_accordion` for CSS Settings

### CSS Settings

- [ ] `--accordion-enabled` on `.{context}_accordion`
- [ ] `--accordion-mode` set (closed, highlight, or sheet)
- [ ] `--accordion-exclusive` set if non-exclusive needed
- [ ] `--accordion-icon` set (default: angle)
- [ ] `--accordion-size` set if non-regular needed
- [ ] Container query on wrapper (`.{context}_component`)
- [ ] Sheet mode: `--panel-mode: sheet` rule for dynamically created panels
- [ ] Sheet mode: critical.liquid has both hide + show-in-panel rules

### Section CSS

- [ ] Only visual styling (colors, spacing, typography)
- [ ] Uses `--accordion-*` override properties where available
- [ ] Does NOT touch icon rendering
- [ ] Does NOT touch panel visibility
- [ ] Does NOT touch disabled behavior
- [ ] Sheet mode: `--panel-mode` set via structural CSS selector (not inline style)

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
/* WRONG — fights with critical.liquid */
.accordion_panel { display: none; }
[aria-expanded="true"] + .accordion_panel { display: block; }

/* CORRECT — critical.liquid handles visibility via aria-hidden */
/* Section CSS only styles the panel content */
.accordion_panel { font-size: var(--font-size--medium); }
```

**3. Icon styles in section CSS**
```css
/* WRONG — duplicates components.accordion.css */
.accordion_toggle::after { content: ''; mask-image: ...; }

/* CORRECT — icon is fully managed by liftr-settings tokens */
/* Only override color if needed: */
.accordion_toggle::after { color: var(--color-scheme--accent); }
```

**4. Missing container query setup**
```css
/* WRONG — no container, CSS Settings won't respond */
.faq_accordion { --accordion-icon: angle; }

/* CORRECT */
.faq_component { container: faq / inline-size; }
.faq_accordion { --accordion-icon: angle; }
```

**5. Using liftr-id for CSS Settings**
```css
/* WRONG */
[liftr-id="product-faq"] { --accordion-mode: closed; }

/* CORRECT */
.product-faq_accordion { --accordion-mode: closed; }
```

**6. Forgetting skeleton attributes**
```html
<!-- WRONG — no skeleton, content flashes -->
<liftr-accordion>

<!-- CORRECT -->
<liftr-accordion liftr-state="loading" liftr-skeleton>
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

**8. Sheet mode: missing panel mode CSS rule**
```css
/* WRONG — JS sets --panel-mode inline (CSS owns configuration) */
panel.style.setProperty('--panel-mode', 'sheet');

/* CORRECT — structural CSS selector matches dynamically created panels */
.filter-group_component > fieldset > liftr-panel {
  --panel-mode: sheet;
}
```

**9. Sheet mode: missing critical.liquid show rule**
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
const { ROLES: PR } = await import('./ui.panel.js');
querySelector(`[${ATTRIBUTES.ROLE}~="${PR.CLOSE}"]`);
```
