# liftr-list-sort -- Sort Controls

**File:** `ui.list-sort.js`

Sort controls via dropdown select or button triggers.

---

## HTML Template -- Select

```liquid
<liftr-list-sort liftr-target="store-list">
  <select liftr-role="sort-select">
    <option value="">{{ 'sort.default' | t }}</option>
    <option value="name:asc">{{ 'sort.name_az' | t }}</option>
    <option value="name:desc">{{ 'sort.name_za' | t }}</option>
    <option value="distance_m:asc">{{ 'sort.nearest' | t }}</option>
  </select>
</liftr-list-sort>

<script src="{{ 'ui.list-sort.js' | asset_url }}" type="module"></script>
```

## HTML Template -- Button Triggers

```liquid
<liftr-list-sort liftr-target="store-list">
  <button liftr-role="panel-trigger" type="button">
    <span liftr-role="sort-label">{{ 'sort.label' | t }}</span>
  </button>
  <button liftr-role="sort-clear" type="button">{{ 'sort.default' | t }}</button>
  <button liftr-role="sort-trigger" liftr-value="name:asc" type="button">Name A-Z</button>
  <button liftr-role="sort-trigger" liftr-value="name:desc" type="button">Name Z-A</button>
  <button liftr-role="sort-trigger" liftr-value="bestseller:desc" type="button">Popular</button>
</liftr-list-sort>
```

---

## Required Attributes

| Attribute | On | Required | Description |
|-----------|-----|----------|-------------|
| `liftr-target` | Root | **Yes** | liftr-id of target list |
| `liftr-role="sort-select"` | `<select>` | Either select or triggers | Dropdown |
| `liftr-role="sort-trigger"` | `<button>` | Either select or triggers | Sort button |
| `liftr-value` | Trigger/Option | **Yes** | Format: `"key:direction"` (e.g. `"name:asc"`) |
| `liftr-role="sort-clear"` | `<button>` | Optional | Reset to default order |
| `liftr-role="sort-label"` | `<span>` | Optional | Dynamic label text |

---

## CSS Setting

```css
liftr-list-sort.my-sort {
  --list-sort-label: label;   /* Default: use trigger textContent */
  --list-sort-label: field;   /* Use liftr-field attribute instead */
}
```

Read once on mount via `getComputedStyle` (not `watchSettings`).

---

## Toggle Behavior

- **Paired triggers** (name:asc + name:desc) -- clicking same key toggles direction
- **Single triggers** (bestseller:desc) -- direction stays fixed, no toggle

---

## Output: liftr-state

On host:

| Token | Meaning |
|-------|---------|
| `sort-asc` | Ascending sort active |
| `sort-desc` | Descending sort active |
| `sort-{key}` | Dynamic key token (e.g. `sort-bestseller`) |

On triggers:

| Token | Meaning |
|-------|---------|
| `active` | This trigger is active |
| `sort-asc` / `sort-desc` | Direction |

On clear trigger:

| Token | Meaning |
|-------|---------|
| `active` | No sort active (default order) |

---

## CSS Targeting

```css
/* Direction icons */
liftr-list-sort[liftr-state~="sort-asc"] [liftr-role~="sort-label"]::after {
  mask-image: var(--icon--sort-asc);
}
liftr-list-sort[liftr-state~="sort-desc"] [liftr-role~="sort-label"]::after {
  mask-image: var(--icon--sort-desc);
}

/* Key-specific icons */
liftr-list-sort[liftr-state~="sort-bestseller"] [liftr-role~="sort-label"]::after {
  mask-image: var(--icon--star);
}
```

---

## Distance Sort Triggers

Sort triggers containing "distance" in `liftr-value` are auto-managed:

1. **On mount:** Disabled (no PLZ yet)
2. **On PLZ entry:** `liftr:store:distance-changed` with `valid: true` -- enabled
3. **On PLZ clear:** `liftr:store:distance-changed` with `valid: false` -- disabled

```liquid
<button liftr-role="sort-trigger" liftr-value="distance_m:asc" type="button">
  {{ 'sort.nearest' | t }}
</button>
```

CSS targeting:

```css
[liftr-role~="sort-trigger"]:disabled {
  opacity: var(--opacity--muted);
  cursor: not-allowed;
}
```

---

## Events

| Event | Detail |
|-------|--------|
| `liftr:list-sort:changed` | `{ target, key, direction }` |

---

## Public API

```javascript
const sort = document.querySelector('liftr-list-sort');

sort.clear();                          // Reset to default
sort.setSort('name', 'asc');           // Set programmatically
sort.targetId;                         // string
sort.activeKey;                        // string | null
sort.activeDirection;                  // 'asc' | 'desc'
sort.isActive;                         // boolean
```

---

## Module Constants

```javascript
const ROLES = Object.freeze({
  SELECT:  'sort-select',
  TRIGGER: 'sort-trigger',
  CLEAR:   'sort-clear',
  LABEL:   'sort-label'
});

const STATES = Object.freeze({
  SORT_ASC:  'sort-asc',
  SORT_DESC: 'sort-desc',
  ACTIVE:    'active'
});

const EVENTS = Object.freeze({
  CHANGED: 'changed'
});

const SETTINGS = Object.freeze({});
```

---

## Checklist

- [ ] `liftr-target` on root
- [ ] Select has `liftr-role="sort-select"` with `value="key:direction"` options
- [ ] OR buttons have `liftr-role="sort-trigger"` + `liftr-value="key:direction"`
- [ ] Clear button has `liftr-role="sort-clear"` (optional)
- [ ] Label span has `liftr-role="sort-label"` (optional)
- [ ] Distance triggers use `liftr-value` containing "distance" for auto-disable
- [ ] Script loaded as `type="module"`
- [ ] **NO duplicate styles** from ui.list.css
