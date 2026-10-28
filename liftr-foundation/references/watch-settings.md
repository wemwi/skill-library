# watchSettings() & NAV Control System

CSS decides, JS reads. `watchSettings()` is the only bridge from CSS Settings
(`--{module}-*` custom properties) to a module. Source: `assets/core.module.js`
(`watchSettings`) → `assets/core.utilities.js` (`createUnifiedWatcher`, `readCSSSettings`,
`readNavSettings`) and `assets/core.liftr.js` (`NAV`).

Where CSS Settings are declared (consumer class, `@property` registration, Container Queries)
→ `css-system.md`. DEFAULTS vs. CSS_SCHEMA boundary → `core.md` Section 5.

---

## 1. API

```javascript
const watcher = this.watchSettings('slider', {
  enabled: '--slider-enabled',   // optional: CSS var for enable/disable
  css: CSS_SCHEMA,               // optional: responsive settings schema
  nav: true,                     // optional: read --nav-* settings
  resize: true,                  // optional: include { width, height } in changes
  debounce: 100                  // optional: onChange debounce in ms (default 100)
}, {
  onEnable:  (settings) => this.#enable(settings),   // { css, nav, size }
  onDisable: (settings) => this.#disable(),
  onChange:  (changes)  => this.#update(changes)     // only changed parts: { css?, nav?, size? }
});

watcher.isEnabled();   // boolean
watcher.getCSS();      // current CSS settings
watcher.getNav();      // current nav settings
// destroy() runs automatically on unmount (registered as disposable)
```

- One `ResizeObserver` per module for enabled state, CSS settings, nav settings and size.
- Read-first: all `getComputedStyle` reads happen before any write (no forced reflow).
- **Enabled:** any value except `false` counts as enabled — an unset `--{module}-enabled` means *enabled*.
- On disable the watcher clears `liftr-state` and adds `disabled`; on enable it removes `disabled`.
- While disabled, CSS/nav changes are not reported.

## 2. CSS_SCHEMA

```javascript
const CSS_SCHEMA = Object.freeze({
  mode:      { type: 'string', default: 'closed', valid: ['closed', 'highlight', 'sheet'] },
  exclusive: { type: 'bool',   default: true },
  speed:     { type: 'number', default: 50 },
  offset:    { type: 'px',     default: 0 }
});
```

| Key → CSS var | Rule |
|---|---|
| `mode` → `--{prefix}-mode` | camelCase keys become kebab-case (`hideDistance` → `--header-hide-distance`) |

| `type` | Parsing | Fallback |
|---|---|---|
| `bool` | `raw === 'true'` | `default` if unset |
| `string` | raw value; with `valid` only listed values | `default` if unset or invalid |
| `number` | `parseFloat` | `default` if NaN |
| `px` | `parseInt` without `px` | `default` if NaN |

`default` must match the `@property` `initial-value` (if registered) → `css-system.md`.

## 3. NAV Control System

Modules with `nav: true` (slider, scroll) read six CSS settings from their host:

| CSS var | Valid values | Default (`NAV.DEFAULTS`) |
|---|---|---|
| `--nav-mode` | `false`, `auto`, `static` | `auto` |
| `--nav-size` | `small`, `regular`, `medium`, `large` | `regular` |
| `--nav-icon` | `angle`, `arrow`, `chevron` | `arrow` |
| `--nav-theme` | `light`, `dark`, `plain` | `light` |
| `--nav-style` | `square`, `round` | `round` |
| `--nav-position` | `inside`, `outside`, `edge` | `inside` |

Invalid values fall back to the default (`NAV.VALID`).

**Two modes:**

- **auto** — the module generates the buttons and writes `liftr-nav` on its **root**
  (`NAV.applyOutput(this, nav)` → `liftr-nav="regular arrow light round inside"`).
- **static** — buttons already exist in the DOM (inside, or outside via `liftr-target`); JS
  writes `liftr-nav` on the **buttons** and ensures the shared roles (`NAV.ensureRoles(btn, 'prev')`).
- **false** — no buttons.

Shared roles: `nav-control` (`NAV.CONTROL_ROLE`) plus direction roles `nav-prev`, `nav-next`,
`nav-up`, `nav-down`, `nav-toggle` (`NAV.DIRECTION_ROLES`).

**NAV CSS** lives in `assets/core.liftr.css` (`@layer modules`): base `[liftr-nav]`,
`[liftr-role~="nav-control"]` (icon via `::before` mask). Size tokens set the icon size; the button is
twice the icon:

| `--nav-size` | Icon | Button |
|---|---|---|
| `small` | `--icon-size--xsmall` (0.75rem) | 1.5rem |
| `regular` | `--icon-size--small` (1rem) | 2rem |
| `medium` | `--icon-size--regular` (1.5rem) | 3rem |
| `large` | `--icon-size--medium` (2rem) | 4rem |

Section CSS only positions external buttons — never restyle `nav-control`.
