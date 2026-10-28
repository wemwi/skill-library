# LIFTR Audit

Systematic review of LIFTR theme code. For implementation rules, see the referenced files in liftr-foundation, liftr-components, liftr-liquid and liftr-commerce.

**This skill owns the PRUEF-Perspektive** -- what to check, in what order.
The other liftr skills own the WARUM and WIE -- load them for fixes.

---

## Audit Scenarios

### Scenario 1: Section Audit

Single section, full depth.

**Input:** Section name (e.g. `hero`, `product`)

**Steps:**

1. Read section file: `sections/[name].liquid`
2. Read section CSS: `assets/section.[name].css`
3. Run HTML Audit checklist (below)
4. Run CSS Audit checklist (below)
5. Run Schema Audit checklist (below)
6. If section contains `<liftr-*>` components: Run JS-relevant checks from HTML Audit
7. Run Grep Commands scoped to section files
8. For fixes: load `section.md` (liftr-liquid), `css-system.md` (liftr-foundation), `block.md` (liftr-liquid), `i18n.md` (liftr-liquid) as needed

### Scenario 2: Module Audit

Single JS module, full depth.

**Input:** Module name (e.g. `slider`, `panel`)

**Steps:**

1. Read module file: `assets/ui.[name].js`
2. Read module CSS: `assets/ui.[name].css` or the module block in `assets/core.liftr.css` (both `@layer modules`)
3. Run JS Audit checklist (below)
4. Run CSS Audit checklist for component selectors
5. Run Grep Commands scoped to module file
6. For fixes: load `core.md` (liftr-foundation) + the component reference (e.g. `slider.md`, liftr-components)

### Scenario 3: All-Sections Audit

Batch audit, breadth first.

**Steps:**

1. List all section files: `ls sections/*.liquid`
2. Run Grep Commands (full theme scope) -- catches bulk violations fast
3. For each section: Run Scenario 1 checks 1-6
4. Compile findings per section, deduplicate shared patterns
5. Prioritize by severity: Broken > Wrong > Suboptimal

### Scenario 4: Theme Audit (Full)

Complete theme review. Most expensive -- plan accordingly.

**Steps:**

1. Run Grep Commands (full theme scope) -- fast triage
2. All Sections: Scenario 3
3. All JS Modules: `ls assets/ui.*.js assets/api.*.js` -- Scenario 2 for each
4. Cross-cutting checks:
   - i18n completeness: missing keys, unused keys
   - Schema consistency: setting patterns across sections
   - Event contracts: emitters vs listeners match
   - Custom colors: guard contract compliance
5. Compile report grouped by: Critical / Warning / Info

---

## HTML Audit

### LIFTR Components

- [ ] Custom element tags: `<liftr-slider>`, `<liftr-accordion>`, etc.
- [ ] `liftr-role` with module prefix: `slider-panel`, `accordion-toggle`
- [ ] `liftr-state="loading"` only on skeleton modules, set in HTML (never by JS)
- [ ] `liftr-skeleton="true"` (with value) on root or children, set in HTML
- [ ] `liftr-id` only when `liftr-target` reference exists
- [ ] No `data-*` attributes -- only `liftr-*`

Fix: `core.md` (liftr-foundation) Sec 2 (attributes), component references (liftr-components)

### ARIA

- [ ] `aria-label` set in Liquid with i18n, not by JS
- [ ] Combined pattern: `{{ 'sections.*.name' | t }} ({{ 'components.*.name' | t }})`
- [ ] Slider: `aria-roledescription` and items' `role="group"` + `aria-roledescription="slide"` are set by `ui.slider.js` — not duplicated in Liquid
- [ ] Clone elements: `aria-hidden="true"`

Fix: `i18n.md` (liftr-liquid), component references (liftr-components)

### Images

- [ ] `sizes` in REM, never pixels
- [ ] `widths` calculated from CSS via lookup table
- [ ] No unnecessary `loading: 'lazy'` (it's Shopify default)
- [ ] Above-fold: `loading: 'eager'` + `fetchpriority: 'high'`

Fix: `images.md` (liftr-liquid)

### Liquid

- [ ] Translation filter `| t` on all frontend texts
- [ ] No hardcoded strings in schema -- all `t:` keys
- [ ] No comparisons inside `assign` in `{%- liquid %}` blocks (guards via if/endif)
- [ ] Only REM, no PX (exception: borders)
- [ ] `custom-colors` render with correct scope/name/id
- [ ] `is_custom` guard before `custom-colors` render

Fix: `i18n.md` (liftr-liquid), `custom-colors.md` (liftr-liquid), `section.md` (liftr-liquid)

---

## CSS Audit

### Selectors

- [ ] LIFTR root: `liftr-{name}` tag selector
- [ ] Roles scoped: `liftr-{name} [liftr-role~="..."]`
- [ ] States on root: `liftr-{name}[liftr-state~="..."]`
- [ ] No flat `[liftr-role~="..."]` without custom element scope
- [ ] Client-First for section CSS: `._component`, `._element`

Fix: `css-system.md` (liftr-foundation), Tree 3 (selectors)

### Variables

- [ ] Owner-Pattern: `--[name]--[property]`
- [ ] Inline Fallback for colors: `var(--name--prop, var(--color-scheme--*))`
- [ ] No declarations of color variables on `_component`
- [ ] `color-mix()` not `rgba()` for scheme-adaptive transparency
- [ ] Z-index from scale: `var(--z--elevated)` etc.
- [ ] Gaps with `--space--*` tokens
- [ ] Transitions with `var(--transition--*)` tokens
- [ ] Easings with `var(--ease--*)` tokens

Fix: `css-system.md` (liftr-foundation), Tree 1 + Inline Fallback, `custom-colors.md` (liftr-liquid)

### Structure

- [ ] Length values with units: `0px` not `0` (breaks `calc()`)
- [ ] Nesting per whitelist only
- [ ] CQ mirrors component block 1:1
- [ ] LIFTR CSS Settings on the consumer element (`liftr-x.context_x`), not on `_component`, not via `[liftr-id]`
- [ ] `prefers-reduced-motion` handled
- [ ] Correct CSS layer and file (File & Layer Map in `css-system.md`)

Fix: `css-system.md` (liftr-foundation)

---

## JS Audit

### Module Structure

- [ ] Extends `LiftrModule`, not `HTMLElement` directly
- [ ] `static NAME` set
- [ ] `static DEFAULTS` for all config values
- [ ] `customElements.define('liftr-{name}', LiftrClass)` at file end
- [ ] `super.unmount()` called in `unmount()`

### Constants

- [ ] ROLES, STATES, EVENTS, SETTINGS as `Object.freeze({})`
- [ ] ROLES keys `SCREAMING_SNAKE`, values `{name}-kebab`
- [ ] STATES/EVENTS values `kebab-case`
- [ ] PROPERTIES only if JS sets CSS variables: `--{name}-{property}` (single dash)
- [ ] CSS_SCHEMA / LISTEN internal only -- not exported
- [ ] No string literals -- constants used everywhere

### DOM Queries

- [ ] `this.role()` / `this.roleAll()` -- not `querySelector('[liftr-role~="..."]')`
- [ ] `this.target()` / `this.targetAll()` for incoming references
- [ ] Outgoing references: manual `getAttribute` + `querySelector`

### Cleanup

- [ ] Every listener wrapped in `this.addDisposable()`
- [ ] No manual `removeEventListener` in `unmount()`
- [ ] `on()` return value passed to `addDisposable()`

### Events

- [ ] `this.emit(EVENTS.ACTION, detail)` for own module events
- [ ] `emit('liftr:{name}:{action}', detail)` only for cross-module
- [ ] Event pattern: `liftr:{name}:{action}` -- no type segment
- [ ] Listeners use LISTEN constants for external events
- [ ] Event layer: DOM-replacing -> UI-Events, data-reading -> Data-Events

### Imports

- [ ] Bare specifiers from the import map only (`'core.module'`, `'core.liftr'`, `'core.utilities'`, `'ui.*'`, `'api.*'`) — no relative `./*.js` (loads modules twice); new module registered in `snippets/core.head.liquid`
- [ ] No forbidden imports: `core.boot.js`, `core.const.js`, `core.events.js`, `core.skeleton.js`, `core.i18n.js`
- [ ] `ATTRIBUTES.*` constants for attribute access
- [ ] `FX.*` constants for effect classes

### Responsive & Settings

- [ ] `watchSettings()` for responsive behavior -- not manual resize listeners
- [ ] CSS Settings type matches usage: `'number'`, `'px'`, `'string'`
- [ ] `onEnable` / `onDisable` / `onChange` callbacks implemented

### Exports

- [ ] Class + public constants: `export { LiftrClass, ROLES, STATES, EVENTS, SETTINGS }`
- [ ] PROPERTIES exported only if defined
- [ ] CSS_SCHEMA, LISTEN never exported

Fix: `core.md` (liftr-foundation) — all JS items

---

## Schema Audit

- [ ] All labels via `t:` translation keys
- [ ] Global keys reused, not duplicated per section
- [ ] `color_mode` Auto/Custom with `visible_if`
- [ ] Content setting IDs with `content_` prefix
- [ ] Color setting IDs match reserved suffixes
- [ ] `"tag": null` on theme blocks
- [ ] Presets with functional examples

Fix: `i18n.md` (liftr-liquid), `custom-colors.md` (liftr-liquid), `block.md` (liftr-liquid), `merchant-ux.md` (liftr-liquid)

---

## Grep Commands

### HTML / Liquid

```bash
# Flat role selectors (should be scoped to custom element)
grep -rP "^\[liftr-role" assets/*.css

# Missing skeleton attributes on LIFTR components
grep -r "<liftr-" sections/ | grep -v "liftr-state"

# PX values in section CSS (should be REM, except borders)
grep -rP ":\s*\d+px" assets/section.*.css | grep -v "border"

# data-* attributes (should be liftr-*)
grep -r "data-" sections/ snippets/ blocks/ | grep -v "shopify" | grep -v "data-aid"

# Hardcoded strings in schema (should be t: keys)
grep -rP '"(label|info|content|name)":\s*"[^t]' sections/ blocks/ | grep -v ".css"
```

### CSS

```bash
# rgba() usage (should be color-mix())
grep -r "rgba(" assets/section.*.css

# Old variable prefixes (should be Owner-Pattern)
grep -rP "--section-|--block-|--component-" assets/section.*.css
```

### JS

```bash
# String literals instead of ROLES/STATES constants
grep -rP "this\.role\(['\"]" assets/*.js

# Direct querySelector for liftr attributes (should use this.role())
grep -rP "querySelector.*liftr-role" assets/*.js

# Missing super.unmount()
grep -A5 "unmount()" assets/*.js | grep -L "super.unmount"

# Manual removeEventListener (should use addDisposable)
grep -r "removeEventListener" assets/*.js

# Forbidden imports (removed files)
grep -rP "from\s+['\"](\.\/)?core\.(boot|const|events|skeleton|i18n)(\.js)?['\"]" assets/*.js

# Relative imports (should be bare specifiers from the import map)
grep -rnP "(from\s+|import\s*\(\s*)['\"]\.\/(core|ui|api)\." assets/*.js

# Hardcoded FX class strings (should use FX.* constants)
grep -rP "classList\.(add|remove|toggle)\(['\"]fx-" assets/*.js

# Hardcoded attribute strings (should use ATTRIBUTES.*)
grep -rP "(get|set|has|remove)Attribute\(['\"]liftr-" assets/*.js
```
