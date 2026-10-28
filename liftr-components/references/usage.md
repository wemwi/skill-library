# LIFTR Components — Markup & Styling Guide

**Scope:** How to use LIFTR Web Components in Liquid templates.  
**Not covered here:** JS internals (see `core.md`, liftr-foundation), individual JS APIs (see the component references, e.g. `slider.md`).

---

## 1. HTML Structure Pattern

Every LIFTR component follows the same structure:

```liquid
{%- comment -%} Container: Utility container + Section/Block Wrapper {%- endcomment -%}
<div class="container-large">
  <div class="featured-products_component">

    {%- comment -%} Custom Element: The Component {%- endcomment -%}
    <liftr-slider class="featured-products_slider" liftr-axis="x"
      aria-label="{{ t_section_name }} ({{ 'components.slider.name' | t }})">

      {%- comment -%} Viewport → Panel → Items {%- endcomment -%}
      <div liftr-role="slider-viewport">
        <div liftr-role="slider-panel">
          {%- for product in collection.products -%}
            <div liftr-role="slider-item">
              {% render 'product', product: product %}
            </div>
          {%- endfor -%}
        </div>
      </div>

      {%- comment -%} Nav Controls: generated in auto mode; write them only for static mode {%- endcomment -%}

    </liftr-slider>
  </div>
</div>
```

### Container Naming Convention

```
.{context}_{module}
```

| Example | Context | Module |
|---------|---------|--------|
| `.featured-products_slider` | featured-products | slider |
| `.aside-cart_recommendations` | aside-cart | recommendations |
| `.store_accordion` | store | accordion |
| `.filter_accordion` | filter | accordion |

The **Consumer-Klasse** (e.g. `.featured-products_slider`) lives directly on the Custom Element. CSS Settings target this class via compound selector: `liftr-slider.featured-products_slider { }`.

### Key Rules

- Custom element (`<liftr-slider>`) is the component — no `liftr-component` attribute
- Consumer-Klasse on the Custom Element is the CSS Settings scope — never use `[liftr-id]` for styling
- Compound selector `liftr-{module}.{context}_{module}` for CSS Settings
- Roles are space-separated: `liftr-role="slider-prev nav-control nav-prev"`
- States are space-separated, set by JS: `liftr-state="active can-next"`

---

## 2. CSS Settings — Per Module Reference

CSS Settings let sections configure component behavior responsively via CSS custom properties. JS reads these values through `watchSettings()`.

### How It Works

```css
/* Section CSS: Configure the component via compound selector */
liftr-slider.featured-products_slider {
  --slider-enabled: true;
  --slider-cols: 4;
  --slider-gap: var(--space--medium);
}

/* Responsive via unnamed Container Query (Desktop-First) */
@container (max-width: 48rem) {
  liftr-slider.featured-products_slider {
    --slider-cols: 2;
    --slider-gap: var(--space--small);
  }
}

@container (max-width: 30rem) {
  liftr-slider.featured-products_slider {
    --slider-cols: 1;
  }
}
```

### Module Reference

#### liftr-slider

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `--slider-enabled` | bool | `true` (unset = enabled) | Enable/disable |
| `--slider-cols` | number | 1 | Visible columns (read by CSS item formula) |
| `--slider-gap` | REM | `0px` | Gap between items (read by CSS) |
| `--slider-peek` | REM | `0px` | Peek of next item (read by CSS) |
| `--slider-loop` | bool | `true` | Infinite loop |
| `--slider-autoplay` | bool | `false` | Auto-advance |
| `--slider-dots` | string | `"false"` | Dot navigation: `"false"`, `"true"`, `"bar"` |
| `--slider-mode` | string | `"single"` | `"single"` or `"all"` |

Config: `nav: true`, `resize: true`

#### liftr-scroll

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `--scroll-enabled` | bool | `true` (unset = enabled) | Enable/disable |

No CSS_SCHEMA — scroll has no configurable CSS properties beyond enabled.  
Config: `nav: true`, `resize: true`

#### liftr-accordion

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `--accordion-enabled` | bool | `true` (unset = enabled) | Enable/disable |
| `--accordion-mode` | string | "closed" | Initial state: "closed", "highlight", "sheet" |
| `--accordion-exclusive` | bool | true | Only one open at a time |
| `--accordion-icon` | string | "angle" | Icon type: "angle", "plus", "chevron", "arrow", "bell", "none" |
| `--accordion-size` | string | "regular" | Size: "xsmall", "small", "regular", "medium", "large" |

Config: no `nav`, no `resize`

#### liftr-panel

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `--panel-enabled` | bool | `true` (unset = enabled) | Enable/disable |
| `--panel-mode` | string | "popup" | Mode: "popup", "sheet", "sidebar-left", "sidebar-right", "dropdown", "menu" |

Config: `resize: true`

#### liftr-marquee

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `--marquee-enabled` | bool | `true` (unset = enabled) | Enable/disable |
| `--marquee-speed` | number | 50 | Scroll speed (px/s) |
| `--marquee-direction` | string | "forward" | Direction: "forward", "reverse" |

Config: `resize: true`

#### liftr-header

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `--header-enabled` | bool | `true` (unset = enabled) | Enable/disable |
| `--header-hide-distance` | number | 80 | Scroll px before hide |
| `--header-dwell-time` | number | 300 | Sustained scroll ms |
| `--header-top-zone` | number | 100 | Always-visible zone px |

Config: `resize: true`

#### liftr-tabs

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `--tabs-enabled` | bool | `true` (unset = enabled) | Enable/disable |

No CSS_SCHEMA.

#### liftr-list-sort

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `--list-sort-label` | string | "label" | Label source: "label" (textContent) or "field" (liftr-field attr) |

Read via direct `getComputedStyle`, not watchSettings.

#### Modules WITHOUT CSS Settings

These modules have no `watchSettings` and are always active:

- `liftr-copyclip` — always enabled
- `liftr-list` — always enabled
- `liftr-list-filter` — always enabled
- `liftr-range` — always enabled (disabled via `liftr-requires`)

`liftr-sticky` does use `watchSettings` (`--sticky-enabled`, `--sticky-mode`) → `sticky.md`.

---

## 3. Container Query Setup

Container classes, CQ scale and CQ rules (unnamed, `max-width`, flat) → `css-system.md` (liftr-foundation),
section "Responsive". Module-specific: the container class sits on a parent wrapper, never on the Custom Element.

---

## 4. NAV System

Components with `nav: true` in their watchSettings config get automatic navigation controls.

### NAV Roles

| Role | Element | Purpose |
|------|---------|---------|
| `nav-prev` | `<button>` | Previous navigation |
| `nav-next` | `<button>` | Next navigation |
| `slider-dot` | `<button>` | Dot pagination (slider only, module role — see `slider.md`) |
| `nav-control` | Any | Generic nav element (visibility group) |

### NAV CSS Settings

Values, defaults and the `liftr-nav` output → `watch-settings.md` (liftr-foundation), section "NAV Control System".

### NAV HTML

```liquid
<liftr-scroll class="store-list_scroll" liftr-axis="x">
  <div liftr-role="scroll-viewport">
    <div liftr-role="scroll-panel">
      {%- comment -%} Content {%- endcomment -%}
    </div>
  </div>

  <button liftr-role="nav-prev nav-control" aria-label="{{ 'components.scroll.button.prev' | t }}">
    {% render 'icon', id: 'angle-left' %}
  </button>
  <button liftr-role="nav-next nav-control" aria-label="{{ 'components.scroll.button.next' | t }}">
    {% render 'icon', id: 'angle-right' %}
  </button>
</liftr-scroll>
```

### NAV CSS Settings (Section)

```css
liftr-scroll.store-list_scroll {
  --scroll-enabled: true;
  --nav-mode: auto;
  --nav-size: medium;
  --nav-icon: angle;
  --nav-position: inside;
}
```

### External NAV Buttons (Static Mode)

Static mode supports buttons **outside** the module element, linked via `liftr-target`:

```html
<!-- Buttons in header, outside slider -->
<div class="section-header">
  <h2>Recommendations</h2>
  <div class="nav-buttons">
    <button liftr-target="my-slider" liftr-role="slider-prev" aria-label="Previous">
    <button liftr-target="my-slider" liftr-role="slider-next" aria-label="Next">
  </div>
</div>

<liftr-slider liftr-id="my-slider" class="reco_slider">
  ...
</liftr-slider>
```

**Requirements:**
- Module MUST have `liftr-id`
- Button MUST have `liftr-target` matching that ID
- Button MUST have `liftr-role` with module-specific role
- JS automatically applies `liftr-nav` settings to external buttons

### NAV CSS Architecture (in core.liftr.css, `@layer modules`)

```css
/* 1. BASE: tokens on the element carrying liftr-nav (root in auto mode, button in static mode) */
[liftr-nav] { --_nav-icon-size: var(--icon-size--regular); --_nav-size: calc(var(--_nav-icon-size) * 2); }
[liftr-nav~="medium"] { --_nav-icon-size: var(--icon-size--regular); }

/* 2. CONTROL: size, shape, colors, icon via ::before mask */
[liftr-role~="nav-control"] { width: var(--_nav-size, 2.5rem); height: var(--_nav-size, 2.5rem); }

/* 3. MODULE-SPECIFIC: positioning only */
liftr-slider [liftr-role~="nav-prev"] { /* ... */ }
```

External buttons receive `liftr-nav` attribute from JS -- size/icon/theme work automatically. Section CSS only handles **positioning**:

```css
.section-header [liftr-role~="nav-control"] {
  position: relative; /* Override absolute from base */
}
```

Size tokens → `watch-settings.md` (liftr-foundation).

### NAV Position (mode: auto only)

| Position | Description |
|----------|-------------|
| `inside` | Overlapping content |
| `outside` | Outside module bounds |
| `edge` | Centered on module edge (50% overlap) |

### NAV Accessibility

```html
<button liftr-role="slider-prev nav-control nav-prev"
  type="button"
  aria-label="Previous slide"
  aria-disabled="false">
```

States: `aria-disabled="true"` (reduced opacity), `:focus-visible` (outline). Keyboard handled by module.

---

## 5. Skeleton & FOUC

Which modules need `core.critical.liquid` rules and when to use `liftr-state="loading"` +
`liftr-skeleton="true"` → `css-system.md` (liftr-foundation), section "FOUC / Critical CSS".
Short version: slider, accordion, scroll, marquee and panel are FOUC-safe via `:not(:defined)` rules —
no skeleton needed. Each component reference lists the critical rules that already exist for it.

---

## 7. CSS File Ownership

File and layer map → `css-system.md` (liftr-foundation). Module mechanics (overflow, transforms, state
visibility, NAV, `@property`) live in `core.liftr.css` or `ui.{module}.css` — both `@layer modules`.
Visual component styling lives in `core.components-critical.css` / `core.components.css` (`@layer components`).

### What Lives in Section CSS

Section CSS only handles:

- **CSS Settings** (via compound selector on Custom Element)
- **Responsive breakpoints** (unnamed Container Queries)
- **Layout** (grid, padding, margins)
- **Visual design** (colors, fonts, borders, shadows)

**Never duplicate in section CSS:**
- Component structural rules (overflow, positioning)
- State-based visibility (`[liftr-state~="open"]`)
- NAV arrow styles
- FX animation classes
- Mask gradient definitions

---

## 8. JS-Written CSS Properties

These properties are set by JS and can be read by CSS for styling:

### Per Module

| Module | Property | Type | Purpose |
|--------|----------|------|---------|
| slider | `--slider-offset` | px | Current slide transform offset |
| slider | `--slider-drag` | px | Drag offset during interaction |
| slider | `--slider-cols` | number | Computed visible columns |
| slider | `--slider-progress` | 0–1 | Slide progress |
| slider | `--slider-thumb-width` | % | Progress thumb width |
| scroll | `--scroll-progress-x` | 0–1 | Horizontal scroll progress |
| scroll | `--scroll-progress-y` | 0–1 | Vertical scroll progress |
| panel | `--panel-origin` | CSS value | Transform origin |
| panel | `--panel-slide` | px | Slide offset |
| panel | `--panel-drag-y` | px | Drag-to-close offset |
| marquee | `--marquee-duration` | s | Computed animation duration |
| header | `--header-progress` | 0–1 | Page scroll progress |
| range | `--range-percent` | % | Current value as percentage |
| range | `--range-value` | number | Current raw value |

### Usage in CSS

```css
/* Progress bar fill based on slider progress */
.slider_progress-fill {
  transform: scaleX(var(--slider-progress, 0));
}

/* Scroll mask based on scroll progress */
liftr-scroll::after {
  opacity: var(--scroll-progress-x, 0);
}
```

---

## 9. Attributes Quick Reference

### Set in Liquid (Static)

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `liftr-id` | JS targeting | `liftr-id="cart-sidebar"` |
| `liftr-role` | Element roles | `liftr-role="slider-item"` |
| `liftr-target` | Reference to liftr-id | `liftr-target="store-list"` |
| `liftr-axis` | Scroll/slide direction | `liftr-axis="x"` |
| `liftr-field` | Filter/sort field | `liftr-field="opening"` |
| `liftr-value` | Filter/sort value | `liftr-value="open"` |
| `liftr-merge` | List item merge | `liftr-merge="add"` |
| `liftr-persist` | Exclude from clear | `liftr-persist` |
| `liftr-requires` | Dependency | `liftr-requires="postal"` |
| `liftr-skeleton` | Skeleton target | `liftr-skeleton="true"` |
| `liftr-state="loading"` | Initial loading | Only on skeleton components |

### Set by JS (Dynamic) — Don't Set in Liquid

| Attribute | Purpose |
|-----------|---------|
| `liftr-state` | State tokens (except initial "loading") |
| `liftr-nav` | NAV configuration tokens |
| `liftr-settings` | Output config tokens |
| `liftr-mask` | Overflow fade mask directions |

---

## 10. Common Mistakes

| Mistake | Fix |
|---------|-----|
| CSS Settings via descendant: `.section liftr-slider { }` | Use compound selector: `liftr-slider.context_slider { }` |
| CSS Settings on `[liftr-id]` selector | Use compound selector with Consumer-Klasse |
| Double-dash module properties: `--slider--cols` | Single-dash: `--slider-cols` |
| Double-dash on enabled: `--slider--enabled` | Single-dash: `--slider-enabled` |
| Duplicating `overflow: hidden` in section CSS | Already in `core.liftr.css` / `ui.{module}.css` |
| Duplicating nav arrow styles | Already in `core.liftr.css` |
| Duplicating state visibility rules | Already in `core.liftr.css` / `ui.{module}.css` |
| Setting `liftr-state` in Liquid (except "loading") | Let JS manage states |
| Setting `liftr-nav` in Liquid | Let JS manage nav |
| Using named containers on section elements | Use utility container class (`container-large` etc.) |
| Using `@container style(...)` style queries | Use unnamed `@container (max-width: ...)` |
| Using `min-width` in Container Queries | Desktop-First: always `max-width` |
| Missing utility container class on parent | Required for Container Queries |
| Gap/peek values in px (unitless numbers) | Use REM values or `var(--space--*)` tokens |
| Missing `liftr-axis` on scroll/slider | Required for CSS direction rules |
| Missing aria-label on nav buttons | Required for accessibility |
| Using `liftr-component` attribute | Removed — the custom element IS the component |
| `liftr-skeleton` without value | Always use `liftr-skeleton="true"` |

---

## 11. State Tokens Reference

`liftr-state` is space-separated. JS manages all tokens except the initial `loading` (set in Liquid).

### Module States

| Token | Meaning |
|-------|---------|
| `loading` | Component loading (FOUC prevention — set in Liquid) |
| `active` | Component active/enabled |
| `disabled` | Component disabled |
| `paused` | Animation/autoplay paused |
| `dragging` | User is dragging |

### Opening States

| Token | Meaning |
|-------|---------|
| `open` | Currently open |
| `closed` | Currently closed |
| `opening` | Transitioning to open |
| `closing` | Transitioning to closed |

### Navigation States

| Token | Meaning |
|-------|---------|
| `can-prev` | Can navigate backward |
| `can-next` | Can navigate forward |
| `can-scroll` | Content is scrollable |
| `at-start` | At beginning |
| `at-end` | At end |

### Feature Flags

| Token | Meaning |
|-------|---------|
| `has-distance` | Distance data available |
| `has-schedule` | Schedule data available |

### Prefixed States (Exclusive — Only One Active)

**Distance:** `distance-near` (<5km) · `distance-mid` (5–15km) · `distance-far` (15–50km) · `distance-remote` (>50km) · `distance-unknown`

**Timer:** `timer-ok` · `timer-soon` · `timer-urgent` · `timer-expired`

**Summary:** `summary-open` · `summary-closed` · `summary-opening` · `summary-closing`

### CSS Usage

```css
/* Module state */
liftr-slider[liftr-state~="active"] { }
liftr-slider[liftr-state~="dragging"] { }

/* Opening state */
liftr-accordion[liftr-state~="open"] { }

/* Navigation state */
liftr-scroll[liftr-state~="can-next"] [liftr-role~="nav-next"] { display: flex; }

/* Prefixed state */
liftr-store[liftr-state~="distance-near"] { --_status: var(--color-global--success); }
liftr-delivery[liftr-state~="timer-urgent"] { --_status: var(--color-global--warning); }
```
