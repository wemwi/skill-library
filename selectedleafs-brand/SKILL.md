---
name: selectedleafs-brand
description: "Style kit for selectedleafs.com — the dark, nature-premium Kratom brand (Räuchermischung), with Tea and Special-Herbs lines. Provides exact color palette, typography, spacing tokens, logo guidance, component recipes, real product mockup images, icon sprite sheets, and design language for creating React demo artifacts, mockups, and visual prototypes that approximate the real store look. Use whenever creating demos, visual prototypes, landing page mockups, product grids/cards, reporting with brand styling, or any artifact that should look and feel like selectedleafs or needs real selectedleafs product imagery, brand logos, or store icons. Also use when the design-exploration skill needs brand values for a demo. Triggers on: demo, mockup, prototype, brand colors, selectedleafs style, visual preview, approximate style, logo, product images, product cards, icons, sprite, Kratom, Tee, packaging."
---

# Brand Kit: selectedleafs

Style reference for creating artifacts that approximate the selectedleafs.com look and feel.

**Use case:** React demos, HTML mockups, visual prototypes — NOT for Shopify theme code (use liftr-* skills for that).

> **Canonical values → `references/tokens.json`.** That file is the machine-readable mirror of the live theme (`core.base.css` v6.0), with exact CSS strings (incl. fluid `clamp()` sizes), `$source` provenance, and `$meta.corrections`. **It is the source of truth.** The tables in this document are a hand-readable *quick reference* — deliberately rounded/condensed for fast demo work. If a value here ever disagrees with `tokens.json`, **tokens.json wins.** Read it whenever you need exact, current, or complete values (full scales, status colors, breakpoints, effects).

---

## 1. Design Language

**One-liner:** Dark nature-premium with glass effects — forest greens, gold accents, organic warmth.

**Characteristics:**
- Dark backgrounds with subtle gradient depth
- Glassmorphism cards (translucent, blurred backdrop)
- Gold for premium/highlight moments
- Leaf green for actions and CTAs
- Restrained, confident — no flashy animations
- Noise texture overlay on body for organic feel

---

## 2. Color Palette

### Brand Colors

| Token | Hex | Role |
|-------|-----|------|
| `--brand--primary` | `#1a3c33` | Dark forest green — deepest background |
| `--brand--primary-accent` | `#b8923a` | Gold — premium highlights, badges |
| `--brand--secondary` | `#1e4d42` | Medium dark green — sections, panels |
| `--brand--secondary-accent` | `#6c9c4a` | Leaf green — CTAs, primary buttons |

### Body Background

```css
/* Darkened 2-stop forest gradient ("Subtil", live since 2026-06-12) */
background: linear-gradient(180deg, #245145 1%, #16342c 100%);
/* Plus noise texture overlay for organic feel */
```

### Light Scheme (background-1)

| Role | Value |
|------|-------|
| Background | `#ffffff` |
| Card | `#f5f5f5` |
| Text | `#121212` |
| Button Primary | `#6c9c4a` (text: `#ffffff`) |
| Button Secondary | `#ffffff` (text: `#6c9c4a`) |

> Cream `#f0e2c0` is **not** a scheme/body color — it's only a `.page-header` surface override (custom CSS). Body is always the green gradient above.

### Dark Scheme (primary theme)

| Role | Value |
|------|-------|
| Background | `#1a3c33` |
| Gradient | `linear-gradient(180deg, #183f36, #173931)` |
| Card | `#1e4d42` |
| Text | `#ffffff` |
| Border | `rgba(255,255,255,0.1)` |

### Highlight Colors (all gradients)

| Label | Color | Gradient | Solid Fallback |
|-------|-------|----------|----------------|
| New / Promo | Salbei | `linear-gradient(135deg, #93b389, #7a9c6f)` | `#93b389` |
| Sale / Error | Zinnober | `linear-gradient(180deg, #c2403a, #a8332c)` | `#c2403a` |
| Info | Petrol | `linear-gradient(135deg, #44707d, #355a66)` | `#44707d` |
| Warning | Amber | `linear-gradient(180deg, #d4842a, #b66e1f)` | `#d4842a` |
| Success | Leaf Green | `linear-gradient(180deg, #6c9c4a, #609142)` | `#6c9c4a` |
| Bestseller / Rating | Gold | `linear-gradient(135deg, #d4ad5a, #b8923a 50%, #96751e)` | `#b8923a` |

> The **Salbei/Petrol/Amber/Zinnober** status palette went **live in the theme on 2026-06-12** (replacing the old Teal/Rot/Orange/Blau set). Success (Leaf) and Bestseller/Rating (Gold) are unchanged. A Status END-REVIEW (WCAG finalization) is still open per project notes — see `tokens.json` → `color.highlight` / `color.system` / `$meta.statusColorNote` for the authoritative state.

---

## 3. Typography

### Font Families

| Role | Font | Fallback |
|------|------|----------|
| Headings | **Lora** (Bold, 700) | Georgia, serif |
| Body | **DM Sans** (Regular, 400) | system-ui, sans-serif |

For React demos: Use Google Fonts import or approximate with `Georgia` / `system-ui`.

```html
<link href="https://fonts.googleapis.com/css2?family=Lora:wght@700&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
```

### Font Sizes (Desktop end — demo set)

> Live theme uses fluid `clamp()` (320→1440px). The rows below are the desktop end of the sizes a demo actually reaches for. **Full scale + exact `clamp()` strings → `tokens.json` → `typography.fontSize`** (`tiny` 0.75rem · `medium` 1.25rem · `h4`=`large` 1.5625rem also live there).

| Token | Desktop | Usage |
|-------|---------|-------|
| `small` | 0.875rem (14px) | Captions, labels |
| `regular` | 1rem (16px) | Body text |
| `h3` | 2rem (32px) | Section sub-headings |
| `h2` | 2.5rem (40px) | Section headings |
| `h1` | 3.125rem (50px) | Page titles |

### Font Weights

| Token | Value | Usage |
|-------|-------|-------|
| Regular | 400 | Body text |
| Bold | 500 | Emphasis, labels |
| XBold | 700 | Headings |

### Line Heights

| Context | Value |
|---------|-------|
| Headings | 1.3 |
| Body text | 1.5 |
| Compact | 1.0 |

### Text Opacity

| Style | Opacity | Usage |
|-------|---------|-------|
| Subtle | 0.8 | Secondary text |
| Muted | 0.5 | Tertiary, timestamps |
| Faint | 0.3 | Disabled, placeholders |

---

## 4. Spacing

### Space Scale (Desktop end — demo set)

> Fluid `clamp()` in the theme; rows below are the desktop end of the common rungs. **Full scale → `tokens.json` → `spacing.scale`** (adds `tiny` 2px · `xxsmall` 4px · `xsmall` 8px · `xxlarge` 64px · `huge` 96px).

| Token | Value | Usage |
|-------|-------|-------|
| `small` | 16px | Element gaps inside cards |
| `medium` | 24px | Card padding, content gaps |
| `large` | 32px | Section content gaps |
| `xlarge` | 48px | Between content blocks |

**Grid gaps:** `gap-small` 12px · `gap-medium` 20px · `gap-large` 28px (`tokens.json` → `spacing.gap`).

### Section Padding & Page Gutter

| Token | Desktop | tokens.json |
|-------|---------|-------------|
| Section Small / Medium / Large | 48 / 80 / 128px | `spacing.layout.padding-section-*` |
| Padding Global (gutter) | 40px (mobile 16px) | `spacing.layout.padding-global` |

---

## 5. Borders & Radius

| Token | Value | Usage |
|-------|-------|-------|
| `border-radius--small` | 4px (0.25rem) | Buttons, inputs, badges |
| `border-radius--medium` | 8px (0.5rem) | Cards, sections |
| `border-radius--large` | 16px (1rem) | Large panels, modals |
| `border-radius--full` | 9999px | Pills, avatars |

Border color: always `rgba(text, 0.1)` — on dark bg: `rgba(255,255,255,0.1)`.

---

## 6. Shadows & Glass

**Box shadows:** Small `0 2px 5px rgba(0,0,0,.1)` · Medium `0 4px 12px rgba(0,0,0,.15)` · Large `0 8px 24px rgba(0,0,0,.2)` (full set → `tokens.json` → `shadow.box`).

### Glassmorphism Cards (signature style)

```css
/* On dark backgrounds (primary theme): */
.glass-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(48px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  padding: 24px;
}

/* On light backgrounds: */
.glass-card-light {
  background: rgba(0, 0, 0, 0.04);
  backdrop-filter: blur(48px);
  border-radius: 0.5rem;
  padding: 24px;
}
```

---

## 7. Transitions & Easing

Plain CSS transitions — no motion framework involved. **Demo default:** `250ms cubic-bezier(0.22, 1, 0.36, 1)` (= `base` + `ease-out`); use `150ms` for hovers. The `BRAND` object in §12 ships both as `transitionBase` / `transitionFast`.

Full duration ladder (`instant` 50ms → `deliberate` 600ms) and the easing set (`ease-in`, `spring`, `smooth`, `snappy`) → `tokens.json` → `transition.duration` / `transition.easing`.

---

## 8. Icons

**Sizes:** 12 / 16 / 24 (regular) / 32 / 40 / 48px — full token list → `tokens.json` → `iconSize`.

Icon set is **"light"** weight (thin strokes). For quick demos use **Lucide** icons as closest match — but for high-fidelity selectedleafs mockups, prefer the real sprite sets below.

### Real Icon Sprites (`assets/icons/`)

The actual store icons (Font Awesome, `currentColor` fill) ship as four **SVG sprite sheets** — each is a hidden `<svg>` containing many `<symbol id="...">`. Reference a symbol with `<use>`; color follows `currentColor`, size via width/height.

```html
<!-- 1. Inline the sprite sheet once (it renders nothing, display:none) -->
<!-- paste contents of assets/icons/icon-default.svg here -->

<!-- 2. Use any symbol by id, anywhere: -->
<svg width="24" height="24" style="color:#6c9c4a"><use href="#bag-shopping"/></svg>
```

| File | Symbols | Contains |
|------|---------|----------|
| `assets/icons/icon-critical.svg` | 4 | Above-the-fold essentials: `bag-shopping`, `check`, `grip-lines`, `user` |
| `assets/icons/icon-default.svg` | 43 | General UI: arrows (`angle-right`, `arrow-right`, `arrows-rotate`…), `plus`/`minus`/`xmark`, `trash-can`, `heart`, `star-sharp`, `gift`, `envelope`, `phone`, `store`, `tag`/`tags`, `truck-fast`, `shield-check`, `sparkles`, `trophy`, `circle-info`/`circle-question`/`circle-exclamation`, etc. |
| `assets/icons/icon-social.svg` | 17 | Social brands: `instagram`, `facebook-f`, `x-twitter`, `tiktok`, `youtube`, `whatsapp`, `discord`, `spotify`, `threads`, `linkedin-in`, `pinterest-p`, `snapchat`, `twitch`, `vimeo-v`, `tumblr`, `line`, `kakao-talk` |
| `assets/icons/icon-store.svg` | 19 | Store-finder / mobility: `location-dot`, `location-arrow`, `diamond-turn-right`, `bicycle`, `car`, `taxi-bus`, `moped`, `person-walking`, `wheelchair-move`, `square-parking`, `credit-card`, `nfc-signal`, `wifi`, `dog-leashed`, `money-bill-1-wave`, `box`, `heart`, `user-hair-long`, `location-question` |

Notes: all viewBox `0 0 640 640`. Some `icon-store` glyphs use two-tone paths (`opacity=".4"` layer) — they still inherit `currentColor`. When you only need a couple of glyphs in a demo, copy just those `<symbol>` blocks rather than the whole sheet.

---

## 9. Z-Index Scale

Layer order (low→high): `base` 1 · `above` 2 · `elevated` 10 · `dropdown` 100 · `sticky` 200 · `overlay` 300 · `panel-overlay` 400 · `panel` 500 · `modal-backdrop` 900 · `modal` 1000 · `notification` 1100. Exact values → `tokens.json` → `zIndex`.

---

## 10. Component Recipes for Demos

### Primary Button

```css
.btn-primary {
  background: #6c9c4a;
  color: #ffffff;
  font-family: 'DM Sans', system-ui, sans-serif;
  font-weight: 500;
  padding: 12px 24px;
  border-radius: 0.25rem;
  border: none;
  cursor: pointer;
  transition: all 150ms cubic-bezier(0.22, 1, 0.36, 1);
}
```

### Secondary Button

```css
/* Light scheme: white fill, leaf-green text + hairline border */
.btn-secondary {
  background: #ffffff;
  color: #6c9c4a;
  border: 1px solid rgba(0, 0, 0, 0.1);
  font-family: 'DM Sans', system-ui, sans-serif;
  font-weight: 500;
  padding: 12px 24px;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 150ms cubic-bezier(0.22, 1, 0.36, 1);
}
/* On dark backgrounds, use a translucent glass fill instead:
   background: rgba(255,255,255,0.08); color: #fff;
   border: 1px solid rgba(255,255,255,0.1); */
```

### Section (dark, typical)

```css
.section-dark {
  background: linear-gradient(180deg, #1e4d42, #1a3c33);
  color: #ffffff;
  padding: 80px 40px;
}
```

### Heading Group

```css
.heading-group h2 {
  font-family: 'Lora', Georgia, serif;
  font-weight: 700;
  font-size: 2.5rem;
  line-height: 1.3;
  color: #ffffff;
}

.heading-group .pre-heading {
  font-family: 'DM Sans', system-ui, sans-serif;
  font-size: 1rem;
  font-weight: 400;
  text-transform: uppercase;
  color: #b8923a;
}
```

### Badge (Highlight)

```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: #ffffff;
}
.badge-sale { background: linear-gradient(180deg, #c2403a, #a8332c); } /* Zinnober */
.badge-new  { background: linear-gradient(135deg, #93b389, #7a9c6f); } /* Salbei */
.badge-best { background: linear-gradient(135deg, #d4ad5a, #b8923a 50%, #96751e); } /* Gold */
```

---

## 11. Logo & Identity

The real logos live in `assets/logos/` as fully path-outlined SVGs (no `<text>`, no embedded font). They are self-contained and render identically everywhere — **prefer inlining them over any approximation.** The custom display typeface is baked into the paths; there is no font file to load.

### Asset Files

| File | Ink color | Use on | Dimensions (viewBox) |
|------|-----------|--------|----------------------|
| `assets/logos/Logo-Dark-Plain.svg` | Black wordmark | **Light** backgrounds | 360×116 (~3.1:1) |
| `assets/logos/Logo-Light-Plain.svg` | White wordmark | **Dark** backgrounds | 360×116 (~3.1:1) |
| `assets/logos/Logo-Dark-Claim.svg` | Black + gold claim | **Light** backgrounds | 360×175 |
| `assets/logos/Logo-Light-Claim.svg` | White + gold claim | **Dark** backgrounds | 360×175 |
| `assets/logos/Favicon.svg` | Gradient + white leaf | Anywhere | 155×155 |

Naming: **Dark** = dark ink (for light backgrounds), **Light** = light/white ink (for dark backgrounds). **Plain** = wordmark + leaf only. **Claim** = adds the gold tagline (`#B8923A`) below the wordmark, hence the taller viewBox.

For the selectedleafs site (dark theme) the default is `Logo-Light-Plain.svg`.

### Wordmark

Two-line custom display typeface — **not** a standard Google Font. Line 1: "Selected", Line 2: "leafs." (with period). High-contrast serifs with decorative terminals. Always use the full wordmark — no abbreviation.

### Leaf Icon

Organic two-part leaf to the upper-right of the wordmark. The leaf keeps its brand greens in **both** the Dark and Light variants — it does *not* turn white on dark backgrounds; only the wordmark ink color flips.

| Part | Color | Hex |
|------|-------|-----|
| Upper leaf (larger, sweeping) | Dark green | `#21453A` |
| Lower leaf (smaller, upward) | Medium green | `#326757` |

### Favicon

Rounded mark with a multi-stop green gradient background and a white leaf centered. 155×155.

Gradient stops (top→bottom): `#1A3C33 → #1E4D42 → #2B6E5E → #1E4D42`.

Demo approximation (when you don't want to inline `assets/logos/Favicon.svg`):

```jsx
<div style={{
  width: 32, height: 32,
  borderRadius: '30%',
  background: 'linear-gradient(180deg, #1A3C33, #2B6E5E 60%, #1E4D42)',
  display: 'flex', alignItems: 'center', justifyContent: 'center',
}}>
  <Leaf size={18} color="#fff" strokeWidth={1.5} />
</div>
```

### Logo in Demos — decision order

1. **Exact logo (preferred):** read the relevant file from `assets/logos/` and paste the SVG markup inline. It has no external dependencies, so it works as-is in any React/HTML artifact. Pick the variant by background (Light ink on dark, Dark ink on light).
2. **Quick approximation (throwaway mockups only):** wordmark as `'Lora', Georgia, serif` bold rendering "Selected" + "leafs."; leaf as Lucide `Leaf` in brand greens (`#326757` / `#21453A`).

---

## 12. React Demo Starter

Minimal `BRAND` object for Tailwind-free React artifacts:

```jsx
const BRAND = {
  // Core palette
  primary:      '#1a3c33',
  secondary:    '#1e4d42',
  accent:       '#b8923a',
  cta:          '#6c9c4a',
  // Light scheme
  light:        '#ffffff',
  lightCard:    '#f5f5f5',
  dark:         '#121212',
  warmLight:    '#f0e2c0', // cream — .page-header surface accent only, NOT body/buttons
  // Dark scheme helpers
  bodyGradient: 'linear-gradient(180deg, #245145 1%, #16342c 100%)',
  glass:        'rgba(255, 255, 255, 0.08)',
  glassBorder:  'rgba(255, 255, 255, 0.1)',
  glassBlur:    'blur(48px)',
  border:       'rgba(255, 255, 255, 0.1)',
  // Typography
  fontHeading:  "'Lora', Georgia, serif",
  fontBody:     "'DM Sans', system-ui, sans-serif",
  // Transitions
  transitionFast: '150ms cubic-bezier(0.22, 1, 0.36, 1)',
  transitionBase: '250ms cubic-bezier(0.22, 1, 0.36, 1)',
  // Radius
  radiusSmall:  '0.25rem',
  radiusMedium: '0.5rem',
  radiusLarge:  '1rem',
  // Leaf icon colors
  leafDark:     '#21453A',
  leafLight:    '#326757',
  faviconGradient: 'linear-gradient(180deg, #122620, #21453A)',
};
```

**Google Fonts `<head>` import:** see §3 Typography (same `<link>`).

---

## 13. Product Mockups

Real product packaging shots live in `assets/products/` as **transparent WebP** (1200×1200, alpha channel, ~70 KB each). Use them as actual `<img>` sources in demos and product grids instead of placeholder boxes — they cut out cleanly on any background (dark theme, glass cards, light sections).

**Usage:** read the file from `assets/products/<filename>.webp` and inline/reference it. Filenames follow `<category>-<product>.webp`, all lowercase.

### Catalog

> ⚠️ **COMPLIANCE — Pflicht.** Die Spalte „Interne Sortier-Kategorie" (und jede Mood-/Stimmungs-Angabe unten) ist **ausschließlich interne Sortier-Hilfe**, um die Sorten auseinanderzuhalten. Diese Begriffe dürfen **NIEMALS** in sichtbarer Ausgabe erscheinen — nicht in Demo-Copy, Produktkarten, Badges, Headings, Alt-Text oder Tooltips. Für Kratom und alle anderen Produkte gilt: **keine Wirkungs-, Effekt- oder Verzehrsprache** (Mehmet-/Compliance-Test). Im Zweifel die Kategorie weglassen und nur Sorte + Vein/Band zeigen.

**Kratom** — Räuchermischung · *Mitragyna speciosa* · 50g · band color = vein color

| Product | File | Vein / Band | Interne Sortier-Kategorie |
|---------|------|-------------|---------------------------|
| Indo Fusion | `white-kratom-indo-fusion.webp` | White (gold band) | Klarheit & Konzentration |
| Suma Rush | `white-kratom-suma-rush.webp` | White (gold band) | Klarheit & Konzentration |
| Java Spark | `white-kratom-java-spark.webp` | White (gold band) | Klarheit & Konzentration |
| Borneo Lift | `green-kratom-borneo-lift.webp` | Green | Balance & Leichtigkeit |
| Indo Fresh | `green-kratom-indo-fresh.webp` | Green | Balance & Leichtigkeit |
| Bali Oasis | `green-kratom-bali-oasis.webp` | Green | Balance & Leichtigkeit |
| Suma Sooth | `red-kratom-suma-sooth.webp` | Red | Ruhe & Geborgenheit |
| Borneo Bliss | `red-kratom-borneo-bliss.webp` | Red | Ruhe & Geborgenheit |
| Bali Sunset | `red-kratom-bali-sunset.webp` | Red | Ruhe & Geborgenheit |
| Indo Legend | `limited-kratom-indo-legend.webp` | Limited (gold band, white circle) | Tiefe & Verbindung |
| Indo Spirit | `limited-kratom-indo-spirit.webp` | Limited (gold band, white circle) | Tiefe & Verbindung |

**Tea & Blütenaufgüsse** — 50g

| Product | File | Type | Interne Sortier-Kategorie |
|---------|------|------|---------------------------|
| Inca Sungod | `energy-tea-inca-sungod.webp` | Yerba Mate · *Ilex paraguariensis* · mit Koffein (green band) | Fokus & Konzentration |
| Tribal Charge | `energy-tea-tribal-charge.webp` | Guayusa · *Ilex guayusa* · mit Koffein · BIO (green band) | Fokus & Konzentration |
| Georgia Green | `green-tea-georgia-green.webp` | Grüntee · *Camellia sinensis* (green band) | mild bis feinherb |
| Georgia Black | `black-tea-georgia-black.webp` | Schwarztee · *Camellia sinensis* (black band) | kräftig bis herb |
| Magic Morning | `special-tea-magic-morning.webp` | Butterfly Pea · *Clitoria ternatea* · Farbwechsel (purple band) | Exotischer Blütenaufguss |
| Dream of Luxor | `special-tea-dream-of-luxor.webp` | Blue Lotus · *Nymphaea caerulea* (purple band) | Ruhe & Balance |

**Special Herbs** — Adaptogen Komplex · Kapseln · 90 Kapseln · brown/gold band

| Product | File | Botanical | Interne Sortier-Kategorie |
|---------|------|-----------|---------------------------|
| Ashwa Balance | `special-herbs-ashwa-balance.webp` | Ashwagandha · *Withania somnifera* | Harmonie & Balance |
| Primal Force | `special-herbs-primal-force.webp` | Tongkat Ali · *Eurycoma longifolia* | Vitalität & Libido |
| Maca Reign | `special-herbs-maca-reign.webp` | Black Maca · *Lepidium meyenii* | Libido & Kraft |

### Demo notes

- Transparent background → drop them straight onto the body gradient or glass cards; no extra masking needed.
- Square 1:1 aspect — for product cards keep the image area square and let the pouch sit centered.
- Compliance: Kratom products are sold as **Räuchermischung** ("Nicht zum Verzehr bestimmt", 18+). Keep that framing in any demo copy — **and never surface the internal sort-category / mood words as customer-facing text** (see the compliance box above): no effect, mood, or consumption language anywhere visible.

---

## Scope & Boundaries

**This skill provides:** Visual values for approximation in demos and mockups, plus real product mockup imagery in `assets/products/`, brand logos in `assets/logos/`, icon sprite sheets in `assets/icons/`, and the canonical machine-readable token set in `references/tokens.json`.

**This skill does NOT cover:**
- Shopify Liquid syntax → liftr-section, liftr-block, liftr-snippet
- CSS architecture (layers, container queries, owner pattern) → liftr-css-system
- Layout decisions (grid vs slider, breakpoints) → `figma-standards.md` + liftr-section
- Spacing hierarchy rules (when to use which level) → `figma-standards.md`
- Component mechanics (slider, panel, accordion) → liftr-slider, liftr-panel, etc.
