---
name: liftr-marquee
description: Implementation guide for the liftr-marquee Web Component in LIFTR v4.9. Use whenever building, configuring, or debugging infinite scroll marquees, tickers, announcement bars, or any CSS-animated looping content. Triggers on any mention of liftr-marquee, marquee, ticker, infinite scroll text, scrolling banner, announcement loop, or auto-scrolling content within the LIFTR ecosystem. Also use when implementing USP bars, brand logo tickers, review tickers, or any continuously scrolling content with hover pause and keyboard accessibility.
---

# liftr-marquee -- Implementation Guide

**Element:** `<liftr-marquee>`  
**File:** `ui.marquee.js`  
**Version:** 4.9.1  
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

### `critical.liquid` (Section 9 -- inlined in `<head>`)

FOUC prevention. Loaded before JS. These rules **already exist**:

```css
/* Viewport: flex row, hidden overflow */
[liftr-role~="marquee-viewport"] {
  display: flex;
  flex-direction: row;
  overflow: hidden;
}

/* Panel + Clone: flex, no shrink */
[liftr-role~="marquee-panel"],
[liftr-role~="marquee-clone"] {
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

Also in `critical.liquid` (Section 6): the **Mask Utility** that powers `liftr-mask`. These rules **already exist** -- never duplicate:

```css
[liftr-mask] {
  /* Gradient-based edge fade on border-box */
  /* Directions set via attribute: left, right, top, bottom */
}
[liftr-mask~="left"]   { --_mask--l: var(--mask--edge); }
[liftr-mask~="right"]  { --_mask--r: var(--mask--edge); }
/* ... etc. */
```

### `core.liftr.css` (@layer components -- the module CSS)

Animation, states, keyframes. These rules **already exist**:

```css
/* Root: block, defaults for speed/direction/duration */
liftr-marquee {
  display: block; position: relative;
  --marquee-enabled: true;
  --marquee-speed: 50;
  --marquee-direction: 1;
  --marquee-duration: 20s;
}

/* Pre-defined fallback */
liftr-marquee:not(:defined) { min-height: 2em; }

/* Viewport: flex + overflow hidden */
[liftr-role~="marquee-viewport"] { display: flex; overflow: hidden; }

/* Axis-specific flex direction */
liftr-marquee[liftr-axis="x"] [liftr-role~="marquee-viewport"] { flex-direction: row; }
liftr-marquee[liftr-axis="y"] [liftr-role~="marquee-viewport"] { flex-direction: column; }

/* Panel + Clone: animation (paused by default) */
[liftr-role~="marquee-panel"],
[liftr-role~="marquee-clone"] {
  display: flex; flex-shrink: 0;
  animation-play-state: paused;
}

/* Axis-specific keyframes */
liftr-marquee[liftr-axis="x"] ... { animation: marquee-x var(--marquee-duration) linear infinite; }
liftr-marquee[liftr-axis="y"] ... { animation: marquee-y var(--marquee-duration) linear infinite; }

/* State: active -> running */
liftr-marquee[liftr-state~="active"] ... { animation-play-state: running; }

/* State: paused -> paused */
liftr-marquee[liftr-state~="paused"] ... { animation-play-state: paused; }

/* State: disabled -> no animation */
liftr-marquee[liftr-state~="disabled"] ... { animation: none; }

/* Keyframes */
@keyframes marquee-x { to { transform: translateX(calc(-100% * var(--marquee-direction))); } }
@keyframes marquee-y { to { transform: translateY(calc(-100% * var(--marquee-direction))); } }

/* Reduced motion */
@media (prefers-reduced-motion: reduce) { animation: none; }
```

### Section CSS (your responsibility)

**Only these things belong in your section/block CSS:**

```css
/* 1. Container query setup + edge mask size */
.my-section_component {
  container: my-section / inline-size;
  --mask--edge: clamp(4rem, 25cqi, 30rem);
}

/* 2. CSS Settings */
.my-section_marquee {
  --marquee-enabled: true;
  --marquee-speed: 60;          /* px/s -- higher = faster */
  --marquee-direction: 1;       /* 1 = forward, -1 = reverse */
}

/* 3. Responsive disable */
@container my-section (min-width: 64rem) {
  .my-section_marquee {
    --marquee-enabled: false;
  }
}

/* 4. Content layout (item gap, sizing) */
.my-section_marquee [liftr-role~="marquee-panel"],
.my-section_marquee [liftr-role~="marquee-clone"] {
  gap: var(--space--large);
}
```

### Summary Table

| Property | critical.liquid | core.liftr.css | Section CSS |
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

`<liftr-marquee>` does **NOT** use `liftr-state="loading"` or `liftr-skeleton`.

- Marquee shows real content immediately (static until JS activates animation)
- FOUC handled by `critical.liquid` (`animation: none !important` until defined)
- `core.liftr.css` sets `animation-play-state: paused` by default -- only `active` state starts it

```liquid
<!-- YES CORRECT: No loading state, no skeleton -->
<liftr-marquee liftr-axis="x">
  ...
</liftr-marquee>

<!-- NO WRONG: Marquee doesn't use skeleton -->
<liftr-marquee liftr-axis="x" liftr-state="loading" liftr-skeleton>
  ...
</liftr-marquee>
```

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
            {% render 'icon', icon: block.settings.icon %}
            {{ block.settings.text }}
          </span>
        {% endfor %}
      </div>
      <div liftr-role="marquee-clone" aria-hidden="true">
        {% for block in section.blocks %}
          <span class="header-usp_item">
            {% render 'icon', icon: block.settings.icon %}
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
  container: header-usp / inline-size;
  --mask--edge: clamp(4rem, 25cqi, 30rem);
}

.header-usp_marquee {
  --marquee-enabled: true;
  --marquee-speed: 40;
}

/* Desktop: disable marquee, show as static flex row */
@container header-usp (min-width: 64rem) {
  .header-usp_marquee {
    --marquee-enabled: false;
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
| `--marquee-direction` | number | `1` | `1` = forward, `-1` = reverse |
| `--mask--edge` | length | `3rem` (:root) | Edge fade distance. Set on `_component`. Recommended: `clamp(4rem, 25cqi, 30rem)` |

**Duration is auto-calculated:** `contentWidth / speed = seconds`  
JS sets `--marquee-duration` on the root element.

**Edge mask** is purely CSS -- set `liftr-mask` in Liquid, `--mask--edge` in Section CSS. The mask utility lives in `critical.liquid` (Section 6). No JS involved.

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
  container: announcement / inline-size;
  --mask--edge: clamp(4rem, 25cqi, 30rem);
}

.announcement_marquee {
  --marquee-enabled: true;
  --marquee-speed: 40;
}

.announcement_marquee [liftr-role~="marquee-panel"],
.announcement_marquee [liftr-role~="marquee-clone"] {
  gap: var(--space--xlarge);
}

@container announcement (min-width: 64rem) {
  .announcement_marquee {
    --marquee-enabled: false;
  }
  /* When disabled: show as centered flex */
  .announcement_marquee [liftr-role~="marquee-viewport"] {
    justify-content: center;
  }
  .announcement_marquee [liftr-role~="marquee-clone"] {
    display: none;
  }
}
```

### Brand Logo Ticker

```css
.brands_component {
  container: brands / inline-size;
  --mask--edge: clamp(4rem, 25cqi, 30rem);
}

.brands_marquee {
  --marquee-enabled: true;
  --marquee-speed: 30;
}

.brands_marquee [liftr-role~="marquee-panel"],
.brands_marquee [liftr-role~="marquee-clone"] {
  gap: var(--space--xxlarge);
  align-items: center;
}

.brands_marquee img {
  height: 2rem;
  width: auto;
}
```

### Reverse Direction

```css
.my-section_marquee {
  --marquee-direction: -1; /* Scrolls right-to-left becomes left-to-right */
}
```

---

## 17. Disabled State Layout

When `--marquee-enabled: false`, JS sets `disabled` state. The clone should be hidden and content displayed as a static row. Handle this in Section CSS:

```css
/* When disabled: hide clone, center content */
@container my-section (min-width: 64rem) {
  .my-section_marquee {
    --marquee-enabled: false;
  }
  .my-section_marquee [liftr-role~="marquee-viewport"] {
    justify-content: center;
  }
  .my-section_marquee [liftr-role~="marquee-clone"] {
    display: none;
  }
}
```

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
- [ ] Container query on parent for responsive disable
- [ ] `--marquee-enabled` in section CSS
- [ ] `--marquee-speed` set (default 50 if omitted)
- [ ] Disabled state hides clone in section CSS
- [ ] `<script src="ui.marquee.js" type="module">` loaded
- [ ] **NO duplicate styles** from critical.liquid or core.liftr.css
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
| Duplicating `overflow: hidden` | Already in critical.liquid and core.liftr.css |
| Duplicating keyframes | Already in core.liftr.css |
| Duplicating `animation-play-state` | Already in core.liftr.css via state selectors |
| Duplicating mask utility CSS | Already in critical.liquid Section 6 -- never redefine `[liftr-mask]` rules |
| Clone visible when disabled | Add `display: none` on clone in disabled media query |
| Content wraps to multiple lines | Items must be flex children, no wrapping |
| Missing `liftr-axis` | Required -- JS reads it; CSS uses it for flex-direction |

---

## 20. Imports

```javascript
// In other modules interacting with marquee
import { ROLES, STATES, EVENTS, PROPERTIES } from './ui.marquee.js';

// Listen for pause/resume
document.addEventListener('liftr:marquee:paused', (e) => {
  const { trigger } = e.detail; // 'hover' | 'visibility' | 'keyboard'
});
```
