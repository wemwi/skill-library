---
name: liftr-commerce
description: >-
  Commerce im LIFTR-Theme: Shop-API api.shop.js (Warenkorb, Rewards, Rabattcodes,
  Varianten, Preise), Store-Finder mit liftr_store-Metaobject, store.liquid und
  Öffnungszeiten-Logik sowie Card-Architektur und Density-System für Produkt- und
  Store-Karten. Laden bei Arbeit an Warenkorb, Store-Finder oder Karten.
metadata:
  version: "1.0.0"
---

# LIFTR Commerce

Warenkorb- und Produktlogik, Store-Finder und die gemeinsame Architektur aller Karten im LIFTR-Theme.
Geprüft gegen liftr-shopify-theme main, Stand 28.10.2026.

## Wann was lesen

| Aufgabe | Datei |
|---|---|
| Warenkorb, Rewards, Rabattcodes, Produkt-Registry, Preis-Helfer, `liftr:shop:*`-Events (`window.liftrShop`) | `references/shop.md` |
| Store-Finder: `liftr_store`-Metaobject, `store.liquid`/`store-data.liquid`/`store-panel.liquid`, Filterfelder, Sortier-Scores, Öffnungszeiten (Google), Distanz-States | `references/store.md` |
| Neue Karte oder Karten-Layout: Golden-Ratio-Grid, Margin-Spacing, Layouts (vertical/horizontal/auto), Selektor-Strategie, Price Swap, rechtliche Grenzen | `references/card-architecture.md` |
| Density-CQs einer Karte: P1–P4-Taxonomie, D0–D3, Token-Wechsel, Floors, Breakpoints, Auto-Flip | `references/card-density.md` |

## Zusammenhänge

- Store-Karten sitzen in `<liftr-list>` → Filter/Sort in **liftr-components** (`list.md`).
- Rating- und Status-Snippets der Karten → **liftr-liquid** (`rating.md`, `status.md`).
- Benachrichtigungen nach Warenkorb-Aktionen → **liftr-components** (`notifications.md`).
