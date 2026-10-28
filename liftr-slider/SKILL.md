---
name: liftr-slider
description: Implementation guide for the liftr-slider Web Component in LIFTR v4.9. Use whenever building, configuring, or debugging carousels, sliders, slideshows, or any transform-based slide navigation with touch/swipe, autoplay, dots, progress bars, or infinite loop. Triggers on any mention of liftr-slider, carousel, slideshow, autoplay slider, dot pagination, slide navigation, or swipe-based content cycling within the LIFTR ecosystem. Also use when implementing product carousels, hero sliders, testimonial rotators, or any component that cycles through items with prev/next controls and optional auto-advancement.
---

# liftr-slider -- Implementation Guide

**Element:** `<liftr-slider>`  
**File:** `ui.slider.js`  
**Version:** 4.9.0  
**Category:** UI Module (Web Component)

---

## What It Does

Transform-based carousel/slider with:
- Responsive layout via CSS custom properties (cols, gap, peek)
- Infinite loop with dynamic clones
- Touch/swipe drag navigation (Pointer Events)
- Prev/Next arrow controls (auto-generated or static)
- Dot pagination (auto-generated or existing)
- Progress bar indicator (proportional thumb)
- Autoplay with pause/hover/focus control
- Declarative edge mask via `liftr-mask`
- Responsive enable/disable via CSS Settings
- Full ARIA compliance with live region
- Reduced motion support
- Navigation modes: single (1 slide) or page (all visible)
- FX Set dependent timing (CSS-driven transitions)

---

## 1. CSS Ownership -- What Exists Where

!! **CRITICAL: Do NOT duplicate these styles in Section CSS!**

Three files provide slider styles. Each has a clear responsibility:

### `critical.liquid` (Section 12 -- inlined in `<head>`)

FOUC prevention + item sizing formula. Loaded before JS. These rules **already exist**:

```css
/* Root: position context (overflow: visible implicit, set in ui.slider.css) */
liftr-slider { position: relative; }

/* Viewport: clips content, handles peek */
[liftr-role~="slider-viewport"] {
  overflow: clip;
  padding-right: var(--slider-peek, 0px);
}

/* Panel: flex track */
[liftr-role~="slider-panel"] {
  display: flex;
  gap: var(--slider-gap, 0px);
}

/* Item sizing formula (100cqw-based) */
[liftr-role~="slider-item"] {
  flex: var(--slider-autofit, 1) 0 calc(
    (100cqw - var(--slider-gap, 0px) * (var(--slider-cols, 1) - 1))
    / var(--slider-cols, 1)
  );
  min-width: 0;
}

/* FOUC: Hide non-first items until defined */
liftr-slider:not(:defined) [liftr-role~="slider-item"]:not(:first-child) {
  display: none !important;
}

/* FOUC: Hide nav until defined */
liftr-slider:not(:defined) [liftr-role~="slider-nav"] {
  display: none !important;
}
```

### `core.liftr.css` (@layer components -- the module CSS)

Component behavior, transform, drag, dots, progress, states. These rules **already exist**:

```css
/* Root: display, touch-action, cursor, dot variables */
liftr-slider { display: block; position: relative; touch-action: pan-y pinch-zoom; cursor: grab; ... }

/* Viewport: position context only (overflow + peek padding in critical.liquid) */
[liftr-role~="slider-viewport"] { position: relative; }

/* Panel: transform from CSS vars, transition from FX Set */
[liftr-role~="slider-panel"] {
  transform: translateX(calc(var(--slider-offset) + var(--slider-drag)));
  transition: transform var(--fx-morph-duration) var(--fx-morph-ease);
  will-change: transform;
}

/* Item: pointer-events none when aria-hidden */
[liftr-role~="slider-item"][aria-hidden="true"] { pointer-events: none; }

/* Dots: layout, sizing, active state */
[liftr-role~="slider-nav"] { display: flex; justify-content: center; ... }
[liftr-role~="slider-dot"] { ... }
[liftr-role~="slider-dot"][aria-selected="true"] { ... }

/* Progress bar: track + thumb */
[liftr-role~="slider-progress"] { height: 2px; ... }
[liftr-role~="slider-thumb"] { width: calc(var(--slider-thumb-width) * 100%); ... }

/* States: dragging, disabled, can't scroll */
liftr-slider[liftr-state~="dragging"] { cursor: grabbing; }
liftr-slider[liftr-state~="dragging"] [liftr-role~="slider-panel"] { transition: none; }
liftr-slider[liftr-state~="disabled"] [liftr-role~="slider-panel"] { transform: none; }
liftr-slider:not([liftr-state~="can-scroll"]) [liftr-role~="nav-prev/next/nav/progress"] { display: none; }

/* Accessibility */
@media (prefers-reduced-motion: reduce) { ... transition: none; }
@media (forced-colors: active) { ... border: 2px solid currentColor; }
```

### Section CSS (your responsibility)

**Only these things belong in your section/block CSS:**

```css
/* 1. Container query setup */
.my-section_component { container: my-section / inline-size; }

/* 2. CSS Settings */
.my-section_slider {
  --slider-enabled: true;
  --slider-cols: 4;
  --slider-gap: var(--space--medium);
  --slider-peek: 0%;
  --slider-loop: true;
  --slider-dots: false;        /* false | true | bar */
  --slider-autoplay: false;
  --slider-mode: single;       /* single | all */
  --nav-mode: auto;
  --nav-size: medium;
}

/* 3. Responsive overrides */
@container my-section (max-width: 64rem) {
  .my-section_slider {
    --slider-enabled: true;
    --slider-cols: 2;
  }
}
@container my-section (max-width: 48rem) {
  .my-section_slider {
    --slider-cols: 1;
    --slider-peek: 15%;
  }
}

/* 4. Disable on desktop (show as grid) */
@container my-section (min-width: 64rem) {
  .my-section_slider {
    --slider-enabled: false;
  }
}
```

### Summary Table

| Property | critical.liquid | core.liftr.css | Section CSS |
|----------|:-:|:-:|:-:|
| `overflow: clip` + peek padding (FOUC) | YES | -- | NO never |
| Item sizing formula (cqw) | YES | -- | NO never |
| Hide non-first items (FOUC) | YES | -- | NO never |
| `display: block` | -- | YES | NO never |
| Transform + transition | -- | YES | NO never |
| Drag states (cursor, transition:none) | -- | YES | NO never |
| Disabled state reset | -- | YES | NO never |
| Dots styling | -- | YES | NO never |
| Progress bar styling | -- | YES | NO never |
| Nav visibility (can-scroll) | -- | YES | NO never |
| Mask utility | YES (Section 5) | -- | NO never |
| Container query | -- | -- | YES yours |
| `--slider-cols` | -- | -- | YES yours |
| `--slider-gap` | -- | -- | YES yours |
| `--slider-peek` | -- | -- | YES yours |
| `--slider-enabled` | -- | -- | YES yours |
| `--slider-loop/dots/autoplay/mode` | -- | -- | YES yours |
| Nav settings (`--nav-*`) | -- | -- | YES yours |

---

## 2. HTML Template (Liquid)

### Standard (Horizontal Carousel)

```liquid
<div class="my-section_component">
  <liftr-slider
    class="my-section_slider"
    liftr-axis="x"
  >
    <div liftr-role="slider-viewport" liftr-mask="left right">
      <div liftr-role="slider-panel">
        {% for block in section.blocks %}
          <div liftr-role="slider-item">
            {% render 'product-card', product: block.settings.product %}
          </div>
        {% endfor %}
      </div>
    </div>
  </liftr-slider>
</div>

<script src="{{ 'ui.slider.js' | asset_url }}" type="module"></script>
```

### With Static External Navigation

```liquid
<div class="my-section_component">
  <div class="section-header">
    <h2>{{ section.settings.title }}</h2>
    <div class="nav-buttons">
      <button liftr-target="{{ section.id }}-slider" liftr-role="slider-prev" type="button"><</button>
      <button liftr-target="{{ section.id }}-slider" liftr-role="slider-next" type="button">></button>
    </div>
  </div>

  <liftr-slider
    class="my-section_slider"
    liftr-id="{{ section.id }}-slider"
    liftr-axis="x"
  >
    <div liftr-role="slider-viewport" liftr-mask="left right">
      <div liftr-role="slider-panel">
        {% for block in section.blocks %}
          <div liftr-role="slider-item">{{ block.settings.content }}</div>
        {% endfor %}
      </div>
    </div>
  </liftr-slider>
</div>
```

### With Existing Dots + Pause Button

```liquid
<liftr-slider
  class="my-section_slider"
  liftr-axis="x"
>
  <div liftr-role="slider-viewport">
    <div liftr-role="slider-panel">
      {% for block in section.blocks %}
        <div liftr-role="slider-item">{{ block.settings.content }}</div>
      {% endfor %}
    </div>
  </div>

  <div liftr-role="slider-nav" role="tablist" aria-label="Slide controls">
    {% for block in section.blocks %}
      <button liftr-role="slider-dot" type="button" role="tab"
        aria-selected="{% if forloop.first %}true{% else %}false{% endif %}"
        aria-label="{{ 'slider.go_to_slide' | t: index: forloop.index }}"
        data-page="{{ forloop.index0 }}"
        data-start-index="{{ forloop.index0 }}">
      </button>
    {% endfor %}
  </div>

  <button liftr-role="slider-pause" type="button" aria-label="{{ 'slider.pause' | t }}">
    {% render 'icon-pause' %}
  </button>
</liftr-slider>
```

### Hero Slider (Full-Width, Autoplay)

```liquid
<div class="hero_component">
  <liftr-slider
    class="hero_slider"
    liftr-axis="x"
  >
    <div liftr-role="slider-viewport">
      <div liftr-role="slider-panel">
        {% for block in section.blocks %}
          <div liftr-role="slider-item">
            {{ block.settings.image | image_url: width: 1920 | image_tag }}
          </div>
        {% endfor %}
      </div>
    </div>
  </liftr-slider>
</div>
```

```css
.hero_component { container: hero / inline-size; }
.hero_slider {
  --slider-enabled: true;
  --slider-cols: 1;
  --slider-loop: true;
  --slider-autoplay: true;
  --slider-dots: bar;
  --nav-mode: auto;
  --nav-position: inside;
}
```

---

## 3. Required Attributes

### On `<liftr-slider>` (Root)

| Attribute | Required | Values | Description |
|-----------|----------|--------|-------------|
| `liftr-axis="x"` | **Yes** | `x` | Scroll/slide axis (always horizontal) |
| `class` | **Yes** | Section class | CSS Settings target |
| `liftr-id` | Optional | String | Required for static/external navigation |

### On Children (Roles)

| Role | Required | Element | Description |
|------|----------|---------|-------------|
| `slider-viewport` | **Yes** | `<div>` | Viewport (clip + mask target) |
| `slider-panel` | **Yes** | `<div>` | Transform track (flex container) |
| `slider-item` | **Yes** | `<div>` | Individual slide |

### Navigation Roles (Optional)

| Role | Mode | Description |
|------|------|-------------|
| `slider-prev` | auto/static | Previous button |
| `slider-next` | auto/static | Next button |
| `slider-nav` | auto/static | Dots container |
| `slider-dot` | auto/static | Individual dot button |
| `slider-pause` | static only | Autoplay pause toggle |
| `slider-live` | static only | ARIA live region |

---

## 4. DOM Structure

```
<liftr-slider liftr-axis="x">             <- Root (overflow: visible, nav never clipped)
  <div liftr-role="slider-viewport">     <- Viewport (overflow: clip, padding-right=peek)
    <div liftr-role="slider-panel">      <- Transform track (no overflow, movement via translateX)
      [clones-start]                     <- Loop clones (JS-generated)
      <div liftr-role="slider-item">     <- Original slides
      [clones-end]                       <- Loop clones (JS-generated)
    </div>
  </div>
  [auto-generated nav buttons]           <- Root children — never clipped
  [auto-generated dots/progress]         <- Dots mode "true"/"bar"
  [auto-generated live region]           <- ARIA announcements
</liftr-slider>
```

---

## 5. CSS Settings (Section CSS)

### Layout Variables

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `--slider-enabled` | bool | `true` | Enable/disable slider |
| `--slider-cols` | number | `1` | Visible items |
| `--slider-gap` | px | `0px` | Gap between items |
| `--slider-peek` | % | `0%` | Visible portion of next item |
| `--slider-autofit` | number | `1` | Flex-grow for items (critical.liquid) |

### Behavior Variables (CSS Schema)

| Property | Type | Values | Default | Description |
|----------|------|--------|---------|-------------|
| `--slider-loop` | bool | `true`/`false` | `true` | Infinite loop |
| `--slider-autoplay` | bool | `true`/`false` | `false` | Auto-advance |
| `--slider-dots` | string | `false`/`true`/`bar` | `false` | Pagination type |
| `--slider-mode` | string | `single`/`all` | `single` | Navigation mode |

### Navigation Controls

```css
.my-section_slider {
  --nav-mode: auto;        /* false | auto | static */
  --nav-size: medium;      /* small | regular | medium | large */
  --nav-icon: angle;       /* angle | arrow | chevron */
  --nav-theme: light;      /* light | dark */
  --nav-style: round;      /* plain | square | round */
  --nav-position: inside;  /* inside | outside | edge */
}
```

### Navigation Mode

| Mode | Behavior |
|------|----------|
| `single` | 1 slide per prev/next click |
| `all` | All visible slides per click (page-based) |

### NAV Size Tokens

| Size | Button | Icon | Use Case |
|------|--------|------|----------|
| `small` | 1.5rem | 0.875rem | Compact UI, mobile |
| `regular` | 2rem | 1rem | Default alternative |
| `medium` | 2.5rem | 1.25rem | Default, most cases |
| `large` | 3rem | 1.5rem | Hero sections |

### NAV Position (auto mode only)

| Position | Description |
|----------|-------------|
| `inside` | Overlapping content |
| `outside` | Outside module bounds |
| `edge` | Centered on module edge (50% overlap) |

---

## 6. Output Attributes (Set by JS)

### liftr-state

| Token | Meaning |
|-------|---------|
| `disabled` | Slider deactivated (no transform, no controls) |
| `dragging` | User is currently dragging |
| `can-scroll` | Content overflows, navigation possible |

### liftr-nav

Space-delimited: `"auto medium angle light round inside"` (auto mode only)

### liftr-active (on items)

Set on the current active slide item.

### liftr-mask (on viewport)

For non-loop: toggles `left`/`right` based on position. Loop mode doesn't toggle mask.

---

## 7. CSS Custom Properties (Set by JS)

| Property | On Element | Description |
|----------|-----------|-------------|
| `--slider-offset` | slider-panel | Current slide position (px) |
| `--slider-drag` | slider-panel | Live drag offset (px) |
| `--slider-cols` | :root/computed | Visible column count |
| `--slider-progress` | slider-progress | Thumb position (0-1) |
| `--slider-thumb-width` | slider-progress | Thumb width ratio (0.08-1) |

---

## 8. JavaScript Configuration (DEFAULTS)

Static config only. CSS-driven keys (loop, mode, autoplay, dots) live
exclusively in CSS_SCHEMA -- see CSS Settings in Section 5.

```javascript
{
  initialSlide: 0,           // Starting slide index
  autoplayInterval: 5000,    // ms between slides
  pauseOnHover: true,        // Pause autoplay on mouse hover
  pauseOnFocus: true,        // Pause autoplay on focus inside
  swipeThreshold: 50,        // px minimum for swipe detection
  swipeTimeout: 300          // ms maximum for swipe gesture
}
```

Override via `settings.modules.slider` in theme settings JSON.

---

## 9. Module Constants

```javascript
const ROLES = Object.freeze({
  VIEWPORT:   'slider-viewport',
  ITEM:       'slider-item',
  PREV:       'slider-prev',
  NEXT:       'slider-next',
  DOT:        'slider-dot',
  PROGRESS:   'slider-progress',
  PAUSE:      'slider-pause',
  LIVE:       'slider-live',
  THUMB:      'slider-thumb',
  NAV:        'slider-nav',
  PANEL:      'slider-panel'
});

const STATES = Object.freeze({
  CAN_SCROLL: 'can-scroll',
  DRAGGING:   'dragging',
  DISABLED:   'disabled'
});

const EVENTS = Object.freeze({
  CHANGED:  'changed',
  ENABLED:  'enabled',
  DISABLED: 'disabled'
});

const SETTINGS = Object.freeze({});
```

---

## 10. Events

### Emitted

| Event | Detail | When |
|-------|--------|------|
| `liftr:slider:changed` | `{ index, total, page, pageCount }` | After slide navigation completes |
| `liftr:slider:enabled` | `{ index }` | When slider becomes enabled |
| `liftr:slider:disabled` | `{}` | When slider becomes disabled |

---

## 11. Public API

```javascript
const slider = document.querySelector('liftr-slider');

// Navigation
slider.goToSlide(2);          // Go to slide index 2
slider.goToSlide(0, false);   // Jump without animation
slider.prev();                // Previous slide/page
slider.next();                // Next slide/page

// Autoplay
slider.pauseAutoplay();
slider.resumeAutoplay();
slider.toggleAutoplay();

// Read state
slider.currentIndex;       // number (0-based real index)
slider.totalSlides;        // number
slider.maxIndex;           // number
slider.currentPage;        // number (for mode: 'all')
slider.pageCount;          // number
slider.perMove;            // number (1 or visibleCount)
slider.isDisabled;         // boolean
slider.isAutoplayPaused;   // boolean
slider.canScroll;          // boolean (content overflows)
```

---

## 12. Drag/Swipe Behavior

- **Pointer Events** based (works on touch + mouse)
- **Two-phase drag:** Track pointer first, commit after 10px threshold
- **Interactive elements:** Drag starts on buttons/links after 10px movement, click suppressed after drag
- **Swipe detection:** Fast gesture (< 300ms, > 50px) -> single slide advance
- **Slow drag:** Proportional -- slides moved = distance / step width
- **Vertical scroll preserved:** If vertical movement > horizontal, drag is cancelled
- **Click suppression:** Flag-based, resets on next pointerdown

---

## 13. Infinite Loop (Clone System)

- Clones are created dynamically based on visible count
- Clone count = `min(visibleCount, totalSlides)`
- Prepended (start clones) and appended (end clones)
- After loop-wrap animation: instant jump to real position (no transition)
- Clones get `liftr-clone="start|end"`, `aria-hidden`, `inert`
- Visible clones at edges get `aria-hidden="false"` for pointer-events (v4.3.6)
- Clones are removed and rebuilt on resize if visible count changes

---

## 14. Keyboard Navigation

| Key | Action |
|-----|--------|
| ArrowLeft | Previous slide/page |
| ArrowRight | Next slide/page |
| Home | Go to first slide |
| End | Go to last slide |

---

## 15. Section CSS Examples

### Product Carousel (Mobile Peek -> Desktop Grid)

```css
.products_component { container: products / inline-size; }

.products_slider {
  --slider-enabled: true;
  --slider-cols: 1;
  --slider-peek: 15%;
  --slider-gap: var(--space--small);
  --slider-loop: false;
  --slider-dots: true;
  --nav-mode: auto;
  --nav-size: medium;
  --nav-position: inside;
}

@container products (min-width: 48rem) {
  .products_slider {
    --slider-cols: 2;
    --slider-peek: 0%;
    --slider-gap: var(--space--medium);
  }
}

@container products (min-width: 64rem) {
  .products_slider {
    --slider-enabled: false;
    --slider-cols: 4;
  }
}
```

### Hero Slideshow (Full-Width, Autoplay, Progress Bar)

```css
.hero_component { container: hero / inline-size; }

.hero_slider {
  --slider-enabled: true;
  --slider-cols: 1;
  --slider-loop: true;
  --slider-autoplay: true;
  --slider-dots: bar;
  --nav-mode: auto;
  --nav-position: inside;
  --nav-theme: light;
}
```

### Testimonial Slider (Page Mode)

```css
.testimonials_component { container: testimonials / inline-size; }

.testimonials_slider {
  --slider-enabled: true;
  --slider-cols: 3;
  --slider-gap: var(--space--medium);
  --slider-mode: all;
  --slider-dots: true;
  --nav-mode: false;
}

@container testimonials (max-width: 48rem) {
  .testimonials_slider {
    --slider-cols: 1;
    --slider-mode: single;
  }
}
```

### Custom Mask Size

```css
.my-section_slider [liftr-role~="slider-viewport"] {
  --mask-edge: 5rem; /* Override default 3rem from critical.liquid */
}
```

---

## 16. Checklist

Before shipping a `<liftr-slider>` implementation:

- [ ] `slider-viewport`, `slider-panel`, `slider-item` roles in DOM
- [ ] `liftr-axis="x"` on root element
- [ ] Container query on parent for responsive layout
- [ ] `--slider-enabled` in section CSS
- [ ] `--slider-cols` and `--slider-gap` in section CSS
- [ ] `--slider-peek` if partial next-item visibility desired
- [ ] Navigation mode chosen (`--nav-mode`)
- [ ] External buttons have `liftr-target` matching `liftr-id`
- [ ] `<script src="ui.slider.js" type="module">` loaded
- [ ] **NO duplicate styles** from critical.liquid or core.liftr.css
- [ ] **NO padding/margin on `[liftr-role~="slider-viewport"]`** -- owned by Peek system in critical.liquid
- [ ] Only layout variables and CSS Settings in section CSS
- [ ] `liftr-mask` on viewport (if edge fade desired, non-loop only)

---

## 17. Common Mistakes

| Mistake | Fix |
|---------|-----|
| `liftr-axis` on slider-panel instead of root | Move to `<liftr-slider liftr-axis="x">` -- must be on same element as `liftr-nav` for nav positioning |
| Duplicating `overflow: clip` | Already in critical.liquid |
| Duplicating flex/gap on panel | Already in critical.liquid |
| Duplicating item sizing formula | Already in critical.liquid |
| Writing transform CSS | Already in core.liftr.css |
| Writing drag state CSS | Already in core.liftr.css |
| Writing dot styles | Already in core.liftr.css |
| Setting `--slider-cols` without container | Items use `100cqw` -- needs container context |
| Mask on viewport in loop mode | Mask doesn't toggle in loop (by design) |
| External buttons without `liftr-id` | Static mode needs `liftr-id` + `liftr-target` match |
| Autoplay without pause button | Provide `slider-pause` role for accessibility |
| Setting padding/margin on `slider-viewport` in section CSS | Owned by Peek system in critical.liquid |

---

## 18. Imports

```javascript
// In other modules interacting with slider
import { ROLES, STATES, EVENTS, PROPERTIES } from './ui.slider.js';

// Listen for slide changes
document.addEventListener('liftr:slider:changed', (e) => {
  const { index, total, page, pageCount } = e.detail;
});
```
