# liftr-marquee -- Implementation Guide

**Element:** `<liftr-marquee>`  
**File:** `ui.marquee.js`  
**Category:** UI Module (Web Component)

---

## What It Does

CSS-animated infinite scroll marquee with:
- Horizontal or vertical infinite loop via CSS animation (not transform-based JS)
- Edge fade mask via `liftr-mask` utility (declarative, no JS)
- Progressive hover pause (slow down -> pause)
- Tab visibility pause (saves resources when tab hidden)
- Keyboard toggle (Space/Enter to pause/resume)
- Speed and direction via CSS Settings
- Responsive enable/disable
- Reduced motion: auto-disabled
- Duration calculated from content size / speed

---

## 1. CSS Ownership -- What Exists Where

!! **CRITICAL: Do NOT duplicate these styles in Section CSS!**

Three files provide marquee styles. Each has a clear responsibility:

### `core.critical.liquid` (Section 9 -- inlined in `<head>`)

FOUC prevention. Loaded before JS. These rules **already exist**:

```css
/* Viewport: flex row, hidden overflow */
liftr-marquee [liftr-role~="marquee-viewport"] {
  display: flex;
  flex-direction: row;
  overflow: hidden;
}

/* Panel + Clone: flex, no shrink */
liftr-marquee [liftr-role~="marquee-panel"],
liftr-marquee [liftr-role~="marquee-clone"] {
  display: flex;
  min-width: 100%;
  flex-shrink: 0;
}

/* Prevent animation until JS ready */
liftr-marquee:not(:defined) [liftr-role~="marquee-panel"],
liftr-marquee:not(:defined) [liftr-role~="marquee-clone"],
liftr-marquee[liftr-state~="loading"] [liftr-role~="marquee-panel"],
liftr-marquee[liftr-state~="loading"] [liftr-role~="marquee-clone"] {
  animation: none !important;
}
```

Also in `core.critical.liquid` (Section 6): the **Mask Utility** that powers `liftr-mask`. These rules **already exist** -- never duplicate:

```css
[liftr-mask] {
  /* Gradient-based edge fade on border-box */
  /* Directions set via attribute: left, right, top, bottom */
}
[liftr-mask~="left"]   { --_mask--l: var(--mask--edge); }
[liftr-mask~="right"]  { --_mask--r: var(--mask--edge); }
/* ... etc. */
```

### `ui.marquee.css` (@layer modules -- the module CSS)

Animation, states, keyframes. These rules **already exist**:

```css
/* Root: block, defaults for speed/direction/duration */
liftr-marquee {
  display: block; position: relative;
  --marquee-enabled: true;
  --marquee-speed: 50;
  --marquee-direction: forward;
  --marquee-duration: 20s;
}

/* Pre-defined fallback */
liftr-marquee:not(:defined) { min-height: 2em; }

/* Axis-specific flex direction */
liftr-marquee[liftr-axis="x"] [liftr-role~="marquee-viewport"] { flex-direction: row; }
liftr-marquee[liftr-axis="y"] [liftr-role~="marquee-viewport"] { flex-direction: column; }

/* Panel + Clone: animation (paused by default) */
/* Axis-specific keyframes, state: active -> running, paused -> paused, disabled -> none */

/* Keyframes: fixed -100%; reverse direction = animation-direction set by JS */
@keyframes marquee-x { to { transform: translateX(-100%); } }
@keyframes marquee-y { to { transform: translateY(-100%); } }

/* Reduced motion */
@media (prefers-reduced-motion: reduce) { animation: none; }
```

### Section CSS (your responsibility)

**Only these things belong in your section/block CSS** (consumer class, unnamed CQ, desktop-first → `css-system.md`, liftr-foundation):

```css
/* 1. Edge mask size on the component (inherits to the viewport) */
.my-section_component {
  --mask--edge: clamp(4rem, 25cqi, 30rem);
}

/* 2. CSS Settings on the consumer element */
liftr-marquee.my-section_marquee {
  --marquee-enabled: false;     /* desktop: static row */
  --marquee-speed: 60;          /* px/s -- higher = faster */
  --marquee-direction: forward; /* forward | reverse */
}

/* 3. Responsive enable */
@container (max-width: 64rem) {
  liftr-marquee.my-section_marquee {
    --marquee-enabled: true;
  }
}

/* 4. Content layout (item gap, sizing) */
liftr-marquee.my-section_marquee [liftr-role~="marquee-panel"],
liftr-marquee.my-section_marquee [liftr-role~="marquee-clone"] {
  gap: var(--space--large);
}
```

### Summary Table

| Property | core.critical.liquid | ui.marquee.css | Section CSS |
|----------|:-:|:-:|:-:|
| `overflow: hidden` on viewport | YES | YES | NO never |
| `display: flex` on viewport | YES | YES | NO never |
| `flex-shrink: 0` on panel/clone | YES | YES | NO never |
| Animation prevention (FOUC) | YES | -- | NO never |
| Mask utility (`[liftr-mask]`) | YES | -- | NO never |
| `display: block` on root | -- | YES | NO never |
| Keyframes (marquee-x/y) | -- | YES | NO never |
| State-based play-state | -- | YES | NO never |
| Reduced motion | -- | YES | NO never |
| Container query | -- | -- | YES yours |
| `--mask--edge` on component | -- | -- | YES yours |
| `liftr-mask` on viewport | -- | -- | YES yours (Liquid) |
| `--marquee-enabled` | -- | -- | YES yours |
| `--marquee-speed` | -- | -- | YES yours |
| `--marquee-direction` | -- | -- | YES yours |
| Content gap/sizing | -- | -- | YES yours |

---

## 2. No Skeleton Loading

Marquee shows real content immediately (static until JS sets `active`); FOUC is handled by
`core.critical.liquid` §9. No `liftr-state="loading"`, no `liftr-skeleton` (rule → `css-system.md`, liftr-foundation).

---

## 3. HTML Template (Liquid)

### Standard (Horizontal)

```liquid
<div class="my-section_component">
  <liftr-marquee class="my-section_marquee" liftr-axis="x">
    <div liftr-role="marquee-viewport" liftr-mask="left right">
      <div liftr-role="marquee-panel">
        {% for item in section.blocks %}
          <span class="my-section_item">{{ item.settings.text }}</span>
        {% endfor %}
      </div>
      <div liftr-role="marquee-clone" aria-hidden="true">
        {% for item in section.blocks %}
          <span class="my-section_item">{{ item.settings.text }}</span>
        {% endfor %}
      </div>
    </div>
  </liftr-marquee>
</div>

{{ 'ui.marquee.css' | asset_url | stylesheet_tag }}
<script src="{{ 'ui.marquee.js' | asset_url }}" type="module"></script>
```

### Vertical

```liquid
<liftr-marquee class="my-section_marquee" liftr-axis="y">
  <div liftr-role="marquee-viewport" liftr-mask="top bottom">
    <div liftr-role="marquee-panel">
      {% for item in items %}
        <div class="my-section_item">{{ item.content }}</div>
      {% endfor %}
    </div>
    <div liftr-role="marquee-clone" aria-hidden="true">
      {% for item in items %}
        <div class="my-section_item">{{ item.content }}</div>
      {% endfor %}
    </div>
  </div>
</liftr-marquee>
```

### USP Bar (Header)

```liquid
<div class="header-usp_component">
  <liftr-marquee class="header-usp_marquee" liftr-axis="x">
    <div liftr-role="marquee-viewport" liftr-mask="left right">
      <div liftr-role="marquee-panel">
        {% for block in section.blocks %}
          <span class="header-usp_item">
            {% render 'icon', id: block.settings.icon %}
            {{ block.settings.text }}
          </span>
        {% endfor %}
      </div>
      <div liftr-role="marquee-clone" aria-hidden="true">
        {% for block in section.blocks %}
          <span class="header-usp_item">
            {% render 'icon', id: block.settings.icon %}
            {{ block.settings.text }}
          </span>
        {% endfor %}
      </div>
    </div>
  </liftr-marquee>
</div>
```

```css
.header-usp_component {
  --mask--edge: clamp(4rem, 25cqi, 30rem);
}

/* Desktop (base): static flex row */
liftr-marquee.header-usp_marquee {
  --marquee-enabled: false;
  --marquee-speed: 40;
}

@container (max-width: 64rem) {
  liftr-marquee.header-usp_marquee {
    --marquee-enabled: true;
  }
}
```

---

## 4. Clone Requirement

**The clone must be in the HTML (Liquid), not JS-generated.**

The marquee creates the illusion of infinite scroll by having two identical copies side by side. When the first copy scrolls fully out, the animation loops seamlessly.

```
[ Panel content... ][ Clone content... ]
 <------------------- scrolls <-----------
```

- Panel and Clone must have **identical content**
- Clone gets `aria-hidden="true"` (screen readers skip it)
- Both get the same CSS animation
- JS calculates `--marquee-duration` from panel width / speed

---

## 5. Required Attributes

### On `<liftr-marquee>` (Root)

| Attribute | Required | Values | Description |
|-----------|----------|--------|-------------|
| `liftr-axis` | **Yes** | `x` or `y` | Scroll direction |
| `class` | **Yes** | Section class | CSS Settings target |
| `liftr-id` | Optional | String | External targeting |

### On Children (Roles)

| Role | Required | Element | Description |
|------|----------|---------|-------------|
| `marquee-viewport` | **Yes** | `<div>` | Flex container, overflow hidden |
| `marquee-panel` | **Yes** | `<div>` | Original content |
| `marquee-clone` | **Yes** | `<div>` | Duplicate content (aria-hidden) |

### On Viewport (Mask)

| Attribute | Required | Values | Description |
|-----------|----------|--------|-------------|
| `liftr-mask` | **Yes** | `"left right"` (x-axis) or `"top bottom"` (y-axis) | Edge fade mask. Static in Liquid -- both sides always active for infinite marquee. |

---

## 6. DOM Structure

```
<liftr-marquee>                                          <- Root (Web Component)
  <div liftr-role="marquee-viewport"                     <- Flex container, overflow hidden
       liftr-mask="left right">                          <- Edge fade mask
    <div liftr-role="marquee-panel">                     <- Original content (animated)
      ...items...
    </div>
    <div liftr-role="marquee-clone"                      <- Duplicate (animated, aria-hidden)
         aria-hidden="true">
      ...same items...
    </div>
  </div>
</liftr-marquee>
```

---

## 7. CSS Settings (Section CSS)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `--marquee-enabled` | bool | `true` | Enable/disable marquee |
| `--marquee-speed` | number | `50` | Pixels per second |
| `--marquee-direction` | string | `forward` | `forward` or `reverse` (JS sets `animation-direction`) |
| `--mask--edge` | length | `3rem` (:root) | Edge fade distance. Set on `_component`. Recommended: `clamp(4rem, 25cqi, 30rem)` |

**Duration is auto-calculated:** `contentWidth / speed = seconds`  
JS sets `--marquee-duration` on the root element.

**Edge mask** is purely CSS -- set `liftr-mask` in Liquid, `--mask--edge` in Section CSS. The mask utility lives in `core.critical.liquid` (Section 6). No JS involved.

---

## 8. Output Attributes (Set by JS)

### liftr-state

| Token | Meaning |
|-------|---------|
| `active` | Animation running |
| `paused` | Animation paused (hover, visibility, keyboard) |
| `disabled` | Marquee disabled (CSS Settings or reduced motion) |

---

## 9. CSS Custom Properties (Set by JS)

| Property | On Element | Description |
|----------|-----------|-------------|
| `--marquee-duration` | root | Calculated animation duration (e.g. `12.5s`) |

---

## 10. JavaScript Configuration (DEFAULTS)

Static config only. CSS-driven keys (speed, direction) live exclusively
in CSS_SCHEMA -- see CSS Settings in Section 7.

```javascript
{
  pauseOnHover: true,     // Progressive hover pause
  hoverSlowRate: 0.2,     // Playback rate during slow phase (0-1)
  hoverPauseDelay: 500,   // ms delay before pausing after slowdown
  pauseOnHidden: true,    // Pause when tab not visible
  keyboardToggle: true    // Space/Enter to toggle pause
}
```

Override via `settings.modules.marquee` in theme settings JSON.

---

## 11. Module Constants

```javascript
const ROLES = Object.freeze({
  VIEWPORT: 'marquee-viewport',
  PANEL:    'marquee-panel',
  CLONE:    'marquee-clone'
});

const STATES = Object.freeze({
  ACTIVE:   'active',
  PAUSED:   'paused',
  DISABLED: 'disabled'
});

const EVENTS = Object.freeze({
  PAUSED:  'paused',
  RESUMED: 'resumed'
});

const SETTINGS = Object.freeze({});
```

---

## 12. Events

### Emitted

| Event | Detail | When |
|-------|--------|------|
| `liftr:marquee:paused` | `{ trigger: 'hover'|'visibility'|'keyboard' }` | Animation pauses |
| `liftr:marquee:resumed` | `{ trigger: 'hover'|'visibility'|'keyboard' }` | Animation resumes |

---

## 13. Hover Behavior (Progressive Pause)

Not an instant stop -- two-phase deceleration:

1. **Mouse enter:** Playback rate drops to `hoverSlowRate` (default 0.2 = 20% speed)
2. **After `hoverPauseDelay` ms:** Full pause, state becomes `paused`
3. **Mouse leave:** Immediately resume at normal speed (rate 1.0)

This creates a smooth, natural feeling instead of abrupt stop/start.

---

## 14. Reduced Motion

`prefers-reduced-motion: reduce` -> marquee is **auto-disabled**.

- JS checks on mount, sets `disabled` state
- CSS also has `animation: none` media query as fallback
- Content remains visible as static flex row

---

## 15. Keyboard Accessibility

- Root element gets `tabindex="0"` if not already focusable
- **Space** or **Enter** toggles pause/resume
- `isPausedByUser` flag prevents hover/visibility from overriding manual pause

---

## 16. Section CSS Examples

### USP Announcement Bar

```css
.announcement_component {
  --mask--edge: clamp(4rem, 25cqi, 30rem);
}

liftr-marquee.announcement_marquee {
  --marquee-enabled: false;
  --marquee-speed: 40;
}

liftr-marquee.announcement_marquee [liftr-role~="marquee-panel"],
liftr-marquee.announcement_marquee [liftr-role~="marquee-clone"] {
  gap: var(--space--xlarge);
}

/* Desktop (base): static centered row */
liftr-marquee.announcement_marquee [liftr-role~="marquee-viewport"] {
  justify-content: center;
}

liftr-marquee.announcement_marquee [liftr-role~="marquee-clone"] {
  display: none;
}

@container (max-width: 64rem) {
  liftr-marquee.announcement_marquee {
    --marquee-enabled: true;
  }

  liftr-marquee.announcement_marquee [liftr-role~="marquee-viewport"] {
    justify-content: flex-start;
  }

  liftr-marquee.announcement_marquee [liftr-role~="marquee-clone"] {
    display: flex;
  }
}
```

### Brand Logo Ticker

```css
.brands_component {
  --mask--edge: clamp(4rem, 25cqi, 30rem);
}

liftr-marquee.brands_marquee {
  --marquee-enabled: true;
  --marquee-speed: 30;
}

liftr-marquee.brands_marquee [liftr-role~="marquee-panel"],
liftr-marquee.brands_marquee [liftr-role~="marquee-clone"] {
  gap: var(--space--xxlarge);
  align-items: center;
}

.brands_logo {
  height: 2rem;
  width: auto;
}
```

### Reverse Direction

```css
liftr-marquee.my-section_marquee {
  --marquee-direction: reverse; /* JS sets animation-direction: reverse on panel + clone */
}
```

---

## 17. Disabled State Layout

When `--marquee-enabled: false`, JS sets `disabled` state. The clone should be hidden and content
displayed as a static row. Handle this in Section CSS — see the USP example above (base = static,
CQ = enabled; desktop-first).

---

## 18. Checklist

Before shipping a `<liftr-marquee>` implementation:

- [ ] `liftr-axis` set to `x` or `y`
- [ ] `marquee-viewport`, `marquee-panel`, `marquee-clone` roles in DOM
- [ ] Clone has **identical content** to panel
- [ ] Clone has `aria-hidden="true"`
- [ ] `liftr-mask="left right"` on `marquee-viewport` (or `"top bottom"` for vertical)
- [ ] `--mask--edge` set on `_component` (recommended: `clamp(4rem, 25cqi, 30rem)`)
- [ ] NO `liftr-state="loading"` or `liftr-skeleton`
- [ ] Container class on a parent wrapper for responsive enable/disable
- [ ] `--marquee-enabled` in section CSS
- [ ] `--marquee-speed` set (default 50 if omitted)
- [ ] Disabled state hides clone in section CSS
- [ ] `ui.marquee.css` (stylesheet_tag) + `ui.marquee.js` (`type="module"`) loaded
- [ ] **NO duplicate styles** from core.critical.liquid or ui.marquee.css
- [ ] Gap set on panel AND clone (both need identical gap)
- [ ] Content fits in one row (no wrapping -- flex items must be inline)

---

## 19. Common Mistakes

| Mistake | Fix |
|---------|-----|
| Clone content differs from panel | Must be identical -- copy the same Liquid loop |
| Gap only on panel, not on clone | Set gap on both: `[liftr-role~="marquee-panel"], [liftr-role~="marquee-clone"]` |
| Missing `aria-hidden` on clone | Add `aria-hidden="true"` to clone in Liquid |
| Missing `liftr-mask` on viewport | Add `liftr-mask="left right"` -- edges appear hard-cut without it |
| Missing `--mask--edge` on component | Set `--mask--edge: clamp(4rem, 25cqi, 30rem)` on `_component` -- default `:root` value (3rem) is too small for marquees |
| Adding skeleton to marquee | Marquee doesn't use skeleton -- content is static until JS |
| Duplicating `overflow: hidden` | Already in core.critical.liquid and ui.marquee.css |
| Duplicating keyframes | Already in ui.marquee.css |
| Duplicating `animation-play-state` | Already in ui.marquee.css via state selectors |
| Duplicating mask utility CSS | Already in core.critical.liquid Section 6 -- never redefine `[liftr-mask]` rules |
| Clone visible when disabled | Hide the clone where `--marquee-enabled: false` applies (base or CQ) |
| Content wraps to multiple lines | Items must be flex children, no wrapping |
| Missing `liftr-axis` | Required -- JS reads it; CSS uses it for flex-direction |

---

## 20. Imports

```javascript
// In other modules interacting with marquee
import { ROLES, STATES, EVENTS, PROPERTIES } from 'ui.marquee';

// Listen for pause/resume
document.addEventListener('liftr:marquee:paused', (e) => {
  const { trigger } = e.detail; // 'hover' | 'visibility' | 'keyboard'
});
```
