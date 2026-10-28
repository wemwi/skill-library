# liftr-list Ecosystem — Implementation Guide

**Elements:** `<liftr-list>`, `<liftr-list-filter>`, `<liftr-list-sort>`, `<liftr-range>`
**Files:** `ui.list.js`, `ui.list-filter.js`, `ui.list-sort.js`, `ui.list-filter-range.js`, `api.list.js`
**Category:** UI Modules (Web Components) + API Module

---

## Component References

After reading this file, load ONLY the reference(s) you need:

| Working with... | Read |
|---|---|
| liftr-list (coordinator, items, counts, clear, static blocks) | `list-coordinator.md` |
| liftr-list-filter (checkbox, radio, threshold, match counts) | `list-filter.md` |
| liftr-list-sort (select, buttons, distance sort, toggle) | `list-sort.md` |
| liftr-range (slider, persist, postal dependency, keyboard) | `list-range.md` |

---

## Architecture Overview

Four components communicate via events:

```
liftr-list-filter ──→ liftr:list-filter:changed ──→ liftr-list
liftr-list-sort   ──→ liftr:list-sort:changed   ──→ liftr-list
liftr-range       ──→ liftr:list-range:changed   ──→ liftr-list
                                                      │
liftr-list ────────→ liftr:list:updated ───────────→ liftr-list-filter (match counts)
liftr-list ────────→ liftr:list:cleared ───────────→ all (reset)
liftr-list ────────→ liftr:list:mounted ───────────→ all (late registration)
```

**Key principle:** Components target a list by `liftr-target` matching `liftr-id`. They can live anywhere in the DOM — they don't need to be inside the list element.

---

## CSS Ownership — What Exists Where

### `ui.list.css` (@layer modules)

All base component styles. These rules **already exist**:

```css
/* Root display */
liftr-list, liftr-list-filter, liftr-list-sort { display: block; }
liftr-range { display: block; position: relative; }

/* List: hidden items, empty state, count badges */
liftr-list [liftr-role~="list-item"][liftr-state~="hidden"] { display: none; }
liftr-list[liftr-state~="empty"] [liftr-role~="list-empty"] { display: block; }
liftr-list[liftr-state~="empty"] [liftr-role~="list-wrapper"] { display: none; }

/* Filter: fieldset reset, match count styling */
liftr-list-filter fieldset { display: contents; }
[liftr-role~="filter-match-count"] { transition: opacity 0.15s ease-out; }

/* Sort: label direction icons (mask-image based) */
[liftr-role~="sort-label"]::after { mask-image: var(--icon--sort); ... }
liftr-list-sort[liftr-state~="sort-asc"] [liftr-role~="sort-label"]::after { ... }
liftr-list-sort[liftr-state~="sort-desc"] [liftr-role~="sort-label"]::after { ... }

/* Range: track, fill, thumb, display, disabled, dragging */
liftr-range [liftr-role~="range-track"] { ... }
liftr-range [liftr-role~="range-fill"] { width: var(--range-percent); ... }
liftr-range [liftr-role~="range-thumb"] { left: var(--range-percent); ... }
liftr-range[liftr-state~="dragging"] ... { transition: none; }
liftr-range[liftr-state~="disabled"] ... { cursor: not-allowed; filter: grayscale(1); }

/* Count badges: empty/hidden handling */
[liftr-role~="list-count-filters"]:empty { display: none; }
[liftr-role~="filter-count"]:empty { display: none; }
```

### Section CSS (your responsibility)

```css
/* Container for list items (grid/flex layout) */
.store-list_wrapper { display: grid; gap: var(--space--medium); }

/* Filter bar layout */
.store-filter-bar_component { display: flex; flex-flow: wrap; gap: var(--space--large); }

/* Filter item styling */
.store-filter_item { ... }

/* Range: color overrides (component API, consumer element) */
liftr-range.store-filter_range {
  --range--fill: var(--color-scheme--accent);
  --range--track-bg: var(--color-scheme--text);
}

/* Sort button styling */
.store-sort_trigger { ... }
```

### Summary Table

| Property | ui.list.css | Section CSS |
|----------|:-:|:-:|
| Component `display: block` | ✅ | ❌ never |
| Hidden item `display: none` | ✅ | ❌ never |
| Empty state toggle | ✅ | ❌ never |
| Count badge visibility | ✅ | ❌ never |
| Sort label direction icons | ✅ | ❌ never |
| Range track/fill/thumb positioning | ✅ | ❌ never |
| Range dragging/disabled states | ✅ | ❌ never |
| Filter match count opacity | ✅ | ❌ never |
| Reduced motion | ✅ | ❌ never |
| List item grid/layout | — | ✅ yours |
| Filter bar layout | — | ✅ yours |
| Filter/sort button design | — | ✅ yours |
| Range color overrides | — | ✅ yours |

---

## No Skeleton Loading, No core.critical.liquid

List items are rendered by Liquid and visible immediately; filters, sort and range are enhancements.
No `core.critical.liquid` entries, no skeleton for the list modules themselves (rule → `css-system.md`,
liftr-foundation). Store cards inside the list use their own skeleton (→ `store.md`, liftr-commerce).

---

## Event Communication Map

### Filter → List

```
liftr-list-filter → liftr:list-filter:changed → liftr-list
                     { target, field, values, mode }
                     mode: null | 'threshold-min' | 'threshold-max'

liftr-list-filter → liftr:list-filter:register → liftr-list
                     { target, field, values, mode }

liftr-range       → liftr:list-range:changed   → liftr-list
                     { target, field, max, persist }
```

### Sort → List

```
liftr-list-sort   → liftr:list-sort:changed    → liftr-list
                     { target, key, direction }
```

### List → Filters (feedback)

```
liftr-list → liftr:list:updated → liftr-list-filter (match counts)
             { visible, total, filters, sort, matchCounts }

liftr-list → liftr:list:cleared → liftr-list-filter, liftr-list-sort, liftr-range
             { listId }

liftr-list → liftr:list:mounted → all filters (late registration)
             { element, root, rootId }
```

### External → List

```
liftr-store → liftr:store:opening-changed  → liftr-list (re-filter)
liftr-store → liftr:store:distance-changed → liftr-list (re-filter + enable distance sort)
```

---

## Timing: Late Mount Pattern

Filters may mount **before** the target list (e.g. filter in sidebar, list in main content). Solution:

1. Filter mounts → tries to register → list doesn't exist yet → fails silently
2. List mounts → emits `liftr:list:mounted` automatically (LiftrModule)
3. Filter hears `liftr:list:mounted` → re-registers → works

**Also applies to distance data:** Stores may compute distance from saved PLZ before list mounts. List checks existing `liftr-store` states on mount via `#checkInitialDistanceState()`.

---

## Complete Example

```liquid
{%- comment -%} Filter bar {%- endcomment -%}
<div class="store-filter-bar_component">
  <liftr-list-filter liftr-target="store-list" liftr-field="opening">
    <fieldset>
      <legend class="sr-only">{{ 'filter.opening' | t }}</legend>
      <label>
        <input type="checkbox" liftr-role="filter-input" liftr-value="open">
        {{ 'filter.open_now' | t }}
        <span liftr-role="filter-match-count"></span>
      </label>
    </fieldset>
  </liftr-list-filter>

  {%- comment -%} Threshold-min: Rating ≥ 4 {%- endcomment -%}
  <liftr-list-filter liftr-target="store-list" liftr-field="rating" liftr-mode="threshold">
    <fieldset>
      <legend class="sr-only">{{ 'filter.rating' | t }}</legend>
      <label>
        <input type="checkbox" liftr-role="filter-input" liftr-value="4">
        4+ {{ 'filter.stars' | t }}
        <span liftr-role="filter-match-count"></span>
      </label>
    </fieldset>
  </liftr-list-filter>

  {%- comment -%} Threshold-max: Distance ≤ 5km {%- endcomment -%}
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

  <liftr-range
    liftr-target="store-list"
    liftr-field="distance_km"
    liftr-requires="postal"
    liftr-persist="true"
    min="5" max="60" step="5" value="50"
  >
    <div liftr-role="range-track">
      <div liftr-role="range-fill"></div>
      <button liftr-role="range-thumb" type="button" aria-label="{{ 'range.distance' | t }}">
        <span liftr-role="range-display">50</span>km
      </button>
    </div>
  </liftr-range>

  <liftr-list-sort liftr-target="store-list">
    <select liftr-role="sort-select">
      <option value="">{{ 'sort.default' | t }}</option>
      <option value="name:asc">{{ 'sort.name_az' | t }}</option>
      <option value="distance_m:asc">{{ 'sort.nearest' | t }}</option>
    </select>
  </liftr-list-sort>

  <span liftr-role="list-count-visible" liftr-target="store-list">0</span>
  /
  <span liftr-role="list-count-total" liftr-target="store-list">0</span>

  <button liftr-role="list-clear" liftr-target="store-list" type="button">
    {{ 'filter.clear' | t }}
    <span liftr-role="list-count-filters" liftr-target="store-list"></span>
  </button>
</div>

{%- comment -%} List {%- endcomment -%}
<liftr-list liftr-id="store-list">
  <div liftr-role="list-wrapper">
    {% for store in stores %}
      <div liftr-role="list-item">
        <span liftr-field="opening" liftr-value="{{ store.opening }}">{{ store.opening_label }}</span>
        <span liftr-field="distance_m" liftr-value="{{ store.distance_m }}" liftr-fieldtype="number">{{ store.distance_m }}</span>
        <span liftr-field="distance_km" liftr-value="{{ store.distance_km }}" liftr-fieldtype="number">{{ store.distance_km }}km</span>
        <span liftr-field="rating" liftr-value="{{ store.rating }}"></span>
        <span liftr-field="name" liftr-value="{{ store.name }}">{{ store.name }}</span>
      </div>
    {% endfor %}
  </div>
  <div liftr-role="list-empty">{{ 'list.no_results' | t }}</div>
</liftr-list>

{{ 'ui.list.css' | asset_url | stylesheet_tag }}
<script src="{{ 'ui.list.js' | asset_url }}" type="module"></script>
<script src="{{ 'ui.list-filter.js' | asset_url }}" type="module"></script>
<script src="{{ 'ui.list-sort.js' | asset_url }}" type="module"></script>
<script src="{{ 'ui.list-filter-range.js' | asset_url }}" type="module"></script>
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Filter not connecting to list | Check `liftr-target` matches list's `liftr-id` exactly |
| Match counts not updating | Ensure `liftr-value` on inputs matches `liftr-value` on list items |
| Threshold-min shows wrong count but filters wrong | Both use numeric path now — check `liftr-fieldtype="number"` on item fields |
| Threshold filter misses items with values not in checkboxes | This is fixed — threshold uses numeric ≥/≤, not value expansion |
| Sort not working | `liftr-value` format must be `"key:direction"` (e.g. `"name:asc"`) |
| Range not filtering | Needs both `liftr-target` AND `liftr-field` for filter mode |
| Clear button not resetting range | Range has `liftr-persist` — remove it or accept this is intended |
| Distance sort always disabled | List needs to receive `liftr:store:distance-changed` with `valid: true` |
| Filter count shows persist ranges | Persist ranges are excluded — this is correct behavior |
| Items jump when sorted | Use CSS grid/flex on wrapper — list uses `style.order` |
| DOM manipulation on items | List uses CSS order, not DOM reorder — don't `appendChild` items |
| Writing hidden/empty state CSS | Already in ui.list.css — don't duplicate |
| Static block moves during sort | Needs `liftr-list-index` attribute with positive integer |

---

## Imports

```javascript
// From list
import { ROLES, STATES, EVENTS } from 'ui.list';

// From filter
import { ROLES, STATES, EVENTS } from 'ui.list-filter';

// From sort
import { ROLES, STATES, EVENTS } from 'ui.list-sort';

// From range
import { ROLES, STATES, EVENTS, PROPERTIES } from 'ui.list-filter-range';

// API module (pure logic, no Web Component)
import {
  filterItems,
  filterItemsWithRanges,
  filterItemsCombined,           // discrete + range + threshold
  sortItems,
  calculateAllMatchCounts,
  calculateThresholdMatchCounts, // numeric ≥/≤ counting
  matchesThresholdFilter         // single item threshold check
} from 'api.list';
```
