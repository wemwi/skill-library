# liftr-range -- Range Slider

**File:** `ui.list-filter-range.js`

Single-handle range slider. Works standalone or as a list filter.

---

## HTML Template -- Standalone

```liquid
<liftr-range min="0" max="100" value="50">
  <div liftr-role="range-track">
    <div liftr-role="range-fill"></div>
    <button liftr-role="range-thumb" type="button" aria-label="{{ 'range.adjust' | t }}">
      <span liftr-role="range-display">50</span>
    </button>
  </div>
</liftr-range>

<script src="{{ 'ui.list-filter-range.js' | asset_url }}" type="module"></script>
```

## HTML Template -- List Filter (with Postal Dependency)

```liquid
<liftr-range
  liftr-target="store-list"
  liftr-field="distance_km"
  liftr-requires="postal"
  liftr-persist="true"
  min="5" max="60" step="5" value="50"
>
  <div liftr-role="range-track">
    <div liftr-role="range-fill"></div>
    <button liftr-role="range-thumb" type="button" aria-label="{{ 'range.max_distance' | t }}">
      <span liftr-role="range-display">50</span>km
    </button>
  </div>
</liftr-range>
```

---

## Required Structure

| Element | Role | Description |
|---------|------|-------------|
| `range-track` | `<div>` | Track (click to jump) |
| `range-fill` | `<div>` | Progress fill bar |
| `range-thumb` | `<button>` | Draggable handle |
| `range-display` | `<span>` | Value text (auto-updated) |

---

## Attributes

| Attribute | Required | Default | Description |
|-----------|----------|---------|-------------|
| `min` | Optional | `0` | Minimum value |
| `max` | Optional | `100` | Maximum value |
| `step` | Optional | `1` | Step increment |
| `value` | Optional | `max` | Initial value (defaults to max for "up to X" pattern) |
| `liftr-target` | For filter | -- | Target list liftr-id |
| `liftr-field` | For filter | -- | Field name to filter on |
| `liftr-requires` | Optional | -- | `"postal"` for PLZ dependency |
| `liftr-persist` | Optional | `false` | Exclude from filter count/clear |

---

## Persist Filters

When `liftr-persist` is set:
- Not counted in `list-count-filters`
- Not cleared by `clearFilters()` or clear button
- Still filters items normally

Use case: Distance range that shouldn't reset when user clears other filters.

---

## Postal Dependency

When `liftr-requires="postal"` is set:
- Starts disabled
- Enables on `liftr:location:resolved` with a valid location (emitted by `<liftr-location>`, `ui.location.js`)
- Disables again when the location becomes invalid/cleared
- No DOM watch on a postal input any more (`LISTEN.LOCATION_RESOLVED`)

---

## CSS Custom Properties (Set by JS)

| Property | Description |
|----------|-------------|
| `--range-percent` | Value as percentage (e.g. `75%`) -- drives fill width + thumb position |
| `--range-value` | Raw numeric value (e.g. `45`) |

---

## Component API (Override in Section CSS)

Defined in `ui.list.css` (`@layer modules`):

```css
liftr-range.store-filter_range {
  --range--track-bg: var(--color-scheme--text);    /* Track background (parent override) */
  --range--fill: var(--color-scheme--accent);       /* Fill color or gradient (parent override) */
  --range--text: inherit;                           /* Display text color (parent override) */
}
/* Internal (declared on liftr-range, modifier-level only):
   --range--track-height: .375rem;  --range--thumb-size: 1.875rem; */
```

---

## Output: liftr-state

| Token | Meaning |
|-------|---------|
| `disabled` | Slider disabled (e.g. no postal code) |
| `dragging` | Thumb is being dragged |

---

## Keyboard

| Key | Action |
|-----|--------|
| Arrow Right/Up | +1 step |
| Arrow Left/Down | -1 step |
| Page Up | +10 steps |
| Page Down | -10 steps |
| Home | Set to min |
| End | Set to max |

---

## ARIA

JS sets `role="slider"`, `aria-valuemin`, `aria-valuemax`, `aria-valuenow` on the thumb.

---

## Events

| Event | Detail | Scope |
|-------|--------|-------|
| `liftr:range:input` | `{ value }` | During drag (live) |
| `liftr:range:changed` | `{ value }` | After drag ends |
| `liftr:list-range:changed` | `{ target, field, max, persist }` | Global emit for list integration |

---

## Public API

```javascript
const range = document.querySelector('liftr-range');

range.value;       // get: number
range.value = 30;  // set: triggers change
range.min;         // number (read-only)
range.max;         // number (read-only)
range.step;        // number (read-only)
range.persist;     // boolean (read-only)
range.reset();     // Reset to max
range.enable();    // Enable slider
range.disable();   // Disable slider
```

---

## Module Constants

```javascript
const ROLES = Object.freeze({
  TRACK:   'range-track',
  FILL:    'range-fill',
  THUMB:   'range-thumb',
  DISPLAY: 'range-display'
});

const STATES = Object.freeze({
  DISABLED: 'disabled',
  DRAGGING: 'dragging'
});

const EVENTS = Object.freeze({
  INPUT:   'input',
  CHANGED: 'changed'
});

const SETTINGS = Object.freeze({});
```

---

## Checklist

- [ ] Track has `liftr-role="range-track"`
- [ ] Fill has `liftr-role="range-fill"` inside track
- [ ] Thumb has `liftr-role="range-thumb"` inside track
- [ ] Display has `liftr-role="range-display"` inside thumb
- [ ] For filter mode: `liftr-target` + `liftr-field`
- [ ] For persist: `liftr-persist="true"` (or just `liftr-persist`)
- [ ] For postal dependency: `liftr-requires="postal"`
- [ ] Script loaded as `type="module"`
- [ ] **NO duplicate styles** from ui.list.css
