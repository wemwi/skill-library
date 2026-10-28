# LIFTR Effects Guide

**File:** `assets/core.fx.css` — `@layer states` (keyframes outside the layer). Loaded in `snippets/core.liftr.liquid` unless `settings.fx_timing == 'none'`.

---

## Architecture

Sets control **timing and easing only** -- not animation type or clip-path. Every effect has one animation, the set determines speed and feel.

```html
<body liftr-fx="smooth">
<a class="nav-link fx-hover-primary">Shop</a>
```

### Sets

| Set | Tempo | Duration | Ease | Perception |
|-----|-------|----------|------|------------|
| `swift` | Fast | 150ms | `--ease--snappy` | Direct, functional |
| `smooth` | Medium | 280ms | `--ease--out` | Natural, balanced |
| `gentle` | Slow | 400ms | `--ease--smooth` | Luxurious, considered |

### What Sets Control

Two core variables + derived:

```css
[liftr-fx="swift"]  { --fx-duration: 150ms; --fx-ease: var(--ease--snappy); }
[liftr-fx="smooth"] { --fx-duration: 280ms; --fx-ease: var(--ease--out); }
[liftr-fx="gentle"] { --fx-duration: 400ms; --fx-ease: var(--ease--smooth); }

/* Derived (once, not per set) */
:where([liftr-fx]) {
  --fx-duration-fast: calc(var(--fx-duration) * 0.5);
  --fx-duration-long: calc(var(--fx-duration) * 1.5);
  --fx-duration-exit: calc(var(--fx-duration) * 0.65);
}
```

Additional per-set variables: `--fx-hover-fill` (opacity varies), `--fx-ambient-duration/-ease/-intensity`, `--fx-notification-stagger`.

Forwarded aliases for JS consumers: `--fx-enter-duration`, `--fx-exit-duration`, `--fx-loading-exit-duration`, `--fx-morph-duration`, etc. -- all derived from `--fx-duration`.

### Theme Setting

`config/settings_schema.json`:

```json
{
  "type": "select",
  "id": "fx_timing",
  "label": "t:theme_settings.label.fx_timing",
  "options": [
    { "value": "swift", "label": "t:theme_settings.option.fx_timing.swift" },
    { "value": "smooth", "label": "t:theme_settings.option.fx_timing.smooth" },
    { "value": "gentle", "label": "t:theme_settings.option.fx_timing.gentle" }
  ],
  "default": "smooth"
}
```

`layout/theme.liquid`:

```liquid
{%- liquid
  assign fx_timing = settings.fx_timing
-%}
<body class="page-wrapper" liftr-fx="{{ fx_timing }}">
```

---

## Variable Naming

```
--fx-{context}-{property}[-{modifier}]
```

| Context | Purpose |
|---------|---------|
| `hover` | Hover fill effects |
| `enter` | Enter animations |
| `exit` | Exit animations |
| `loading` | Loading/result states |
| `notification` | Toast/alert feedback |
| `ambient` | Continuous background effects |
| `morph` | Layout/state transitions |

---

## Hover Effects

One clip-path (Wipe Right) for all sets. No set-specific selectors.

### Element Mapping

| Element | Class |
|---------|-------|
| Nav links, primary buttons, cards | `fx-hover-primary` |
| Secondary/ghost buttons, tabs, breadcrumbs | `fx-hover-secondary` |
| Footer links, social icons, utility links | `fx-hover-muted` |
| Explicit opt-out | `fx-none` |

### Classes

**`fx-hover-primary`** -- Wipe Right
Main interactions. `::before` with `clip-path: inset(0 100% 0 0)` to `inset(0)` on hover.

```html
<a class="nav-link fx-hover-primary">Shop</a>
<button class="button fx-hover-primary">Add to cart</button>
```

**`fx-hover-secondary`** -- Fade
Supporting elements. `::before` opacity 0 to 1 on hover.

```html
<button class="button-ghost fx-hover-secondary">Cancel</button>
```

**`fx-hover-muted`** -- Opacity
Minimal feedback. No pseudo-elements, opacity on the element itself (0.5 to 0.85).

```html
<a class="footer-link fx-hover-muted">Impressum</a>
```

**`fx-none`** -- Opt-out
Disables all effects on the element.

```html
<span class="fx-none">No hover effect</span>
```

### Technical Structure

```css
/* Base: all hover classes */
.fx-hover-primary,
.fx-hover-secondary,
.fx-hover-muted {
  position: relative;
}

/* Fill layer */
.fx-hover-primary::before { /* clip-path: inset(0 100% 0 0) -> inset(0) */ }
.fx-hover-secondary::before { /* opacity: 0 -> 1 */ }

/* Content above effect layers */
.fx-hover-primary > *,
.fx-hover-secondary > *,
.fx-hover-muted > * {
  position: relative;
  z-index: 0;
}
```

No `[liftr-fx="..."]` selectors -- timing comes from inherited `--fx-duration` / `--fx-ease`.

---

## Enter/Exit Animations

Applied via JS class toggle. One keyframe per effect type.

| Class | Animation |
|-------|-----------|
| `fx-enter-pop` | Scale 0 to 1 |
| `fx-exit-pop` | Scale 1 to 0 |
| `fx-enter-fade` | Opacity 0 to 1 |
| `fx-exit-fade` | Opacity 1 to 0 |

```html
<div class="fx-enter-pop">Appearing element</div>
```

No set-specific selectors or keyframes.

---

## Loading States

Two modes on `.fx-loading`:

**Replace Mode** (default) -- Icons centered, content fades out.
**Slide Mode** (`.button-label` present) -- Icon slides in from left, content shifts.

### States via `liftr-state`

```html
<!-- Idle -->
<button class="button fx-loading fx-hover-primary">Add to cart</button>

<!-- Loading -->
<button class="button fx-loading fx-hover-primary" liftr-state="loading">Add to cart</button>

<!-- Success -->
<button class="button fx-loading fx-hover-primary" liftr-state="success">Add to cart</button>

<!-- Error -->
<button class="button fx-loading fx-hover-primary" liftr-state="error">Add to cart</button>
```

### Slide Mode

```html
<button class="button fx-loading">
  <span class="button-label">Add to cart</span>
</button>
```

### Transition Strategy (Asymmetric)

- **Base:** NO opacity transition -> exit is instant (prevents wrong icon flash)
- **Active state:** WITH opacity transition -> enter is smooth

### Loading x Hover Compatibility

When `fx-loading` and `fx-hover-*` are on the same element:

- No `liftr-state` -> Hover owns `::before`
- `liftr-state` present -> Loading owns `::before`

The `[liftr-state]` attribute acts as ownership switch. Only Primary + Secondary supported.

---

## Ambient Effects

Continuous background animations. Set controls intensity and duration via `--fx-ambient-*` variables.

| Class | Effect |
|-------|--------|
| `fx-ambient-glow` | Moving radial gradient on `::before` |
| `fx-ambient-pulse` | Opacity pulse on `::before` |
| `fx-ambient-shimmer` | Sweeping highlight on `::before` |

```html
<div class="reward-card fx-ambient-glow">Next reward</div>
```

Content positioned above ambient layer via `z-index: 1`. No set-specific selectors -- animation assigned directly on `::before`, timing from `--fx-ambient-duration` / `--fx-ambient-ease`.

---

## Attention Pulse

Expanding ripple ring. Duration 2s.

```html
<span class="marker fx-attention-pulse">Next Goal</span>
```

No `position: relative` set -- element may already be `position: absolute` (e.g. reward markers).

CSS variable for color: `--gradient` or falls back to `currentColor`.

---

## Morph

Smooth property transitions for state changes (layout shifts, background changes):

```html
<div class="fx-morph">Morphing element</div>
```

Transitions `transform`, `opacity`, and `background-color` using `--fx-morph-duration` and `--fx-morph-ease` (derived from `--fx-duration-long` and `--fx-ease`).

---

## Set-Dependent vs. Set-Independent

| Set-Dependent | Set-Independent |
|---------------|-----------------|
| Hover fills | Loading spinner rotation |
| Ambient effects | Error shake |
| Enter/exit animations | Form validation |
| Attention pulse | Skeleton pulse |

**Rule:** If it is "how does the brand feel?" -> set-dependent. If it is "did it work?" -> set-independent with consistent fast timing.

---

## Accessibility

At `prefers-reduced-motion: reduce`:

- Hover: Instant opacity, no clip-path animations
- Enter/exit: Fast fade only (150ms)
- Ambient: Static or hidden (no loops)
- Attention pulse: Static glow (no animation)
- Loading: Instant transitions (0ms), no spinner rotation
- Morph: Instant (0ms)

---

## Checklist

- [ ] `liftr-fx` set on `<body>` (via theme setting `fx_timing`)?
- [ ] Correct class chosen for element role (primary/secondary/muted)?
- [ ] Element is interactive? (don't add hover effects to non-interactive elements)
- [ ] Loading states use `liftr-state` (loading/success/error)?
- [ ] Slide mode: `.button-label` wrapper present?
- [ ] Ambient effects only on elements that warrant attention?
- [ ] `fx-none` for explicit opt-out where needed?
- [ ] `prefers-reduced-motion` handled (automatic via core.fx.css)?
