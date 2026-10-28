---
name: liftr-shop
description: "Integration guide for the LIFTR Shop API (api.shop.js). Covers Cart API (add, update, remove, clear, setNote), Rewards system (thresholds, free product auto-add/remove), Product Registry (variant selection, option availability), pricing helpers (formatMoney, isOnSale, calculateDiscount), and all shop events. Use whenever working with cart operations, reward thresholds, variant selection, product pricing, discount codes, or any Shopify cart/product integration within the LIFTR ecosystem. Also use when debugging cart merging, reward progress calculation, or variant unavailable errors."
---

# liftr-shop — LIFTR Shop API

**Version:** 4.9.0
**Source:** `api.shop.js`
**Global:** `window.liftrShop`

---

## 1. Quick Reference

```javascript
// Cart
const cart = liftrShop.cart.get();
await liftrShop.cart.add({ id: 12345, quantity: 2 });
await liftrShop.cart.update(key, 3);
await liftrShop.cart.remove(key);
await liftrShop.cart.setNote('Bitte als Geschenk verpacken');
await liftrShop.cart.clear();

// Rewards
const progress = liftrShop.getRewardProgress();

// Pricing
liftrShop.formatMoney(1999);              // "19,99 EUR"
liftrShop.isOnSale(variant);              // true/false
liftrShop.calculateDiscount(2999, 1999);  // 33

// Product Registry
const handle = liftrShop.registerProduct(productId, productData);
handle.selectOption(0, 'Rot');
handle.getVariant();
```

---

## 2. Initialization

```javascript
// Auto-init on import
import './api.shop.js';

// Wait for ready
document.addEventListener('liftr:shop:ready', (e) => {
  const cart = e.detail.cart;
});

// Or manual
await liftrShop.init();
if (liftrShop.isInitialized()) { /* ... */ }
```

---

## 3. Cart API

### cart.add(items)

```javascript
// Single
await liftrShop.cart.add({ id: 12345678, quantity: 2, properties: { '_gift_wrap': 'true' } });

// Multiple
await liftrShop.cart.add([
  { id: 12345678, quantity: 1 },
  { id: 87654321, quantity: 2 }
]);
// Returns: { addedItems: [...], cart: {...} }
```

Events: `liftr:shop:cart-adding` (before), `liftr:shop:cart-added` (after), `liftr:shop:reward-progress` (if applicable)

### cart.update(key, quantity)

```javascript
await liftrShop.cart.update('abc123:def456', 3);  // Change quantity
await liftrShop.cart.update('abc123:def456', 0);   // Remove
// Returns: cart object
```

Events: `liftr:shop:cart-updating` (before), `liftr:shop:cart-updated` (after)

### cart.remove(key)

Shortcut for `update(key, 0)`.

### cart.setNote(note)

```javascript
await liftrShop.cart.setNote('Bitte als Geschenk verpacken');
```

Events: `liftr:shop:cart-updating`, `liftr:shop:cart-updated` (action: 'note_changed')

### cart.clear()

Events: `liftr:shop:cart-updating`, `liftr:shop:cart-cleared`, `liftr:shop:reward-locked` (per reward)

### cart.get() — Enhanced

```javascript
const cart = liftrShop.cart.get();
// Standard Shopify fields + enhanced:
// cart.rewardsProgress = { subtotal, subtotalFormatted, rewards: [...], nextReward }
```

---

## 4. Rewards API

### getRewardProgress()

```javascript
const progress = liftrShop.getRewardProgress();
// { subtotal, subtotalFormatted, rewards: [{ type, name, threshold,
//   thresholdFormatted, unlocked, percent, remaining, remainingFormatted }],
//   nextReward }
```

### Reward Types

| Type | Behavior |
|------|----------|
| `"Free shipping"` | Visual indicator only |
| `"Free product"` | Auto-adds/removes product at threshold |
| `"Discount percent"` | Visual indicator only |

### Free Product Logic

- **Unlock:** Product auto-added with `_liftr_reward` property
- **Lock:** Product auto-removed when dropping below threshold

```liquid
{%- if item.properties['_liftr_reward'] -%}
  <!-- Reward item -- hide quantity controls -->
{%- endif -%}
```

### Threshold Calculation Gotcha

Use `total_price` (post-discount) minus reward item costs, NOT `original_line_price`.

### Configuration

```javascript
// In settings.market.rewards
{
  rewards: [
    {
      type: "Free shipping",
      name: "Kostenloser Versand",
      threshold: { amount: "40.0", currency_code: "EUR" }
    },
    {
      type: "Free product",
      name: "Gratis Tee",
      threshold: { amount: "60.0", currency_code: "EUR" },
      free_product: "gid://shopify/ProductVariant/12345"
    }
  ]
}
```

---

## 5. Product Registry

Client-side variant selection without page reload.

```javascript
const handle = liftrShop.registerProduct(productId, {
  variants: product.variants,
  options: product.options,
  selectedVariant: currentVariant
});
```

### Handle Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `getVariant()` | variant object | Currently selected variant |
| `getOptions()` | string[] | Current option selections |
| `selectOption(index, value)` | `{ success, variant }` | Select option by index |
| `selectVariant(variantId)` | `{ success, variant }` | Select variant directly |
| `isOptionAvailable(index, value)` | boolean | Check if combo is in stock |
| `unregister()` | void | Remove from registry |

Events on selectOption: `liftr:shop:variant-changed` (success) or `liftr:shop:variant-unavailable` (failure)

---

## 6. Pricing API

```javascript
liftrShop.formatMoney(1999);              // "19,99 EUR" (uses Shopify currency)
liftrShop.isOnSale(variant);              // Has compare-at price?
liftrShop.calculateDiscount(2999, 1999);  // 33 (rounded percentage)
```

---

## 7. Events

| Event | Detail | Layer |
|-------|--------|-------|
| `liftr:shop:ready` | `{ cart }` | Data |
| `liftr:shop:cart-adding` | `{ items }` | Data |
| `liftr:shop:cart-added` | `{ addedItems, cart }` | Data |
| `liftr:shop:cart-updating` | `{ key?, quantity?, action? }` | Data |
| `liftr:shop:cart-updated` | `{ cart, action, key?, quantity? }` | Data |
| `liftr:shop:cart-cleared` | `{ cart }` | Data |
| `liftr:shop:reward-progress` | `{ subtotal, rewards, nextReward }` | Data |
| `liftr:shop:reward-unlocked` | `{ type, name, threshold }` | Data |
| `liftr:shop:reward-locked` | `{ type, name, threshold }` | Data |
| `liftr:shop:variant-changed` | `{ productId, variant, previousVariant }` | Data |
| `liftr:shop:variant-unavailable` | `{ productId, attemptedOptions }` | Data |
| `liftr:shop:error` | `{ action, error }` | Data |

All shop events are **Data Layer** events (immediate, data changed). DOM-replacing modules should listen to **UI Layer** events instead (e.g. `liftr:product:added`).

---

## 8. Error Handling

### Error Object

```javascript
{
  code: 'SHOPIFY_ERROR' | 'NETWORK_ERROR' | 'INVALID_ITEM' | 'INVALID_QUANTITY',
  status: 422,           // HTTP status (for SHOPIFY_ERROR)
  message: 'Description',
  details: { ... }       // Original error data
}
```

### Pattern

```javascript
try {
  await liftrShop.cart.add({ id: 123, quantity: 1 });
} catch (error) {
  if (error.code === 'SHOPIFY_ERROR') {
    liftrNotification.error('Fehler', error.message);
  }
}

// Or via event
on('liftr:shop:error', (e) => {
  const { action, error } = e.detail;
});
```

---

## 9. Gotchas

- **Cart item merging:** Shopify splits identical variants when automatic discounts apply. LIFTR merges them visually using `liftr-merge` attribute.
- **`#isRewardItem()`:** Check only `_liftr_reward` property, not variant ID set membership.
- **`{{ product | json }}`** excludes `inventory_quantity` -- must manually build product JSON in Liquid.
- **Money metafields in Liquid:** Use `| json` filter to serialize nil as null (prevents invalid JSON).
- **Shopify Cart API `discount` parameter (Summer '25):** Supports applying discount codes via `/cart/update.js`.
