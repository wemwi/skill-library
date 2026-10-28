# liftr-list-filter — Filter Controls

**File:** `ui.list-filter.js` (v4.5.0)

Checkbox/radio filter controls that emit selection changes.

---

## HTML Template

```liquid
<liftr-list-filter liftr-target="store-list" liftr-field="opening">
  <fieldset>
    <legend class="sr-only">{{ 'filter.opening' | t }}</legend>
    {% for option in opening_options %}
      <label class="filter-item_component">
        <input type="checkbox" liftr-role="filter-input" liftr-value="{{ option.value }}">
        {{ option.label }}
        <span liftr-role="filter-match-count"></span>
      </label>
    {% endfor %}
  </fieldset>
</liftr-list-filter>

<script src="{{ 'ui.list-filter.js' | asset_url }}" type="module"></script>
```

---

## Required Attributes

| Attribute | On | Required | Description |
|-----------|-----|----------|-------------|
| `liftr-target` | Root | **Yes** | liftr-id of target list |
| `liftr-field` | Root | **Yes** | Field name to filter on |
| `liftr-mode` | Root | Optional | `"threshold"`, `"threshold-min"`, or `"threshold-max"` |
| `liftr-role="filter-input"` | `<input>` | **Yes** | Filter input (checkbox/radio) |
| `liftr-value` | `<input>` | **Yes** | Value to match |
| `liftr-role="filter-match-count"` | `<span>` | Optional | Shows count of matching items |
| `liftr-role="filter-count"` | `<span>` | Optional | Shows active filter count (with animation) |

---

## Threshold Mode

For numeric comparison filters. Three mode values:

| Mode | Attribute | Logic | Use Case |
|------|-----------|-------|----------|
| `threshold` | `liftr-mode="threshold"` | >= (alias for `threshold-min`) | Rating >= 4 |
| `threshold-min` | `liftr-mode="threshold-min"` | >= (aufwaerts) | Rating >= 4 |
| `threshold-max` | `liftr-mode="threshold-max"` | <= (abwaerts) | Distance <= 5000m |

### Threshold-min (Rating >= 4)

```liquid
<liftr-list-filter liftr-target="product-list" liftr-field="rating" liftr-mode="threshold">
  <fieldset>
    <legend class="sr-only">{{ 'filter.rating' | t }}</legend>
    <label>
      <input type="checkbox" liftr-role="filter-input" liftr-value="3">
      3+ Stars
      <span liftr-role="filter-match-count"></span>
    </label>
    <label>
      <input type="checkbox" liftr-role="filter-input" liftr-value="4">
      4+ Stars
      <span liftr-role="filter-match-count"></span>
    </label>
    <label>
      <input type="checkbox" liftr-role="filter-input" liftr-value="5">
      5 Stars
      <span liftr-role="filter-match-count"></span>
    </label>
  </fieldset>
</liftr-list-filter>
```

Checking "4" matches all items where `rating >= 4`.
Works even when item values (e.g. "5") don't exist as checkbox values.

### Threshold-max (Distance <= 5000m)

```liquid
<liftr-list-filter liftr-target="store-list" liftr-field="distance_m" liftr-mode="threshold-max">
  <fieldset>
    <legend class="sr-only">{{ 'filter.distance' | t }}</legend>
    <label>
      <input type="checkbox" liftr-role="filter-input" liftr-value="5000">
      {{ 'filter.max_distance' | t: distance: '5' }}
      <span liftr-role="filter-match-count"></span>
    </label>
  </fieldset>
</liftr-list-filter>
```

Checking "5000" matches items where `distance_m <= 5000`.
Items with `SORT_SENTINEL` (99999 / distance-unset) always pass.

### Match Counts

Both threshold modes use `calculateThresholdMatchCounts()` from `api.list.js`.
Cross-filter pattern applies: counts exclude own field from active filters.

| Mode | Count Logic |
|------|-------------|
| `threshold-min` | How many items have field value >= checkbox value |
| `threshold-max` | How many items have field value <= checkbox value |

### Data Flow

```
Both threshold-min and threshold-max:
  Filter emits raw checked values + mode
  -> ui.list.js routes to #activeThresholdFilters
  -> api.list.js matchesThresholdFilter() does numeric comparison

threshold-min:  itemValue >= lowest checked value  (e.g., rating >= 4)
threshold-max:  itemValue <= highest checked value (e.g., distance <= 5000)

Standard (no mode):
  Filter emits checked values
  -> ui.list.js routes to #activeFilters
  -> api.list.js matchesFilter() does discrete OR matching
```

---

## Output: liftr-state

On labels:

| Token | Meaning |
|-------|---------|
| `active` | Input is checked |
| `empty` | Match count is 0 |

---

## Events

| Event | Detail |
|-------|--------|
| `liftr:list-filter:changed` | `{ target, field, values, mode }` |
| `liftr:list-filter:register` | `{ target, field, values, mode }` |

`mode` is `null` for standard filters, `'threshold-min'` or `'threshold-max'` for threshold filters.

---

## Public API

```javascript
const filter = document.querySelector('liftr-list-filter[liftr-field="opening"]');

filter.clear();                    // Clear all selections
filter.select(['open', 'soon']);   // Select specific values
filter.targetId;                   // string
filter.field;                      // string
filter.mode;                       // string | null ('threshold-min', 'threshold-max')
filter.activeValues;               // string[]
```

---

## Module Constants

```javascript
const ROLES = Object.freeze({
  INPUT:       'filter-input',
  COUNT:       'filter-count',
  MATCH_COUNT: 'filter-match-count'
});

const STATES = Object.freeze({
  ACTIVE: 'active',
  EMPTY:  'empty'
});

const EVENTS = Object.freeze({
  CHANGED:  'changed',
  REGISTER: 'register'
});

const SETTINGS = Object.freeze({});
```

---

## Checklist

- [ ] `liftr-target` + `liftr-field` on root
- [ ] Inputs have `liftr-role="filter-input"` + `liftr-value`
- [ ] Match count spans have `liftr-role="filter-match-count"` inside label
- [ ] Threshold-min mode: `liftr-mode="threshold"` or `liftr-mode="threshold-min"` on root
- [ ] Threshold-max mode: `liftr-mode="threshold-max"` on root
- [ ] Threshold values are numeric (works with `liftr-fieldtype="number"` fields)
- [ ] Script loaded as `type="module"`
- [ ] **NO duplicate styles** from core.liftr.css
