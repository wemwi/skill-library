# skill-library

![Version](https://img.shields.io/github/v/release/wemwi/skill-library)

> Versionierte Heimat meiner Agent Skills für Claude (claude.ai, Claude Code, API).

## Zweck

Dieses Repo ist die **einzige Quelle der Wahrheit** für meine Agent Skills.
Ein Ordner pro Skill (Ordnername == `name` im Frontmatter); installierte
`.skill`-Pakete sind nur Build-Artefakte daraus. So bleiben Skills versioniert,
reproduzierbar und an einem Tag pinbar statt an `main`.

## Bereitstellung

Enthaltenes Inventar:

| Skill | Zweck |
|-------|-------|
| `figma-onlineprinters` | Onlineprinters-Druckvorlagen (Dielines) in Figma übertragen, skalieren und als Print-Template-Component dokumentieren. |
| `global-agent-framework` | Build-Time-Framework für Claude Managed Agents (Config, Deploy, Cron-Trigger, Permissions, Debug). |
| `global-credentials` | Stack-weite Regeln für Zugangsdaten: Token je Anwendung und Zweck, Namen, Rechte, Ablage, Aufräumen. |
| `global-git-conventions` | Repo-Standard: README, SemVer, CHANGELOG, release-please. |
| `global-make-conventions` | Konventionsstandard & Audit-Maßstab für Make-Szenarien: Architektur-Muster + MUST/SHOULD-Regelliste. |
| `global-mcp-framework` | Custom-MCP-Server als Cloudflare Worker (OAuth 2.1, Foundation-Tag). |
| `global-stress-test` | Denk-Modus zum Härten von Konzepten/Architektur: Bruchstellen, Skalierbarkeit, blinde Winkel. |
| `global-workflow` | Universelles Arbeitsprotokoll: Task-Analyse, Modell-Routing, Nachfragen, Planung. |
| `liftr-accordion` | Web Component liftr-accordion (LIFTR v4.9). |
| `liftr-audit` | Audit-Checkliste für LIFTR-Theme-Code (HTML, CSS, JS, Schema). |
| `liftr-block` | Shopify-Blocks im LIFTR-Theme anlegen (Section Blocks und Theme Blocks). |
| `liftr-button-group` | Theme-Block Button Group. |
| `liftr-card-architecture` | Gemeinsame Card-Architektur des LIFTR-Themes. |
| `liftr-card-density` | Dichte-System für alle LIFTR-Cards. |
| `liftr-components` | LIFTR-Web-Components in Liquid-Sections und -Blocks einsetzen. |
| `liftr-copyclip` | Web Component liftr-copyclip (LIFTR v4.9). |
| `liftr-core` | Grundlage des LIFTR-Frameworks: LiftrModule, Core-Exports, CSS-Layer, Attribut- und Event-System. |
| `liftr-css-system` | CSS-Architektur des LIFTR-Themes. |
| `liftr-custom-colors` | Farb-Overrides für Merchants. |
| `liftr-debug` | Systematisches Debugging von CSS und JavaScript. |
| `liftr-fx` | LIFTR-FX-System (Effekte). |
| `liftr-heading-group` | Theme-Block Heading Group. |
| `liftr-i18n` | Übersetzung und Internationalisierung im LIFTR-Theme. |
| `liftr-icons` | Icon-System mit drei Render-Modi (SVG-Sprite, CSS-Mask, CSS-only). |
| `liftr-images` | Bilder im LIFTR-Theme. |
| `liftr-list` | List-Ökosystem: liftr-list, -list-filter, -list-sort, liftr-range. |
| `liftr-marquee` | Web Component liftr-marquee (LIFTR v4.9). |
| `liftr-merchant-ux` | UX-Qualität der Theme-Editor-Schemas für Merchants. |
| `liftr-notification` | Notification-System (api.notification.js + ui.notification.js). |
| `liftr-panel` | Web Component liftr-panel (LIFTR v4.9). |
| `liftr-rating` | Rating-Snippet. |
| `liftr-scroll` | Web Component liftr-scroll (LIFTR v4.9). |
| `liftr-section` | Shopify-Sections im LIFTR-Theme anlegen. |
| `liftr-section-rendering` | API-Sections erstellen und nutzen (Section Rendering). |
| `liftr-shop` | Shop-API (api.shop.js). |
| `liftr-slider` | Web Component liftr-slider (LIFTR v4.9). |
| `liftr-snippet` | Wiederverwendbare Liquid-Snippets im LIFTR-Theme. |
| `liftr-status` | Status-Dot-Snippet. |
| `liftr-sticky` | Web Component liftr-sticky (LIFTR v4.9). |
| `liftr-store` | Store-Snippet und liftr_store-Metaobject. |
| `selectedleafs-brand` | Style-Kit der selectedleafs-Marke (Farben, Typo, Mockups, Icons). |
| `selectedleafs-city-content` | Content-Strategie für lokale City Landing Pages. |
| `selectedleafs-figma` | Regeln für alle selectedleafs-Figma-Dateien (Variablen, Modi, Audit, MCP-Lehren, Icons). |
| `selectedleafs-pos-operations` | Konsolidierter Runtime-Skill der POS-Operations-Agenten: Restock, Inventory, Invoice (Provisionsabrechnung), Telegram-Handwerk, Werte-Verzeichnis. |
| `selectedleafs-pos-restock` | Runtime-Anleitung an den `pos-restock`-Agent: Übergabeprotokoll auswerten & in Drive ablegen. |
| `selectedleafs-telegram` | Posting-Playbook für lokale Telegram City-Channels. |
| `tailwind-4-docs` | Tailwind CSS v4 Doku-Snapshot + Migrations-Workflow. |

Versionen stehen bewusst nicht hier — sie leben im jeweiligen SKILL.md
(`metadata.version`), in der [`CHANGELOG.md`](./CHANGELOG.md) und im Release-Badge
oben. So kann die Tabelle nicht driften.

Namens-Familien: `global-*` (projektübergreifend), `selectedleafs-*`
(markenspezifisch), `liftr-*` (LIFTR-Theme), `figma-*` (Print/Figma).

## Setup

Skill-Ordner als `.skill` packen (via `skill-creator`, Ordner als ZIP-Root).

- **claude.ai:** das `.skill` in den Einstellungen installieren (gleicher Name überschreibt).
- **Claude Code:** dieses Repo in den Kontext geben und den Skill-Ordner direkt lesen.

Bei einer Änderung: `metadata.version` im SKILL.md erhöhen, committen — den Tag
setzt release-please, danach neu packen und in claude.ai neu installieren.

## Gotchas

- _(noch keine — Symptom → Ursache → Fix)_

## Versionierung

Versionen und Änderungen: siehe [`CHANGELOG.md`](./CHANGELOG.md). Versionierung
läuft automatisch über Conventional Commits + release-please — Tags nicht von Hand setzen.
