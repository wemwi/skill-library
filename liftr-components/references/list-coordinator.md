# liftr-list — Coordinator Component

**File:** `ui.list.js`

The coordinator. Receives filter/sort events, applies logic, updates visibility and counts.

---

## HTML Template

```liquid
<liftr-list liftr-id="store-list">
  <div liftr-role="list-wrapper">
    {% for store in stores %}
      <div liftr-role="list-item">
        <span liftr-field="opening" liftr-value="{{ store.opening }}">{{ store.opening_label }}</span>
        <span liftr-field="distance_km" liftr-value="{{ store.distance }}">{{ store.distance }} km</span>
        {{ store.name }}
      </div>
    {% endfor %}

    {%- comment -%} Static block at position 3 (stays in place during sort) {%- endcomment -%}
    <div liftr-list-index="3">
      {% render 'promo-card' %}
    </div>
  </div>

  <div liftr-role="list-empty">
    {{ 'list.no_results' | t }}
  </div>
</liftr-list>

<script src="{{ 'ui.list.js' | asset_url }}" type="module"></script>
```

---

## Required Structure

| Element | Role/Attribute | Description |
|---------|---------------|-------------|
| Root | `liftr-id="..."` | **Required.** Identifier for targeting |
| Wrapper | `liftr-role="list-wrapper"` | Container for items (hidden when empty) |
| Items | `liftr-role="list-item"` | Filterable items |
| Field values | `liftr-field="..." liftr-value="..."` | Data attributes on elements inside items |
| Empty state | `liftr-role="list-empty"` | Shown when 0 visible items |
| Static blocks | `liftr-list-index="N"` | Fixed-position blocks (survive sort) |

---

## External Count/Clear Elements

These can live **anywhere** in the DOM and target the list by `liftr-target`:

```liquid
<!-- Visible/total counts -->
<span liftr-role="list-count-visible" liftr-target="store-list">0</span>
<span>of</span>
<span liftr-role="list-count-total" liftr-target="store-list">0</span>

<!-- Active filter count badge -->
<span liftr-role="list-count-filters" liftr-target="store-list"></span>

<!-- Clear all filters button -->
<button liftr-role="list-clear" liftr-target="store-list" type="button">
  {{ 'list.clear_filters' | t }}
</button>
```

---

## Output: liftr-state

| Token | Meaning |
|-------|---------|
| `empty` | 0 visible items |
| `filtered` | Non-persist filters active |
| `has-distance` | Distance data available (PLZ entered) |

---

## Sorting: CSS Order (not DOM)

List uses `style.order` instead of DOM manipulation to prevent:
- Store reconnect events (opening-changed, distance-changed)
- Infinite event loops
- Layout thrashing

Static blocks keep their `liftr-list-index` order value. Sorted items flow around them.

---

## Static Content in Lists

Static blocks (promos, featured cards) keep their position during sorting:

```liquid
<div liftr-role="list-wrapper">
  <div liftr-role="list-item">Store 1</div>
  <div liftr-role="list-item">Store 2</div>
  <div liftr-list-index="3">{% render 'promo-card' %}</div>
  <div liftr-role="list-item">Store 3</div>
</div>
```

- `liftr-list-index="3"` → `style.order: 3` (fixed)
- Sorted items get order values that skip reserved positions
- Hidden items get `order: 9999`

---

## Events

| Event | Detail | When |
|-------|--------|------|
| `liftr:list:ready` | `{ total, visible }` | After mount |
| `liftr:list:updated` | `{ visible, total, filters, sort, matchCounts }` | After filter/sort applied |
| `liftr:list:cleared` | `{ listId }` | After clear button clicked |
| `liftr:list:mounted` | `{ element, root, rootId }` | Automatic (LiftrModule) |

---

## Public API

```javascript
const list = document.querySelector('liftr-list[liftr-id="store-list"]');

list.clearFilters();       // Clear non-persist filters (discrete + threshold + range)
list.clearSort();          // Clear active sort
list.visibleCount;         // number
list.totalCount;           // number
list.filterCount;          // discrete filter count
list.rangeFilterCount;     // non-persist range filter count
list.totalFilterCount;     // discrete + threshold + non-persist range
list.hasDistanceData;      // boolean
```

---

## Module Constants

```javascript
const ROLES = Object.freeze({
  WRAPPER:       'list-wrapper',
  ITEM:          'list-item',
  COUNT_VISIBLE: 'list-count-visible',
  COUNT_TOTAL:   'list-count-total',
  COUNT_FILTERS: 'list-count-filters',
  CLEAR:         'list-clear',
  SORT_TRIGGER:  'sort-trigger',
  SIDEBAR_CLOSE: 'sidebar-close'
});

const STATES = Object.freeze({
  HIDDEN:       'hidden',
  EMPTY:        'empty',
  FILTERED:     'filtered',
  HAS_DISTANCE: 'has-distance',
  DISABLED:     'disabled'
});

const EVENTS = Object.freeze({
  READY:   'ready',
  UPDATED: 'updated',
  CLEARED: 'cleared'
});

const SETTINGS = Object.freeze({});
```

---

## Checklist

- [ ] `liftr-id` set on root
- [ ] Items have `liftr-role="list-item"` with `liftr-field` + `liftr-value` data
- [ ] Wrapper has `liftr-role="list-wrapper"`
- [ ] Empty state has `liftr-role="list-empty"`
- [ ] External count elements have `liftr-target` matching list's `liftr-id`
- [ ] Static blocks have `liftr-list-index` with positive integer
- [ ] Script loaded as `type="module"`
- [ ] **NO duplicate styles** from ui.list.css
- [ ] **NO skeleton loading** attributes
