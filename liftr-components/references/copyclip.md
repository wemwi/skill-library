# liftr-copyclip — Implementation Guide

**Element:** `<liftr-copyclip>`  
**File:** `ui.copyclip.js`  
**Category:** UI Module (Web Component)

---

## What It Does

Click-to-copy with visual feedback:
- Clipboard API with `execCommand` fallback
- Temporary success/error state with auto-reset
- Configurable copy text (attribute, element, or trigger content)
- Configurable success message (attribute or i18n)
- ARIA live region for screen reader announcements
- Keyboard support (Enter/Space)

---

## 1. CSS Ownership — What Exists Where

### `core.liftr.css` (@layer modules)

Component behavior. These rules **already exist**:

```css
/* Root */
liftr-copyclip { display: inline-block; position: relative; }

/* Toggle: cursor + active feedback */
liftr-copyclip [liftr-role~="copyclip-toggle"] { cursor: pointer; transition: opacity var(--transition--fast) var(--ease--out); }
liftr-copyclip [liftr-role~="copyclip-toggle"]:active { opacity: 0.7; }

/* Status: visually hidden (screen reader only) */
liftr-copyclip [liftr-role~="copyclip-status"] { position: absolute; clip: rect(0,0,0,0); ... }

/* State: copied → green text */
liftr-copyclip[liftr-state~="copied"] [liftr-role~="copyclip-toggle"] {
  background: var(--color-global--success);
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* State: error → red text */
liftr-copyclip[liftr-state~="error"] [liftr-role~="copyclip-toggle"] {
  background: var(--color-global--error);
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) { ... transition: none; }
```

### Section CSS (your responsibility)

**Only visual design belongs in your section CSS:**

```css
/* Button appearance, sizing, colors — that's yours */
liftr-copyclip.my-section_copyclip [liftr-role~="copyclip-toggle"] {
  padding: var(--space--xsmall) var(--space--small);
  border: 1px dashed var(--color-scheme--border);
  border-radius: var(--border-radius--small);
  font-family: monospace;
}
```

### Summary Table

| Property | core.liftr.css | Section CSS |
|----------|:-:|:-:|
| `display: inline-block` | ✅ | ❌ never |
| Toggle cursor + active | ✅ | ❌ never |
| Status sr-only | ✅ | ❌ never |
| Copied/error text color | ✅ | ❌ never |
| Reduced motion | ✅ | ❌ never |
| Button appearance (padding, border, font) | — | ✅ yours |

---

## 2. No Skeleton, No core.critical.liquid

Static, visible button — no FOUC risk, no skeleton (rule → `css-system.md`, liftr-foundation). JS only adds click-to-copy.

---

## 3. HTML Template (Liquid)

### Discount Code

```liquid
<liftr-copyclip
  liftr-copyclip-text="{{ discount.code }}"
  liftr-copyclip-message="{{ 'copyclip.copied' | t }}"
>
  <button liftr-role="copyclip-toggle" type="button" aria-label="{{ 'copyclip.copy_code' | t }}">
    <span liftr-role="copyclip-text">{{ discount.code }}</span>
  </button>
  <span liftr-role="copyclip-status" class="sr-only" aria-live="polite"></span>
</liftr-copyclip>

<script src="{{ 'ui.copyclip.js' | asset_url }}" type="module"></script>
```

### Share Link

```liquid
<liftr-copyclip
  liftr-copyclip-text="{{ shop.url }}{{ product.url }}"
  liftr-copyclip-message="{{ 'copyclip.link_copied' | t }}"
>
  <button liftr-role="copyclip-toggle" type="button" aria-label="{{ 'copyclip.copy_link' | t }}">
    {% render 'icon-link' %}
    <span liftr-role="copyclip-text">{{ 'copyclip.copy_link' | t }}</span>
  </button>
  <span liftr-role="copyclip-status" class="sr-only" aria-live="polite"></span>
</liftr-copyclip>
```

### Minimal (Text from Element)

```liquid
<liftr-copyclip>
  <button liftr-role="copyclip-toggle" type="button">
    <span liftr-role="copyclip-text">SAVE20</span>
  </button>
  <span liftr-role="copyclip-status" class="sr-only" aria-live="polite"></span>
</liftr-copyclip>
```

---

## 4. Copy Text Priority

JS resolves what to copy in this order:

| Priority | Source | Example |
|----------|--------|---------|
| 1 | `liftr-copyclip-text` attribute on root | `liftr-copyclip-text="SAVE20"` |
| 2 | `copyclip-text` role element content | `<span liftr-role="copyclip-text">SAVE20</span>` |
| 3 | Trigger element text content | `<button liftr-role="copyclip-toggle">SAVE20</button>` |

Use **priority 1** when the displayed text differs from the copied value (e.g. showing "Copy Code" but copying "SAVE20").

---

## 5. Required Attributes

### On `<liftr-copyclip>` (Root)

| Attribute | Required | Description |
|-----------|----------|-------------|
| `liftr-copyclip-text` | Optional | Text to copy (priority 1) |
| `liftr-copyclip-message` | Optional | Success message (overrides i18n) |

### On Children (Roles)

| Role | Required | Element | Description |
|------|----------|---------|-------------|
| `copyclip-toggle` | **Yes** | `<button>` | Click target |
| `copyclip-text` | Optional | `<span>` | Text display (priority 2 source + message swap target) |
| `copyclip-status` | Recommended | `<span>` | ARIA live region (sr-only) |

---

## 6. DOM Structure

```
<liftr-copyclip>                              ← Root (Web Component)
  <button liftr-role="copyclip-toggle">       ← Click target
    <span liftr-role="copyclip-text">         ← Text display (swapped on copy)
      SAVE20
    </span>
  </button>
  <span liftr-role="copyclip-status"          ← Screen reader announcement
        class="sr-only" aria-live="polite">
  </span>
</liftr-copyclip>
```

---

## 7. Output Attributes (Set by JS)

### liftr-state

| Token | Meaning | Duration |
|-------|---------|----------|
| `copied` | Copy succeeded | Auto-resets after `resetDelay` |
| `error` | Copy failed | Auto-resets after `resetDelay` |

Both states auto-clear. The `copyclip-text` element swaps to the success message during `copied` state, then reverts to original text.

---

## 8. Behavior Flow

```
1. User clicks toggle button
2. JS reads copy text (priority 1 → 2 → 3)
3. Clipboard API (or execCommand fallback)
4. On success:
   - state.add('copied')
   - copyclip-text swaps to success message
   - copyclip-status announces to screen readers
   - liftr:copyclip:copied event emitted
5. After resetDelay (default 1200ms):
   - state.remove('copied')
   - copyclip-text reverts to original
   - copyclip-status cleared
```

---

## 9. JavaScript Configuration (DEFAULTS)

```javascript
{
  resetDelay: 1200  // ms before state resets
}
```

Override via `settings.modules.copyclip` in theme settings JSON.

---

## 10. Module Constants

```javascript
const ROLES = Object.freeze({
  TOGGLE: 'copyclip-toggle',
  TEXT:   'copyclip-text',
  STATUS: 'copyclip-status'
});

const STATES = Object.freeze({
  COPIED: 'copied',
  ERROR:  'error'
});

const EVENTS = Object.freeze({
  COPIED: 'copied',
  ERROR:  'error'
});

const SETTINGS = Object.freeze({});
```

---

## 11. Events

| Event | Detail | When |
|-------|--------|------|
| `liftr:copyclip:copied` | `{ value }` | Text copied successfully |
| `liftr:copyclip:error` | `{ error }` | Copy operation failed |

---

## 12. Public API

None — copyclip is interaction-only. No public methods exposed.

---

## 13. Checklist

Before shipping a `<liftr-copyclip>` implementation:

- [ ] `copyclip-toggle` role on the click target (must be `<button>`)
- [ ] `copyclip-text` role if you want text swap on copy
- [ ] `copyclip-status` with `class="sr-only"` and `aria-live="polite"` for a11y
- [ ] `liftr-copyclip-text` attribute if copy value differs from displayed text
- [ ] `liftr-copyclip-message` attribute if custom success message needed
- [ ] NO `liftr-state="loading"` or `liftr-skeleton`
- [ ] `<script src="ui.copyclip.js" type="module">` loaded
- [ ] **NO duplicate styles** from core.liftr.css
- [ ] Button has `type="button"` (prevent form submission)

---

## 14. Common Mistakes

| Mistake | Fix |
|---------|-----|
| Missing `copyclip-toggle` role | Required — JS won't bind click handler |
| Using `<a>` instead of `<button>` | Use `<button type="button">` for click targets |
| Missing `aria-live` on status | Add `aria-live="polite"` for screen reader announcement |
| Duplicating copied/error color styles | Already in core.liftr.css via state selectors |
| Copy value has leading/trailing whitespace | JS trims text content — or use attribute for exact value |
| Styling the status element | `core.liftr.css` already hides it visually (`sr-only` class optional) — keep it accessible |

---

## 15. Imports

```javascript
// In other modules interacting with copyclip
import { ROLES, STATES, EVENTS } from 'ui.copyclip';

// Listen for copy events
document.addEventListener('liftr:copyclip:copied', (e) => {
  const { value } = e.detail;
});
```
