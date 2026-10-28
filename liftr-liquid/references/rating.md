# LIFTR Rating Snippet

**File:** `snippets/rating.liquid` — CSS in `core.components.css`

Renders star ratings using CSS `mask-image`. No SVG in Liquid. Empty stars are always visible (gray layer at 30% opacity). Filled and half stars overlay with `--color-global--rating` gradient.

---

## Architecture

### Star Rendering (CSS Mask)

Each star is a stacked pair of two `<div>` elements inside a `<span>`:

```
.rating_star .is-full
├── .rating_star-empty    (absolute, mask: star-full, color-scheme--text, 0.3 opacity)
└── .rating_star-filled   (absolute, mask: star-full, color-global--rating, z-elevated)
```

State determines which mask and visibility:

| State | `.rating_star-empty` | `.rating_star-filled` | Filled Mask |
|-------|---------------------|-----------------------|-------------|
| `is-full` | Visible (gray base) | Visible | `--icon--star-full` |
| `is-half` | Visible (gray base) | Visible | `--icon--star-half` |
| `is-empty` | Visible (gray base) | `display: none` | — |

The empty star layer is always rendered so the user sees all 5 positions. The filled layer overlays with higher z-index.

### Half-Star Precision

Input values are rounded to nearest 0.5:

```
4.4 → rating_doubled = 9 (4.4 × 2, rounded) → rating_rounded = 4.5
4.2 → rating_doubled = 8 (4.2 × 2, rounded) → rating_rounded = 4.0
4.7 → rating_doubled = 9 (4.7 × 2, rounded) → rating_rounded = 4.5
```

Comma-separated values (German locale) are handled via `replace: ',', '.'` before calculation.

### DOM Structure

```html
<div class="rating_component"
     role="img"
     aria-label="4.5 out of 5">

  <div class="rating_stars" aria-hidden="true">
    <span class="rating_star is-full">...</span>    <!-- Star 1 -->
    <span class="rating_star is-full">...</span>    <!-- Star 2 -->
    <span class="rating_star is-full">...</span>    <!-- Star 3 -->
    <span class="rating_star is-full">...</span>    <!-- Star 4 -->
    <span class="rating_star is-half">...</span>    <!-- Star 5 -->
  </div>

  <span class="rating_value">4,5</span>
  <span class="rating_count">
    <span class="text-style-muted">(512)</span>
  </span>

</div>
```

---

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `rating` | Number | `0` | Rating value 0–5 (e.g. `4.4`). Rounded to nearest 0.5. |
| `compact` | Boolean | `false` | Compact mode — shows 1 star + value instead of 5 stars |
| `count` | Number | `0` | Review count. Hidden when `0`. |
| `count_format` | String | `'none'` | Count display format: `short`, `long`, `long-brackets`, `none` |
| `layout` | String | `'stars-value-count'` | Element order — see Layout section |

**Guard Contract:** No external guard needed. Snippet handles blank and zero internally.

---

## Layout

The `layout` parameter controls which elements render and in which order. The value is parsed via `contains` checks — no separate show/hide parameters needed.

| Layout | Output | Elements |
|--------|--------|----------|
| `stars-value-count` | ★★★★★ 4,5 (512) | Stars + Value + Count |
| `value-stars-count` | 4,5 ★★★★★ (512) | Value + Stars + Count |
| `stars-value` | ★★★★★ 4,5 | Stars + Value |
| `value-stars` | 4,5 ★★★★★ | Value + Stars |
| `stars-count` | ★★★★★ (512) | Stars + Count |
| `stars-only` | ★★★★★ | Stars only |

### Parsing Logic

Three guards derived from `layout`:

| Guard | Condition | Controls |
|-------|-----------|----------|
| `show_value` | layout contains `'value'` | Value element visibility |
| `show_count` | layout contains `'count'` | Count element visibility |
| `is_value_before_stars` | layout contains `'value-stars'` | Value placement (before or after stars) |

Value only renders when `rating_rounded > 0` — prevents showing "0" for unrated items.

---

## Count Format

| Format | Output | Use Case |
|--------|--------|----------|
| `none` | *(hidden)* | Default — no count shown |
| `short` | (512) | Compact contexts (cards, lists) |
| `long` | 512 Bewertungen | Detailed contexts (store page) |
| `long-brackets` | (512 Bewertungen) | Mixed contexts |

`long` and `long-brackets` use the `snippets.rating.label.reviews_count` translation key.

---

## Compact Mode

When `compact: true`, only 1 star renders instead of 5. Typically combined with `layout: 'stars-value'` or `value-stars`:

```liquid
{% render 'rating', rating: 4.4, compact: true, layout: 'value-stars' %}
```

Output: `4,4 ★`

Adds `is-compact` modifier on `_component` root.

---

## CSS

### Variables

| Variable | Set By | Default | Purpose |
|----------|--------|---------|---------|
| `--rating--icon-size` | Parent Override | `0.875rem` | Star width/height |
| `--rating--value-font-size` | Parent Override | `var(--font-size--small)` | Value element font size |
| `--rating--count-font-size` | Parent Override | `var(--font-size--tiny)` | Count element font size |
| `--color-global--rating` | Theme globals | — | Filled star color/gradient |
| `--color-scheme--text` | Color scheme inheritance | — | Empty star color (at `--opacity--faint`) |

### Selectors

```css
.rating_component { }             /* Root — flex container */
  &.is-compact { }                /* Compact modifier (L1 nesting, Pflicht) */

.rating_stars { }                 /* Stars flex container */

.rating_star { }                  /* Single star wrapper */
  &.is-half .rating_star-filled   /* Half mask override (L2 modifier-child) */
  &.is-empty .rating_star-filled  /* Hide filled layer (L2 modifier-child) */

.rating_star-empty { }            /* Gray base layer */
.rating_star-filled { }           /* Colored overlay layer */

.rating_value { }                 /* Numeric value */
.rating_count { }                 /* Review count */
```

### Nesting Applied

Per Hard Rule 9 in `css-system.md` (liftr-foundation):

| Selector | Level | Rule |
|----------|-------|------|
| `&.is-compact` | L1 same-element | Pflicht |
| `&.is-half .rating_star-filled` | L2 modifier-child | Allowed, max 1 level |
| `&.is-empty .rating_star-filled` | L2 modifier-child | Allowed, max 1 level |

All other selectors are flat (different DOM elements, no modifier relationship).

### CSS Masks

Stars use Mode 3 (CSS-only) from the icon system — no `icon.liquid` snippet, no gradient class. The mask variables come from `media.icon-mask.css`:

| Mask Variable | Used By |
|---------------|---------|
| `--icon--star-full` | Empty layer + filled layer (full stars) |
| `--icon--star-half` | Filled layer override (half stars) |

Both masks must have Base64 data in the active icon set. Empty mask variables → invisible stars.

---

## Accessibility

| Element | Attribute | Purpose |
|---------|-----------|---------|
| `.rating_component` | `role="img"` | Treats the entire component as a single image for assistive tech |
| `.rating_component` | `aria-label="4.5 out of 5"` | Semantic rating for screen readers |
| `.rating_stars` | `aria-hidden="true"` | Hides decorative star visuals |

The `aria-label` is composed in Liquid: `{{ rating_rounded }} {{ t_out_of_5 }}`. The numeric value comes from the computed variable — the locale key `out_of_5` must NEVER contain the number itself (e.g. `"out of 5"`, not `"4.5 out of 5"`).

---

## i18n Keys

### Theme (`de.default.json` / `en-GB.json`)

```json
{
  "snippets": {
    "rating": {
      "aria": {
        "out_of_5": "out of 5"
      },
      "label": {
        "reviews_count": "Reviews"
      }
    }
  }
}
```

German:

```json
{
  "snippets": {
    "rating": {
      "aria": {
        "out_of_5": "von 5 Sternen"
      },
      "label": {
        "reviews_count": "Bewertungen"
      }
    }
  }
}
```

---

## Parent Override

No custom-colors, no merchant color settings. The snippet inherits `--color-global--rating` and `--color-scheme--text` from its context.

All sizing and typography is controlled via CSS variables — no Liquid parameters needed:

```css
.store-card_component .rating_component {
  --rating--icon-size: 0.75rem;
  --rating--value-font-size: var(--font-size--tiny);
  --rating--count-font-size: var(--font-size--tiny);
}
```

---

## Usage Examples

### Basic

```liquid
{% render 'rating', rating: 4.4 %}
```

### Store Locator Card

```liquid
{% render 'rating', rating: store.rating.value, layout: 'value-stars-count', count: store.reviews_count, count_format: 'short' %}
```

### Product Page (detailed)

```liquid
{% render 'rating', rating: product.metafields.reviews.rating.value, layout: 'stars-value-count', count: product.metafields.reviews.count.value, count_format: 'long-brackets' %}
```

### Compact (card list)

```liquid
{% render 'rating', rating: 4.8, compact: true, layout: 'value-stars' %}
```

### Stars only (minimal)

```liquid
{% render 'rating', rating: 3.5, layout: 'stars-only' %}
```

---

## Checklist

### Before using the snippet:
- [ ] `rating` value is numeric (0–5)? Comma-separated locale values are handled.
- [ ] `--icon--star-full` and `--icon--star-half` have Base64 data in active icon set?
- [ ] `--color-global--rating` defined in theme globals?
- [ ] `layout` value matches one of the 6 options?
- [ ] `count_format` set when `count` > 0 and layout contains `count`?
- [ ] Icon/font size overrides done via CSS variables, not Liquid parameters?

### CSS conventions applied:
- [ ] Root class: `rating_component` (with `_component` suffix)
- [ ] Root has `role="img"` and `aria-label="{{ rating_rounded }} {{ t_out_of_5 }}"`
- [ ] Modifier: `is-compact` on root (not BEM `--compact`)
- [ ] Star states: `is-full`, `is-half`, `is-empty` (not BEM `--full`)
- [ ] CSS variable: `--rating--icon-size` default `0.875rem` on `.rating_star` (Owner-Pattern, double dash)
- [ ] CSS variables: `--rating--value-font-size` (fallback `--font-size--small`), `--rating--count-font-size` (fallback `--font-size--tiny`)
- [ ] Nesting: `&.is-compact` (L1 Pflicht), `&.is-half/empty .child` (L2 allowed)
- [ ] CSS file header with variable documentation
- [ ] No `_component` suffix on child elements (`_star`, `_value`, `_count`)

### i18n:
- [ ] `snippets.rating.aria.out_of_5` in both `de.default.json` and `en-GB.json`
- [ ] `out_of_5` contains only the suffix text (`"out of 5"` / `"von 5 Sternen"`) — numeric value comes from Liquid, never from the key
- [ ] `snippets.rating.label.reviews_count` in both `de.default.json` and `en-GB.json`
- [ ] Namespace: `snippets` (not `general`, not `global`)
