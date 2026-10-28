---
name: liftr-css-system
description: CSS architecture guide for the LIFTR Shopify theme. Covers Custom Properties (Owner-Pattern), Override decisions (colors vs layout vs LIFTR Settings), selector patterns (Client-First + scoped LIFTR), nesting whitelist, Container Queries (container classes, enable/disable pattern), FOUC prevention (critical.liquid, skeleton loading), and design tokens. Use whenever writing, reviewing, or debugging CSS for any LIFTR section, snippet, block, or component. Also use when deciding where CSS belongs (which file, which layer), how to name variables, whether to use a Custom Property or direct value, how to structure a CSS file, how to set up responsive behavior, or whether a component needs critical CSS. This is the CSS counterpart to liftr-core (JS) — read it BEFORE writing any CSS.
---

# LIFTR CSS System

## Philosophy

CSS is the Single Source of Truth for layout and responsive behavior. JavaScript reads, CSS decides.

Five principles guide every CSS decision:

1. **Direct over indirect.** Use a property value directly. Only introduce a Custom Property when someone else needs to control that value.
2. **Explicit over inherited.** Declare values where they're consumed. Use CSS Inheritance only for ambient context (colors). Target specific components explicitly for everything else.
3. **Scoped over global.** Every selector identifies its owner. No orphan attribute selectors, no unscoped variables.
4. **Flat over nested.** Nesting is allowed only for same-element states and single-level modifier-children. Everything else is flat.
5. **Fluid over breakpoints.** Use `clamp()` for spacing and type. Use Container Queries for layout switches. Use Media Queries only for full-viewport changes.

---

## Decision Trees

### Tree 1: Do I Need a Custom Property?

```
I'm writing a CSS value. Do I need a Custom Property?

Is it a color the merchant can override?
  → YES: Custom Property + Inline Fallback (never declare)
  → Example: color: var(--hero--text, var(--color-scheme--text));

Is it a LIFTR Setting that JS reads?
  → YES: Custom Property on Consumer-Klasse (directly on liftr-* element)
  → Example: liftr-slider.hero_slider { --slider-cols: 3; }

Must a DIFFERENT selector change this value?
  (Parent Override, Section, Container Query)
  → YES: Public Custom Property + Inline Fallback → --[owner]--[prop]
  → Example: gap: var(--faqs--gap, var(--space--xlarge));

Must only a MODIFIER on the same component change this value?
  (is-small, is-large, is-icon -- size and proportion)
  -> YES: Internal Custom Property -> --_[prop]
  -> Example: padding: var(--_padding, var(--space--small) var(--space--large));
  -> Modifier sets: --_padding: var(--space--xsmall) var(--space--small);

Is it a color derived from the component's own STATE?
  (success/error/warning/denied mapped to color tokens)
  -> YES: Internal Custom Property -> --_status
  -> Host sets per state, children map explicitly to --gradient
  -> Example: liftr-location[liftr-state~="success"] { --_status: var(--color-global--success); }
  -> Child: liftr-location [liftr-role~="geo-toggle"] { --gradient: var(--_status); }

None of the above?
  → NO Custom Property. Use the value directly.
  → Example: gap: var(--space--large);
```

### Public vs. Internal Properties

| Type | Pattern | Darf gesetzt werden von | Beispiel |
|------|---------|------------------------|---------|
| **Public** | `--[owner]--[prop]` | Parents, Sections, Context | `--button--primary` |
| **Internal** | `--_[prop]` | Nur Modifier (`is-*`) oder eigener State | `--_padding`, `--_font-size`, `--_status` |

**Regel:** Groesse und Proportionen eines Components sind immer internal. Farben und kontextabhaengige Layout-Entscheidungen sind immer public. State-abgeleitete Farben (`--_status`) sind internal -- der Wert kommt aus dem eigenen State, nicht von aussen.

```css
/* [x] Korrekt — public für Farbe, internal für Größe */
.button {
  --_padding:     var(--space--small) var(--space--large);
  --_font-size:   var(--font-size--medium);
  --_border-radius: var(--border-radius--medium);

  padding:      var(--_padding);
  font-size:    var(--_font-size);
  border-radius: var(--_border-radius);
  color:        var(--button--primary-text, var(--color-scheme--button-primary-text));

  &.is-small {
    --_padding:   var(--space--xsmall) var(--space--small);
    --_font-size: var(--font-size--regular);
  }
}

/* Parent darf Farbe setzen — nie Größe */
.some-context .button {
  --button--primary: hotpink;  /* [x] public */
  --_padding: 0;               /* [!] VIOLATION — internal */
}
```

**Warum kein Public-Slot für Größe?**
Größen-Properties (padding, font-size, border-radius) werden von Modifier-Klassen kontrolliert.
Ein Parent der Größe überschreiben will, setzt die Modifier-Klasse — nicht die Property direkt.

### Tree 2: Where Does My CSS Go?

```
What kind of CSS am I writing?

Reusable UI component? (button, card, badge, heading-group)
  → Above-the-fold on page load? → core.components-critical.css → @layer components
  → Only visible after interaction? → core.components.css → @layer components
  → (See "Component CSS Split" section below)

LIFTR module mechanics? (display/visibility of liftr-* and [liftr-role],
  slider transforms, panel positioning, accordion height, overflow, NAV base)
  → core.liftr.css → @layer modules

  Eigene Datei ui.{module}.css statt core.liftr.css?
    Module hat eigene Container Queries?           → YES: ui.{module}.css
    Module hat 3+ funktionale States auf Host?     → YES: ui.{module}.css
    Regeln wuerden >30 Zeilen in core.liftr.css?   → YES: ui.{module}.css
    Keines davon?                                  → core.liftr.css

  ui.{module}.css existiert NUR parallel zu ui.{module}.js — nie ohne JS-Modul.
  Layer bleibt @layer modules (gleich wie core.liftr.css).

Section-specific layout? (hero grid, FAQ columns, product slider config)
  → section.{name}.css → @layer sections

Snippet with own visual identity? (>50 lines, not shared UI)
  → snippet.{name}.css → @layer components

Temporary state override? (skeleton, loading, aria-busy)
  → core.critical.liquid → @layer states

Editor-only? (empty states, design_mode visibility)
  → core.editor.css → @layer editor
```

### Tree 3: Which Selector Do I Use?

**Harte Trennungsregel (→ liftr-core "Attribute vs. Class Contract"):**
- Funktionalität (States, Sichtbarkeit, Error/Success, JS-Targeting) → **immer** `liftr-*` Attribut-Selektor
- Visuelles Styling (Layout, Farben, Typografie, Spacing) → **immer** CSS-Klasse
- Base-Styles für Web Components (alle `liftr-*` Attribute) → `core.liftr.css` (oder `ui.{module}.css` bei eigenen CQ / 3+ States) → `@layer modules`
- Visuelles Component-Styling → `core.components.css`, `section.*.css`, `snippet.*.css` → `@layer components` / `@layer sections`

```
What am I styling?

FUNCTIONAL (state, visibility, role targeting)?
  → Attribute selector, scoped to Custom Element
  → liftr-location [liftr-role~="success-message"] { display: none; }
  → liftr-location[liftr-state~="success"] [liftr-role~="success-message"] { display: block; }
  → File: core.liftr.css or ui.{module}.css → @layer modules
  → NEVER in @layer components or @layer sections
  → NEVER: .success-message, .is-success .success-message

A LIFTR Custom Element root?
  → liftr-slider { }

A LIFTR role (child of Custom Element)?
  → ALWAYS scoped: liftr-slider [liftr-role~="slider-panel"] { }
  → NEVER flat: [liftr-role~="slider-panel"] { }

A LIFTR state on root?
  → liftr-slider[liftr-state~="dragging"] { }

A LIFTR state on root affecting child?
  → Flat descendant: liftr-slider[liftr-state~="dragging"] [liftr-role~="slider-panel"] { }

A section/snippet element?
  → Client-First: .hero_heading { }

A section element with LIFTR module?
  → Consumer-Klasse: liftr-slider.hero_slider { }

A modifier variant?
  → Nested (Pflicht): &.is-compact { }
```

### Tree 4: Nesting — Is This Allowed?

```
I want to nest a selector. Is it allowed?

Does the nested selector target the SAME DOM element?
  (&:hover, &.is-*, &::before, &[attr])
  → YES: Level 1 — Same-element. PFLICHT zu nesten.

Is it a chain on the same element?
  (&.is-sort { &::after { } })
  → YES: Level 2 — Same-element Chain. Allowed.

Is it a modifier on _component with child elements?
  (._component.is-horizontal { ._title { } })
  → YES: Level 2 — Modifier-Children. Max 1 parent→child level.

Anything else?
  → NO: Forbidden. Write it flat.
```

### Modifier Order

Modifier-Klassen werden in dieser Reihenfolge deklariert — innerhalb von `_component`:

| Priorität | Kategorie | Beispiele | Warum |
|-----------|-----------|-----------|-------|
| 1 | **Größe** | `is-small`, `is-medium`, `is-large` | Setzt `--_*` Properties die Varianten konsumieren können |
| 2 | **Variante** | `is-secondary`, `is-icon`, `is-text`, `is-link` | Überschreibt Farben und Struktur auf Basis der Größe |
| 3 | **Layout** | `is-horizontal`, `is-stacked`, `is-compact` | Ändert Anordnung, nicht Größe oder Farbe |
| 4 | **State** | `is-active`, `is-current`, `is-loading` | Überschreibt alle anderen — immer zuletzt |

```css
/* [x] Korrekte Reihenfolge */
.button {
  &.is-small { }      /* 1. Größe */
  &.is-secondary { }  /* 2. Variante */
  &.is-icon { }       /* 2. Variante */
  &.is-text { }       /* 2. Variante */
  &.is-link { }       /* 2. Variante */
  &:disabled { }      /* 4. State */
}
```

---

## File Topology

Every section/snippet CSS file follows this order:

```css
/* ── Component ── */
.section_component { }             /* Own layout, modifiers (&.is-*) */

/* ── LIFTR Settings ── */
liftr-slider.section_slider { }    /* Directly on Consumer (no inheritance) */

/* ── Elements ── */
.section_heading { }               /* Colors (Inline Fallback), typography */
.section_component.is-compact {    /* Modifier-Children: directly at element */
  .section_heading { }
}

/* ── Parent Overrides ── */
.section_component .child_component {
  --child--alignment: left;
}

/* ── Container Queries ── */
@container (max-width: 48rem) {
  .section_component { }           /* Mirrors Component block */
  liftr-slider.section_slider { }  /* Mirrors LIFTR Settings */
  .section_component .child_component { } /* Mirrors Parent Overrides */
}
```

**CQ Rule:** Container Queries mirror the full file structure 1:1. Every base value that changes responsively has a CQ counterpart.

---

## Patterns

### Pattern 1: Section with Layout + Colors

```css
/* ── Component ── */
.testimonials_component {
  display: grid;
  gap: var(--space--large);
  grid-template-columns: 1fr 1fr 1fr;

  &.is-featured {
    grid-template-columns: 2fr 1fr;
  }
}

/* ── LIFTR Settings ── */
liftr-slider.testimonials_slider {
  --slider-enabled: false;
}

/* ── Elements ── */
.testimonials_heading {
  color: var(--testimonials--text, var(--color-scheme--text));
}

.testimonials_card {
  background: var(--testimonials--card, var(--color-scheme--card));
}

/* ── Container Queries ── */
@container (max-width: 48rem) {
  .testimonials_component {
    grid-template-columns: 1fr 1fr;

    &.is-featured {
      grid-template-columns: 1fr;
    }
  }

  liftr-slider.testimonials_slider {
    --slider-enabled: true;
  }
}

@container (max-width: 30rem) {
  .testimonials_component {
    grid-template-columns: 1fr;
    gap: var(--space--medium);
  }
}
```

### Pattern 2: Section with Child-Components + Parent Override

```css
/* ── Component ── */
.faqs_component {
  display: grid;
  grid-template-columns: 1fr 1.618fr;
  gap: var(--space--xlarge);

  &.is-stacked {
    grid-template-columns: 1fr;
    max-width: 48rem;
    margin-inline: auto;
  }
}

/* ── LIFTR Settings ── */
liftr-accordion.faqs_accordion {
  --accordion-mode: single;
}

/* ── Elements ── */
.faqs_heading {
  color: var(--faqs--text, var(--color-scheme--text));
}

/* ── Parent Overrides ── */
.faqs_component .heading-group_component {
  --heading-group--alignment: left;
}

.faqs_component.is-stacked .heading-group_component {
  --heading-group--alignment: center;
}

/* ── Container Queries ── */
@container (max-width: 48rem) {
  .faqs_component {
    grid-template-columns: 1fr;
  }

  liftr-accordion.faqs_accordion {
    --accordion-mode: multi;
  }

  .faqs_component .heading-group_component {
    --heading-group--alignment: center;
  }
}
```

### Pattern 3: Merchant Color Override (Liquid)

```liquid
{%- render 'custom-colors',
  scope: 'section', name: 'hero', id: section.id,
  background: section.settings.background,
  text: section.settings.text
-%}
```

This renders `#shopify-section-{id} { --hero--background: ...; --hero--text: ...; }`.
Colors inherit to all children. CSS never declares these — only consumes with Inline Fallback.

### Pattern 4: Status Variable (State-driven Color)

When a module maps `liftr-state` values to colors (success/error/warning), use a two-step pattern instead of setting `--gradient` directly on the host.

**Step 1 -- Host:** State maps to internal `--_status`

```css
liftr-location[liftr-state~="success"] {
  --_status: var(--color-global--success);
}

liftr-location[liftr-state~="denied"] {
  --_status: var(--color-global--error);
}
```

**Step 2 -- Consumer:** Each child that needs the color maps explicitly

```css
liftr-location [liftr-role~="location-geo-toggle"] {
  --gradient: var(--_status);
}
```

**Why:**
- Visible which elements consume the status color
- No uncontrolled bleed-through via inheritance
- Internal (`--_status`) because the value comes from own state, not from a parent

**Reference:** `--_accent` / `--_icon-mask` in Notifications follow the same principle.

---

## Hard Rules

1. **REM only.** No px except borders.
2. **No inline styles.** Dynamic values via Liquid `{% style %}` + `#id` selector.
3. **No IDs for styling.** Only for Merchant Override specificity (Liquid-generated).
4. **Owner-Pattern for variables:** `--[owner]--[property]`. No `--section-*`, `--block-*`, `--layout-*`.
5. **Layer-Boundary:** `@layer modules` = LIFTR Web Component mechanics (display, visibility, transforms, overflow, positioning of `liftr-*` elements and `[liftr-role]` children). `@layer components` = reusable UI building blocks (colors, typography, border-radius, shadow). `@layer sections` = context-specific layout. Layer priority (normal): `editor > states > sections > components > modules > base`. Layer priority (!important): INVERTED — `base > modules > components > sections > states > editor`. Third-party CSS (no layer) wins over ALL layers.
   **Display Protection Rule:** `modules` sits BELOW `components` and `sections` — the cascade does NOT protect it. By **convention**, `components` and `sections` layers must NEVER set `display` on `liftr-*` Custom Elements or `[liftr-role]` elements when the value affects module visibility. All functional display/visibility of Web Component internals is owned exclusively by `@layer modules` (`core.liftr.css` / `ui.{module}.css`). Violating this breaks module mechanics (e.g. accordion panels stay visible, slider items lose their layout).
6. **!important in same layer.** All `!important` declarations for the same property must live in the same layer (inverted priority).
7. **@font-face outside layers.** CSS spec limitation — will be ignored inside `@layer`.
8. **Focus states in core.base.css only.** No `:focus-visible` in section/component CSS. Exception: documented with `/* EXCEPTION: ... */`.
9. **Nesting is mandatory.** Allowed patterns MUST be nested. Flat `.button_component.is-large` is a violation → must be `&.is-large`.
10. **LIFTR Settings on Consumer, not _component.** Declare directly on `liftr-*.consumer_class`. No inheritance for settings. Inheritance is for colors only.

---

## Property Registration (@property)

LIFTR CSS Settings are registered via `@property` with `inherits: false`. This prevents unintended inheritance through the DOM — a nested `<liftr-panel>` inside a sidebar never inherits the sidebar's `--panel-mode`.

**File:** `core.base.css`, top of file (before `@layer`)

### When to Register

```
Is the variable a LIFTR CSS Setting (read by JS via watchSettings)?
  → YES: Register with @property, inherits: false
  → File: core.base.css

Is the variable a NAV Setting (shared between slider/scroll)?
  → YES: Register with @property, inherits: false
  → File: core.base.css

Is the variable a color? (--gradient, --button--*, --color-scheme--*)
  → NO: Never register. These NEED inheritance.

Is the variable a public layout override? (--faqs--gap, --story-link--width)
  → NO: These use Inline Fallback or DRY Declaration. Inheritance is harmless
  because the consuming element declares the value explicitly.
```

### Registry

| Variable | Module | Syntax | Default |
|----------|--------|--------|---------|
| **Panel** | | | |
| `--panel-enabled` | panel | `<custom-ident>` | `true` |
| `--panel-mode` | panel | `<custom-ident>` | `popup` |
| **Slider** | | | |
| `--slider-enabled` | slider | `<custom-ident>` | `true` |
| `--slider-cols` | slider | `<integer>` | `1` |
| `--slider-gap` | slider | `<length-percentage>` | `0px` |
| `--slider-peek` | slider | `<length-percentage>` | `0px` |
| `--slider-loop` | slider | `<custom-ident>` | `false` |
| `--slider-dots` | slider | `<custom-ident>` | `false` |
| `--slider-autoplay` | slider | `<custom-ident>` | `false` |
| `--slider-mode` | slider | `<custom-ident>` | `single` |
| **Accordion** | | | |
| `--accordion-enabled` | accordion | `<custom-ident>` | `true` |
| `--accordion-mode` | accordion | `<custom-ident>` | `closed` |
| `--accordion-exclusive` | accordion | `<custom-ident>` | `true` |
| `--accordion-icon` | accordion | `<custom-ident>` | `angle` |
| `--accordion-size` | accordion | `<custom-ident>` | `regular` |
| **Scroll** | | | |
| `--scroll-enabled` | scroll | `<custom-ident>` | `true` |
| **NAV (shared: slider + scroll)** | | | |
| `--nav-mode` | nav | `<custom-ident>` | `auto` |
| `--nav-size` | nav | `<custom-ident>` | `medium` |
| `--nav-icon` | nav | `<custom-ident>` | `angle` |
| `--nav-theme` | nav | `<custom-ident>` | `light` |
| `--nav-style` | nav | `<custom-ident>` | `round` |
| `--nav-position` | nav | `<custom-ident>` | `inside` |
| **Marquee** | | | |
| `--marquee-enabled` | marquee | `<custom-ident>` | `true` |
| `--marquee-speed` | marquee | `<number>` | `50` |
| `--marquee-direction` | marquee | `<integer>` | `1` |
| **Sticky** | | | |
| `--sticky-enabled` | sticky | `<custom-ident>` | `false` |
| `--sticky-mode` | sticky | `<custom-ident>` | `auto` |

### Rules

1. **`inherits: false` — always.** CSS Settings are configuration, never ambient context. Each module reads only its own element.
2. **`initial-value` = JS default.** Must match the `default` in the module's `CSS_SCHEMA`. If they diverge, CSS and JS disagree on the unset state.
3. **File: `core.base.css`** — all registrations in one block, before `@layer`. `@property` lives outside layers (CSS spec).
4. **New module = new registration.** When adding a CSS Setting to a LIFTR module, add the `@property` here. Forgetting it reintroduces the inheritance bug.
5. **Never register color variables.** `--gradient`, `--button--*`, `--color-scheme--*`, `--[owner]--background/text/accent` — these all rely on DOM inheritance for the Override system.

### Adding a New Registration

```css
/* In core.base.css, @property block */
@property --{module}-{setting} {
  syntax: '<custom-ident>';    /* or <integer>, <number>, <length-percentage> */
  inherits: false;
  initial-value: {js-default};
}
```

Then verify: Does `CSS_SCHEMA.{setting}.default` in the JS module match `initial-value`? If not, align them.

---

## Responsive

**Fluid-First:** `clamp()` for spacing and typography → no breakpoints needed.
**Container Queries:** For layout switches within components. CQ preferred scale: `30rem`, `48rem`, `64rem`, `85rem`. For rationale and Content Minimums → DESIGN_PRINCIPLES.md.
**Media Queries:** Only for full-viewport changes (hide-tablet, hide-mobile). Desktop-first (`max-width`).

**CSS → JS Communication:** CSS sets Custom Properties in CQ. JS reads via `getComputedStyle(this).getPropertyValue('--setting')`. No synchronization issues because CSS is source of truth.

### Container Classes

Utility container classes provide `container-type: inline-size` for Container Queries. The container class goes on a parent wrapper — **never** on the Custom Element itself.

| Class | Max-Width | Use Case |
|-------|-----------|----------|
| `.container-large` | `85rem` | Standard sections |
| `.container-medium` | `64rem` | Narrow content |
| `.container-small` | `48rem` | Very narrow content |
| `.container-inline` | none (100%) | Full-width with CQ only |
| `.container-full` | none (100%) | Full-width centered |

### CQ Key Rules

- **No named containers.** All CQs are unnamed and resolve against the nearest `container-type: inline-size` ancestor.
- **No style queries.** Don't use `@container style(...)`.
- **No `container-type` on section elements.** The utility container class handles this.
- **Desktop-First.** Always `max-width`, never `min-width`.
- **CQ selectors are flat.** No nesting of child selectors inside CQ. Same-element modifiers (`&.is-*`) are allowed.

### Enable/Disable Pattern

When `--{module}-enabled: false`, the module tears down (removes listeners, resets state). When it becomes `true` again, it re-initializes. This is how responsive behavior works — a slider on mobile becomes a static grid on desktop.

```css
/* Desktop: static grid */
liftr-slider.featured-products_slider {
  --slider-enabled: false;
  --slider-cols: 4;
}

/* Tablet: becomes slider */
@container (max-width: 48rem) {
  liftr-slider.featured-products_slider {
    --slider-enabled: true;
    --slider-cols: 2;
  }
}
```

---

## FOUC / Critical CSS

`core.critical.liquid` is inlined in `<head>` via `theme.liquid`. It contains the minimum CSS to prevent Flash of Unstyled Content before JS loads.

**Decision principle:** Would the user see a flash or shift without it? → Critical. Position fixed/absolute elements are always potentially visible → always critical.

### Which Modules Need Critical CSS

| Component | Critical | What It Prevents |
|-----------|----------|-----------------|
| liftr-slider | Yes | All items visible → only first visible |
| liftr-accordion | Yes | Panels flash open → hidden |
| liftr-scroll | Yes | Nav buttons visible before JS |
| liftr-marquee | Yes | Items stacking vertically → flex row |
| liftr-panel | Yes | Dialog visible → hidden |
| liftr-copyclip | No | Static button, always correct |
| liftr-list | No | Items visible from start |
| liftr-list-filter | No | Inputs visible from start |
| liftr-range | No | Track visible from start |
| liftr-tabs | No | Panels hidden via accordion critical pattern |
| liftr-header | No | Visible from start, JS only adds hide behavior |

### Critical CSS Rules

- **ONLY** styles that prevent visible FOUC
- No transitions, animations, hover states
- No `will-change` or performance hints
- Inlined in `<head>` — not a CSS file

### Skeleton Loading

For modules that need FOUC prevention with a loading indicator (currently: liftr-slider):

```liquid
<liftr-slider class="hero_slider"
  liftr-axis="x" liftr-state="loading" liftr-skeleton="true">
```

Two attributes: `liftr-state="loading"` (JS removes after mount) and `liftr-skeleton="true"` (CSS targets shimmer animation). Two-phase: Phase 1 (CSS) shows shimmer overlay, Phase 2 (JS) removes `loading` state → skeleton fades out.

---

## Component CSS Split

`core.components.css` is split into two files. Both use `@layer components` — no layer change, only a loading strategy difference.

| File | Loading | Contains |
|------|---------|----------|
| `core.components-critical.css` | Synchronous in `<head>` (render-blocking) | Components visible above-the-fold on page load |
| `core.components.css` | Deferred in `<body>` | Components visible only after interaction |

### Decision: Critical or Deferred?

```
Is this component visible on initial page load (above-the-fold)?
  → YES: core.components-critical.css
  → Examples: heading-group, button, store-summary, rating, badge

Is this component only visible after user interaction?
  (Opens via panel, cart action, menu toggle)
  → YES: core.components.css (deferred)
  → Examples: cart line items, menu overlays, panel content

Component appears in BOTH contexts?
  (e.g. button: above-fold CTA AND inside cart panel)
  → core.components-critical.css — above-fold wins
```

### Rules

1. **Same layer.** Both files declare `@layer components`. The cascade treats them identically — split is purely about loading order.
2. **No duplication.** A component's styles live in exactly one of the two files, never both.
3. **Above-fold wins.** If a component appears anywhere on initial page load, it goes in the critical file — even if it also appears in deferred contexts (panels, cart).
4. **Review on new components.** When adding a shared component to `core.components*.css`, decide critical vs. deferred based on the rule above. Document the decision in the CSS file header comment.

---

## Deferred CSS Loading

Interaction-only CSS files (`core.cart.css`, `core.menu.css`) are loaded via `requestIdleCallback` instead of synchronous `<link>` tags. This removes them from the critical rendering path entirely.

### Mechanism

Implemented in `core.liftr.liquid`:

1. **URL storage:** CSS file URLs are stored as `<script type="application/json">` (not executed, no render-blocking).
2. **Idle injection:** An inline script reads the URLs and injects `<link rel="stylesheet">` tags via `requestIdleCallback`.
3. **Promise gate:** `window.__deferredCSS` exposes a Promise that resolves when all deferred stylesheets have loaded.

```html
<!-- In core.liftr.liquid -->
<script type="application/json" id="deferred-css">
  ["{{ 'core.cart.css' | asset_url }}", "{{ 'core.menu.css' | asset_url }}"]
</script>
<script>
  window.__deferredCSS = new Promise(function(resolve) {
    function load() {
      var urls = JSON.parse(document.getElementById('deferred-css').textContent);
      var remaining = urls.length;
      urls.forEach(function(url) {
        var link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = url;
        link.onload = link.onerror = function() { if (--remaining === 0) resolve(); };
        document.head.appendChild(link);
      });
    }
    if ('requestIdleCallback' in window) {
      requestIdleCallback(load);
    } else {
      setTimeout(load, 200);
    }
  });
</script>
```

### Edge Case: Interaction Before CSS

A user may open a panel (cart sidebar, mobile menu) before the deferred CSS has loaded. Without styles, the panel content renders unstyled.

**Solution:** The LIFTR Framework gates panel open on `window.__deferredCSS`. The panel module awaits the Promise before showing content. This adds a near-zero delay on fast connections and a brief loading state on slow connections — always better than an unstyled flash.

### Decision: Synchronous vs. Deferred

```
Is the CSS for a component that is NEVER visible without interaction?
  (Panel content, cart sidebar, mobile menu)
  → Deferred via requestIdleCallback

Is ANY part of the CSS visible on page load?
  (Header base styles, footer, above-fold sections)
  → Synchronous (head or body)

Is it a LIFTR module CSS (core.liftr.css, ui.*.css)?
  → Synchronous — modules control FOUC-critical display/visibility
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| State/Sichtbarkeit per CSS-Klasse: `.is-success .success-msg` | Attribut-Selektor: `[liftr-state~="success"] [liftr-role~="success-message"]` |
| Rolle per CSS-Klasse: `.error-panel { display: none }` | Attribut-Selektor: `[liftr-role~="error-panel"] { display: none }` |
| CSS Settings via descendant: `.section liftr-slider { }` | Compound selector: `liftr-slider.context_slider { }` |
| CSS Settings on `[liftr-id]` | Compound selector mit Consumer-Klasse |
| Double-dash module properties: `--slider--cols` | Single-dash: `--slider-cols` |
| Duplicating `overflow: hidden` in section CSS | Already in core.liftr.css (`@layer modules`) |
| Duplicating NAV arrow styles | Already in core.liftr.css (`@layer modules`) |
| Duplicating state visibility rules | Already in core.liftr.css (`@layer modules`) |
| Setting `display` on `[liftr-role]` in section/component CSS | Module visibility lives in `@layer modules` (`core.liftr.css` / `ui.{module}.css`). Never override in `@layer components` or `@layer sections` — breaks module mechanics. |
| Using named containers on section elements | Use utility container class |
| Using `@container style(...)` | Use unnamed `@container (max-width: ...)` |
| Using `min-width` in Container Queries | Desktop-First: always `max-width` |
| Gap/peek values in px | Use REM values or `var(--space--*)` tokens |
| Parent setzt `--_[prop]` | `--_*` sind internal — Parent setzt `is-*` Modifier-Klasse |
| Modifier setzt `--[owner]--[prop]` fuer Groesse | Groesse ist internal -> `--_[prop]` |
| `--gradient` direkt auf Host bei State-Farben | Status Variable Pattern: `--_status` auf Host, Kind mapped `--gradient: var(--_status)` |
| Neue CSS Setting ohne `@property` | Registrieren in `core.base.css` mit `inherits: false` |

---

## Token Reference

For the complete design token tables (spacing, typography, shadows, transitions, z-index, etc.), read: `references/tokens.md`

Key scales for quick reference:

**Spacing:** `tiny | xxsmall | xsmall | small | medium | large | xlarge | xxlarge | huge | xhuge | xxhuge`
**Component gaps:** `--gap--small | --gap--medium | --gap--large` (tighter than --space--)
**Transitions:** `instant(50ms) | fast(150ms) | base(250ms) | slow(360ms) | slower(400ms) | deliberate(600ms)`
**Z-index:** `base(1) | above(2) | elevated(10) | dropdown(100) | sticky(200) | overlay(300) | sidebar(500) | modal(1000)`
