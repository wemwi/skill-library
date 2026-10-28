---
name: liftr-foundation
description: >-
  Framework des LIFTR-Shopify-Themes: LiftrModule, core.liftr/-utilities, Imports
  per Import-Map, Attribute, Events, watchSettings, CSS-Layer und Datei-Ablage,
  Custom Properties, Tokens, FOUC/Skeleton, FX. Laden vor jeder JS- oder
  CSS-Arbeit am LIFTR-Theme und beim Debuggen eines konkreten LIFTR-Problems.
metadata:
  version: "1.0.0"
---

# LIFTR Foundation

Grundlage für alle anderen `liftr-*`-Skills: wie Module gebaut, importiert und per CSS gesteuert werden.
Geprüft gegen liftr-shopify-theme main, Stand 28.10.2026.

Theme-Quelle: `wemwi/liftr-shopify-theme`, Branch `main` (Live-Theme). `liftr-shopify-theme-2.0` ist eine
ruhende Migration und nicht maßgeblich.

## Wann was lesen

| Aufgabe | Datei |
|---|---|
| JS-Modul schreiben oder ändern: Import-Konvention, ATTRIBUTES, LiftrModule-API, Konstanten, Events, i18n/settings-JSON, Utilities, Runtime-Helfer | `references/core.md` |
| Responsives Verhalten aus CSS: `watchSettings()`, CSS_SCHEMA-Typen, NAV-Settings und -Größen | `references/watch-settings.md` |
| CSS schreiben oder prüfen: Custom Properties, Inline Fallback, Parent Override, Selektoren, Nesting, Datei- und Layer-Ablage, `@property`, Container Queries, FOUC/Skeleton, Deferred CSS | `references/css-system.md` |
| Design-Tokens (Spacing, Typo, Z-Index, Farben, Icons) | `references/tokens.md` |
| Hover-, Loading-, Enter/Exit-, Ambient-Effekte, FX-Timing (`fx_timing`) | `references/fx.md` |
| Ein konkretes LIFTR-Problem debuggen (Methode + LIFTR-Schnellchecks) | `references/debug.md` |

## Wo die Regeln wohnen

Jede Regel steht genau einmal; andere Dateien verweisen dorthin.

| Regel | Zuhause |
|---|---|
| Import-Schreibweise (Bare Specifier der Import-Map) | `core.md` §1 |
| Attribut vs. Klasse, State-Platzierung | `core.md` §2–3 |
| DEFAULTS vs. CSS_SCHEMA | `core.md` §5 |
| Inline Fallback, Parent Override | `css-system.md` |
| Datei- und Layer-Ablage, Skeleton/FOUC | `css-system.md` |
| `custom-colors`, `visible_if`, Übersetzungs-Keys | liftr-liquid (`custom-colors.md`, `merchant-ux.md`, `i18n.md`) |

## Nachbar-Skills

- **liftr-components** — Markup und API der einzelnen Web Components.
- **liftr-liquid** — Sections, Blocks, Snippets, Schema, Übersetzungen.
- **liftr-commerce** — Shop-API, Store-Finder, Karten.
- **liftr-audit** — nur auf ausdrückliche Anfrage (Code-Review).
