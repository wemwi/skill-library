---
name: liftr-panel
description: Implementation guide for the liftr-panel Web Component in LIFTR v4.9. Use whenever building, configuring, or debugging dialogs, modals, sidebars, bottom sheets, dropdowns, or context menus based on native HTML dialog element. Triggers on any mention of liftr-panel, panel, modal, popup, sidebar, sheet, bottom sheet, dropdown panel, context menu, dialog, overlay, or any toggleable content layer within the LIFTR ecosystem. Also use when implementing cart sidebars, filter panels, variant selectors, mobile menus, or any component that opens as an overlay with backdrop, anchored positioning, or drag-to-close.
---

# liftr-panel -- Implementation Guide

**Element:** `<liftr-panel>`  
**File:** `ui.panel.js`  
**Version:** 4.9.1  
**Category:** UI Module (Web Component)

---

## What It Does

Native `<dialog>`-based panel system with 6 position modes:
- **popup** -- Centered modal with backdrop (default)
- **sheet** -- Bottom sheet with drag-to-close
- **sidebar-left** -- Left sidebar with backdrop
- **sidebar-right** -- Right sidebar with backdrop
- **dropdown** -- Anchored to trigger, no backdrop
- **menu** -- Anchored to trigger corner, no backdrop

Features:
- CSS-driven open/close animations per mode (`@starting-style`)
- Responsive mode switching via CSS custom property
- Drag-to-close for sheet mode (velocity + threshold detection)
- External toggle buttons via `liftr-target`
- Backdrop click to close (modal modes)
- ESC key to close
- Focus trap (native dialog behavior)
- Focus management: title focus on open (prevents iOS keyboard popup)
- Scroll-to-target after close
- Nesting support (sidebar > popup, etc.)
- Stacked panels: secondary sidebars get transparent backdrop

---

## 1. CSS Ownership -- What Exists Where

CRITICAL: Do NOT duplicate these styles in Section CSS!

Three files provide panel styles. Each has a clear responsibility:

### `critical.liquid` (Section 10 -- inlined in `<head>`)

FOUC prevention + display logic. These rules **already exist**:

```css
/* Before JS: hidden */
liftr-panel:not(:defined) { display: none; }

/* Closed (without closing animation): hidden */
liftr-panel:has(dialog:not([open])):not([liftr-state~="closing"]) { display: none; }

/* Open OR closing: out of flow */
liftr-panel:has(dialog[open]),
liftr-panel[liftr-state~="closing"] { display: contents; }

/* Body scroll lock when panel open */
body:has(liftr-panel[liftr-state~="open"]) { overflow: hidden; }
```

### `ui.panel.css` (@layer components -- the module CSS)

All panel behavior, variants, animations. These rules **already exist**:

```css
/* Root: display contents */
liftr-panel { display: contents; }

/* Base dialog: flex column, colors, backdrop */
liftr-panel .panel_component { max-width: 100vw; max-height: 100dvh; ... }
liftr-panel .panel_component::backdrop { background: rgba(0,0,0,0.3); ... }

/* Variant-specific sizing, positioning, border-radius */
liftr-panel[liftr-settings~="popup"] > .panel_component { ... }
liftr-panel[liftr-settings~="sheet"] > .panel_component { ... }
liftr-panel[liftr-settings^="sidebar"] > .panel_component { ... }
liftr-panel[liftr-settings~="dropdown"] > .panel_component { ... }
liftr-panel[liftr-settings~="menu"] > .panel_component { ... }

/* Open/close animations per mode (@starting-style) */
/* Backdrop animations */
/* Drag handle styling */
/* Header, module, footer layout */
/* States: disabled, dragging */
/* Reduced motion */
```

### Section CSS (your responsibility)

**Only these things belong in your section/block CSS:**

```css
/* 1. Mode selection (responsive) */
liftr-panel[liftr-id="cart"] {
  --panel-mode: sidebar-right;
}
@media (max-width: 48rem) {
  liftr-panel[liftr-id="cart"] {
    --panel-mode: sheet;
  }
}

/* 2. Enable/disable */
liftr-panel[liftr-id="my-panel"] {
  --panel-enabled: true;
}

/* 3. Color overrides (optional) */
liftr-panel[liftr-id="my-panel"] {
  --panel-text: #333;
  --panel-background: #fff;
}
```

### Summary Table

| Property | critical.liquid | ui.panel.css | Section CSS |
|----------|:-:|:-:|:-:|
| `display: none` (FOUC) | x | -- | never |
| `display: contents` (open) | x | x | never |
| Body scroll lock | x | -- | never |
| Dialog sizing/positioning | -- | x | never |
| Backdrop styling | -- | x | never |
| Open/close animations | -- | x | never |
| Variant layouts (sidebar, sheet, etc.) | -- | x | never |
| Header/module/footer flex | -- | x | never |
| Drag handle | -- | x | never |
| State styles (disabled, dragging) | -- | x | never |
| `--panel-mode` | -- | -- | yours |
| `--panel-enabled` | -- | -- | yours |
| Color overrides | -- | -- | yours |

---

## 2. No Skeleton Loading

`<liftr-panel>` does **NOT** use `liftr-state="loading"` or `liftr-skeleton`.

- Panels are hidden by default (native `<dialog>` + critical.liquid `display: none`)
- No visible content until opened -- no FOUC possible
- JS only adds toggle/open/close behavior

---

## 3. HTML Template (Liquid)

### Standard Modal (Popup)

```liquid
<liftr-panel liftr-id="my-modal">
  <dialog class="panel_component" aria-label="{{ t_title }}">
    <div class="panel_header">
      <h2 class="panel_title" liftr-role="panel-title">{{ section.settings.title }}</h2>
      <button liftr-role="panel-close" class="panel_menu" type="button" aria-label="{{ 'panel.close' | t }}">
        {% render 'icon-close' %}
      </button>
    </div>
    <div class="panel_module">
      {{ section.settings.content }}
    </div>
    <div class="panel_footer">
      <button type="button" class="button">{{ 'actions.confirm' | t }}</button>
    </div>
  </dialog>
</liftr-panel>

<!-- External toggle -->
<button liftr-role="panel-toggle" liftr-target="my-modal" type="button">
  Open Modal
</button>

<script src="{{ 'ui.panel.js' | asset_url }}" type="module"></script>
```

### Sidebar (Cart)

```liquid
<liftr-panel liftr-id="cart-sidebar">
  <dialog class="panel_component" aria-label="{{ 'cart.title' | t }}">
    <div class="panel_header">
      <h2 class="panel_title" liftr-role="panel-title">{{ 'cart.title' | t }}</h2>
      <button liftr-role="panel-close" class="panel_menu" type="button" aria-label="{{ 'panel.close' | t }}">
        {% render 'icon-close' %}
      </button>
    </div>
    <div class="panel_module">
      {% render 'cart-items' %}
    </div>
    <div class="panel_footer">
      {% render 'cart-footer' %}
    </div>
  </dialog>
</liftr-panel>
```

```css
liftr-panel[liftr-id="cart-sidebar"] {
  --panel-mode: sidebar-right;
}
```

### Bottom Sheet (with Drag Handle)

```liquid
<liftr-panel liftr-id="variant-selector">
  <dialog class="panel_component" aria-label="{{ 'product.select_variant' | t }}">
    <div liftr-role="panel-drag"></div>
    <div class="panel_header">
      <h2 class="panel_title" liftr-role="panel-title">{{ 'product.select_variant' | t }}</h2>
    </div>
    <div class="panel_module">
      {% render 'variant-options' %}
    </div>
  </dialog>
</liftr-panel>
```

```css
liftr-panel[liftr-id="variant-selector"] {
  --panel-mode: sheet;
}
```

### Dropdown (Anchored to Trigger)

```liquid
<button liftr-role="panel-toggle" liftr-target="sort-dropdown" type="button">
  Sort by
</button>

<liftr-panel liftr-id="sort-dropdown">
  <dialog class="panel_component" aria-label="Sort">
    <div class="panel_header">
      <span class="panel_title" liftr-role="panel-title">Sort</span>
    </div>
    <div class="panel_module">
      {% render 'sort-options' %}
    </div>
  </dialog>
</liftr-panel>
```

```css
liftr-panel[liftr-id="sort-dropdown"] {
  --panel-mode: dropdown;
}
```

### Responsive Mode (Desktop Dropdown > Mobile Sheet)

```liquid
<liftr-panel liftr-id="filter-panel" liftr-scroll-to="product-list-{{ section.id }}">
  <dialog class="panel_component" aria-label="{{ 'collection.filter' | t }}">
    <div liftr-role="panel-drag"></div>
    <div class="panel_header">
      <h2 class="panel_title" liftr-role="panel-title">{{ 'collection.filter' | t }}</h2>
      <button liftr-role="panel-close" class="panel_menu" type="button">
        {% render 'icon-close' %}
      </button>
    </div>
    <div class="panel_module">
      {% render 'filter-form' %}
    </div>
    <div class="panel_footer">
      <button type="button" class="button">{{ 'actions.apply' | t }}</button>
    </div>
  </dialog>
</liftr-panel>
```

```css
liftr-panel[liftr-id="filter-panel"] {
  --panel-mode: dropdown;
}
@media (max-width: 48rem) {
  liftr-panel[liftr-id="filter-panel"] {
    --panel-mode: sheet;
  }
}
```

---

## 4. Required Structure

### On `<liftr-panel>` (Root)

| Attribute | Required | Values | Description |
|-----------|----------|--------|-------------|
| `liftr-id` | **Yes** (for external toggle) | String | Panel identifier |
| `liftr-scroll-to` | Optional | liftr-id string | Scroll to element after close |

**NEVER put `aria-label` on `<liftr-panel>`** -- custom elements have no implicit ARIA role (`generic`), making `aria-label` prohibited. Always put `aria-label` on `<dialog>` instead.

### DOM Structure (Fixed)

```
<liftr-panel>                                     -- Root (Web Component, NO aria-label)
  <dialog class="panel_component"                 -- Native dialog (MUST be direct child)
          aria-label="...">                       -- Accessible name HERE
    <div liftr-role="panel-drag"></div>            -- Drag handle (sheet only, optional)
    <div class="panel_header">                    -- Fixed top
      <h2 class="panel_title"                     -- Title element
          liftr-role="panel-title">...</h2>       -- REQUIRED for focus management
      <button liftr-role="panel-close">           -- Close button
    </div>
    <div class="panel_module">                    -- Grow + scroll area
      ...content...
      <liftr-panel>...</liftr-panel>              -- Nested panels live here
    </div>
    <div class="panel_footer">                    -- Fixed bottom
      ...actions...
    </div>
  </dialog>
</liftr-panel>
```

**Critical:** Dialog must be a **direct child** of `<liftr-panel>` (`:scope > dialog`).

### Roles

| Role | Element | Description |
|------|---------|-------------|
| `panel-toggle` | `<button>` | External open/close trigger (needs `liftr-target`) |
| `panel-close` | `<button>` | Close button inside dialog |
| `panel-drag` | `<div>` | Drag handle for sheet mode |
| `panel-title` | `<h2>`, `<h3>`, `<span>` | Title element for focus management on open |

**Focus behavior:** On open, JS focuses `panel-title` via `this.role(ROLES.TITLE)`.
This prevents iOS Safari from auto-focusing the first `<input>`/`<textarea>`
and opening the virtual keyboard. JS adds `tabindex="-1"` automatically if missing.

Panels without `panel-title` fall back to the first focusable element.
If that element is a text input, iOS will open the keyboard on panel open.

---

## 5. Panel Modes

| Mode | Modal? | Anchored? | Backdrop | Animation | Use Case |
|------|--------|-----------|----------|-----------|----------|
| `popup` | Yes | No | Dark blur | Scale + Fade | Confirmations, alerts |
| `sheet` | Yes | No | Dark blur | Slide up | Mobile selectors, actions |
| `sidebar-left` | Yes | No | Dark blur | Slide from left | Navigation menus |
| `sidebar-right` | Yes | No | Dark blur | Slide from right | Cart, filters |
| `dropdown` | No | Yes | Transparent | Slide + Fade | Sort, select |
| `menu` | No | Yes | Transparent | Scale from origin | Context menus |

### Modal vs Anchored

- **Modal** (`showModal()`): Backdrop, focus trap, ESC close, top layer
- **Anchored** (`showModal()` with positioning): Positioned relative to trigger, closes on scroll/resize, transparent backdrop

---

## 6. CSS Settings (Section CSS)

| Property | Values | Default | Description |
|----------|--------|---------|-------------|
| `--panel-enabled` | `true`/`false` | `true` | Enable/disable panel |
| `--panel-mode` | `popup`, `sheet`, `sidebar-left`, `sidebar-right`, `dropdown`, `menu` | `popup` | Panel position mode |

### Color Overrides (Optional)

```css
liftr-panel[liftr-id="my-panel"] {
  --panel-text: var(--color-scheme--text);
  --panel-background: var(--color-scheme--background);
  --panel-link: var(--color-scheme--link);
}
```

---

## 7. Output Attributes (Set by JS)

### liftr-state

| Token | Meaning |
|-------|---------|
| `open` | Panel is open |
| `disabled` | Panel is disabled |
| `dragging` | Sheet drag in progress |
| `closing` | Exit animation in progress |

### liftr-settings

Space-delimited, managed by JS to match current mode:

| Token | Meaning |
|-------|---------|
| `popup` | Popup mode active |
| `sheet` | Sheet mode active |
| `sidebar-left` | Left sidebar active |
| `sidebar-right` | Right sidebar active |
| `dropdown` | Dropdown active |
| `menu` | Menu active |
| `backdrop-none` | Transparent backdrop (stacked sidebars) |

---

## 8. CSS Custom Properties (Set by JS on dialog)

| Property | Description |
|----------|-------------|
| `--panel-origin` | Transform origin for anchored panels (e.g. `top left`) |
| `--panel-slide` | Slide direction in px for dropdown (e.g. `8px` or `-8px`) |
| `--panel-drag-y` | Sheet drag offset during touch (e.g. `45px`) |

Do NOT override these in Section CSS -- JS manages them.

---

## 9. Module Constants

```javascript
const ROLES = Object.freeze({
  TOGGLE: 'panel-toggle',
  CLOSE:  'panel-close',
  DRAG:   'panel-drag',
  TITLE:  'panel-title'
});

const STATES = Object.freeze({
  OPEN:     'open',
  DISABLED: 'disabled',
  DRAGGING: 'dragging',
  CLOSING:  'closing'
});

const EVENTS = Object.freeze({
  OPENED: 'opened',
  CLOSED: 'closed'
});

const SETTINGS = Object.freeze({
  POPUP:         'popup',
  SHEET:         'sheet',
  SIDEBAR_LEFT:  'sidebar-left',
  SIDEBAR_RIGHT: 'sidebar-right',
  DROPDOWN:      'dropdown',
  MENU:          'menu',
  BACKDROP_NONE: 'backdrop-none'
});

const LISTEN = Object.freeze({
  PANEL_CLOSE: 'liftr:panel:close'
});
```

---

## 10. Events

### Emitted

| Event | Detail | When |
|-------|--------|------|
| `liftr:panel:opened` | `{ id, type }` | Panel opened |
| `liftr:panel:closed` | `{ id, type }` | Panel closed |

### Listened

| Event | Response |
|-------|----------|
| `liftr:panel:close` | Closes panel if `detail.id` matches |

```javascript
// Programmatically close a panel
document.dispatchEvent(new CustomEvent('liftr:panel:close', {
  detail: { id: 'cart-sidebar' }
}));
```

---

## 11. Public API

```javascript
const panel = document.querySelector('liftr-panel[liftr-id="cart-sidebar"]');

// Actions
panel.open(triggerElement);    // Open (optional trigger for anchored positioning)
panel.close();                 // Close
panel.toggle(triggerElement);  // Toggle open/close

// Read state
panel.isOpen;     // boolean
panel.mode;       // string ('popup', 'sheet', etc.)
panel.panelId;    // string | null
```

All methods are safe to call before `mount()` -- they silently return.

---

## 12. Sheet Drag-to-Close

Sheet mode supports touch drag on the `panel-drag` handle:

1. **Touch start** on drag handle > tracking begins
2. **Touch move** > dialog offset via `--panel-drag-y` (downward only)
3. **Touch end** > decision:
   - **Fast swipe** (velocity >= 0.5 px/ms) > close
   - **Past threshold** (>= 30% of dialog height) > close
   - Otherwise > snap back to original position

**Configuration:**

```javascript
static DEFAULTS = {
  dragThreshold: 0.3,       // 30% of dialog height
  velocityThreshold: 0.5    // px/ms
}
```

**Requirement:** Add `<div liftr-role="panel-drag"></div>` inside dialog for sheet mode.

---

## 13. Nesting Support

Panels can be nested (e.g. sidebar > popup inside it):

- CSS uses `>` child combinators to prevent style leakage
- Each `panel-close` only closes its direct parent dialog
- Secondary sidebars automatically get transparent backdrop (`backdrop-none`)

```liquid
<!-- Sidebar contains a popup -->
<liftr-panel liftr-id="cart-sidebar">
  <dialog class="panel_component" aria-label="{{ 'cart.title' | t }}">
    <div class="panel_module">
      <!-- Nested popup -->
      <liftr-panel liftr-id="confirm-remove">
        <dialog class="panel_component" aria-label="{{ 'cart.confirm_remove' | t }}">
          <p>Remove item?</p>
          <button liftr-role="panel-close">Cancel</button>
        </dialog>
      </liftr-panel>
    </div>
  </dialog>
</liftr-panel>
```

---

## 14. Scroll-to After Close

Add `liftr-scroll-to` to scroll to an element after the panel closes:

```liquid
<liftr-panel liftr-id="filter-panel" liftr-scroll-to="product-list-{{ section.id }}">
  ...
</liftr-panel>

<!-- Target element -->
<div liftr-id="product-list-{{ section.id }}">
  {% render 'product-grid' %}
</div>
```

- Scrolls to target's closest `.shopify-section` (or target itself)
- Only scrolls if target exists
- Respects `prefers-reduced-motion` (instant vs smooth)
- Deferred to next animation frame after close

---

## 15. Keyboard

| Key | Action |
|-----|--------|
| Escape | Close panel (configurable via `closeOnEscape`) |
| Tab | Focus trap within dialog (native behavior) |

---

## 16. Checklist

Before shipping a `<liftr-panel>` implementation:

- [ ] `<dialog class="panel_component">` is **direct child** of `<liftr-panel>`
- [ ] `aria-label` on `<dialog>`, **NOT** on `<liftr-panel>` (custom element = generic role, `aria-label` prohibited)
- [ ] `liftr-id` set on root (required for external toggles)
- [ ] `--panel-mode` set in section CSS
- [ ] Toggle buttons have `liftr-role="panel-toggle"` + `liftr-target` matching `liftr-id`
- [ ] Close button has `liftr-role="panel-close"` inside dialog
- [ ] Title element has `liftr-role="panel-title"` (prevents iOS keyboard on open)
- [ ] Sheet mode has `<div liftr-role="panel-drag">` inside dialog
- [ ] NO `liftr-state="loading"` or `liftr-skeleton`
- [ ] `<script src="ui.panel.js" type="module">` loaded
- [ ] **NO duplicate styles** from critical.liquid or ui.panel.css
- [ ] Content inside `.panel_module` (scrollable area)
- [ ] Actions inside `.panel_footer` (sticky bottom)
- [ ] Responsive mode switch if needed (`@media` on `--panel-mode`)

---

## 17. Common Mistakes

| Mistake | Fix |
|---------|-----|
| `aria-label` on `<liftr-panel>` | Move to `<dialog>` — custom elements have no implicit role, `aria-label` prohibited on generic |
| Dialog not direct child of liftr-panel | Must be `:scope > dialog` -- move it |
| Missing `liftr-id` | Required for external toggles and programmatic close |
| Missing `class="panel_component"` on dialog | CSS selectors target this class |
| Missing `liftr-role="panel-title"` on title | iOS Safari focuses first input instead, keyboard opens |
| Missing drag handle in sheet mode | Add `<div liftr-role="panel-drag">` |
| Setting `display: none` on panel | critical.liquid handles visibility -- don't override |
| Writing open/close animations | Already in ui.panel.css per mode |
| Writing backdrop styles | Already in ui.panel.css |
| Content outside `.panel_module` | Won't scroll -- put content in module div |
| Nested panel close affecting parent | Each close button only closes its direct dialog |
| `liftr-scroll-to` value not matching | Must match exact `liftr-id` value on target |

---

## 18. Imports

```javascript
// In other modules interacting with panel
import { ROLES, STATES, EVENTS, SETTINGS, PROPERTIES } from './ui.panel.js';

// Listen for panel events
document.addEventListener('liftr:panel:opened', (e) => {
  const { id, type } = e.detail;
});

// Programmatic close
document.dispatchEvent(new CustomEvent('liftr:panel:close', {
  detail: { id: 'my-panel' }
}));
```
