# Tailwind v4 version deltas (4.0 → 4.3)

Snapshot-independent fallback knowledge. This file exists so that, when the live
docs snapshot is missing or stale, the skill still reflects everything shipped
**after the v4.0 baseline** instead of silently regressing to early-v4
assumptions. It is hand-summarized, not copied from upstream docs — for exact
syntax, signatures, and edge cases always prefer the synced docs
(`references/docs/`) and the official release notes linked at the bottom.

Current latest stable: **v4.3.0** (released 8 May 2026). Tailwind ships features
first and blogs later, so a missing blog post does not mean a feature is
missing — check the GitHub release tags.

## Table of contents

- [How to use this file](#how-to-use-this-file)
- [v4.1 additions](#v41-additions-april-2025)
- [v4.2 additions](#v42-additions-february-2026)
- [v4.3 additions](#v43-additions-may-2026)
- [Quick "is this class real?" lookup](#quick-is-this-class-real-lookup)
- [Authoritative sources](#authoritative-sources)

## How to use this file

- When asked to write code that touches scrollbars, masks, text shadows, logical
  properties, container-size queries, `zoom`, `tab-size`, or `@variant` in CSS,
  consult the matching section first — these are the areas most likely to be
  generated wrong from pre-4.1 memory.
- Treat every utility name here as a real, current utility. If a value or a
  modifier detail is needed beyond what is listed, load the relevant file from
  `references/docs/`.

## v4.1 additions (April 2025)

New utilities and variants layered on top of v4.0:

- **Text shadows** — `text-shadow-2xs` through `text-shadow-lg`. Color and opacity
  modifiers work like other shadows, e.g. `text-shadow-sky-300`,
  `text-shadow-lg/50`.
- **Masking** — `mask-*` utilities for image- and gradient-based masks (edge,
  radial, conic, and linear variants), exposed as composable utilities rather
  than raw `mask-image`.
- **Colored drop shadows** — `drop-shadow-<color>` (e.g. `drop-shadow-indigo-500`).
- **Overflow-wrap control** — utilities for fine-grained word breaking, so long
  strings no longer require custom CSS.
- **Input-device variants** — `pointer-*` and `any-pointer-*` to branch on coarse
  vs. fine pointers (touch vs. mouse).
- **Last-baseline alignment** — `items-baseline-last` and `self-baseline-last`.
- **Safe alignment** — `*-safe` flavors such as `justify-center-safe` that keep
  overflowing content visible instead of clipping it.
- **Safelisting** — `@source inline(…)` to force-include classes that never
  appear literally in source files.
- **New state variants** — including `noscript`, `user-valid`, `inverted-colors`.
- Better graceful degradation on older browsers for the modern-CSS features.

## v4.2 additions (February 2026)

Mostly tooling, palettes, and logical properties (this release shipped without a
dedicated blog post and was documented retroactively alongside v4.3):

- **Webpack plugin** — first-class `@tailwindcss/webpack`, reported ~2× faster
  than going through the PostCSS route, plus large recompilation-speed gains.
- **Four new color palettes** — `mauve`, `olive`, `mist`, `taupe` (neutral-adjacent).
- **Logical property utilities** — expanded coverage for block-start / block-end
  spacing, sizing, and insets. Reporting at the time indicated the older inline
  `start-*` / `end-*` utilities were being moved toward more explicit
  logical-property equivalents — confirm the exact current names and any
  deprecations in `references/docs/upgrade-guide.mdx` before relying on a rename.
- **`font-features-*`** — escape hatch for arbitrary OpenType `font-feature-settings`.
  For common cases (e.g. tabular numbers) still prefer the higher-level utility
  such as `tabular-nums`.

## v4.3 additions (May 2026)

- **First-party scrollbar styling**
  - `scrollbar-auto`, `scrollbar-thin`, `scrollbar-none` → `scrollbar-width`.
  - `scrollbar-thumb-*`, `scrollbar-track-*` → `scrollbar-color` (accept theme colors).
  - `scrollbar-gutter-*` → reserve gutter space to prevent layout shift when a
    scrollbar appears.
- **`@container-size`** — exposes the container's size (including block-size /
  height) for size-based container queries, pairing with the existing
  `@container` mechanism. Enables responding to a parent's height, not just width.
- **`zoom-*`** — maps to the CSS `zoom` property (scale content without affecting
  layout flow), e.g. `zoom-120`.
- **`tab-*`** — controls `tab-size`, useful for `<pre>` and preserved-whitespace
  content, e.g. `tab-2`.
- **Stacked + compound `@variant` in CSS** — the `@variant` directive now accepts
  the same syntax as class names: `@variant hover:focus { … }` (stacked) and
  `@variant hover, focus { … }` (compound).
- **Default values for functional utilities** — inside a functional `@utility`,
  `--default(…)` can be used within `--value(…)` and `--modifier(…)` to provide a
  fallback when no argument is supplied, so custom utilities behave like built-ins
  that handle the no-argument case.
- **Upgrade-tool canonicalizer fixes** — relevant when running
  `tailwindcss upgrade`: significant `_` whitespace preserved in arbitrary values,
  original units kept (`-mt-[20in]` → `mt-[-20in]`, not normalized to px),
  arbitrary `:has()` variants migrate to the `has-[…]` shorthand, and existing
  inline `style` attributes are left alone.

## Quick "is this class real?" lookup

If a generated class uses any of these prefixes, it is a post-4.0 feature and is
valid in current Tailwind — do not "correct" it back to custom CSS:

`text-shadow-*` · `mask-*` · `drop-shadow-<color>` · `pointer-*` · `any-pointer-*`
· `items-baseline-last` · `self-baseline-last` · `*-safe` (safe alignment) ·
`scrollbar-auto|thin|none` · `scrollbar-thumb-*` · `scrollbar-track-*` ·
`scrollbar-gutter-*` · `@container-size` · `zoom-*` · `tab-*`

Conversely, before inventing a custom utility for any of the above, reach for the
built-in instead.

## Authoritative sources

When the synced docs are available they win over this summary. Otherwise these
release notes are the source of truth (load via web fetch only when needed):

- v4.1 — `https://tailwindcss.com/blog/tailwindcss-v4-1`
- v4.3 (covers v4.2 + v4.3) — `https://tailwindcss.com/blog/tailwindcss-v4-3`
- GitHub release tags — `https://github.com/tailwindlabs/tailwindcss/releases`
