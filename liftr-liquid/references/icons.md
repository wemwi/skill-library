# LIFTR Icons

**One icon, three paths — choose the right one for the context.**

The system uses two rendering technologies (SVG Sprite + CSS Mask) across three usage modes.

---

## Architecture & Files

| Layer | Files | Loading | Content |
|-------|-------|---------|---------|
| **Masks** | `assets/media.icon-mask.css` | Always (`snippets/core.liftr.liquid`) | CSS-masked icons as `:root` variables (gradient-capable) |
| **SVG Sprites** | `assets/media.icon-{set}.svg` — sets `default`, `critical`, `social`, `store` | On-demand per `<use href>` | Icon library per set |

```liquid
{{ 'media.icon-mask.css' | asset_url | stylesheet_tag }}   {%- comment -%} in core.liftr.liquid {%- endcomment -%}
```

`assets/core.icon-mask.css` and `assets/core.icon-mask-thin.css` also exist but are **not loaded**
anywhere (theme main, 28.10.2026). Variables defined only there (e.g. `--icon--chevron`, `--icon--sort`,
`--icon--sort-asc`, `--icon--sort-desc`, `--icon--bell`, `--icon--bell-slash`, `--icon--warning`,
`--icon--star`, `--icon--dot`, `--icon--heart`, `--icon--square`, `--icon--rotate-right`) resolve to nothing → invisible icons.

**Naming:**

| Type | Pattern | Example |
|------|---------|---------|
| Mask variable | `--icon--{id}` | `--icon--check` |
| Sprite fragment | `#{id}` in SVG | `#check` |
| Sprite file | `media.icon-{set}.svg` | `media.icon-default.svg` |
| Mask file | `media.icon-mask.css` | `media.icon-mask.css` |

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
| `id` | String | `''` | Icon ID (e.g. `'check'`; `_` becomes `-`) — **required** |
| `set` | String | `'default'` | Sprite set → `media.icon-{set}.svg` (ignored in gradient mode) |
| `title` | String | `nil` | Accessible label → `role="img" aria-label` |
| `class` | String | `''` | Additional CSS classes |
| `role` | String | `nil` | `liftr-role` attribute |
| `gradient` | Boolean | `false` | Enable gradient mode (CSS Mask) |

### Constraints

- `id` must exist as `--icon--{id}` in `media.icon-mask.css` when `gradient: true`
- Caller must check `id` — Guard Contract: no internal blank check

### Usage

```liquid
{%- comment -%} Standard: SVG Sprite {%- endcomment -%}
{% render 'icon', id: 'check' %}

{%- comment -%} Other sprite set {%- endcomment -%}
{% render 'icon', id: 'square-parking', set: 'store' %}

{%- comment -%} Gradient: CSS Mask {%- endcomment -%}
{% render 'icon', id: 'check', gradient: true %}

{%- comment -%} With accessible label {%- endcomment -%}
{% render 'icon', id: 'check', title: 'Verified', gradient: true %}
```

---

## Mode 1: SVG Sprite (Default)

```html
<svg viewBox="0 0 640 640" class="icon" aria-hidden="true">
  <use href="media.icon-default.svg#check"></use>
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

**CSS pattern** (`core.base.css`, Gradient Utilities):
```css
.gradient {
  background: var(--gradient, currentColor);

  &.icon {
    mask-image: var(--icon);
    mask-size: contain;
    mask-repeat: no-repeat;
    mask-position: center;
    /* + -webkit- prefixes */
  }
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

**Step 2:** Add to `media.icon-mask.css` on `:root`:
```css
:root {
  /* --- Category --- */
  --icon--{id}: url("data:image/svg+xml;base64,{BASE64}");
}
```

### New SVG Icon

Add the `<symbol id="{id}">` fragment to `media.icon-{set}.svg`.

### Decision: Mask vs SVG?

| Use Mask | Use SVG Sprite |
|----------|---------------|
| Icon needs `--gradient` | Icon is style-only (no gradient) |
| Status/state indicator | Content icon (USP, feature lists) |
| CSS-only `::after` usage | Set via snippet `id` param |

**Registered masks (loaded `media.icon-mask.css`):** `check`, `info`, `ban` (system) · `spinner-third` (loading) · `angle`, `arrow` (nav) · `plus`, `xmark` (actions) · `star-full`, `star-half`, `star-sharp` (rating) · `badge-percent`, `badge-check`, `trophy`, `sparkles` (status/promo) · `tags`, `gift`, `box-circle-check` (misc) · `location-dot`, `location-arrow` (location) · `quote` (misc)

Referenced by theme CSS but **not** in the loaded file: `chevron`, `sort`, `sort-asc`, `sort-desc`, `bell`, `bell-slash`, `warning` (see Architecture).

---

## Sizing

`.icon` (`core.base.css`) is square and sized by `--icon--size` (fallback `--icon-size--regular`):

```css
.store_badge .icon { --icon--size: var(--icon-size--small); }
```

| Token | Size |
|-------|------|
| `--icon-size--xsmall` | 0.75rem |
| `--icon-size--small` | 1rem |
| `--icon-size--regular` | 1.5rem |
| `--icon-size--medium` | 2rem |
| `--icon-size--large` | 2.5rem |
| `--icon-size--xlarge` | 3rem |

There are no `icon-1x1-*` / `icon-height-*` utility classes in the theme.

**CSS-only sizing:** Set `width`/`height` directly with the tokens.

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
- [ ] `--icon--{id}` exists in `media.icon-mask.css` (for gradient/CSS-only)?
- [ ] Accessibility: decorative → no `title`, informative → set `title`
- [ ] Icon size in REM / design token (not PX)?

### Registering new mask (media.icon-mask.css):
- [ ] SVG viewBox `0 0 640 640`?
- [ ] Base64-encoded as `url("data:image/svg+xml;base64,...")`?
- [ ] Key pattern: `--icon--{id}` (kebab-case)?
- [ ] Category comment in CSS?

### Registering new SVG icon (media.icon-{set}.svg, e.g. media.icon-default.svg):
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
