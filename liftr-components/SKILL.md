---
name: liftr-components
description: >-
  Web Components des LIFTR-Themes: liftr-accordion, -panel, -slider, -scroll,
  -marquee, -sticky, -copyclip, Notifications und das List-Ökosystem (list,
  list-filter, list-sort, range) — Markup, CSS Settings, States, Events, Public
  API. Laden, wenn eine dieser Komponenten eingebaut, konfiguriert oder gedebuggt
  wird.
metadata:
  version: "1.0.0"
---

# LIFTR Components

Wie die LIFTR-Web-Components in Liquid eingesetzt, per CSS konfiguriert und per JS angesprochen werden.
Geprüft gegen liftr-shopify-theme main, Stand 28.10.2026.

Voraussetzung für JS- oder CSS-Arbeit: **liftr-foundation** (`core.md`, `css-system.md`, `watch-settings.md`).

## Wann was lesen

| Aufgabe | Datei |
|---|---|
| Komponente in Section/Block einbauen: Struktur, Consumer-Klasse, CSS Settings je Modul, NAV-Markup, JS-gesetzte Properties, State-Tokens | `references/usage.md` |
| Akkordeon, FAQ, Filtergruppen, Bottom-Sheet-Modus | `references/accordion.md` |
| Dialog, Modal, Sidebar, Sheet, Dropdown, Menü (`<dialog>`) | `references/panel.md` |
| Karussell/Slider mit Transform, Loop, Dots, Autoplay | `references/slider.md` |
| Scroll-Container mit Navigation, Masken, Shadow-Bleed | `references/scroll.md` |
| Lauftext, USP-Leiste, Logo-Ticker | `references/marquee.md` |
| Sticky-CTA am unteren Rand | `references/sticky.md` |
| Copy-to-Clipboard (z. B. Rabattcode) | `references/copyclip.md` |
| Toasts/Benachrichtigungen (`liftrNotification`) | `references/notifications.md` |
| Filter- und sortierbare Listen: Überblick, Event-Map, Gesamtbeispiel | `references/list.md` |
| … nur der Koordinator `<liftr-list>` (Items, Counts, Clear, statische Blöcke) | `references/list-coordinator.md` |
| … nur `<liftr-list-filter>` (Checkbox, Radio, Threshold, Match Counts) | `references/list-filter.md` |
| … nur `<liftr-list-sort>` (Select, Buttons, Distanz-Sortierung) | `references/list-sort.md` |
| … nur `<liftr-range>` (Slider, Persist, PLZ-Abhängigkeit) | `references/list-range.md` |

## Dateien im Theme

JS: `assets/ui.{modul}.js` (Range: `ui.list-filter-range.js`, Notifications: `ui.notifications.js` + `api.notification.js`).
Modul-CSS (`@layer modules`): `assets/ui.{accordion,list,marquee,panel,slider}.css`, sonst `assets/core.liftr.css`.
FOUC-Regeln: `snippets/core.critical.liquid`.

Keine eigenen Referenzen gibt es für `liftr-tabs`, `liftr-header`, `liftr-location`, `liftr-delivery`,
`liftr-service`, `liftr-cart`, `liftr-product`, `liftr-store-summary` — vor Arbeit daran die Datei im Theme lesen.
