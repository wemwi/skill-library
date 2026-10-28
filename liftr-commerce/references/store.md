# LIFTR Store

Reference guide for the Store Finder ecosystem.
A store card is assembled from **several** snippets. Documented here: `store.liquid` (card root),
`store-data.liquid` (hidden filter fields + JSON payload) and `store-panel.liquid` (sidebar detail).
The rest of the family is listed in §2 — do not assume the ecosystem is only these three.

---

## 1. Metaobject Schema

### `liftr_store` — Core Object

Access in Liquid: `store` (passed as parameter to snippet)

| Field | Key | Type | Required | Access Pattern |
|-------|-----|------|----------|----------------|
| Name | `name` | single_line_text | ✓ | `store.name` |
| Banner | `banner` | file_reference | – | `store.banner` |
| Image | `image` | file_reference | ✓ | `store.image` |
| Products | `product_list` | list.product_reference | ✓ | `store.product_list` (Array) |
| Collections | `collection_list` | list.collection_reference | ✓ | `store.collection_list` (Array) |
| Assortment | `assortment_list` | list.metaobject_reference | – | `store.assortment_list` (Array → `liftr_assortment`) |
| Service | `service_list` | list.metaobject_reference | – | `store.service_list` (Array → `liftr_service`) |
| Rating | `rating` | rating | ✓ | `store.rating.value` → float (e.g. `4.5`) |
| Rating Count | `rating_count` | number_integer | ✓ | `store.rating_count` |
| Address | `adress` | single_line_text | ✓ | `store.adress` ⚠️ typo in schema, intentional |
| Postal Code | `postal_code` | number_integer | ✓ | `store.postal_code` |
| City | `city` | metaobject_reference | ✓ | `store.city.value` → `liftr_city` object |
| District | `district` | metaobject_reference | ✓ | `store.district.value` → `liftr_district` object |
| Phone | `phone` | single_line_text | ✓ | `store.phone` |
| TikTok | `tiktok` | single_line_text | – | `store.tiktok` |
| Facebook | `facebook` | single_line_text | – | `store.facebook` |
| Instagram | `instagram` | single_line_text | – | `store.instagram` |
| WhatsApp | `whatsapp` | single_line_text | – | `store.whatsapp` |
| Website | `website` | url | – | `store.website` |
| Google Place | `google_place` | json | ✓ | `store.google_place.value` (JSON Object) |
| Opening Hours | `opening_hours` | json | ✓ | `store.opening_hours.value` (Google composite `{regular, current}`) |
| ~~Opening Hours (Holiday)~~ | ~~`opening_hours_holiday`~~ | – | – | **Removed from the definition.** Holidays now come from Google (`current.periods`). |
| Highlight | `highlight` | boolean | – | `store.highlight` |
| Featured | `featured` | boolean | – | `store.featured` |
| New | `new` | boolean | – | `store.new` |

**System fields** (always available on any metaobject):

| Field | Access | Example |
|-------|--------|---------|
| Handle | `store.system.handle` | `"kratom-koenig-berlin"` |
| Created At | `store.system.created_at` | Unix timestamp via `\| date: '%s'` |
| ID | `store.system.id` | GID string |

---

### Related Metaobjects

#### `liftr_city` — Referenced by `store.city`

Access: `store.city.value`

| Field | Key | Type | Access |
|-------|-----|------|--------|
| Name | `name` | single_line_text | `store.city.value.name.value` |
| Image | `image` | file_reference | `store.city.value.image` |
| Postal Codes | `postal_codes` | json | `store.city.value.postal_codes.value` |
| Country | `country` | single_line_text | `store.city.value.country.value` |

⚠️ **Deep chain:** `store.city.value.name.value` — two `.value` levels needed.
`store.city` → metaobject_reference → `.value` → `liftr_city` → `.name` → metafield → `.value` → String.

#### `liftr_district` — Referenced by `store.district`

Access: `store.district.value`

| Field | Key | Type | Access |
|-------|-----|------|--------|
| Name | `name` | single_line_text | `store.district.value.name.value` |
| City | `city` | metaobject_reference | `store.district.value.city.value` |

#### `liftr_assortment` — Referenced by `store.assortment_list[]`

| Field | Key | Type | Access |
|-------|-----|------|--------|
| Name | `name` | single_line_text | `item.name.value` |

#### `liftr_service` — Referenced by `store.service_list[]`

| Field | Key | Type | Access |
|-------|-----|------|--------|
| Name | `name` | single_line_text | `item.name.value` |
| Order | `order` | number_integer | `item.order` |

---

### Deep Access — Common Patterns

```liquid
{%- liquid
  # City name (two .value levels)
  assign city_name = store.city.value.name.value

  # District name
  assign district_name = store.district.value.name.value

  # Handle for IDs and JS data
  assign store_handle = store.system.handle

  # Maps query
  assign maps_query = store.adress
    | append: ', '
    | append: store.postal_code
    | append: ' '
    | append: city_name
    | url_encode

  # Opening hours for JS (always use .value on JSON fields)
  # store.opening_hours.value = Google composite { regular, current } — passed through raw
  assign hours_regular = store.opening_hours.value

  # Google Place for JS
  assign google_place = metaobjects.liftr_store[store_handle].google_place.value
-%}
```

⚠️ **JSON fields:** Always use `.value` — `store.opening_hours` is a metafield, not the raw value.

⚠️ **`adress` typo:** The schema key is `adress` (one `d`). This is intentional and must be preserved.

---

## 2. Snippet API

### `store.liquid`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `store` | Object | required | `liftr_store` metaobject |
| `class` | String | `''` | Additional CSS classes on root |

**Usage:**

```liquid
{% render 'store', store: store_object %}
{% render 'store', store: store_object, class: 'is-featured' %}
```

### `store-data.liquid`

The hidden data payload of a card. **No visual output, no CSS.** It renders exactly two things:

1. the `<script type="application/json" liftr-role="store-data">` block (→ §8), and
2. the hidden `<div>` with the `liftr-field` spans consumed by `liftr-list` (→ §4).

It also **computes** `new_score` and `rating_score` itself (→ §7) — those formulas live in this file,
nowhere else.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `store` | Object | required | `liftr_store` metaobject |

**Guard Contract:** the caller passes a valid store object. The snippet does **not** guard against a
blank `store`.

Rendered as the **last** child of `<liftr-store>` in `store.liquid`, after `store-panel` — do not
render separately.

```liquid
{%- comment -%} Already called inside store.liquid {%- endcomment -%}
{%- render 'store-data', store: store -%}
```

### `store-panel.liquid`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `store` | Object | required | Same `liftr_store` metaobject |

Rendered near the end of `store.liquid` (before `store-data`) — do not render separately.

```liquid
{%- comment -%} Already called inside store.liquid {%- endcomment -%}
{% render 'store-panel', store: store %}
```

### Rest of the snippet family — not documented here

`store.liquid` and `store-panel.liquid` delegate further. Verified against `main` (28.10.2026), the
`snippets/` folder also holds: `store-highlights`, `store-info`, `store-product`, `store-query`,
`store-panel-assortment`, `store-panel-opening`, `store-panel-products`, `store-panel-service`.
They have no section in this guide — read the file before assuming its API.

---

## 3. HTML Structure

```html
<liftr-store liftr-state="loading" liftr-role="list-item" class="store_component">

  <!-- Store Image + Badges -->
  <div class="store_image media-wrapper" liftr-skeleton="true">...</div>

  <!-- Store Profile -->
  <div class="store_profile">
    <div class="store_main">
      <div class="store_name">
        <h3>
          <span liftr-field="name">{{ store.name }}</span>
          <span liftr-field="district">{{ store.district.value.name }}</span>
        </h3>
      </div>
      <!-- rating, address-link -->
    </div>

    <div class="store_meta">
      <!-- Distance (store_distance) -->
      <!-- Opening Hours (store_opening) -->
    </div>

    <!-- Panel Toggle -->
    <div class="store_toggle">
      <button liftr-role="panel-toggle" liftr-target="store-panel-{handle}" ...>
    </div>
  </div>

  <!-- Sidebar Panel (store-panel.liquid) -->

  <!-- Hidden payload — LAST child, rendered by store-data.liquid (§2) -->
  {%- render 'store-data', store: store -%}

  <!-- Structured Data -->
  {% render 'schema', type: 'local-business', store: store %}

</liftr-store>
```

⚠️ **Neither the JSON block nor the hidden filter fields are written inline in `store.liquid`.**
Both come from `store-data.liquid`, which expands to:

```html
<script type="application/json" liftr-role="store-data">
  { "handle": "...", "google_place": {...}, "schedule": { "regular": {...} } }
</script>

<div hidden>
  <span liftr-field="name">…</span>
  <span liftr-field="district">…</span>
  <span liftr-field="CITY">…</span>
  <span liftr-field="opening"       liftr-value=""></span>
  <span liftr-field="distance_m"    liftr-value="99999" liftr-fieldtype="number"></span>
  <span liftr-field="distance_km"   liftr-value="50"    liftr-fieldtype="number"></span>
  <span liftr-field="distance_near" liftr-value=""></span>
  <span liftr-field="new_score"     liftr-value="…" liftr-fieldtype="number"></span>
  <span liftr-field="rating_score"  liftr-value="…" liftr-fieldtype="number"></span>
  <span liftr-field="rating"        liftr-value="4.5"></span>   <!-- only if store.rating -->
  <span liftr-field="featured"      liftr-value="1"></span>     <!-- only if featured/highlight -->
  <span liftr-field="products"      liftr-value="{handle}"></span> <!-- one per product -->
</div>
```

The payload sits **after** the panel, not before the image — the ordering in the sketch above is the
real one. Field semantics → §4, JSON shape → §8, score formulas → §7.

---

## 4. liftr-Roles Reference

Roles used across the card — set in Liquid, read by `liftr-store` JS. All of them sit in
`store.liquid` **except** `store-data`, which `store-data.liquid` renders.

| Role | Element | Purpose |
|------|---------|---------|
| `list-item` | `<liftr-store>` root | Marks as item for `liftr-list` |
| `store-data` | `<script>` | JSON payload: handle, google_place, schedule — from `store-data.liquid` |
| `store-label-info` | Distance info wrapper | Shown when distance is calculated |
| `store-label-unknown` | Unknown PLZ wrapper | Shown when PLZ not found |
| `store-action-toggle` | PLZ input toggle | Shown when no PLZ entered (distance-unset) |
| `store-distance-value` | `<span>` | Distance number, set by JS |
| `store-label-unit` | `<span>` | Unit (km/m), set by JS |
| `store-link-walking` | `<a>` | Walking route link, set by JS |
| `store-link-bicycling` | `<a>` | Cycling route link, set by JS |
| `store-link-driving` | `<a>` | Driving route link, set by JS |
| `store-label-walking` | `<span>` | Walking time text, set by JS |
| `store-label-bicycling` | `<span>` | Cycling time text, set by JS |
| `store-label-driving` | `<span>` | Driving time text, set by JS |
| `live-label-next` | `<span>` | Next opening/closing time, set by JS |
| `panel-toggle` | `<button>` | Opens store-panel sidebar |

**Filter/Sort fields** (`liftr-field` on hidden `<span>`) — **all rendered by `store-data.liquid`**,
consumed by `liftr-list`:

| Field | `liftr-fieldtype` | Rendered | Source |
|-------|-------------------|----------|--------|
| `name` | – (text content) | always | `store.name` |
| `district` | – (text content) | always | `store.district.value.name` |
| `CITY` | – (text content) | always | `store.city.option.name.value` ⚠️ see below |
| `opening` | – | always | empty at render — filled by JS (live-plugin) |
| `distance_m` | `number` | always | `99999` at render — filled by JS (distance-calculator) |
| `distance_km` | `number` | always | `50` at render — filled by JS (distance-calculator) |
| `distance_near` | – | always | empty at render — filled by JS (distance-calculator) |
| `new_score` | `number` | always | computed in `store-data.liquid` (→ §7) |
| `rating_score` | `number` | always | computed in `store-data.liquid` (→ §7) |
| `rating` | – | only `{% if store.rating %}` | `store.rating.value \| round: 1` |
| `featured` | – | only if `store.featured` **or** `store.highlight` | literal `"1"` |
| `products` | – | one span per product | `p.handle` over `store.product_list.value` |

⚠️ **`rating` and `featured` carry no `liftr-fieldtype`** — they are string fields to `liftr-list`
despite `rating` holding a number. Do not "fix" this from the doc side; it is what `main` renders.

⚠️ **`featured` is an OR of two metaobject fields.** `store.highlight` alone also emits
`featured="1"` (`is_featured_store` guard). There is no separate `highlight` field.

⚠️ **`CITY` is uppercase and uses `.option`, not `.value`** — `store.city.option.name.value`, unlike
every other city access in the theme (`store.city.value.name.value`, see §1). Both oddities are
verbatim from `main` (28.10.2026); flagged, not fixed here.

⚠️ **`name` / `district` / `CITY` use text content, not `liftr-value`** — the remaining fields use the
`liftr-value` attribute.

---

## 5. liftr-States Reference

States set by `liftr-store` JS on the `<liftr-store>` root element.

### Distance States

| State | Condition | CSS Effect |
|-------|-----------|------------|
| `distance-unset` | No PLZ entered | Shows PLZ toggle button |
| `distance-near` | < 3km | Shows walking + cycling links |
| `distance-mid` | 3–7km | Shows cycling + driving links |
| `distance-far` | 7–12km | Shows cycling + driving links |
| `distance-remote` | > 12km | Shows driving link only |
| `distance-unknown` | PLZ not found in liftr_city.postal_codes | Shows unknown message |

### Opening States (set by live-plugin)

| State | Meaning |
|-------|---------|
| `open` | Store currently open |
| `closed` | Store currently closed |
| `opening` | Opens within the closing threshold (**default 30 min**, `DEFAULTS.closingThresholdMin`) |
| `closing` | Closes within the same threshold (**default 30 min**). All-day windows never fire `closing`. |

---

## 6. CSS API

### `snippet.store.css` — Extension API (colors only)

Sizing is owned by the density CQs and not overridable (→ `card-architecture.md`, Extension API).
Parent override or `custom-colors`:

```css
/* Parent override example (section.store-list.css) */
.store-list_component liftr-store {
  --store--background: var(--color-scheme--background);
}
```

| Variable | Fallback | Description |
|----------|---------|-------------|
| `--store--background` | `color-scheme--card` | Card background |
| `--store--text` | `color-scheme--text` | Card text |
| `--store--accent` | `color-scheme--link` | Hover/link states |
| `--store--button-primary` | `color-scheme--background` | Action button background |
| `--store--button-primary-text` | `color-scheme--text` | Action button text |

### `snippet.store.css` — Panel Color Overrides

⚠️ There is **no** `snippet.store-panel.css`. The panel styles live in the same `snippet.store.css`
as the card variables above.

Set via `custom-colors` snippet or Parent Override:

| Variable | Fallback | Description |
|----------|---------|-------------|
| `--store-panel--text` | `color-scheme--text` | Panel text color |
| `--store-panel--background` | `color-scheme--background` | Panel background |
| `--store-panel--card` | `color-scheme--card` | Card elements inside panel |
| `--store-panel--accent` | `color-scheme--accent` | Partner callout, today marker |
| `--store-panel--border` | `color-scheme--border` | Dividers |
| `--store-panel--grey` | `color-scheme--grey` | Muted surfaces inside the panel |

---

## 7. Sort Score Formulas

Two computed scores for `liftr-list` sorting. **Both are calculated in the DATA block of
`store-data.liquid`** (→ §2) — not in the section head, not in `store.liquid`. Change them there;
this section is a mirror, not the source.

### `new_score` — "Newest" Sort

```liquid
assign new_score = store.system.created_at | date: '%s' | plus: 0
if store.new
  assign new_score = new_score | plus: 9999999999
endif
```
`store.new = true` → always sorts above non-new stores; within each group by creation date.

### `rating_score` — "Popular" Sort

```liquid
assign rating_score = 0
if store.rating
  assign rs_avg     = store.rating.value | append: '' | plus: 0.0
  assign rs_count   = store.rating_count | default: 0 | plus: 0
  assign rs_divisor = rs_count | plus: 1
  assign rs_penalty = 1.0 | divided_by: rs_divisor
  assign rs_weight  = 1.0 | minus: rs_penalty
  assign rating_score = rs_avg | times: rs_weight | times: 10000.0 | round
endif
```

Formula: `avg × (1 − 1/(count + 1)) × 10000` — penalizes low review counts.
`4.5★ × 200 reviews = 44776`, `4.5★ × 2 reviews = 30000`.
Stores without rating keep the initial `0` (sort to bottom on "Popular").
Identical formula to `product.liquid`.

⚠️ **The penalty needs its own `assign`.** Liquid filters chain left to right, so
`1.0 | minus: 1.0 | divided_by: rs_divisor` computes `(1.0 − 1.0) / divisor = 0`, not
`1 − 1/divisor` — that would zero every score. `main` splits it into `rs_penalty` then `rs_weight`.

---

## 8. JS Data Payload

The `<script type="application/json" liftr-role="store-data">` block feeds the `liftr-store` Web Component.
**It is rendered by `store-data.liquid`** (→ §2), as the last child of `<liftr-store>`.

```json
{
  "handle": "kratom-koenig-berlin",
  "google_place": { ... },
  "schedule": {
    "regular": { "regular": { "periods": [ ... ] }, "current": { "periods": [ ... ], "specialDays": [ ... ] } }
  }
}
```

⚠️ **`schedule.regular` carries the whole Google composite.** The Liquid is unchanged — it still pipes
`opening_hours.value` into `schedule.regular`. Since that field now holds `{regular, current}`, the
composite lands one level down. `createOpeningCore` detects the shape via `isGoogleOpeningHours()` and
normalizes it. There is no `schedule.holiday` any more — the store-side dual-read cleanup is done
(`ui.store.js` no longer reads a store holiday override).

Access in Liquid (`store-data.liquid`, HTML OUTPUT block):

```liquid
"google_place": {{ metaobjects.liftr_store[store_handle].google_place.value | json }},
"schedule": {
  "regular": {{ metaobjects.liftr_store[store_handle].opening_hours.value | json }}
}
```

⚠️ Accessed via `metaobjects.liftr_store[handle]` instead of `store.*` — JSON fields on nested metaobjects sometimes need this direct access pattern.

The legacy branch in `createOpeningCore` stays (see the dual-read note below).
**`regular` is mandatory:** if `opening_hours.value` is missing, `#readStoreData` throws
`[store] Missing schedule.regular` — which is why `pos-sync` never overwrites with an empty
`regularOpeningHours`.

### `google_place` JSON Structure

```json
{
  "id": "ChIJjy9mLW11sEcRcapsK62rHEk",
  "displayName": "AR Kiosk",
  "formattedAddress": "Gerberstraße 14, 30169 Hannover, Deutschland",
  "location": {
    "lat": 52.3759568,
    "lng": 9.7213348
  }
}
```

Access in Liquid: `store.google_place.value` → parsed object. Used by `liftr-store` JS for map linking and distance calculation.

### `opening_hours` JSON Structure — Google composite (Places API **New**)

`opening_hours` holds Google's answer raw. Google is the single source for regular hours **and**
holidays; `pos-store` writes it without transforming, `pos-sync` refreshes it every 7 days.

```json
{
  "regular": {
    "periods": [
      { "open": { "day": 1, "hour": 8, "minute": 30 }, "close": { "day": 1, "hour": 23, "minute": 30 } },
      { "open": { "day": 5, "hour": 0, "minute": 0 },  "close": { "day": 0, "hour": 0, "minute": 0 } }
    ],
    "weekdayDescriptions": [ "..." ]
  },
  "current": {
    "periods": [
      { "open": { "date": { "year": 2026, "month": 7, "day": 16 }, "day": 4, "hour": 8, "minute": 30 },
        "close": { "date": { "year": 2026, "month": 7, "day": 16 }, "day": 4, "hour": 23, "minute": 30 } }
    ],
    "specialDays": [ { "date": { "year": 2026, "month": 12, "day": 25 } } ]
  }
}
```

- **`regular`** — weekday-based (`day` 0=Sun..6=Sat), no calendar dates, **no holidays**. Drives the
  recurring week display and the live-status baseline.
- **`current`** — rolling 7-day window, **dated** periods (`open.date`). Holiday hours live **in these
  periods**. Drives per-store date overrides.
- **`specialDays[]` is a marker only** — per the Places REST v1 reference it contains just `{date}`,
  **no hours**. Never read it as an hours source.
- **`openNow` / `nextOpenTime` / `nextCloseTime`** appear in both parts and go stale the moment they are
  stored. **Never read them** — the live status is always computed from the periods.

#### `truncated` — a window edge, never a time

`current.periods` is a **rolling 7-day window**. If the real hours reach beyond it, Google clips the period
to the window edge and marks that endpoint with `truncated: true`.

- A truncated endpoint is **never** an opening or closing time. Never read it as one.
- If **both** edges of a period are truncated, the period carries **no time information** at all — it just
  says "open throughout the whole window". The days it covers are marked all-day, and the closing-edge day
  gets **no** override, so `regular` applies there.
- `buildOverrideFromCurrent` therefore reads `close.truncated === true` as *no known end*: days
  D…D+nSpan−1 become all-day (start day `[oMin, 1440]` when `oMin > 0`), day D+nSpan stays without an
  override. `open.truncated` needs no special case — `oMin` is already `0` at the window edge.

Real case — `kiosk-am-doehrener-turm`, a 24/7 store:

```json
"regular": { "periods": [ { "open": { "day": 0, "hour": 0, "minute": 0 } } ] }
"current": { "periods": [
  { "open":  { "day": 4, "hour": 0,  "minute": 0,  "truncated": true, "date": { "year": 2026, "month": 7, "day": 16 } },
    "close": { "day": 3, "hour": 23, "minute": 59, "truncated": true, "date": { "year": 2026, "month": 7, "day": 22 } } }
] }
```

`regular` has an open without a `close` → 24/7. Read naively, `current` says "closes at 23:59" for a store
that never closes. Handled in `api.live.js`.

#### Internal model — spans (`api.live.js`)

The normalizer emits **spans**, not day-split minute windows. A span is `[startMin, endMin]`, or
`[0, 1440, true]` for all-day.

- Coordinates are **minutes from `00:00` of the anchor day** (the `open` day resp. `open.date`).
- `endMin` may run **past 1440**; `startMin` goes **negative** once a previous day's span is carried into
  today (`spansForDate(anchor, { includeCarry })` shifts carried spans by `−k × 1440`).
- A window crossing midnight is **never split at the day boundary** — it stays one span on the open day.
- Output takes the end **modulo the day**: `1440` → `"00:00"`, `1500` → `"01:00"`
  (`fmtTime(closesMin % 1440)`).

**Period cases the normalizer handles** (`spansForPeriod` via `normalizeGoogleOpeningHours`, `api.live.js`).
`nSpan` = midnights crossed, `oMin`/`cMin` = open/close minute:

| Case | Google encoding | Internal span |
|---|---|---|
| 24/7 | open period with **no `close`** | `[0, 1440, true]` on **every** weekday |
| Same day | `nSpan = 0`, `cMin > oMin` | `[oMin, cMin]` on the open day |
| Degenerate | `nSpan = 0`, `cMin === oMin` | `[0, 1440, true]` — read as all-day |
| **Multi-day 24 h** | `oMin = 0` **and** `cMin = 0`, `nSpan ≥ 1` | every day D…D+nSpan−1 all-day |
| Overnight / multi-day wrap | anything else with `nSpan ≥ 1` | **one** span on the open day `[oMin, nSpan × 1440 + cMin]`; inner days D+1…D+nSpan−1 all-day; **end day D+nSpan gets no entry** |
| Split hours | several periods on the same `open.day` | several spans that day (merged when they touch or overlap) |
| Closed | no period for that day | `[]` |

> **Seam merge** (`seamMergeWeek`). If day D ends on a *finite* span at exactly `1440` and day D+1 starts on
> a *finite* span at `0`, the two collapse into **one** span on D (`[start, 1440 + endₙ]`) and the D+1 entry
> disappears. A finite chain that closes all the way around the week is capped to 24/7. All-day days do not
> take part — structural multi-day 24 h stays one `[0, 1440, true]` per day for the week table.

> **Group by the explicit `day` field, never by array position.** The Places reference states the
> `periods` order is not fixed (it does not necessarily start on Sunday) and is independent of
> `weekdayDescriptions`. Verified case: Callin has Fri **and** Sat as 24 h in **one** period
> (`open{day:5,00:00}` → `close{day:0,00:00}`) with **no** Saturday period — grouping by `open.day`
> alone would silently show Saturday as closed.

**Dual-read.** `createOpeningCore({ regular })` accepts **both** shapes: the legacy weekday
map `{mon..sun: [["09:00","18:00"]]}` and the Google composite. `isGoogleOpeningHours()` picks the path;
both end up in the same span model (legacy overnight `b < a` → `[a, b + 1440]`, no split, no carry).

⚠️ **The legacy branch is not going away.** It is not leftover store scaffolding: the market schedules from
`settings.market` (`ui.service.js`, `ui.store-summary.js`) keep feeding that weekday map into the same core. The
**store-side** dual-read is already gone — do not document the remaining branch as legacy cruft.

**Resolution priority in `spansForDate` / `daySpans`:** 1. per-store `overrideByISO[iso]` (from Google `current`) →
2. market-global holiday slug (legacy only) → 3. `regular[weekdayKey]`. For Google stores the per-store
ISO override **replaces** the market-global slug mechanism (`ui.store.js` no longer passes
`holidayBySlug`/`holidaySlugByISO`).

**Timezone:** market-global (`settings.market.timezone`, default `Europe/Berlin`) — **not** per store.
Google's `timeZone`/`utcOffsetMinutes` are not stored.

Access in Liquid: `store.opening_hours.value` → parsed object. Passed **as-is** to the `liftr-store` JS payload.

---

## 9. Panel ID Convention

Each store card renders its own `<liftr-panel>` with a unique ID:

```liquid
assign id_panel = 'store-panel-' | append: store_handle
```

The panel toggle button references this via `liftr-target`:

```html
<button liftr-role="panel-toggle" liftr-target="store-panel-{{ store_handle }}">
```

---

## 10. Gotchas

| Gotcha | Detail |
|--------|--------|
| `adress` typo | Schema key is `adress` (one d) — intentional, do not fix |
| Deep `.value` chain | `store.city.value.name.value` — TWO `.value` needed for referenced metaobject fields |
| JSON fields | `store.opening_hours.value`, `store.google_place.value` — always `.value` |
| `distance-unset` initial state | JS sets this on mount; `liftr-state="loading"` is initial HTML state |
| Rating access | `store.rating.value` for float — `store.rating` alone returns metafield object |
| `rating_count` has no `.value` | `number_integer` fields are direct: `store.rating_count`, not `store.rating_count.value` |
| `postal_code` has no `.value` | Same — `number_integer` is direct |
| `boolean` fields | `store.new`, `store.featured`, `store.highlight` — direct boolean, no `.value` |
