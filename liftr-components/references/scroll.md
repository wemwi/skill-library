# liftr-scroll — Implementation Guide

**Element:** `<liftr-scroll>`  
**File:** `ui.scroll.js`  
**Category:** UI Module (Web Component)

---

## What It Does

Performant scroll container with:
- Automatic overflow detection (active/inactive state)
- Prev/Next navigation controls (auto-generated or static)
- Scroll progress as CSS custom property (`--scroll-progress-x` / `--scroll-progress-y`)
- Edge masks (fade effect via `liftr-mask`)
- Keyboard navigation (Arrow, Home, End, PageUp/Down)
- Reduced-motion aware smooth scrolling
- Responsive enable/disable via CSS Settings

---

## 1. CSS Ownership — What Exists Where

⚠️ **CRITICAL: Do NOT duplicate these styles in Section CSS!**

Three files provide scroll styles. Each has a clear responsibility:

### `core.critical.liquid` (Section 8 — inlined in `<head>`)

FOUC prevention. Loaded before JS. These rules **already exist** and must NOT be rewritten:

```css
/* Root: position context (overflow: visible implicit, set in core.liftr.css) */
liftr-scroll { position: relative; }

/* Panel: native scroll + hidden scrollbar */
liftr-scroll [liftr-role~="scroll-panel"] {
  overflow: auto; scrollbar-width: none;
}
liftr-scroll [liftr-role~="scroll-panel"]::-webkit-scrollbar { display: none; }

/* Hide nav until ready */
liftr-scroll:not(:defined) [liftr-role~="scroll-nav"],
liftr-scroll[liftr-state~="loading"] [liftr-role~="scroll-nav"] { display: none !important; }
```

### `core.liftr.css` (@layer modules — the module CSS)

Component behavior. These rules **already exist** and must NOT be rewritten:

```css
/* Root: explicit visible overflow (nav never clipped) */
liftr-scroll { position: relative; display: block; min-height: 0; min-width: 0; overflow: visible; }

/* Viewport: mask carrier, neg. margin compensates panel padding */
liftr-scroll [liftr-role~="scroll-viewport"] { position: relative; min-height: 0; min-width: 0; margin: calc(-1 * var(--scroll-bleed, 0px)); }

/* Panel: padding creates shadow-safe zone inside clip boundary */
liftr-scroll [liftr-role~="scroll-panel"] { position: relative; min-height: 0; min-width: 0; padding: var(--scroll-bleed, 0px); }

/* Axis-specific overflow */
liftr-scroll[liftr-axis="x"] [liftr-role~="scroll-panel"] { overflow-x: auto; overflow-y: hidden; }
liftr-scroll[liftr-axis="y"] ... { overflow-x: hidden; overflow-y: auto; }

/* Nav visibility via state (direct child selectors) */
liftr-scroll:not([liftr-state~="active"]) > [liftr-role~="nav-control"] { display: none !important; }
liftr-scroll:not([liftr-state~="can-prev"]) > [liftr-role~="nav-prev"] { display: none !important; }
liftr-scroll:not([liftr-state~="can-next"]) > [liftr-role~="nav-next"] { display: none !important; }

/* Reduced motion */
@media (prefers-reduced-motion: reduce) { ... scroll-behavior: auto; }
```

### Section CSS (your responsibility)

**Only these things belong in your section/block CSS** (consumer class, unnamed CQ, desktop-first → `css-system.md`, liftr-foundation):

```css
/* 1. CSS Settings (enable/disable, navigation) on the consumer element */
liftr-scroll.my-section_scroll {
  --scroll-enabled: false;   /* desktop: static */
  --nav-mode: auto;
  --nav-size: medium;
}

/* 2. Responsive overrides */
@container (max-width: 64rem) {
  liftr-scroll.my-section_scroll { --scroll-enabled: true; }
}

/* 3. Content layout (flex, gap, item sizing) */
liftr-scroll.my-section_scroll [liftr-role~="scroll-content"] {
  display: flex;
  gap: var(--space--medium);
}
.my-section_card {
  flex: 0 0 80%;
}
```

### Summary Table

| Property | core.critical.liquid | core.liftr.css | Section CSS |
|----------|:-:|:-:|:-:|
| Hidden scrollbar | ✅ | — | ❌ never |
| `display: block` | — | ✅ | ❌ never |
| `overflow: visible` on root | — | ✅ | ❌ never |
| Axis overflow (x/y) | — | ✅ | ❌ never |
| Nav visibility states | — | ✅ | ❌ never |
| `position: relative` | ✅ | ✅ | ❌ never |
| Mask utility | ✅ (Section 6) | — | ❌ never |
| Shadow Bleed (panel padding + viewport neg. margin) | — | ✅ | ❌ never (use `--scroll-bleed`) |
| Container query | — | — | ✅ yours |
| CSS Settings vars | — | — | ✅ yours |
| Content layout (flex/grid) | — | — | ✅ yours |
| Item sizing | — | — | ✅ yours |
| Gap, spacing | — | — | ✅ yours |
| Mask edge size override | — | — | ✅ yours |

---

## 2. No Skeleton Loading

`<liftr-scroll>` shows real content immediately; FOUC is handled by `core.critical.liquid` §8.
No `liftr-state="loading"`, no `liftr-skeleton` (rule → `css-system.md`, liftr-foundation).

---

## 3. HTML Template (Liquid)

### Minimal (Horizontal)

```liquid
<liftr-scroll liftr-axis="x" liftr-id="{{ section.id }}-scroll">
  <div liftr-role="scroll-viewport" liftr-mask="right">
    <div liftr-role="scroll-panel">
      <div liftr-role="scroll-content">
        {% for item in items %}
          <div class="my-section_item">{{ item.content }}</div>
        {% endfor %}
      </div>
    </div>
  </div>
</liftr-scroll>

<script src="{{ 'ui.scroll.js' | asset_url }}" type="module"></script>
```

### Vertical

```liquid
<liftr-scroll liftr-axis="y" liftr-id="{{ section.id }}-scroll">
  <div liftr-role="scroll-viewport" liftr-mask="bottom">
    <div liftr-role="scroll-panel">
      <div liftr-role="scroll-content">
        {% for item in items %}
          <div>{{ item.content }}</div>
        {% endfor %}
      </div>
    </div>
  </div>
</liftr-scroll>
```

### With Static Navigation (Internal)

```liquid
<liftr-scroll liftr-axis="x" liftr-id="{{ section.id }}-scroll">
  <div liftr-role="scroll-viewport" liftr-mask="left right">
    <div liftr-role="scroll-panel">
      <div liftr-role="scroll-content">...</div>
    </div>
  </div>
  
  <button liftr-role="scroll-toggle-prev" type="button" aria-label="{{ 'scroll.prev' | t }}">‹</button>
  <button liftr-role="scroll-toggle-next" type="button" aria-label="{{ 'scroll.next' | t }}">›</button>
</liftr-scroll>
```

### With External Navigation (Buttons Outside Module)

```liquid
<div class="section-header">
  <h2>{{ section.settings.title }}</h2>
  <div class="nav-buttons">
    <button liftr-target="{{ section.id }}-scroll" liftr-role="scroll-toggle-prev" type="button">‹</button>
    <button liftr-target="{{ section.id }}-scroll" liftr-role="scroll-toggle-next" type="button">›</button>
  </div>
</div>

<liftr-scroll liftr-axis="x" liftr-id="{{ section.id }}-scroll">
  <div liftr-role="scroll-viewport" liftr-mask="left right">
    <div liftr-role="scroll-panel">
      <div liftr-role="scroll-content">...</div>
    </div>
  </div>
</liftr-scroll>
```

### With Start/End Buttons

```liquid
<liftr-scroll liftr-axis="x" liftr-id="{{ section.id }}-scroll">
  <div liftr-role="scroll-viewport">
    <div liftr-role="scroll-panel">
      <div liftr-role="scroll-content">...</div>
    </div>
  </div>
  
  <button liftr-role="scroll-toggle-start" type="button">⇤</button>
  <button liftr-role="scroll-toggle-prev" type="button">‹</button>
  <button liftr-role="scroll-toggle-next" type="button">›</button>
  <button liftr-role="scroll-toggle-end" type="button">⇥</button>
</liftr-scroll>
```

---

## 4. Required Attributes

### On `<liftr-scroll>` (Root)

| Attribute | Required | Values | Description |
|-----------|----------|--------|-------------|
| `liftr-axis` | **Yes** | `x` or `y` | Scroll direction |
| `liftr-id` | Optional | String | Identifier for external targeting |

### On Children (Roles)

| Role | Required | Element | Description |
|------|----------|---------|-------------|
| `scroll-viewport` | Recommended | `<div>` | Viewport container (mask + clip target) |
| `scroll-panel` | **Yes** | `<div>` | The scrollable element |
| `scroll-content` | Optional | `<div>` | Content wrapper (resize observe target) |

### Navigation Roles (Optional)

| Role | Mode | Description |
|------|------|-------------|
| `scroll-toggle-prev` | auto/static | Previous step button |
| `scroll-toggle-next` | auto/static | Next step button |
| `scroll-toggle-start` | static only | Jump to start button |
| `scroll-toggle-end` | static only | Jump to end button |

---

## 5. DOM Structure

```
<liftr-scroll>                          ← Root (overflow: visible, nav never clipped)
  <div liftr-role="scroll-viewport">    ← Viewport (mask carrier, neg. margin compensates bleed)
    <div liftr-role="scroll-panel">     ← Scrollable container (overflow: auto, padding = bleed)
      <div liftr-role="scroll-content"> ← Content (optional, resize observe)
        ...children...
      </div>
    </div>
  </div>
  [auto-generated nav buttons]         ← Root children — never clipped
</liftr-scroll>
```

**Fallback:** If no `scroll-viewport` exists, module still works. If no `scroll-panel`, `this` (root) is used as panel. If no `scroll-content`, resize observation skips it.

---

## 6. CSS Settings (Section CSS)

### Navigation Controls

```css
liftr-scroll.my-section_scroll {
  --nav-mode: auto;        /* false | auto | static */
  --nav-size: medium;      /* small | regular | medium | large */
  --nav-icon: angle;       /* angle | arrow | chevron */
  --nav-theme: light;      /* light | dark | plain */
  --nav-style: round;      /* square | round */
  --nav-position: inside;  /* inside | outside | edge */
}
```

### Enable/Disable (Responsive)

```css
liftr-scroll.my-section_scroll {
  --scroll-enabled: false;
}

@container (max-width: 64rem) {
  liftr-scroll.my-section_scroll {
    --scroll-enabled: true;
  }
}
```

### Navigation Mode

| Mode | Behavior | Position Applies? |
|------|----------|-------------------|
| `false` | No buttons | No |
| `auto` | Module generates prev/next | Yes |
| `static` | Developer provides buttons in HTML | No (dev controls) |

**NAV values, size tokens and defaults:** → `watch-settings.md` (liftr-foundation); NAV position → `slider.md`.

---

## 7. Output Attributes (Set by JS)

### liftr-state

| Token | Meaning |
|-------|---------|
| `active` | Content overflows, scrolling possible |
| `can-prev` | Can scroll backward |
| `can-next` | Can scroll forward |

### liftr-nav

Space-delimited output: `"auto medium angle light round inside"`

### liftr-mask (on viewport)

Automatically toggled based on scroll position:

| Direction | Added When |
|-----------|-----------|
| `left` | scrollLeft > edgeThreshold |
| `right` | scrollLeft < maxScroll - edgeThreshold |
| `top` | scrollTop > edgeThreshold |
| `bottom` | scrollTop < maxScroll - edgeThreshold |

**Requirement:** `liftr-mask` must be present in HTML on viewport. JS only toggles direction values.

The mask CSS utility is defined in `core.critical.liquid` Section 6 — do NOT rewrite it.

---

## 8. CSS Custom Properties (Set by JS on scroll-panel)

| Property | Range | Description |
|----------|-------|-------------|
| `--scroll-progress-x` | 0–1 | Horizontal scroll progress |
| `--scroll-progress-y` | 0–1 | Vertical scroll progress |

```css
/* Example: progress-based opacity in Section CSS */
liftr-scroll.my-section_scroll [liftr-role~="scroll-panel"]::after {
  opacity: var(--scroll-progress-x, 0);
}
```

---

## 9. JavaScript Configuration (DEFAULTS)

```javascript
{
  enabled: true,
  pageFactor: 0.9,       // Scroll distance per step (fraction of viewport)
  stepPx: null,           // Override: fixed pixel step (overrides pageFactor)
  smooth: true,           // Smooth scrolling (respects prefers-reduced-motion)
  observeResize: true,    // ResizeObserver on panel + content
  edgeThreshold: 2,       // px tolerance for edge detection
  wheelLock: 'none',      // 'none' | 'x' | 'y' — redirect wheel axis
  activateOnOverflow: true // Only show active state when content overflows
}
```

Override via `settings.modules.scroll` in theme settings JSON.

---

## 10. Module Constants

```javascript
const ROLES = Object.freeze({
  VIEWPORT: 'scroll-viewport',
  PANEL:    'scroll-panel',
  CONTENT:  'scroll-content',
  PREV:     'scroll-toggle-prev',
  NEXT:     'scroll-toggle-next',
  START:    'scroll-toggle-start',
  END:      'scroll-toggle-end'
});

const STATES = Object.freeze({
  ACTIVE:   'active',
  CAN_PREV: 'can-prev',
  CAN_NEXT: 'can-next'
});

const EVENTS = Object.freeze({
  STATE: 'state'
});

const SETTINGS = Object.freeze({});
```

---

## 11. Events

### Emitted

| Event | Detail | When |
|-------|--------|------|
| `liftr:scroll:state` | `{ axis, active, canPrev, canNext, progress }` | On every state change |

### Listened

| Event | Response |
|-------|----------|
| `liftr:panel:opened` | Recalculates if inside open dialog |

---

## 12. Public API

```javascript
const scroll = document.querySelector('liftr-scroll');

// Navigation
scroll.scrollPrev();           // Step backward
scroll.scrollNext();           // Step forward
scroll.scrollToStart();        // Jump to beginning
scroll.scrollToEnd();          // Jump to end
scroll.scrollTo(0.5);          // Scroll to 50% (progress 0-1)
scroll.scrollTo(200, false);   // Scroll to 200px, no smooth

// Read state
scroll.progress;    // number (0-1)
scroll.canPrev;     // boolean
scroll.canNext;     // boolean
scroll.isActive;    // boolean
scroll.isDisabled;  // boolean
scroll.axis;        // 'x' | 'y'
scroll.maxScroll;   // number (px)
```

---

## 13. Keyboard Navigation

| Key | Axis X | Axis Y |
|-----|--------|--------|
| ArrowLeft | Prev step | — |
| ArrowRight | Next step | — |
| ArrowUp | — | Prev step |
| ArrowDown | — | Next step |
| Home | Jump to start | Jump to start |
| End | Jump to end | Jump to end |
| PageUp | — | Prev step |
| PageDown | — | Next step |

Focus must be inside scroll-panel for keyboard nav to activate.

---

## 14. Section CSS Examples

### Horizontal Product Scroll (Desktop Grid → Mobile Scroll)

```css
liftr-scroll.products_scroll {
  --scroll-enabled: false;
  --nav-mode: auto;
  --nav-size: medium;
  --nav-position: inside;
}

/* Content layout — THIS is Section CSS responsibility */
liftr-scroll.products_scroll [liftr-role~="scroll-content"] {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space--medium);
}

@container (max-width: 64rem) {
  liftr-scroll.products_scroll {
    --scroll-enabled: true;
  }

  liftr-scroll.products_scroll [liftr-role~="scroll-content"] {
    display: flex;
  }

  .products_card {
    flex: 0 0 calc(50% - var(--space--medium));
  }
}

@container (max-width: 48rem) {
  .products_card {
    flex: 0 0 80%;
  }
}
```

### Vertical Scroll in Sidebar

```css
liftr-scroll.sidebar_scroll {
  --scroll-enabled: true;
  --nav-mode: false;
}
```

### Custom Mask Size

```css
liftr-scroll.my-section_scroll [liftr-role~="scroll-viewport"] {
  --mask--edge: 5rem; /* Override default 3rem from core.critical.liquid */
}
```

### Shadow Bleed Override

```css
/* Default: 0px (no bleed, tight clip).
   Set when items have box-shadow: */
liftr-scroll.my-section_scroll {
  --scroll-bleed: 1rem;  /* Shadow-safe zone on all sides */
}

/* ⚠ --scroll-bleed only accepts static <length> values (0px, 1rem, 12px).
   No clamp(), calc(), or spacing tokens that resolve to math functions.

   How it works:
   - Panel gets padding: var(--scroll-bleed) → shadows land inside clip boundary
   - Viewport gets margin: calc(-1 * var(--scroll-bleed)) → compensates the inset
   - Mask on viewport covers the full area including shadow zone */

/* ❌ NEVER set padding/margin directly on scroll-panel or scroll-viewport */
liftr-scroll.my-section_scroll [liftr-role~="scroll-panel"] {
  padding-block: var(--space--large);  /* WRONG — breaks Bleed system */
}
```

---

## 15. Checklist

Before shipping a `<liftr-scroll>` implementation:

- [ ] `liftr-axis` set to `x` or `y`
- [ ] `scroll-panel` role exists in DOM
- [ ] NO `liftr-state="loading"` or `liftr-skeleton` on scroll
- [ ] `liftr-mask` in HTML on **viewport** (not panel — if masks desired)
- [ ] Container class on a parent wrapper for responsive enable/disable
- [ ] `--scroll-enabled` in section CSS
- [ ] Navigation mode chosen (`--nav-mode`)
- [ ] Static buttons have correct roles (`scroll-toggle-prev`, `scroll-toggle-next`)
- [ ] External buttons have `liftr-target` matching `liftr-id`
- [ ] Content uses `flex` for horizontal, normal flow for vertical
- [ ] `<script src="ui.scroll.js" type="module">` loaded
- [ ] **NO duplicate styles** from core.critical.liquid or core.liftr.css in section CSS
- [ ] **NO padding/margin on `[liftr-role~="scroll-panel"]` or `[liftr-role~="scroll-viewport"]`** — use `--scroll-bleed` variable instead
- [ ] Only layout/sizing/settings in section CSS

---

## 16. Common Mistakes

| Mistake | Fix |
|---------|-----|
| Duplicating `overflow: auto` in section CSS | Already in core.critical.liquid — remove it |
| Duplicating `scrollbar-width: none` | Already in core.critical.liquid — remove it |
| Duplicating `display: block` on root | Already in core.liftr.css — remove it |
| Adding `liftr-skeleton` to scroll | Scroll doesn't use skeleton — remove it |
| Writing nav visibility CSS | Already in core.liftr.css via state selectors |
| Rewriting mask utility CSS | Already in core.critical.liquid Section 6 |
| Missing `liftr-axis` | Always required: `liftr-axis="x"` or `"y"` |
| Mask not toggling | `liftr-mask` must be in HTML; JS only toggles values |
| External buttons not binding | `liftr-target` must match `liftr-id` exactly |
| Scroll inside dialog broken | Module listens `liftr:panel:opened` — ensure panel emits it |
| Setting padding/margin on `scroll-panel` or `scroll-viewport` in section CSS | Owned by Shadow Bleed system in `@layer modules` — use `--scroll-bleed` variable instead |

---

## 17. Imports

```javascript
// In other modules interacting with scroll
import { ROLES, STATES, EVENTS, PROPERTIES } from 'ui.scroll';

// Or listen for events
document.addEventListener('liftr:scroll:state', (e) => {
  const { axis, active, canPrev, canNext, progress } = e.detail;
});
```
