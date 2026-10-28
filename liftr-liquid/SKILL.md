---
name: liftr-liquid
description: >-
  Liquid im LIFTR-Theme: Sections, Theme- und Section-Blocks, Snippets,
  Schema-UX für Merchants, Übersetzungen (de.default/en-GB), custom-colors,
  API-Sections (Section Rendering), Bilder, Icons sowie die Bausteine
  heading-group, button-group, rating, status. Laden beim Anlegen oder Ändern von
  .liquid-Dateien, Schemas oder Locale-Keys.
metadata:
  version: "1.0.0"
---

# LIFTR Liquid

Aufbau von Sections, Blocks und Snippets im LIFTR-Theme, ihr Schema und ihre Übersetzungen.
Geprüft gegen liftr-shopify-theme main, Stand 28.10.2026.

CSS-Regeln (Ablage, Inline Fallback, Parent Override, Container Queries) stehen in **liftr-foundation**
(`css-system.md`); Komponenten-Markup in **liftr-components** (`usage.md`).

## Wann was lesen

| Aufgabe | Datei |
|---|---|
| Section anlegen oder ändern: 3-Wrapper-Struktur, Liquid Head, Asset-Laden, Standard-Settings, Presets vs. Default, Platzierung | `references/section.md` |
| Block anlegen: Section- vs. Theme-Block, Schema (`tag: null`), Nested Blocks, Panel-Pattern | `references/block.md` |
| Snippet anlegen: Parameter, Guard Contract, Self-Contained-Prinzip | `references/snippet.md` |
| Schema-UX: Reihenfolge, Header-Gruppen, Info-Texte, Defaults, Presets, `visible_if`, Opt-in/-out, Empty States | `references/merchant-ux.md` |
| Übersetzungen: Locale-Dateien, Key-Formel, Namespaces, Pluralisierung, Parität | `references/i18n.md` |
| Merchant-Farben (Auto/Custom, `custom-colors`-Snippet, Scopes, Forwarding) | `references/custom-colors.md` |
| Server-gerendertes HTML per `?section_id=` (API-Sections) | `references/section-rendering.md` |
| Bilder: media-wrapper, widths/sizes, Loading, Placeholder | `references/images.md` |
| Icons: SVG-Sprite, CSS-Mask, `icon`-Snippet, Masken registrieren | `references/icons.md` |
| Theme-Block heading-group | `references/heading-group.md` |
| Theme-Block button-group | `references/button-group.md` |
| Snippet rating (Sterne) | `references/rating.md` |
| Snippet status (Punkt-Indikator) | `references/status.md` |

## Locale-Dateien

`locales/de.default.json` und `de.default.schema.json` (Deutsch ist Standard), `locales/en-GB.json` und
`en-GB.schema.json`. Eine `en.default.json` gibt es nicht — Details in `references/i18n.md`.
