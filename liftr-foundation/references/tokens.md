# Design Tokens

Source: `assets/core.base.css` (`@layer base`) and `snippets/core.critical.liquid` (fonts, color
schemes, fluid type — generated from Theme Settings). Use tokens instead of raw values; in density
CQs pick a smaller token, never `calc()` on a token (→ `card-density.md`, liftr-commerce).

| Family | Tokens |
|---|---|
| Spacing (`--space--*`) | `tiny` 0.125rem · `xxsmall` 0.25rem · `xsmall` 0.5rem · `small` · `medium` · `large` · `xlarge` · `xxlarge` · `huge` · `xhuge` · `xxhuge` (from `small` up fluid via `clamp()`, viewport 320–1440px) |
| Component gaps (`--gap--*`) | `small` · `medium` · `large` (tighter than `--space--*`; utilities `.gap-fluid-*`) |
| Layout spacing | `--padding-global`, `--padding-section--small` / `--medium` / `--large` (utility classes `padding-section-*`) |
| Breakpoints (for CQs) | `--bp--desktop` 64rem · `--bp--tablet` 48rem · `--bp--mobile` 30rem |
| Font size (`--font-size--*`) | `tiny` · `small` · `regular` · `medium` · `large` · `h1`–`h6` (fluid, in `core.critical.liquid`) |
| Font family / line height | `--font-family--heading` / `--regular`; `--line-height--heading` / `--text` / `--compact` |
| Font weight (`--font-weight--*`) | `regular` 400 · `bold` 500 · `xbold` 700 |
| Border radius (`--border-radius--*`) | `small` 0.25rem · `medium` 0.5rem · `large` 1rem · `full` |
| Shadows | `--box-shadow--small/medium/large`, `--text-shadow--small/medium/large` (`color-mix()` based) |
| Backdrop | `--backdrop-blur--tiny/small/medium/large` |
| Transitions (`--transition--*`) | `instant` 50ms · `fast` 150ms · `base` 250ms · `slow` 360ms · `slower` 400ms · `deliberate` 600ms |
| Easing (`--ease--*`) | `out` · `in` · `in-out` · `spring` · `smooth` · `snappy` |
| Ambient | `--ambient-duration--fast/base/slow/slower` (6–12s), `--ambient-ease--smooth/breathe` |
| Z-index (`--z--*`) | `base` 1 · `above` 2 · `elevated` 10 · `dropdown` 100 · `sticky` 200 · `overlay` 300 · `panel-overlay` 400 · `panel` 500 · `modal-backdrop` 900 · `modal` 1000 · `notification` 1100 |
| Icon size (`--icon-size--*`) | `xsmall` 0.75rem · `small` 1rem · `regular` 1.5rem · `medium` 2rem · `large` 2.5rem · `xlarge` 3rem |
| Opacity (`--opacity--*`) | `subtle` · `muted` · `faint` |
| Color scheme (`--color-scheme--*`) | `background` · `gradient` · `card` · `text` · `accent` · `link` · `border` · `focus` · `grey` · `button-primary` · `button-primary-text` · `button-secondary` · `button-secondary-text` |
| Global colors (`--color-global--*`) | `success` · `warning` · `error` · `info` · `sale` · `new` · `bestseller` · `promotion` · `rating` · `skeleton` |
| Mask | `--mask--edge` (edge fade width of the `liftr-mask` utility) |

Naming: tokens use the double-dash namespace `--{family}--{name}`. FX timing variables are the
exception (`--fx-*`, → `fx.md`); module CSS Settings use a single dash (`--slider-cols`, → `css-system.md`).
