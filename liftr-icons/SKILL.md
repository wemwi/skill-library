---
name: liftr-icons
description: Icon system for the LIFTR Shopify theme with three rendering modes (SVG Sprite, CSS Mask Gradient, CSS-only). Covers the decision matrix for choosing mode, icon.liquid snippet API, gradient inheritance, icon mask registration, sizing system, accessibility per mode, and anti-patterns. Use whenever adding icons to sections/blocks, implementing gradient icons, creating CSS-only icons (::after/::before), calling icon.liquid, registering new icon masks, or debugging invisible/broken icons. Triggers on icon, icon.liquid, gradient icon, SVG sprite, CSS mask, icon-mask, icon sizing, icon accessibility, aria-hidden, or any icon rendering within the LIFTR ecosystem.
---

# LIFTR Icons

**One icon, three paths — choose the right one for the context.**

The system uses two rendering technologies (SVG Sprite + CSS Mask) across three usage modes.

---

## Architecture & Files

| Layer | Files | Loading | Content |
|-------|-------|---------|---------|
| **Masks** | `core.icon-mask.css` | Always | All CSS-masked icons (gradient-capable) |
| **SVG Sprites** | `core.icon.svg` | On-demand per `<use href>` | Full icon library |

**Loading order** (core.head):
```liquid
{{ 'core.icon-mask.css' | asset_url | stylesheet_tag }}
```

**Naming:**

| Type | Pattern | Example |
|------|---------|---------|
| Mask variable | `--icon--{id}` | `--icon--check` |
| Sprite fragment | `#{id}` in SVG | `#check` |
| Sprite file | `core.icon.svg` | `core.icon.svg` |
| Mask file | `core.icon-mask.css` | `core.icon-mask.css` |

---

## Decision Matrix

| Criterion | SVG Sprite | CSS Mask Gradient | CSS-only |
|-----------|:----------:|:-----------------:|:--------:|
| Needs `--gradient` | ✗ | ✓ | ✓ |
| Rendered in Liquid | ✓ | ✓ | ✗ |
| Rendered in CSS (::after) | ✗ | ✗ | ✓ |
| Color via `currentColor` | ✓ | ✓ (fallback) | ✓ |
| Color via `--gradient` | ✗ | ✓ | ✓ |

### Decision Tree

```
Icon needed?
├── In Liquid template
│   ├── Needs --gradient? → YES: gradient: true (Mode 2)
│   │                     → NO:  gradient: false (Mode 1, default)
│
└── Purely decorative in CSS (nav, sort, toggle)
    └── CSS-only ::after (Mode 3)
```

### Typical Usage

| Context | Mode | Reason |
|---------|------|--------|
| Content icons (USP, features) | SVG Sprite | Set choice, no gradient |
| Status badges (verified, open/closed) | CSS Mask Gradient | Reacts to `--gradient` |
| Navigation controls (prev/next) | CSS-only | Decorative, CSS-controlled |
| Sort buttons (asc/desc) | CSS-only | State-dependent via CSS |
| Rating stars | CSS-only | Mask for fill/half/empty |
| Accordion toggle (plus) | CSS-only | Decorative |
| Checkmark labels | CSS Mask Gradient | Gradient shows status color |

---

## Snippet API (icon.liquid)

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | String | `''` | Icon ID (e.g. `'check'`) — **required** |
| `title` | String | `nil` | Accessible label → `role="img" aria-label` |
| `class` | String | `''` | Additional CSS classes |
| `role` | String | `nil` | `liftr-role` attribute |
| `gradient` | Boolean | `false` | Enable gradient mode (CSS Mask) |

### Constraints

- `id` must exist as `--icon--{id}` in `core.icon-mask.css` when `gradient: true`
- Caller must check `id` — Guard Contract: no internal blank check

### Usage

```liquid
{%- comment -%} Standard: SVG Sprite {%- endcomment -%}
{% render 'icon', id: 'check' %}

{%- comment -%} Gradient: CSS Mask {%- endcomment -%}
{% render 'icon', id: 'check', gradient: true %}

{%- comment -%} With accessible label {%- endcomment -%}
{% render 'icon', id: 'check', title: 'Verified', gradient: true %}
```

---

## Mode 1: SVG Sprite (Default)

```html
<svg viewBox="0 0 640 640" class="icon" aria-hidden="true">
  <use href="core.icon.svg#check"></use>
</svg>
```

- Color via `fill: currentColor` (inherits text color)
- **No gradient possible** (SVG `fill` doesn't support CSS `background-image`)

---

## Mode 2: CSS Mask Gradient (Snippet)

```html
<span class="icon gradient"
      style="--icon: var(--icon--check)"
      aria-hidden="true"></span>
```

How it works:
1. `mask-image: var(--icon)` cuts icon shape from element
2. `background: var(--gradient, currentColor)` fills visible area
3. Without `--gradient` → fallback to `currentColor` (looks like normal icon)
4. With `--gradient` from parent → gradient shows through mask

**CSS pattern** (core.components.css):
```css
.gradient {
  background: var(--gradient, currentColor);
}
.icon.gradient {
  display: inline-flex;
  flex-shrink: 0;
  mask-image: var(--icon);
  mask-size: contain;
  mask-repeat: no-repeat;
  mask-position: center;
  -webkit-mask-image: var(--icon);
  -webkit-mask-size: contain;
  -webkit-mask-repeat: no-repeat;
  -webkit-mask-position: center;
}
```

---

## Mode 3: CSS-only (::after / ::before)

For purely decorative, CSS-controlled icons. No Liquid rendering.

```css
.button.is-sort::after {
  content: '';
  width: var(--icon-size--small);
  height: var(--icon-size--small);
  background-color: currentColor;
  mask-image: var(--icon--sort);
  mask-repeat: no-repeat;
  mask-position: center;
  mask-size: contain;
  -webkit-mask-image: var(--icon--sort);
  -webkit-mask-repeat: no-repeat;
  -webkit-mask-position: center;
  -webkit-mask-size: contain;
}

/* State-dependent icon swap */
.button.is-sort[liftr-state~="sort-asc"]::after {
  mask-image: var(--icon--sort-asc);
  -webkit-mask-image: var(--icon--sort-asc);
}
```

### CSS-only vs Snippet

| CSS-only `::after` | Snippet `gradient: true` |
|--------------------|--------------------------|
| Purely decorative | Content element |
| No Liquid access needed | Liquid params control rendering |
| State swap via CSS | Exists in DOM as own element |
| Always `currentColor` | Needs `--gradient` inheritance |

---

## Gradient Inheritance

```
Parent sets --gradient (e.g. via .is-success, custom-colors)
  └── Child with .gradient.is-icon inherits automatically
      └── background: var(--gradient, currentColor) shows through mask
```

**Gradient sources:**

| Source | How set | Example |
|--------|---------|---------|
| State class | `.is-success`, `.is-warning`, `.is-rating` | Auto via CSS |
| Custom colors | `custom-colors.liquid` snippet | Merchant-configured |
| Inline CSS var | `style="--gradient: ..."` | Dynamic via JS |
| State attribute | `[liftr-state*="success"]` | JS-controlled |

**No gradient set?** Fallback: `currentColor` — icon looks like normal single-color icon.

---

## Registering Icons

### New Mask Icon

**Step 1:** Encode SVG path as Base64 (640×640 viewBox)

**Step 2:** Add to `core.icon-mask.css` on `:root`:
```css
:root {
  /* --- Category --- */
  --icon--{id}: url("data:image/svg+xml;base64,{BASE64}");
}
```

### New SVG Icon

Add the `<symbol id="{id}">` fragment to `core.icon.svg`.

### Decision: Mask vs SVG?

| Use Mask | Use SVG Sprite |
|----------|---------------|
| Icon needs `--gradient` | Icon is style-only (no gradient) |
| Status/state indicator | Content icon (USP, feature lists) |
| CSS-only `::after` usage | Set via snippet `id` param |

**Registered masks:** `badge-check` (status) · `location-dot` (location) · `angle`, `chevron`, `arrow` (nav) · `check`, `info`, `warning`, `ban` (system) · `spinner-third` (loading) · `plus`, `xmark`, `rotate-right` (actions) · `sort`, `sort-asc`, `sort-desc` (sorting) · `star`, `star-full`, `star-half` (rating) · `square` (forms) · `bell`, `bell-slash` (status) · `quote`, `dot` (misc) · `heart`, `gift`, `tags`, `box-circle-check` (misc)

---

## Sizing

| Class | Size | Token |
|-------|------|-------|
| `icon-1x1-xsmall` | 0.75rem | `--icon-size--xsmall` |
| `icon-1x1-small` | 1rem | `--icon-size--small` |
| `icon-1x1-regular` | 1.5rem | `--icon-size--regular` |
| `icon-1x1-medium` | 2rem | `--icon-size--medium` |
| `icon-1x1-large` | 2.5rem | `--icon-size--large` |
| `icon-1x1-xlarge` | 3rem | `--icon-size--xlarge` |

**Height-only classes:** `icon-height-{size}` — for icons keeping natural width.

**CSS-only sizing:** Set `width`/`height` directly, no utility classes.

---

## Accessibility

| Context | `title` param | Result |
|---------|:---:|---------|
| Icon next to descriptive text | ✗ | `aria-hidden="true"` |
| Standalone icon button | ✓ | `role="img" aria-label="..."` |
| Status icon without text | ✓ | `role="img" aria-label="..."` |
| Decorative (list bullets) | ✗ | `aria-hidden="true"` |

**CSS-only icons** (`::after`/`::before`): Pseudo-elements are not in accessibility tree — no `aria-hidden` needed. If parent has meaning, use `aria-label` on parent:

```html
<button aria-label="Sort ascending" class="button is-sort">Sort</button>
```

---

## Anti-Patterns

| ❌ Anti-Pattern | ✅ Correct |
|---|---|
| Inline SVG strings in JS | CSS `::after` with `--icon--*` |
| `foreignObject` for SVG gradients | CSS Mask `<span>` with `.icon.gradient` |
| Inline `color` styles on icon | Inherit via parent CSS variable |
| `--icon-mask--{id}` naming (old v2.x) | `--icon--{id}` naming |
| `aria-hidden` + `aria-label` together | Either decorative OR informative |
| PX for icon sizes | Design tokens (`--icon-size--*`) or REM |

---

## Checklist

### Before using an icon:
- [ ] Needs `--gradient`? → Gradient mode or CSS-only
- [ ] Rendered in Liquid? → Use snippet
- [ ] Rendered in CSS? → `::after`/`::before` pattern
- [ ] `--icon--{id}` exists in `core.icon-mask.css` (for gradient/CSS-only)?
- [ ] Accessibility: decorative → no `title`, informative → set `title`
- [ ] Icon size in REM / design token (not PX)?

### Registering new mask (core.icon-mask.css):
- [ ] SVG viewBox `0 0 640 640`?
- [ ] Base64-encoded as `url("data:image/svg+xml;base64,...")`?
- [ ] Key pattern: `--icon--{id}` (kebab-case)?
- [ ] Category comment in CSS?

### Registering new SVG icon (core.icon.svg):
- [ ] `<symbol id="{id}">` with viewBox `0 0 640 640`?
- [ ] ID matches kebab-case convention?

### Quick Reference

```liquid
{%- comment -%} SVG Sprite {%- endcomment -%}
{% render 'icon', id: '{id}' %}

{%- comment -%} Gradient {%- endcomment -%}
{% render 'icon', id: '{id}', gradient: true %}

{%- comment -%} Accessible {%- endcomment -%}
{% render 'icon', id: '{id}', title: '{label}', gradient: true %}
```

```css
/* CSS-only */
.element::after {
  content: '';
  width: var(--icon-size--small);
  height: var(--icon-size--small);
  background-color: currentColor;
  mask-image: var(--icon--{id});
  mask-repeat: no-repeat;
  mask-position: center;
  mask-size: contain;
  -webkit-mask-image: var(--icon--{id});
  -webkit-mask-repeat: no-repeat;
  -webkit-mask-position: center;
  -webkit-mask-size: contain;
}
```
