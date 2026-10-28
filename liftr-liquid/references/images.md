# LIFTR Image Guide

---

## Core Principle

**Container controls ratio (via section/block CSS). Image fills container.**

`media-wrapper` = **Absolute Cover Container**. Every child image is positioned `absolute` with `inset: 0` and defaults to `object-fit: cover`. The image is pulled out of flow — the container MUST have its own dimensions (via `aspect-ratio`, explicit `height`, or grid/flex constraints).

If the image should determine its own height (logos, product images in contain mode) → **do NOT use `media-wrapper`**. Use a plain container instead.

```
Image needs to FILL a fixed container?  → media-wrapper (cover is default)
Image needs to FIT inside a container?  → media-wrapper + component class with `object-fit: contain` (only if container has aspect-ratio)
Image should determine its own height?  → NO media-wrapper (plain <div> or <a>)
```

---

## Media Wrapper Pattern

### How it works (core.base.css)

```css
.media-wrapper {
  position: relative;
  overflow: clip;
  border-radius: var(--border-radius--small);

  /* Ratio modifiers */
  &.is-square     { aspect-ratio: 1; }
  &.is-banner     { aspect-ratio: 2/1; }
  &.is-portrait   { aspect-ratio: 3/4; }
  &.is-widescreen { aspect-ratio: 16/9; }
}

.media-wrapper > img,
.media-wrapper > picture,
.media-wrapper > picture > img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  max-width: none;
  max-height: none;
  object-fit: cover;
}
```

`object-fit: cover` is the default. For `contain`, set `object-fit: contain` on the image via the component's own class (e.g. `section.spotlight-header.css`). There are **no** `cover-media` / `contain-media` utility classes in the theme.

The container MUST define its own size. Without `aspect-ratio` or explicit height, the container collapses to 0.

### Standard (image only)

Component class + `media-wrapper` merged on one element:

```html
<div class="store-card_media media-wrapper">
  {{ image | image_url: width: 800 | image_tag }}
</div>
```

```css
/* Component CSS defines ratio — REQUIRED */
.store-card_media { aspect-ratio: 1 / 1; }
```


### With additional elements (badge, overlay)

Separate wrapper when siblings exist:

```html
<div class="store-card_media">
  <div class="media-wrapper">
    {{ image | image_url: width: 800 | image_tag }}
  </div>
  <span class="store-card_badge">New</span>
</div>
```

### When NOT to use media-wrapper

Flow images that should determine their own height:

```html
<!-- Logo — height comes from image, not container -->
<a class="footer-brand_logo">
  {{ logo | image_url: width: 400 | image_tag: class: 'footer-brand_logo-image' }}
</a>

<!-- Promotional card image — contain, flow height -->
<div class="featured_image">
  {{ image | image_url: width: 400 | image_tag: class: 'featured_image-img' }}
</div>
```

---

## Cover vs. Contain

| Need | Object-Fit | How | media-wrapper? |
|-------|------------|------|:-:|
| Image may be cropped (cards, heroes, backgrounds, avatars) | `cover` | Default inside media-wrapper | ✅ |
| Image must be fully visible — container has aspect-ratio | `contain` | Component class sets `object-fit: contain` | ✅ |
| Image must be fully visible — image determines height | — | Plain container, image in flow | ❌ |

Focal point is set automatically by Shopify — no manual `object-position` needed.

---

## Ratio Reference

These are reference values for component CSS — not utility classes.

| Name | Ratio | Decimal | Typical use |
|------|-------|---------|-------------|
| Story | 9:16 | 0.56 | Product cards, stories |
| Square | 1:1 | 1.00 | Avatars, thumbnails, city/collection cards |
| Teaser | 16:9 | 1.78 | Collections, blog, video, store panel banner |
| Hero | 2:1 | 2.00 | Hero sections |
| Banner | 4:1 | 4.00 | Promo banners |

```css
/* Applied in section/block CSS, not as utility */
.hero_media { aspect-ratio: 2 / 1; }
.product-card_media { aspect-ratio: 9 / 16; }
```

**Prefer the component's own `aspect-ratio`** in its CSS file. `media-wrapper` offers four ratio modifiers (`is-square`, `is-banner`, `is-portrait`, `is-widescreen`) for simple cases.

---

## Responsive Images (widths & sizes)

### The Problem: Blurry Images

Blurry images are almost always caused by `widths` too low or `sizes` incorrect. Use the lookup table — don't calculate manually.

### Formula

```
CSS display size (REM) × 16 × 1.75 (Lighthouse DPR) = Maximum pixel width
```

**Why 1.75?** Lighthouse emulates a Moto G Power with DPR 1.75 — not 2 or 3. Optimizing for ×2 wastes bytes that Lighthouse penalizes without visual benefit at the test DPR.

### Lookup Table

| CSS size | Max pixels | Recommended widths | sizes |
|----------|-----------|-------------------|-------|
| 4rem | 112px | `'75, 115'` | `'4rem'` |
| 6rem | 168px | `'85, 130, 170'` | `'6rem'` |
| 8rem | 224px | `'115, 170, 225'` | `'8rem'` |
| 10rem | 280px | `'140, 210, 280'` | `'10rem'` |
| 15rem | 420px | `'210, 315, 420'` | `'15rem'` |
| 20rem | 560px | `'280, 420, 560'` | `'20rem'` |
| 30rem | 840px | `'420, 630, 840'` | `'30rem'` |
| 40rem | 1120px | `'560, 840, 1120'` | `'40rem'` |
| 100% (container-large) | 2380px | `'800, 1200, 1800, 2400'` | `'85rem'` |

### sizes — Always REM

```liquid
# ❌ WRONG
sizes: '100px'
sizes: 'auto'

# ✅ CORRECT
sizes: '10rem'
sizes: '(max-width: 48rem) 6rem, 10rem'
```

### sizes — Account for All Spacing

**Common mistake:** Forgetting that `padding-global.is-card` adds `margin` on top of section padding. This makes `sizes` too generous → browser downloads oversized images → Lighthouse penalty.

```liquid
# ❌ WRONG — only subtracts section padding
sizes: 'calc(100vw - 2rem)'

# ✅ CORRECT — subtracts section padding + card margin
sizes: 'calc(100vw - 4.5rem)'
```

**Rule:** When calculating `sizes` for images inside cards, inspect the actual rendered space. `padding-global`, `.is-card` margin, grid gaps — all reduce the available width. Miss any and the `sizes` hint is too large.

### Responsive sizes with breakpoints

When an image changes size at breakpoints:

```liquid
sizes: '(max-width: 30rem) 100vw, (max-width: 48rem) 50vw, 20rem'
```

Read right to left: default 20rem, under 48rem 50vw, under 30rem full width.

### When to use explicit widths

| Scenario | Solution |
|----------|----------|
| Image size doesn't change | Shopify auto (omit `widths`) |
| Image changes at breakpoints | Explicit `widths` + `sizes` |
| Very small images (< 200px display) | Explicit `widths` for control |
| Full-width hero/banner | Explicit `widths` with high max |

---

## Loading Strategy

### Default is lazy — don't set it

```liquid
# ❌ REDUNDANT
{{ image | image_url: width: 400 | image_tag: loading: 'lazy' }}

# ✅ CORRECT — default is lazy
{{ image | image_url: width: 400 | image_tag }}
```

### Above-the-fold: eager + fetchpriority

```liquid
{{ image | image_url: width: 1200 | image_tag:
  loading: 'eager',
  fetchpriority: 'high'
}}
```

### Decision

```
Is the image visible on initial page load (above-the-fold)?
  → YES: loading: 'eager', fetchpriority: 'high'
  → NO: Don't set anything (lazy is default)
```

Above-the-fold elements: hero image, header logo, first visible product image (optional).

### Images in Closed Dialogs

**Browsers do NOT reliably load `loading="lazy"` images inside closed `<dialog>` elements.** The images are not in the viewport intersection area, so the lazy trigger never fires — even after the dialog opens (browser may not re-evaluate).

**Affected components:** Panel sidebars, modals, bottom sheets — anything rendered inside `liftr-panel` / `<dialog>`.

**Solution:** Use a data-src pattern and swap on open:

```html
<!-- In Liquid: render with data-src instead of src -->
<img data-src="{{ image | image_url: width: 800 }}" alt="{{ image.alt }}">
```

```js
// In JS: swap on the panel's opened event (emitted on document by ui.panel.js)
import { on } from 'core.liftr';

this.addDisposable(on('liftr:panel:opened', (e) => {
  if (e.detail.id !== 'my-panel') return;
  document.querySelectorAll('liftr-panel[liftr-id="my-panel"] img[data-src]').forEach(img => {
    img.src = img.dataset.src;
    img.removeAttribute('data-src');
  });
}));
```

Theme status: no module implements this swap yet (no `data-src` handling in `assets/*.js`).

**Do NOT** set `loading="eager"` on dialog images as a workaround — they would block initial page load for content the user hasn't requested yet.

---

## Placeholder Images

### placeholder.liquid Snippet

Centralized snippet for placeholder/decorative images:

```liquid
{%- render 'placeholder', type: 'image' -%}
```

The snippet sets `role="presentation"` and resolves the asset `media.{type}.{format}` (format is mapped inside the snippet).

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `type` | String | required | `image` (svg), `founder` (svg), `products` (avif), `logo-white` (svg) — unknown types render nothing |

### Usage

```liquid
{%- if image != blank -%}
  {{ image | image_url: width: 800 | image_tag }}
{%- else -%}
  {%- render 'placeholder', type: 'image' -%}
{%- endif -%}
```

---

## Alt-Text

```liquid
{{ image | image_url: width: 800 | image_tag:
  alt: image.alt | default: fallback_alt
}}
```

**Fallback strategy:**

1. `image.alt` (set by merchant in admin)
2. Context-based fallback (e.g. product title, collection name)
3. Leave empty for purely decorative images

---

## Complete Examples

### Product Card (below fold)

```liquid
<div class="product-card_media media-wrapper">
  {{ product.featured_image | image_url: width: 560 | image_tag:
    widths: '280, 420, 560',
    sizes: '(max-width: 30rem) calc(100vw - 4.5rem), 20rem',
    alt: product.featured_image.alt | default: product.title
  }}
</div>
```

```css
.product-card_media { aspect-ratio: 9 / 16; }
```

### Hero Image (above fold)

```liquid
<div class="hero_media media-wrapper">
  {{ section.settings.image | image_url: width: 2400 | image_tag:
    loading: 'eager',
    fetchpriority: 'high',
    widths: '800, 1200, 1800, 2400',
    sizes: '100vw',
    alt: section.settings.image.alt | default: section.settings.content_heading
  }}
</div>
```

```css
.hero_media { aspect-ratio: 2 / 1; }
```

### Small Thumbnail

```liquid
<div class="avatar_media media-wrapper">
  {{ image | image_url: width: 170 | image_tag:
    widths: '85, 130, 170',
    sizes: '6rem'
  }}
</div>
```

```css
.avatar_media { aspect-ratio: 1 / 1; }
```

### Contain inside media-wrapper (container has ratio)

```liquid
<div class="logo_media media-wrapper">
  {{ logo | image_url: width: 400 | image_tag:
    class: 'logo_image',
    widths: '140, 210, 280',
    sizes: '10rem'
  }}
</div>
```

```css
.logo_media { aspect-ratio: 3 / 1; }
.logo_image { object-fit: contain; }
```

### Flow Image (no media-wrapper)

```liquid
<!-- Logo — image determines height -->
<a class="brand_logo" href="/">
  {{ shop.brand.logo | image_url: width: 400 | image_tag:
    class: 'brand_logo-image',
    widths: '210, 315, 420',
    sizes: '12rem'
  }}
</a>
```

### Panel Image (inside dialog)

```liquid
<!-- Inside liftr-panel: use data-src pattern -->
<div class="panel-card_media media-wrapper">
  <img
    data-src="{{ image | image_url: width: 560 }}"
    alt="{{ image.alt | default: fallback_alt }}"
    width="{{ image.width }}"
    height="{{ image.height }}"
  >
</div>
```

---

## Checklist

- [ ] `media-wrapper` on container? → Only if container has own dimensions (aspect-ratio/height)
- [ ] Aspect ratio defined in component CSS (not on media-wrapper)?
- [ ] Flow image (contain, no fixed ratio)? → **No** `media-wrapper`
- [ ] Cover is the default inside `media-wrapper`; `object-fit: contain` via the component class where the image must not be cropped
- [ ] No `loading: 'lazy'` (is default)?
- [ ] Above-fold? → `loading: 'eager'` + `fetchpriority: 'high'`
- [ ] Inside `<dialog>` / panel? → `data-src` pattern, NOT eager
- [ ] `widths` calculated from lookup table (REM × 16 × 1.75)?
- [ ] `sizes` in REM (not px, not auto)?
- [ ] `sizes` accounts for ALL spacing (section padding + card margin + grid gaps)?
- [ ] Placeholder via `{%- render 'placeholder', type: '...' -%}`?
- [ ] Alt-text with context fallback?
- [ ] No manual `object-position` (Shopify sets focal point automatically)?
