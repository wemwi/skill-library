# LIFTR Card Architecture

**Shared foundation for all card components.** Product Card, Store Card, and future cards share this architecture. Component-specific details live in `store.md` and the CSS docblocks (`snippet.product.css`, `snippet.store.css`).

---

## Golden Ratio Grid (Horizontal)

Horizontal cards use a CSS Grid with Golden Ratio proportions:

```
┌─────────────┬──────────────────────┐
│             │                      │
│   Image     │       Body           │
│   1fr       │       1.618fr        │
│             │                      │
└─────────────┴──────────────────────┘
```

| Property | Value | Rationale |
|----------|-------|-----------|
| `grid-template-columns` | `1fr 1.618fr` | Golden Ratio split |
| `aspect-ratio` | `2.618` | = 1 + φ. Makes image column exactly square |
| Image `aspect-ratio` | `unset` (fills cell) | Grid cell geometry determines ratio |
| Image `grid-row` | `1 / -1` | Spans full height |

**Math:** Component width W → Image column = W / 2.618. Cell height = W / 2.618 (from component aspect-ratio). Image column is W/2.618 × W/2.618 = square.

---

## Spacing: Margin-Based (No Component Padding)

Cards use **margin on children** instead of padding on the component. This avoids the box-sizing asymmetry that breaks the Golden Ratio calculation.

```css
/* Component: NO padding */
._component {
  overflow: hidden;
  border-radius: var(--border-radius--small);
}

/* Children: own margins */
._image {
  margin: var(--space--xsmall);
}

._body {
  margin: var(--space--small);
  padding-top: var(--space--small);  /* Horizontal only — vertical uses 0 */
}
```

**Why not padding on component?**
With `box-sizing: border-box`, padding subtracts from content area asymmetrically — the grid columns get narrower but the cell height loses padding only once. The image column is no longer square. Margin on children keeps the grid geometry intact.

**Density CQs tighten margins** (not padding) when space shrinks:

```css
@container (max-width: 21rem) {
  ._body {
    margin: var(--space--xsmall);
    padding-top: var(--space--xsmall);
  }
}
```

---

## Layouts: Vertical, Horizontal, Auto

### Vertical (`is-vertical`)

```css
._component.is-vertical {
  display: flex;
  flex-direction: column;
}

._component.is-vertical ._body {
  padding-top: 0;                       /* Margin handles image-body gap */
  justify-content: space-between;       /* Even distribution in equal-height grids */
}

._component.is-vertical ._info { margin-top: 0; }
._component.is-vertical .footer { margin-top: 0; }
```

- Height is **flexible** — card grows with content
- `space-between` distributes content evenly when cards have different amounts of content in equal-height grids
- `margin-top: auto` is NOT used — that's for horizontal only
- Only width constrains density
- Rating, Stock always visible (height accommodates)

### Horizontal (`is-horizontal`)

```css
._component.is-horizontal {
  display: grid;
  grid-template-columns: 1fr 1.618fr;
  aspect-ratio: 2.618;
  min-width: 18rem;
}
```

- Height is **fixed** by aspect-ratio
- Both width and height constrain density
- Elements must be removed as card shrinks
- `margin-top: auto` on info/footer pushes content to center and bottom
- **Min-width floor: 18rem** — density system exhausts all levers at D3-b (18rem). Below this, the layout breaks physically. Parent must provide at least 18rem.

### Auto (`is-auto`)

Horizontal by default, flips to vertical via CQ:

```css
._component.is-auto {
  display: grid;
  grid-template-columns: 1fr 1.618fr;
  aspect-ratio: 2.618;
}

/* Flip CQ at ≤34rem: grid → flex column, reset to D0-vertical
   → full requirements and code: card-density.md (Auto-Flip) */
```

**After the flip, `is-auto` = `is-vertical`.** All vertical density CQs apply via `:not(.is-horizontal)`.

---

## Selector Strategy

Five patterns cover all targeting needs. These are the **only** selectors used in card density CQs.

| # | Target | Selector | When to use |
|---|--------|----------|-------------|
| 1 | **Currently horizontal** (is-horizontal + is-auto pre-flip) | `:not(.is-vertical)` | H-CQs **above** flip point |
| 2 | **Forced horizontal** (is-horizontal only, never flips) | `.is-horizontal` | H-CQs **at/below** flip point, min-width |
| 3 | **Currently vertical** (is-vertical + is-auto post-flip) | `:not(.is-horizontal)` | V-CQs (all below flip point) |
| 4 | **Always vertical** (is-vertical only) | `.is-vertical` | Static base overrides (padding-top, space-between) |
| 5 | **Auto flip reset** (is-auto only) | `.is-auto` | Flip CQ — layout switch + D0-vertical reset |

### Why `:not()` instead of explicit selectors

`:not(.is-vertical)` is preferred over `.is-horizontal, .is-auto` because:
- More concise (one selector vs two)
- Future-proof (new layout variants automatically included)
- Same specificity

### Boundary: Flip Point

The flip point (typically ≤34rem) is the dividing line:

```
H-CQs above flip ──── :not(.is-vertical) ──── matches is-horizontal + is-auto
                           ┃ flip point ┃
H-CQs at/below flip ── .is-horizontal ──────── matches is-horizontal only
V-CQs (all below) ──── :not(.is-horizontal) ── matches is-vertical + is-auto
```

### Child Overrides

Horizontal + Auto share identical grid child overrides. Use `:not(.is-vertical)`:

```css
._component:not(.is-vertical) {
  ._image {
    grid-row: 1 / -1;
    min-height: 0;
  }

  ._body {
    min-width: 0;
    min-height: 0;
  }

  .footer {
    min-width: 0;
  }
}
```

`min-width: 0` / `min-height: 0` prevent grid blowout from content overflow.

---

## Density CQ System

Two independent systems for two different physical constraints.

> **Normative Details → `card-density.md`.** This section covers the structural concept. For D0–D3 Range definitions, Token-Wechsel tables, absolute Floors, Trigger-Breakpoint Ranges, max CQ-Steps per Range, and the Monotonie-Regel, see `card-density.md`.

### Horizontal Density (D-Stufen)

Fixed height — elements are removed to fit.

| Range | Steps | Principle |
|-------|-------|-----------|
| D1 | 1–3 | Spacing tightens, description reduced/hidden |
| D2 | 1–2 | P3 hidden, fonts shrink, rating shrunk, price swap |
| D3 | 1–2 | Badges hidden, floors reached, extreme spacing |

### Vertical Density (V-Stufen)

Flexible height — elements hidden only when width makes them unreadable.

| Range | Steps | Principle |
|-------|-------|-----------|
| V-D1 | 1–2 | Spacing tightens |
| V-D2 | 1 | Description hidden, fonts shrink |
| V-D3 | 1–2 | Stock/badges hidden, price swap, footer wraps |

### Min-Width Floor

When all density levers are exhausted (D3 final step), the card has a **physical minimum width** below which no further reduction is possible.

| Layout | Min-Width | Rationale |
|--------|-----------|-----------|
| `is-horizontal` | `18rem` | D3-b exhausts all levers: margin xxsmall, gap 0, title regular, price swapped, badges gone. Below 18rem the layout breaks physically. |
| `is-vertical` | None | Height flexible, content stacks. Footer wraps at V-D3. |
| `is-auto` | None | Flips to vertical before horizontal becomes too small. |

**Implementation:** `min-width` on the component. Parent (grid/slider) must respect this — if the available column is < 18rem, the parent should reduce columns or switch layout.

### Calibration Process

Breakpoints are **calibrated against live data**, not guessed:

1. Deploy with initial breakpoints
2. Run density audit script on all pages containing cards
3. Identify near-misses (cards within 2rem of a breakpoint but not triggering)
4. Adjust breakpoints to cover measured widths with ~1rem buffer
5. Re-run audit to confirm no near-misses

**The audit script** (`density-audit.js`, not part of the theme repo) measures all cards on page, maps widths to breakpoints, flags near-misses. Run on each page with cards at multiple viewport widths.

---

## Density Scaling Priority

Universal priority order for element removal as card width decreases. Applies to all card types. Each step is less reversible than the previous — exhaust earlier steps before moving to later ones.

> **Element-Taxonomie (P1–P4) → `card-density.md`.** This section defines the *action sequence* (what to do first). `card-density.md` defines the *element classification* (which elements belong to which priority tier, per card type). Both are needed: architecture for the sequence, density for the mapping.

### Priority 1: Spacing

Tighten gap, margin, padding. No content loss, hierarchy stays readable. Can cascade multiple times (small → xsmall → 0). Always the first step.

```css
/* Good: spacing first */
@container (max-width: 44rem) {
  ._body { margin: var(--space--xsmall); }
}

/* Bad: hiding content while spacing is still loose */
@container (max-width: 44rem) {
  ._description { display: none; }
}
```

### Priority 2: Redundant Info

Hide content that is accessible elsewhere (Panel, detail page, parent context). Key question: **can the user reach this info with one click?** If yes, it can go.

Examples: address (→ panel), highlights/badges (→ panel), closing time (→ opening status suffices), description (→ detail page).

### Priority 3: Actions

Hide shortcut buttons that have alternatives. The card itself is typically clickable — action buttons are convenience, not exclusive access.

Examples: route button (→ panel), phone button (→ panel), quick-add (→ product page).

### Priority 4: Font Size

Shrink text without hiding it. Works only 1–2 token steps before becoming unreadable.

| Minimum | Context |
|---------|---------|
| `--font-size--small` | Content text (name, description) |
| `--font-size--tiny` | Meta text (count, label, distance) |

Never shrink below these floors. If text is still too large after 2 steps, move to Priority 5.

### Priority 5: Partial Content

Hide parts of a visible element while keeping its core. The primary signal stays, context is lost.

Examples: rating count (stars remain), district name (city remains), dot separator, stock text (status dot remains).

### Priority 6: Whole Components

Remove entire UI blocks. Last resort — the card becomes a pure teaser (image + name). Only when the card is physically too small for the component to be readable.

Examples: rating completely, store-info completely, highlights completely.

### Hard Constraints (Never Hide)

These override all priorities — they are never removed at any density:

| Element | Reason |
|---------|--------|
| **Primary identity** (name, image) | Card is meaningless without it |
| **Unit price** (`.product_price-unit`) | EU Preisangabenverordnung — legal requirement |
| **Price** (at least in one location) | Commercial requirement |

### Horizontal vs. Vertical

The same priority order applies to both layouts, but **horizontal is more aggressive** because fixed height creates a physical ceiling. Vertical cards have flexible height — only width constrains readability, so they reach Priority 5–6 much later (or never).

| Priority | Horizontal | Vertical |
|----------|-----------|----------|
| 1 Spacing | Early (≤44rem) | Late (≤16rem) |
| 2 Redundant Info | Mid (≤38rem) | Managed by child CQs |
| 3 Actions | Mid (≤28rem) | Late (≤16rem) |
| 4 Font Size | Mid-late (≤28rem) | Very late (≤14rem) |
| 5 Partial Content | Late (≤26rem) | Rare |
| 6 Whole Components | Last resort (≤21rem) | Last resort (≤12rem) |

Exact breakpoints are component-specific and calibrated. The table shows typical ranges.

### Self-Contained Children

Child components (e.g. store-info) that have their own `container-inline` and CQs manage their own density through the same priority order. The card's V/D-stufen control only card-owned elements — never reach into a self-contained child's internals.

---

## Rating

**Rating should be preserved as long as possible** — social proof is high-value for conversion. Use Priority 4 (font-size shrink via CSS API) before Priority 6 (removal).

- **Vertical/Auto:** Height is flexible — rating adds ~1rem, card grows. Shrink via CSS API at narrow widths. Hide only as last resort when card is too narrow for stars to be readable.
- **Horizontal (dense):** Shrunk via rating CSS API first, hidden only when fixed height leaves no room.

```css
/* Priority 4: Shrink first */
@container (max-width: 26rem) {
  ._component.is-horizontal .rating_component {
    --rating--icon-size: 0.625rem;
    --rating--count-font-size: var(--font-size--tiny);
    --rating--value-font-size: var(--font-size--tiny);
  }
}

/* Priority 6: Hide only as last resort */
@container (max-width: 18rem) {
  ._component.is-horizontal .store_rating {
    display: none;
  }
}
```

Rating CSS API variables (`--rating--icon-size`, `--rating--value-font-size`, `--rating--count-font-size`) → `rating.md` (liftr-liquid).

---

## Price Swap Pattern

At high density, price moves from body to footer (side-by-side with ATC button):

```
Normal:                          Dense:
┌──────────────────┐             ┌──────────────────┐
│ Title            │             │ Title            │
│ Rating           │             │ Rating           │
│ Price  ←─ body   │             │                  │
│                  │             │ Price   [ATC] ←─ │
│ Stock    [ATC]   │             │   footer         │
└──────────────────┘             └──────────────────┘
```

**Implementation:** Both prices exist in DOM. CSS toggles visibility:

```css
/* Base: body price visible, footer price hidden */
._body > ._price { display: flex; }
.footer ._price { display: none; }

/* Dense: swap */
@container (max-width: ...) {
  ._component > ._body > ._price { display: none; }
  ._component .footer ._price { display: flex; }
}
```

**Selector specificity:** Body price uses child combinator (`>`) to avoid matching footer price.

---

## Legal Constraints

| Constraint | Rule | Source |
|-----------|------|--------|
| Unit Price | **NEVER** hidden at any density | EU Preisangabenverordnung |
| `.product_price-unit` | Always visible, even when body price swaps to footer | German law |

Both body and footer price blocks must contain unit price markup. The swap is transparent to legal compliance.

---

## Extension API Pattern

Cards expose **colors + image ratio** only. Sizing is never overridable — Density CQs are the sole authority.

```css
/* Allowed Parent Overrides (colors + image) */
--{card}--background    → color-scheme--card
--{card}--text          → color-scheme--text
--{card}--accent        → color-scheme--accent
--{card}--border        → none
--{card}--image-ratio   → 1

/* NOT overridable (Density CQ owns these) */
gap, padding, margin, font-size, display
```

---

## New Card Checklist

When creating a new card component:

### Architecture
- [ ] Golden Ratio grid for horizontal (1fr 1.618fr, aspect-ratio 2.618)?
- [ ] Margin-based spacing (no component padding)?
- [ ] Auto layout with CQ flip at ≤34rem?
- [ ] Child overrides using `:not(.is-vertical)` (Selector Strategy #1)?
- [ ] Vertical: `space-between`, `padding-top: 0`, no `margin-top: auto`?
- [ ] Horizontal: `min-width` at D3-b floor?

### Selectors
- [ ] Pre-flip H-CQs use `:not(.is-vertical)` (#1)?
- [ ] At/post-flip H-CQs use `.is-horizontal` (#2)?
- [ ] V-CQs use `:not(.is-horizontal)` (#3)?
- [ ] Vertical base uses `.is-vertical` (#4)?
- [ ] Auto flip uses `.is-auto` (#5)?

### Density
- [ ] Density Scaling Priority followed (Spacing → Redundant → Actions → Font → Partial → Whole)?
- [ ] Elements classified P1–P4 per `card-density.md`?
- [ ] Token-Wechsel from `card-density.md` Token-Wechsel-Tabelle applied?
- [ ] Absolute Floors from `card-density.md` respected?
- [ ] Horizontal D-stufen defined with calibrated breakpoints?
- [ ] Vertical V-stufen defined with calibrated breakpoints?
- [ ] Auto density merged into Vertical (post-flip = vertical)?
- [ ] Rating shrunk via CSS API before hidden?
- [ ] Price swap at highest density (body → footer)?
- [ ] Legal: unit price visible at all densities?
- [ ] Self-contained children manage their own CQs?

### Extension API
- [ ] Only color + image-ratio variables exposed?
- [ ] Sizing NOT overridable (direct tokens, CQ authority)?
- [ ] Inline Fallback on all color variables?

### Calibration
- [ ] Breakpoints tested against live container widths?
- [ ] No near-misses at common viewport sizes?
- [ ] Audit script run on all pages containing the card?

---

## Existing Cards

| Card | Skill/Docblock | H-Stufen | V-Stufen | Flip | Min-Width | Density |
|------|---------------|----------|----------|------|-----------|---------|
| Product | snippet.product.css docblock | D1-a ≤44, D1-b ≤42, D1-c ≤34, D2-a ≤28, D2-b ≤26, D3-a ≤21, D3-b ≤18 (7) | V-D1 ≤16, V-D2 ≤14, V-D3 ≤12 (3) | ≤34rem | 18rem | P-Mapping + Token-Shifts → `card-density.md` |
| Store | snippet.store.css docblock | H1–H7 (≤44rem → ≤18rem) | V1–V3 (≤16rem → ≤8rem) | ≤34rem | TBD | P-Mapping + Token-Shifts → `card-density.md` |
