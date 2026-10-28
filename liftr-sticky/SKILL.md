---
name: liftr-sticky
description: Implementation guide for the liftr-sticky Web Component in LIFTR v4.9. Use whenever building, configuring, or debugging sticky CTAs, fixed-position buttons, floating action bars, or any viewport-anchored element that appears when a reference element scrolls out of view. Triggers on any mention of liftr-sticky, sticky CTA, sticky button, floating CTA, fixed bottom bar, scroll-triggered CTA, sticky filter button, or any element that becomes fixed when its original scrolls away within the LIFTR ecosystem. Also use when implementing sticky add-to-cart bars, floating filter buttons, scroll-aware CTAs, or any component that coordinates visibility with other stickies or scopes to its own section.
---

# liftr-sticky — Implementation Guide

**Element:** `<liftr-sticky>`  
**File:** `ui.sticky.js`  
**Version:** 4.9.0  
**Category:** UI Module (Web Component)

---

## What It Does

Smart sticky CTA that appears at the viewport bottom when a referenced element scrolls out of view:
- Shows when the original CTA (via `liftr-target`) scrolls **above** the viewport
- Only triggers on downward scroll — never before the original CTA has been seen
- Two coordination modes via CSS Settings:
  - **`auto`** (default): Only one sticky visible at a time. Last triggered wins. Hides in footer zone.
  - **`self`**: Scoped to own Shopify section. No coordination with other stickies.
- Responsive enable/disable via CSS Settings
- Footer boundary detection (auto mode)
- Section boundary detection (self mode)

---

## 1. CSS Ownership — What Exists Where

### `core.liftr.css` (@layer components)

Component behavior. These rules **already exist**:

```css
/* Root: fixed bottom, hidden by default */
liftr-sticky {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: var(--z-index--sticky);
  transform: translateY(100%);
  transition: transform 300ms ease;
  pointer-events: none;
}

/* Visible state: slide up */
liftr-sticky[liftr-state~="visible"] {
  transform: translateY(0);
  pointer-events: auto;
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  liftr-sticky { transition: none; }
}
```

### Section CSS (your responsibility)

**Only visual design belongs in your section CSS:**

```css
/* Appearance, padding, background — that's yours */
.collection_sticky {
  --sticky-enabled: true;
  --sticky-mode: auto;
  padding: var(--space--small) var(--space--medium);
  background: var(--color-scheme--background);
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
}
```

### Summary Table

| Property | core.liftr.css | Section CSS |
|----------|:-:|:-:|
| `position: fixed` + bottom | ✅ | ❌ never |
| Hidden by default (translateY) | ✅ | ❌ never |
| Visible state transition | ✅ | ❌ never |
| Reduced motion | ✅ | ❌ never |
| Background, padding, shadow | — | ✅ yours |
| `--sticky-enabled` | — | ✅ yours |
| `--sticky-mode` | — | ✅ yours |

---

## 2. No Skeleton, No critical.liquid

`<liftr-sticky>` has no entries in `critical.liquid` and does **NOT** use skeleton loading.

- Content is hidden by default (translateY) until JS activates it
- No FOUC risk — invisible until the module decides to show it
- JS handles all show/hide logic via IntersectionObserver

---

## 3. HTML Template (Liquid)

### Auto Mode (default — coordinated)

```liquid
<liftr-sticky liftr-target="filter-cta" class="collection_sticky">
  <button type="button" class="btn btn--primary">
    {% render 'icon-filter' %}
    {{ 'collection.filter_button' | t }}
  </button>
</liftr-sticky>

<script src="{{ 'ui.sticky.js' | asset_url }}" type="module"></script>
```

The referenced element elsewhere on the page:

```liquid
<button liftr-id="filter-cta" type="button" class="collection_filter-btn">
  {% render 'icon-filter' %}
  {{ 'collection.filter_button' | t }}
</button>
```

### Self Mode (scoped to section)

```liquid
<liftr-sticky liftr-target="faq-cta" class="faq_sticky">
  <button type="button" class="btn btn--secondary">
    {{ 'faq.contact_support' | t }}
  </button>
</liftr-sticky>

<script src="{{ 'ui.sticky.js' | asset_url }}" type="module"></script>
```

---

## 4. Modes

### Auto Mode (default)

- Coordinated across all auto-mode stickies on the page
- Only **one** sticky visible at a time (last in DOM order wins)
- Automatically hides when footer enters viewport
- Uses a shared static registry + shared footer IntersectionObserver

### Self Mode

- Isolated — no coordination with other stickies
- Visible only while its own `.shopify-section` ancestor is in viewport
- Uses a per-instance boundary IntersectionObserver on the closest `.shopify-section`

---

## 5. CSS Settings

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `--sticky-enabled` | `true` / `false` | `false` | Enable/disable the module |
| `--sticky-mode` | `auto` / `self` | `auto` | Coordination mode |

### Responsive Example

```css
/* Mobile only */
.collection_sticky {
  --sticky-enabled: false;
}

@container collection (width < 768px) {
  .collection_sticky {
    --sticky-enabled: true;
    --sticky-mode: auto;
  }
}
```

---

## 6. Required Attributes

### On `<liftr-sticky>` (Root)

| Attribute | Required | Description |
|-----------|----------|-------------|
| `liftr-target` | **Yes** | `liftr-id` of the original CTA to observe |
| `class` | **Yes** | CSS Settings class (e.g., `collection_sticky`) |

### On Referenced Element

| Attribute | Required | Description |
|-----------|----------|-------------|
| `liftr-id` | **Yes** | Unique ID matching the sticky's `liftr-target` |

---

## 7. DOM Structure

```
<liftr-sticky liftr-target="filter-cta"       ← Root (Web Component)
              class="collection_sticky">
  <button type="button">                       ← CTA content (your markup)
    Filtern und sortieren
  </button>
</liftr-sticky>

<!-- Elsewhere on page: -->
<button liftr-id="filter-cta">                 ← Original CTA being observed
  Filtern und sortieren
</button>
```

---

## 8. Output Attributes (Set by JS)

### liftr-state

| Token | Meaning | Set When |
|-------|---------|----------|
| `visible` | Sticky CTA is shown | Target scrolled above viewport (+ mode conditions met) |

Removed automatically when conditions no longer met.

---

## 9. Behavior Flow

### Auto Mode

```
1. Module mounts, reads --sticky-enabled + --sticky-mode from CSS
2. Finds target element via liftr-target → liftr-id
3. Creates IntersectionObserver on target element
4. Registers in static auto-mode registry
5. Initializes shared footer IntersectionObserver (once)
6. When target scrolls ABOVE viewport:
   - Marks instance as candidate
   - Static #evaluate() runs:
     a. If footer visible → hide all
     b. Filter candidates whose target is hidden
     c. Last in DOM order wins
     d. Previous winner loses visible state
     e. New winner gets visible state
7. Events: liftr:sticky:shown / liftr:sticky:hidden
```

### Self Mode

```
1. Module mounts, reads --sticky-enabled + --sticky-mode from CSS
2. Finds target element via liftr-target → liftr-id
3. Creates IntersectionObserver on target element
4. Creates boundary IntersectionObserver on closest .shopify-section
5. When target scrolls above AND section is in viewport:
   - state.add('visible'), emit shown
6. When either condition fails:
   - state.remove('visible'), emit hidden
```

---

## 10. JavaScript Configuration (DEFAULTS)

```javascript
static DEFAULTS = {};
```

No configuration options — behavior is fully CSS-driven via `--sticky-enabled` and `--sticky-mode`.

---

## 11. Module Constants

```javascript
const ROLES = Object.freeze({});

const STATES = Object.freeze({
  VISIBLE: 'visible'
});

const EVENTS = Object.freeze({
  SHOWN:  'shown',
  HIDDEN: 'hidden'
});

const SETTINGS = Object.freeze({
  ENABLED: '--sticky-enabled'
});
```

### Internal Constants (not exported)

```javascript
const CSS_SCHEMA = Object.freeze({
  mode: { type: 'string', default: 'auto' }
});

const MODES = Object.freeze({
  AUTO: 'auto',
  SELF: 'self'
});

const FOOTER_SELECTOR = '.page-footer';
```

---

## 12. Events

| Event | Detail | When |
|-------|--------|------|
| `liftr:sticky:shown` | `{ root, rootId }` | Sticky CTA became visible |
| `liftr:sticky:hidden` | `{ root, rootId }` | Sticky CTA was hidden |

---

## 13. Public API

None — sticky is observation-only. Visibility is fully automated based on scroll position and mode configuration.

---

## 14. Target Resolution

Sticky uses **outgoing** `liftr-target` (finding the element this component points to), NOT `this.target()` (which finds elements pointing AT this component).

```javascript
// CORRECT — outgoing reference resolution
const targetId = this.getAttribute(ATTRIBUTES.TARGET);
const targetEl = document.querySelector(`[${ATTRIBUTES.ID}="${targetId}"]`);

// WRONG — this finds elements pointing AT sticky, not the referenced element
const targetEl = this.target();
```

This is a common source of confusion. `this.target(role)` resolves **incoming** references. Manual getAttribute + querySelector resolves **outgoing** references.

---

## 15. Static Coordination (Auto Mode Internals)

Auto mode uses static class members for cross-instance coordination:

| Static Member | Type | Purpose |
|---------------|------|---------|
| `#registry` | `Set<LiftrSticky>` | All active auto-mode instances |
| `#active` | `LiftrSticky \| null` | Currently visible instance |
| `#footerObserver` | `IntersectionObserver \| null` | Shared footer observer |
| `#footerVisible` | `boolean` | Footer in viewport flag |

Key method: `static #evaluate()` — runs whenever any target or footer visibility changes. Determines winner by DOM order (last wins), hides previous winner.

The shared footer observer is created with the first auto-mode instance and destroyed when the last one unmounts.

---

## 16. Checklist

Before shipping a `<liftr-sticky>` implementation:

- [ ] `liftr-target` on root pointing to original CTA's `liftr-id`
- [ ] Original CTA has matching `liftr-id`
- [ ] CSS class on root for Settings (e.g., `collection_sticky`)
- [ ] `--sticky-enabled: true` in Section CSS
- [ ] `--sticky-mode` set if not auto (default)
- [ ] Container query wrapper if responsive enable/disable needed
- [ ] NO `liftr-state="loading"` or `liftr-skeleton`
- [ ] `<script src="ui.sticky.js" type="module">` loaded
- [ ] **NO duplicate styles** from core.liftr.css
- [ ] Footer element has `.page-footer` class (for auto mode boundary)
- [ ] Self-mode sticky is inside a `.shopify-section` (for boundary detection)

---

## 17. Common Mistakes

| Mistake | Fix |
|---------|-----|
| Missing `liftr-target` on sticky | Required — JS can't find the original CTA |
| Missing `liftr-id` on original CTA | Required — must match sticky's `liftr-target` |
| Using `this.target()` to find original CTA | Wrong direction — use `getAttribute(ATTRIBUTES.TARGET)` + querySelector |
| Forgetting `--sticky-enabled: true` | Module defaults to disabled |
| Self mode without `.shopify-section` ancestor | Boundary observer needs a section wrapper |
| Duplicating fixed/transform styles | Already in core.liftr.css |
| Multiple auto stickies expecting all to show | Only one auto sticky visible at a time (last in DOM wins) |
| No `.page-footer` element on page | Auto mode can't detect footer — sticky won't hide near footer |

---

## 18. Imports

```javascript
// In other modules interacting with sticky
import { STATES, EVENTS } from './ui.sticky.js';

// Listen for sticky visibility changes
import { on } from './core.liftr.js';
on('liftr:sticky:shown', (e) => {
  const { root } = e.detail;
});
```
