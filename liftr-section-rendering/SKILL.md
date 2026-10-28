---
name: liftr-section-rendering
description: "Guide for creating and consuming API Sections in the LIFTR Shopify theme. API Sections are minimal Liquid sections that serve as server-side data endpoints for the Section Rendering API. Covers naming convention (api-* prefix), section template, schema rules (no presets, no blocks, limit 1), JavaScript fetch pattern (URL construction, template parsing, DOM replacement), loading states, and caching. Use whenever creating a new API section, fetching server-rendered HTML via Section Rendering API, refreshing stock/rewards/hours without page reload, debugging section rendering 404s, or implementing DOM replacement with loading states. Triggers on any mention of API section, Section Rendering API, section_id, server-rendered HTML fetch, stock refresh, cart reward recalculation, or dynamic content reload within the LIFTR ecosystem."
---

# liftr-section-rendering — Section Rendering API Endpoints

**Version:** 1.1.0

---

## 1. Overview

API Sections are minimal Liquid sections that serve as server-side data endpoints. They render only a snippet -- no layout, no wrapper. JavaScript fetches them via Section Rendering API to get server-rendered HTML with full Liquid context (inventory, pricing, translations, settings).

### Why API Sections?

| Data Source | inventory_quantity | Liquid i18n | Theme Settings | Snippet Reuse |
|---|---|---|---|---|
| `/products/{handle}.js` | No | No | No | No |
| Product Recommendations API | No | No | No | No |
| Section Rendering API | Yes | Yes | Yes | Yes |

---

## 2. Naming Convention

### Pattern: `api-{resource}[-{scope}]`

| Section File | Renders | Used by |
|---|---|---|
| `api-product-stock.liquid` | `product-stock` snippet | `ui.product.js` stock refresh |
| `api-cart-rewards.liquid` | `cart-rewards` snippet | `ui.cart.js` reward recalc |
| `api-store-hours.liquid` | `store-hours` snippet | `ui.store.js` hours refresh |

Rules: Always `api-` prefix. Resource matches snippet name. All lowercase (see Gotchas).

### JS Constants

```javascript
const SECTION_STOCK = 'api-product-stock';  // Matches filename without .liquid
```

---

## 3. Section Template

```liquid
{% comment %}
================================================================================
SECTION: api-{resource}
================================================================================
API Section for {description}.
Returns ONLY {what it renders} -- no wrapper, no layout.

Called by {module}.js #{method}() via:
  fetch('{url pattern}')
================================================================================
{% endcomment %}

{%- liquid
  render '{snippet-name}', param1: value1, param2: value2
-%}

{% schema %}
{
  "name": "t:sections.api.{resource}.name",
  "settings": [],
  "limit": 1
}
{% endschema %}
```

### Schema Rules

| Property | Value | Reason |
|---|---|---|
| `name` | `t:sections.api.{resource}.name` | i18n |
| `settings` | `[]` | No merchant configuration |
| `limit` | `1` | Prevents duplicates |
| `presets` | **Omitted** | Invisible in Editor section picker |
| `blocks` | **Omitted** | Not needed |

No `presets` = invisible to merchants in Theme Editor. Only accessible via JS.

### i18n Keys

```json
{
  "sections": {
    "api": {
      "product_stock": { "name": "API: Lagerbestand (intern)" },
      "cart_rewards": { "name": "API: Warenkorb Belohnungen (intern)" }
    }
  }
}
```

`(intern)` / `(internal)` suffix signals non-visual section.

---

## 4. JavaScript Fetch Pattern

### URL Construction

```javascript
// Product context (product.* available in Liquid)
const url = `/products/${handle}?variant=${variantId}&section_id=${SECTION_ID}`;

// Collection context
const url = `/collections/${handle}?section_id=${SECTION_ID}`;

// Cart context
const url = `/cart?section_id=${SECTION_ID}`;

// Current page context
const url = `${window.location.pathname}?section_id=${SECTION_ID}`;
```

URL path determines which Liquid objects are available. `/products/{handle}` makes `product` available. `?variant=` sets `product.selected_or_first_available_variant`.

### Response Parsing

Section Rendering wraps response in `<div id="shopify-section-{id}">`. Parse with `<template>` to avoid triggering browser rendering:

```javascript
const response = await fetch(url);
const html = await response.text();

const template = document.createElement('template');
template.innerHTML = html;

const freshEl = template.content.querySelector(
  `[${ATTRIBUTES.ROLE}~="${ROLES.TARGET_ROLE}"]`
);
```

### DOM Replacement

```javascript
if (freshEl && existingEl) {
  existingEl.replaceWith(freshEl);
}
```

**After `replaceWith()`:** Old references are stale. Re-query roles for fresh DOM.

### Complete Pattern

```javascript
const SECTION_RESOURCE = 'api-resource-name';

async #handleRefresh() {
  if (this.#isRefreshing) return;
  this.#isRefreshing = true;

  const targetState = this.createState(targetElement);
  targetState.add(STATES.LOADING);
  const startTime = performance.now();

  try {
    const url = `/${context}/${this.#slug}?section_id=${SECTION_RESOURCE}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const html = await response.text();
    const template = document.createElement('template');
    template.innerHTML = html;

    const freshEl = template.content.querySelector(
      `[${ATTRIBUTES.ROLE}~="${ROLES.TARGET}"]`
    );
    if (!freshEl) throw new Error('Target not found in section response');

    const existingEl = this.role(ROLES.TARGET);
    if (existingEl) existingEl.replaceWith(freshEl);

    await this.awaitLoading(startTime);
    targetState.remove(STATES.LOADING);

  } catch (error) {
    await this.awaitLoading(startTime);
    targetState.remove(STATES.LOADING);
  } finally {
    this.#isRefreshing = false;
  }
}
```

---

## 5. Loading State

Loading state on **nearest meaningful container**, not on trigger button:

| Scenario | Loading Target | Reason |
|---|---|---|
| Stock refresh in panel | Variant panel | Panel shows skeleton |
| Cart reward recalc | Reward bar element | Only reward section loading |
| Store hours refresh | Store card | Individual card skeleton |

Target must have `liftr-skeleton` in HTML for CSS skeleton effect.

---

## 6. Gotchas

### Filenames MUST be lowercase

Shopify's Section Rendering API does NOT resolve `section_id` with uppercase letters. Theme Editor accepts any casing, but API returns 404 silently.

```
WRONG:  sections/API-product-stock.liquid  --> 404
RIGHT:  sections/api-product-stock.liquid  --> 200
```

**Symptom:** `fetch()` returns 404, no error page. Section renders normally on page load -- only fails via `?section_id=`.

### CSS Already Loaded

API Sections respond with raw HTML -- no `<link>` tags. All CSS for rendered snippets must already be in Theme Head. Since API sections render the same snippets as initial page load, no additional CSS needed.

### Caching

Shopify CDN caches Section Rendering responses (short TTL). Do NOT add cache-busting (`&t=${Date.now()}`) -- defeats CDN with no meaningful accuracy gain.

---

## 7. Checklist

### Section File
- [ ] Filename: `api-{resource}.liquid` (all lowercase)
- [ ] Header comment with section name, caller, URL pattern
- [ ] Renders exactly ONE snippet call (no wrapper HTML)
- [ ] No stylesheet_tag links
- [ ] Schema: `settings: []`, `limit: 1`, NO `presets`, NO `blocks`

### JavaScript
- [ ] `SECTION_*` constant matches filename without .liquid
- [ ] URL uses correct context path
- [ ] Response parsed via `<template>` element
- [ ] Target queried with `ATTRIBUTES.ROLE` constant
- [ ] `replaceWith()` for DOM swap
- [ ] `awaitLoading(startTime)` for MIN_LOADING enforcement
- [ ] Loading state on container, not trigger
- [ ] `#isRefreshing` guard against double-clicks
- [ ] Error path removes loading state

### i18n
- [ ] Section name: `sections.api.{resource}.name`
- [ ] `(intern)` / `(internal)` suffix
