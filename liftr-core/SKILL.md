---
name: liftr-core
description: Foundation guide for the LIFTR v4.9 framework -- LiftrModule base class, core.liftr.js exports, core.utilities.js helpers, CSS layer architecture, attribute system, event system, FX effects, state/mask/settings managers, skeleton loading, CSS Settings watcher, and module authoring patterns. Use whenever writing any LIFTR module, debugging framework issues, understanding imports, authoring CSS for components, working with the attribute system, implementing responsive behavior via watchSettings, using FX animation classes, configuring i18n translations, reading settings JSON, or understanding the CSS layer order (critical.liquid -> base.css -> core.components.css -> ui.effects.css -> section CSS). This is the prerequisite skill -- read it BEFORE any component-specific skill.
---

# LIFTR Core v4.9 -- Framework Foundation

**Files:** `core.liftr.js`, `core.module.js`, `core.utilities.js`
**CSS:** `core.critical.liquid`, `base.css`, `core.components.css`, `ui.effects.css`
**Config:** `core.liftr` snippet (settings JSON + i18n JSON)

---

## Specialized References

After reading this file, load ONLY the reference(s) you need:

| Working with... | Read |
|---|---|
| watchSettings(), CSS Settings Pattern, NAV Control System | `references/responsive.md` |
| FX classes, fx-loading, Skeleton Loading, Snapshot Animations, critical.liquid | `liftr-fx-skeleton` skill |

---

## 1. Imports -- What Comes From Where

### core.module.js

```javascript
import { LiftrModule } from './core.module.js';
```

Only export: `LiftrModule` base class.

### core.liftr.js

```javascript
import { on, once, emit, debug, i18n, settings, ATTRIBUTES, FX, NAV, EVENT, SCRIPT_IDS, MARKET_DEFAULTS } from './core.liftr.js';
```

| Export | Type | Purpose |
|--------|------|---------|
| `on(name, handler, options)` | Function | Register event listener (returns cleanup fn) |
| `once(name, handler, options)` | Function | One-time event listener |
| `emit(name, detail, options)` | Function | Dispatch global custom event |
| `debug` | Object | Logging (info, warn, error, verbose, event, group, timeStart/End) |
| `i18n` | Object | Translations (locale, t, get, global) |
| `settings` | Object | Runtime config (debug, market, discounts, modules) |
| `ATTRIBUTES` | Frozen Object | 14 attribute constants |
| `FX` | Frozen Object | Effect classes + CSS property constants |
| `NAV` | Frozen Object | Navigation control system |
| `EVENT` | Frozen Object | Event pattern regex |
| `SCRIPT_IDS` | Frozen Object | DOM script element IDs |
| `MARKET_DEFAULTS` | Object | Market config defaults (for api.live.js) |

### core.utilities.js

```javascript
import {
  $, $$, rolesGlobal, findJSON, parseDataScripts, ensureId,
  setCSSVar, getCSSVar,
  formatMoney,
  loadModule, loadExternalScript, loadCSS,
  throttle, debounce, raf, cancelRaf, disposables, waitForDOMReady, delay,
  createObserver, observeResize,
  on, once,                          // DOM-level (target, event, handler)
  ensureLive, prefersReducedMotion,
  StateManager, MaskManager, SettingsManager,
  createState, createMask, createSettings,
  readCSSSettings, createUnifiedWatcher, updateImage
} from './core.utilities.js';
```

**Important:** `on()` / `once()` from core.utilities.js are DOM-level helpers (target, event, handler). The `on()` / `once()` from core.liftr.js are framework-level (event name, handler) -- dispatched on `document`.

### Forbidden Imports

```javascript
// NEVER -- these files were removed in v4.0 and don't exist
import from './core.boot.js';     // removed
import from './core.const.js';    // merged into core.liftr.js
import from './core.events.js';   // merged into core.liftr.js
import from './core.skeleton.js'; // removed
import from './core.i18n.js';     // merged into core.liftr.js
```

---

## 2. ATTRIBUTES -- The 14 Framework Attributes

```javascript
export const ATTRIBUTES = Object.freeze({
  // Identity (3)
  ID:       'liftr-id',        // External JS targeting (optional)
  ROLE:     'liftr-role',      // Element roles (space-separated)
  TARGET:   'liftr-target',    // Reference to liftr-id

  // Input -- set in Liquid (2)
  AXIS:     'liftr-axis',      // Scroll/slide axis: x, y, xy
  MASK:     'liftr-mask',      // Overflow fade masks: left, right, top, bottom

  // Output -- set by JS (3)
  NAV:      'liftr-nav',       // Navigation namespace tokens
  STATE:    'liftr-state',     // State tokens (space-separated)
  SETTINGS: 'liftr-settings',  // Output config tokens (space-separated)

  // Dependencies (1)
  REQUIRES: 'liftr-requires',  // Dependency: "postal", "geolocation"

  // Data -- list filtering (4)
  FIELD:    'liftr-field',     // Field name for filter/sort
  VALUE:    'liftr-value',     // Field value (space-separated)
  MERGE:    'liftr-merge',     // Merge behavior for list items
  PERSIST:  'liftr-persist'    // Exclude from filter count/clear
});
```

Plus `liftr-skeleton="true"` (explicit value attribute, not in ATTRIBUTES constant).

### Attribute Roles

| Category | Attributes | Set By | CSS Selector |
|----------|-----------|--------|-------------|
| Identity | ID, ROLE, TARGET | Liquid | `[liftr-id="..."]`, `[liftr-role~="..."]` |
| Input | AXIS, MASK | Liquid | `[liftr-axis="x"]`, `[liftr-mask~="left"]` |
| Output | STATE, SETTINGS, NAV | JS | `[liftr-state~="open"]`, `[liftr-settings~="mode-compact"]` |
| Data | FIELD, VALUE, MERGE, PERSIST | Liquid | `[liftr-field="opening"]` |
| Dependencies | REQUIRES | Liquid | -- |

### Forbidden Attributes

Never use: `liftr-component`, `liftr-plugin`, `liftr-*-status`, `liftr-*-role`

### PERSIST Syntax

| Syntax | Result |
|--------|--------|
| `liftr-persist` | Enabled |
| `liftr-persist=""` | Enabled |
| `liftr-persist="true"` | Enabled |
| `liftr-persist="false"` | Disabled |
| *(absent)* | Disabled |

Use case: Distance slider should not count as "active filter" and not reset on "Clear filters".

### REQUIRES Values

| Value | Description |
|-------|-------------|
| `postal` | Requires postal code input |
| `geolocation` | Requires geolocation permission |

### Attribute vs. Class Contract

**Harte Trennungsregel** -- keine Ausnahmen:

| Verantwortung | Selektor | Beispiele |
|---------------|----------|-----------|
| **Funktionalitaet** -- States, Sichtbarkeit, Error/Success, JS-Targeting | `liftr-*` Attribute (`liftr-role`, `liftr-state`, `liftr-id`, `liftr-target`, ...) | `[liftr-role~="success-message"]`, `[liftr-state~="error"]` |
| **Visuelles Styling** -- Layout, Farben, Typografie, Spacing, Proportionen | CSS-Klassen (`.section_element`, `.is-modifier`) | `.store_card`, `.is-compact`, `.is-horizontal` |

**Warum?** Attribute sind die Sprache zwischen JS und CSS fuer Maschinenzustand. Klassen sind die Sprache fuer Design. Vermischung fuehrt zu fragilen Selektoren und Doppelsteuerung.

**Konkret:**

```css
/* Correct: State-Sichtbarkeit per Attribut */
liftr-location [liftr-role~="success-message"] { display: none; }
liftr-location[liftr-state~="success"] [liftr-role~="success-message"] { display: block; }

/* WRONG: NIEMALS State/Sichtbarkeit per Klasse */
liftr-location .success-message { display: none; }
liftr-location.is-success .success-message { display: block; }
```

**Regel zusammengefasst:**
- `liftr-role` = Was ein Element **tut** (success-message, error-panel, loading-spinner, prev, next)
- `liftr-state` = In welchem **Zustand** das Modul ist (open, active, loading, error, success, dragging)
- CSS-Klasse = Wie ein Element **aussieht** (is-compact, is-horizontal, section_heading)

---

## 3. LiftrModule -- Base Class API

Every UI module extends `LiftrModule` (which extends `HTMLElement`).

### Static Properties (override in subclass)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `NAME` | string | `null` | **Required.** Module name for events |
| `DEFAULTS` | object | `{}` | Default configuration |
| `MIN_LOADING` | number | `900` | Minimum skeleton display (ms) |
| `observedAttributes` | string[] | `[]` | Attribute reactivity |

### Lifecycle

```javascript
class LiftrExample extends LiftrModule {
  static NAME = 'example';
  static DEFAULTS = { exclusive: true };

  mount() {
    // Called on connectedCallback (element added to DOM)
    // Initialize here
  }

  unmount() {
    // Called on disconnectedCallback (element removed from DOM)
    super.unmount();  // CRITICAL: always call!
  }

  onAttributeChange(name, oldValue, newValue) {
    // Called when observedAttributes change (optional)
  }
}

customElements.define('liftr-example', LiftrExample);
export { LiftrExample, ROLES, STATES, EVENTS, SETTINGS };
```

Automatic lifecycle:
1. `connectedCallback()` -> tracks loading start -> calls `mount()` -> finalizes loading -> emits `liftr:{name}:mounted`
2. `disconnectedCallback()` -> emits `liftr:{name}:unmounted` -> calls `unmount()` -> runs all disposables

### DOM Queries

| Method | Returns | Description |
|--------|---------|-------------|
| `this.role(name)` | Element \| null | Single element by role (ownership-filtered) |
| `this.roleAll(name)` | Element[] | All elements by role (ownership-filtered) |
| `this.role(name, scope)` | Element \| null | Single element in explicit scope (no filter) |
| `this.roleAll(name, scope)` | Element[] | All elements in explicit scope |
| `this.target(role)` | Element \| null | External element with matching liftr-target |
| `this.targetAll(role)` | Element[] | All external elements with matching liftr-target |

**Ownership filtering:** `this.role()` / `this.roleAll()` only return elements whose closest ancestor of the same tag equals `this`. Prevents nested components from leaking.

**Scope:** `role()` / `roleAll()` search inside the module. `target()` / `targetAll()` search outside (global) for elements whose `liftr-target` matches this module's `liftr-id`.

**Fallback Pattern (internal OR external):**

```javascript
const prevBtn = this.role(ROLES.PREV) || this.target(ROLES.PREV);
```

### Events

```javascript
this.emit('opened', { index: 0 });
// -> Dispatches: liftr:example:opened
// -> Auto-adds: { root: this, rootId: 'my-id', ...detail }
```

### State Manager

```javascript
this.state.add('open');              // Add token
this.state.add('open', 'active');    // Add multiple
this.state.remove('open');           // Remove token
this.state.remove('open', 'active');
this.state.has('open');              // Check -> boolean
this.state.toggle('open');           // Toggle
this.state.toggle('open', true);     // Force add
this.state.toggle('open', false);    // Force remove
this.state.all();                    // -> ['open', 'active']
this.state.set(['open', 'active']);   // Replace all
this.state.clear();                  // Remove all
```

Reads/writes `liftr-state` attribute (space-separated tokens).

### State Placement Rule

```
DEFAULT: liftr-state wird auf dem Host definiert (dem Custom Element).
  -> this.state.add(STATES.OPEN)
  -> CSS: liftr-slider[liftr-state~="open"] { }

AUSNAHME: Nur wenn die Funktionalitaet einen State auf einem
spezifischen Child erfordert (Items in Listen, Panels in Accordions).
  -> this.createState(element).add(STATES.ACTIVE)
  -> CSS: liftr-list [liftr-role~="list-item"][liftr-state~="active"] { }
  -> Das Child MUSS ein liftr-role haben -- nie auf anonymen DOM-Knoten.

Auch bei Child-States bleibt der Modul-Zustand auf dem Host:
  Host:  liftr-list[liftr-state~="empty"]           -- Modul-Zustand
  Child: [liftr-role~="list-item"][liftr-state~="filtered"]  -- Item-Zustand
```

**Prinzip: Host-State beschreibt Ergebnis, nicht Ursache.**
Ein State bildet ab was das Modul *ist* -- nicht wie es dahin gekommen ist.
Beispiel: `liftr-location[liftr-state~="success"]` -- nicht `postal-success` oder `geo-success`.
Die Eingabemethode gehoert in `e.detail.method` (Event) oder ein Data-Attribut, nicht in `liftr-state`.

### Settings Manager

Same API as StateManager, but on `liftr-settings` attribute:

```javascript
this.settings.add('mode-compact');
this.settings.has('icon-angle');
this.settings.toggle('theme-dark', isDark);
```

### Mask Manager

```javascript
this.mask.add('left');               // Add direction
this.mask.remove('right');           // Remove direction
this.mask.has();                     // Has liftr-mask attribute? -> boolean
this.mask.includes('left');          // Direction active? -> boolean
this.mask.toggle('left', canScroll);
this.mask.all();                     // -> ['left', 'right']
```

Reads/writes `liftr-mask` attribute.

### Child Managers

```javascript
const itemState = this.createState(element);    // StateManager for child
const viewportMask = this.createMask(element);  // MaskManager for child
const childSettings = this.createSettings(element); // SettingsManager for child
```

### Configuration

```javascript
this.config  // Merged: static DEFAULTS + settings.modules[NAME]
```

### Cleanup

```javascript
this.addDisposable(() => el.removeEventListener('click', handler));
this.addDisposable(on('liftr:sidebar:opened', handler));
// All disposables run automatically on unmount()
```

### Specialized APIs (see references/)

- **watchSettings()** -- responsive CSS-to-JS bridge -> `references/responsive.md`
- **FX Loading Helpers** (awaitLoading, awaitResult, awaitResultExit) -> `liftr-fx-skeleton` skill
- **Snapshot Animation Helpers** (morphTransform, morphProperty, animateOnChange) -> `liftr-fx-skeleton` skill

---

## 4. Module Constants Pattern

Every module defines 5-7 frozen constants:

```javascript
const ROLES = Object.freeze({
  ITEM:   'example-item',
  TOGGLE: 'example-toggle',
  PANEL:  'example-panel'
});

const STATES = Object.freeze({
  OPEN:   'open',
  ACTIVE: 'active'
});

const EVENTS = Object.freeze({
  OPENED: 'opened',
  CLOSED: 'closed'
});

const SETTINGS = Object.freeze({
  MODE_COMPACT: 'mode-compact',
  ICON_ANGLE:   'icon-angle'
});

// Only if JS sets CSS variables:
const PROPERTIES = Object.freeze({
  OFFSET: '--example-offset'
});

// Only if using watchSettings():
const CSS_SCHEMA = Object.freeze({
  cols: { type: 'number', default: 1 }
});

// Only if listening to external events:
const LISTEN = Object.freeze({
  SIDEBAR_OPENED: 'liftr:sidebar:opened'
});
```

### Export Rules

```javascript
// Export class + PUBLIC constants only
export { LiftrExample, ROLES, STATES, EVENTS, SETTINGS };

// With PROPERTIES (if defined):
export { LiftrExample, ROLES, STATES, EVENTS, SETTINGS, PROPERTIES };

// NEVER export: CSS_SCHEMA, LISTEN (internal only)
```

### Usage Rules

```javascript
// CORRECT -- use constants
this.role(ROLES.TOGGLE);
this.state.add(STATES.OPEN);
this.emit(EVENTS.OPENED, detail);
this.settings.add(SETTINGS.MODE_COMPACT);
el.style.setProperty(PROPERTIES.OFFSET, value);
on(LISTEN.SIDEBAR_OPENED, handler);

// WRONG -- string literals
this.role('example-toggle');
this.state.add('open');
this.emit('opened', detail);
```

### Naming Convention

| Constant | Key Style | Value Style |
|----------|-----------|-------------|
| ROLES | `SCREAMING_SNAKE` | `{name}-kebab` |
| STATES | `SCREAMING_SNAKE` | `kebab` |
| EVENTS | `SCREAMING_SNAKE` | `kebab` |
| SETTINGS | `SCREAMING_SNAKE` | `{category}-{value}` |
| PROPERTIES | `SCREAMING_SNAKE` | `--{name}--{property}` |

### SETTINGS Token Categories

The `liftr-settings` attribute is the **only** way to output module-specific settings. Separate attributes like `liftr-{name}-mode` are FORBIDDEN.

| Category | Pattern | Examples |
|----------|---------|----------|
| Mode | `mode-{value}` | `mode-closed`, `mode-highlight`, `mode-compact` |
| Icon | `icon-{value}` | `icon-none`, `icon-angle`, `icon-plus` |
| Size | `size-{value}` | `size-xsmall`, `size-small`, `size-regular`, `size-large` |
| Position | `position-{value}` | `position-sheet`, `position-sidebar-left` |
| Columns | `cols-{value}` | `cols-1`, `cols-3`, `cols-auto` |
| Gap | `gap-{value}` | `gap-small`, `gap-medium`, `gap-large` |
| Feature flags | `{feature}` | `loop`, `autoplay`, `snap`, `backdrop-blur` |

CSS selectors for settings tokens:

```css
[liftr-settings~="mode-closed"] { }
liftr-slider[liftr-settings~="loop"][liftr-settings~="autoplay"] { }
liftr-accordion[liftr-settings]:not([liftr-settings~="icon-none"]) { }
```

### Property Scope Rule

| Pattern | Constant | Direction |
|---------|----------|-----------|
| `--{module}-*` | Module `PROPERTIES` | JS writes -> CSS reads |
| `--fx-*` | `FX.PROPERTIES` | CSS defines -> JS reads |

### Shared STATES (from core.liftr.js)

Global state tokens available to all modules:

```javascript
// Lifecycle
LOADING, ACTIVE, DISABLED, HIDDEN, SELECTED, FILTERED, EMPTY, SEARCHING

// Navigation
CAN_PREV, CAN_NEXT, CAN_SCROLL, AT_START, AT_END

// Feature Flags
HAS_DISTANCE, HAS_SCHEDULE

// Distance (prefixed, exclusive)
DISTANCE_NEAR, DISTANCE_MID, DISTANCE_FAR, DISTANCE_REMOTE, DISTANCE_UNKNOWN

// Timer (prefixed, exclusive)
TIMER_OK, TIMER_SOON, TIMER_URGENT, TIMER_EXPIRED

// Summary (prefixed)
SUMMARY_OPEN, SUMMARY_CLOSED, SUMMARY_OPENING, SUMMARY_CLOSING
```

Values follow `kebab-case` convention: `LOADING` -> `'loading'`, `CAN_PREV` -> `'can-prev'`, `DISTANCE_NEAR` -> `'distance-near'`.

### State Naming Rule

```
Modulspezifisch (in STATES-Konstante)?
  -> Ohne Prefix: 'open', 'active', 'dragging'
  -> Scope ergibt sich aus Host-Selektor: liftr-slider[liftr-state~="open"]

Shared, unabhaengige Toggles (beliebig kombinierbar)?
  -> Ohne Prefix: 'loading', 'can-prev', 'has-distance'

Shared, exklusive Gruppe (nur einer aktiv)?
  -> {group}-{value} Prefix: 'distance-near', 'timer-ok', 'summary-open'
  -> Modul muss alte Werte der Gruppe entfernen bevor neuer gesetzt wird
```

### Global Constants (from core.liftr.js)

```javascript
export const NAV = Object.freeze({ PREV: 'prev', NEXT: 'next' });

export const SCRIPT_IDS = Object.freeze({
  SETTINGS: 'liftr-settings',
  I18N: 'liftr-i18n'
});

export const EVENT = Object.freeze({
  PATTERN: /^liftr:[a-z0-9-]+:[a-z0-9-]+$/,
  SOURCE: Object.freeze({ MODULE: 'module', FRAMEWORK: 'framework' })
});
```

---

## 5. Configuration Boundary -- DEFAULTS vs CSS_SCHEMA

Two configuration systems exist. Each has exactly one responsibility.

### DEFAULTS (static JS config)

```javascript
static DEFAULTS = {
  initialOpen: null,     // Which item opens on mount
  swipeThreshold: 50,    // px minimum for swipe detection
  pauseOnHover: true,    // Enable hover pause behavior
  hoverSlowRate: 0.2     // Playback rate during slow phase
};
```

Values that are set once and never change at runtime. No CSS custom property, no Container Query, no Observer. Consumed via `this.config.{key}`.

### CSS_SCHEMA (responsive CSS-driven config)

```javascript
const CSS_SCHEMA = Object.freeze({
  mode:      { type: 'string', default: 'closed' },
  exclusive: { type: 'bool',   default: true },
  cols:      { type: 'number', default: 1 }
});
```

Values that CSS controls and that can change at runtime (Container Query, viewport resize, theme editor). Observed by `watchSettings()`, delivered via `onChange` / `onEnable` / `onDisable` callbacks.

### The Rule

```
Can the value change at runtime via CSS?
  YES -> CSS_SCHEMA only. Read from watchSettings callback.
  NO  -> DEFAULTS only. Read from this.config.

No key in both. No bridge method (#getSetting) needed.
```

### Decision Table

| Signal | System | Access |
|--------|--------|--------|
| Has a `--{module}-{key}` CSS property | CSS_SCHEMA | `changes.css.{key}` |
| Responds to Container Query / resize | CSS_SCHEMA | `changes.css.{key}` |
| Static number/boolean/string from JSON | DEFAULTS | `this.config.{key}` |
| Only set on mount, never changes | DEFAULTS | `this.config.{key}` |

### enabled is NOT a DEFAULTS key

The `enabled` toggle is always CSS-driven via `--{module}-enabled`. The `watchSettings()` system handles enabled/disabled state through `onEnable` / `onDisable` callbacks. Never put `enabled` in DEFAULTS.

### Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| Same key in DEFAULTS and CSS_SCHEMA | Remove from DEFAULTS -- CSS_SCHEMA is SSOT |
| `#getSetting()` bridge that checks CSS then config then DEFAULTS | Remove -- each key has exactly one source |
| `enabled` in DEFAULTS | Remove -- `watchSettings()` handles this via `--{module}-enabled` |

### Example (Accordion)

```javascript
// DEFAULTS -- static only
static DEFAULTS = {
  initialOpen: null       // no CSS equivalent, mount-time only
};

// CSS_SCHEMA -- responsive only
const CSS_SCHEMA = Object.freeze({
  mode:      { type: 'string', default: 'closed' },
  exclusive: { type: 'bool',   default: true },
  icon:      { type: 'string', default: 'plus' },
  size:      { type: 'string', default: 'regular' }
});

// Access -- no bridge needed
mount() {
  const initialOpen = this.config.initialOpen;  // from DEFAULTS
  // mode, icon, size come from watchSettings callbacks
}
```

---

## 6. Event System

### Pattern

```
liftr:{name}:{action}
```

No type segment. Examples: `liftr:accordion:opened`, `liftr:slider:slide-changed`

### this.emit() vs emit()

| Method | Scope | Use When |
|--------|-------|----------|
| `this.emit(action, detail)` | Auto-prefixed with `liftr:{NAME}:` | Own module events |
| `emit(fullName, detail)` | Global, full name required | Cross-module events |

`this.emit()` auto-adds `{ root, rootId }` to detail.

### Listening

```javascript
// String-based
this.addDisposable(
  on('liftr:sidebar:opened', (e) => { /* e.detail */ })
);

// RegExp-based (all accordion events)
on(/^liftr:accordion:/, handler);

// One-time
once('liftr:cart:ready', handler);
```

### Automatic Lifecycle Events

LiftrModule emits these automatically:
- `liftr:{name}:mounted` -- after mount() (payload: `{ element, root, rootId }`)
- `liftr:{name}:unmounted` -- before unmount() (payload: `{ element, root, rootId }`)

Used for Late Registration Pattern: components that mount later listen for `mounted` to register with already-mounted parents.

---

## 7. CSS Layer Architecture

Layer order, assignment table, and layer rules --> liftr-css-system skill.

### CSS Custom Property Naming

Double-dash convention: `--{namespace}--{property}`

```css
/* Design tokens (base.css) */
--color-scheme--background
--space--medium
--font-size--h2
--transition--fast
--ease--out

/* Module properties (JS writes) */
--slider-offset
--range-fill
--panel-origin

/* FX timing (CSS defines, JS reads) */
--fx-morph-duration      /* Exception: single-dash prefix */
--fx-hover-ease

/* Nav internal */
--_nav-icon-size         /* Underscore = private */
```

---

## 8. I18N System

### Liquid Setup

```liquid
<script type="application/json" id="liftr-i18n">
{
  "modules": {
    "accordion": {
      "expand": "{{ 'components.accordion.button.expand' | t }}",
      "collapse": "{{ 'components.accordion.button.collapse' | t }}"
    }
  }
}
</script>
```

### JS Usage

```javascript
import { i18n } from './core.liftr.js';

i18n.locale;                    // 'de'
i18n.t('modules.slider.prev');  // 'Zurueck'
i18n.get('accordion');          // { expand: 'Aufklappen', collapse: 'Zuklappen' }
i18n.global;                    // { close: 'Schliessen', ... }
```

---

## 9. Settings System

### Liquid Setup

```liquid
<script type="application/json" id="liftr-settings">
{
  "market": {
    "handle": "de",
    "money": "{{amount_with_comma_separator}} EUR",
    "timezone": "Europe/Berlin",
    "holidays": [...],
    "opening": { "schedule": { "regular": [...], "holiday": [...] } },
    "shipping": { "transit_time": "...", "minimum": { "amount": "3.95" }, "schedule": {...} },
    "stock": { "threshold_warning": 20, "threshold_critical": 5 },
    "rewards": [...]
  },
  "discounts": { "NEW10": { "threshold": 3500, "value": "10", "type": "fixed" } }
}
</script>
```

### JS Usage

```javascript
import { settings } from './core.liftr.js';

settings.debug.enabled;                // boolean
settings.market.timezone;              // 'Europe/Berlin'
settings.market.money;                 // '{{amount_with_comma_separator}} EUR'
settings.market.shipping.minimum;      // { amount: 395, currency_code: 'EUR' }
settings.market.stock.threshold_warning; // 20
settings.market.rewards;               // [{ name, threshold, type, ... }]
settings.discounts;                    // { NEW10: { threshold: 3500, ... } }
settings.modules.accordion;            // { exclusive: true }
```

Note: `settings.market.shipping.minimum.amount` is in **cents** (normalized from JSON).

---

## 10. Utility Helpers

### DOM

| Function | Signature | Description |
|----------|-----------|-------------|
| `$` | `(selector, context?)` | querySelector (null-safe) |
| `$$` | `(selector, context?)` | querySelectorAll -> Array |
| `rolesGlobal` | `(role)` | Find all elements with role globally |
| `findJSON` | `(root, role)` | Parse JSON script by role |
| `parseDataScripts` | `(root)` | Parse all JSON scripts in root |
| `ensureId` | `(el, prefix?)` | Get or generate element ID |

### CSS

| Function | Signature | Description |
|----------|-----------|-------------|
| `setCSSVar` | `(el, name, value)` | Set custom property |
| `getCSSVar` | `(el, name)` | Get custom property |

### Performance

| Function | Signature | Description |
|----------|-----------|-------------|
| `throttle` | `(fn, ms, options?)` | Throttle with cancel() |
| `debounce` | `(fn, ms, options?)` | Debounce with cancel() |
| `raf` | `(callback)` | requestAnimationFrame |
| `delay` | `(ms)` | Promise-based setTimeout |

### Observers

| Function | Signature | Returns |
|----------|-----------|---------| 
| `observeResize` | `(targets, callback)` | Disconnect function |
| `createObserver` | `(callback, options?)` | IntersectionObserver |

### Formatting

| Function | Signature | Example |
|----------|-----------|---------| 
| `formatMoney` | `(cents, currency?)` | `formatMoney(395)` -> `'EUR3,95'` |

### A11Y

| Function | Signature | Description |
|----------|-----------|-------------|
| `ensureLive` | `(el, role?)` | Add aria-live="polite" |
| `prefersReducedMotion` | `()` | Check preference -> boolean |

---

## 11. Common Mistakes (JS)

CSS-specific mistakes --> liftr-css-system skill.

| Mistake | Fix |
|---------|-----|
| String literals for roles/states/events | Use ROLES.*, STATES.*, EVENTS.* constants |
| `import from './core.events.js'` | Use `import from './core.liftr.js'` |
| `ctx.utilities.*` | Use `this.*` in LiftrModule |
| `return { unmount }` | Use `unmount()` method, call `super.unmount()` |
| `console.log` in modules | Modules are SILENT -- use `throw new Error()` |
| Forgetting `super.unmount()` | Always call in unmount() |
| `querySelector` inside module | Use `this.role(ROLES.*)` |
| `liftr-component` attribute | Use `<liftr-{name}>` custom element |
| `liftr:{type}:{name}:{action}` event | Use `liftr:{name}:{action}` (no type) |
| `'--fx-morph-duration'` string literal | Use `FX.PROPERTIES.MORPH_DURATION` |
| `'fx-enter-pop'` string literal | Use `FX.ENTER_POP` |
| CSS_SCHEMA exported | Keep internal (not in export statement) |
| LISTEN exported | Keep internal (not in export statement) |
| Child using `closest()` to find parent | Parent calls child's API instead |
| Magic strings in `on()` calls | Use `LISTEN.*` constants |
| Missing Public API guards | All methods use `?.` safe access |
| Same key in DEFAULTS and CSS_SCHEMA | Remove from DEFAULTS -- CSS_SCHEMA is SSOT (Section 5) |
| `#getSetting()` bridge method | Remove -- each key has exactly one source (Section 5) |
| `enabled` in DEFAULTS | Remove -- watchSettings handles via `--{module}-enabled` (Section 5) |
