---
name: liftr-status
description: Implementation guide for the status dot snippet in the LIFTR Shopify theme. Covers the pulsating dot animation, gradient color inheritance, silent mode, JS targeting via liftr-role (live-label-current, product-stock-text), reduced motion fallback, and Parent Override via --gradient. Use whenever rendering opening-hours indicators, stock level dots, live event status, store status badges, or debugging invisible/non-pulsating status dots. Triggers on any mention of status dot, status snippet, pulsating dot, opening hours indicator, stock status, live label, live indicator, status_component, status_ping, status_core, --gradient on status, or liftr-role="live-label-current" within the LIFTR ecosystem.
---

# LIFTR Status Snippet

**File:** `snippets/status.liquid` — CSS in `core.components.css`

Pulsating dot indicator for opening hours, stock levels, live events. Dot color is inherited via `--gradient` from parent context (color scheme or `liftr-state` modifiers on ancestor component). No color parameter — the parent controls what color the dot is.

---

## Architecture

### Dot Rendering

Two stacked `<span>` elements inside a wrapper:

```
.status_dot
├── .status_ping    (absolute, same size, pulsating outward animation)
└── .status_core    (absolute, solid circle, static)
```

Both use `background: var(--gradient)` — the color comes from DOM inheritance. Parent components set `--gradient` based on state (e.g. green for open, red for closed).

### Silent Mode

When `silent: true`, the dot is hidden entirely — only the label renders. Use for states where visual pulsing is inappropriate (e.g. "Geschlossen" without a red dot).

### JS Targeting

Two mutually exclusive `liftr-role` values for JavaScript targeting:

| Parameter | Role Attribute | JS Use Case |
|-----------|---------------|-------------|
| `live: true` | `liftr-role="live-label-current"` | Live event label — JS updates text dynamically |
| `stock: true` | `liftr-role="product-stock-text"` | Stock level label — JS updates text dynamically |

Only one role applies per instance. If neither `live` nor `stock` is `true`, no role attribute is rendered.

---

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `state` | String | `'open'` | Status state token (e.g. `open`, `closed`). Informational — does not affect rendering. Parent uses this for `liftr-state` or color decisions. |
| `label` | String | `blank` | Visible label text next to the dot |
| `live` | Boolean | `false` | Adds `liftr-role="live-label-current"` for JS targeting |
| `stock` | Boolean | `false` | Adds `liftr-role="product-stock-text"` for JS targeting |
| `silent` | Boolean | `false` | Hides the dot, shows label only |

**Guard Contract:** No external guard needed — snippet renders in all states. Parent is responsible for providing `--gradient` (e.g. via color scheme or `liftr-state` modifiers).

---

## CSS

### Variables

| Variable | Set By | Default | Purpose |
|----------|--------|---------|---------|
| `--status--gap` | Parent Override | `0.5rem` | Gap between dot and label |
| `--status--dot-size` | Parent Override | `0.5rem` | Dot diameter |
| `--status--font-size` | Parent Override | `var(--font-size--regular)` | Label font size |
| `--status--glow` | Parent Override | — | Glow color for reduced-motion fallback |
| `--gradient` | Color scheme / liftr-state | — | Dot color (both core and ping) |

### Selectors

```css
.status_component { }        /* Root — inline-flex container */
.status_dot { }              /* Dot wrapper — relative positioning */
.status_core { }             /* Solid circle */
.status_ping { }             /* Pulsating ring animation */
.status_label { }            /* Text label */
```

All selectors are flat — no modifiers, no nesting needed.

### Animation

The ping animation scales the outer ring to 2.5× and fades to 0:

```css
@keyframes status-ping {
  75%, 100% {
    transform: scale(2.5);
    opacity: 0;
  }
}
```

Timing: `1.5s cubic-bezier(0, 0, 0.2, 1) infinite`.

### Reduced Motion

When `prefers-reduced-motion: reduce`:
- Animation is disabled (`animation: none`)
- Static glow replaces pulse: `box-shadow: 0 0 0.25rem 0.125rem var(--status--glow)`

**Note:** `--status--glow` must be set by the parent for the reduced-motion fallback to be visible. Without it, the dot shows as a plain circle with no glow.

---

## Gradient Color Contract

The snippet does NOT set its own color. The parent must provide `--gradient` through one of these patterns:

### Pattern 1: Color Scheme Inheritance

Parent component uses a color scheme class (`gradient is-text`) — the snippet's label already has this class, and the dot inherits `--gradient` from the DOM.

### Pattern 2: State-Based Color

Parent sets `--gradient` based on `liftr-state`:

```css
/* Example: store card sets color based on open/closed state */
.store-card_component[liftr-state~="open"] {
  --gradient: var(--color-global--success);
}

.store-card_component[liftr-state~="closed"] {
  --gradient: var(--color-global--error);
}
```

### Pattern 3: Direct Override

Parent sets `--gradient` inline or in CSS:

```css
.custom-section .status_component {
  --gradient: var(--color-global--warning);
}
```

---

## Accessibility

| Element | Attribute | Purpose |
|---------|-----------|---------|
| `.status_component` | `role="status"` | Live region — screen readers announce changes |
| `.status_dot` | `aria-hidden="true"` | Hides decorative dot from assistive technology |

The `role="status"` makes the snippet a polite live region — when JS updates the label text, screen readers will announce the change.

---

## Parent Override

All visual properties are overridable via CSS variables with inline fallbacks:

```css
/* Example: smaller status in a card context */
.store-card_component .status_component {
  --status--gap: 0.375rem;
  --status--dot-size: 0.375rem;
  --status--font-size: var(--font-size--small);
}
```

This is a valid Parent Override (CSS variable with existing fallback in the snippet).

---

## Usage Examples

### Opening Hours (Store Locator)

```liquid
{% render 'status', state: 'open', label: t_open_label %}
```

### Closed State (Silent)

```liquid
{% render 'status', state: 'closed', label: t_closed_label, silent: true %}
```

### Live Event Indicator

```liquid
{% render 'status', live: true, label: t_live_label %}
```

### Product Stock Level

```liquid
{% render 'status', stock: true, label: t_stock_label %}
```

---

## Checklist

### Before using the snippet:
- [ ] Parent provides `--gradient` via color scheme, `liftr-state`, or direct CSS variable?
- [ ] `--status--glow` set if reduced-motion fallback should have a visible glow?
- [ ] Only one of `live` / `stock` is `true` per instance (mutually exclusive)?
- [ ] Label text passed via translation variable (not hardcoded string)?

### CSS conventions applied:
- [ ] Root class: `status_component` (with `_component` suffix)
- [ ] All selectors flat (no nesting, no modifiers)
- [ ] CSS variables: Owner-Pattern `--status--*`
- [ ] Font weight: uses `--font-weight--xbold` token (not hardcoded value)
- [ ] Animation keyframes: `status-ping` (namespaced to component)

### Accessibility:
- [ ] `role="status"` on root element
- [ ] `aria-hidden="true"` on `.status_dot`
- [ ] `prefers-reduced-motion` fallback with static glow
