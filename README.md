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
| `global-setup-audit` | Regelmäßige Prüfung des Claude-Setups (Skills, Konnektoren, Memory, Backup-Abgleich) mit Prüfbericht. |
| `global-stress-test` | Denk-Modus zum Härten von Konzepten/Architektur: Bruchstellen, Skalierbarkeit, blinde Winkel. |
| `global-workflow` | Universelles Arbeitsprotokoll: Task-Analyse, Modell-Routing, Nachfragen, Planung. |
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

PRs werden automatisch gemergt, sobald die Inventar-Prüfung grün ist
(`automerge.yml`). Ausnahmen: Entwürfe, Forks, Renovate und Label `kein-automerge`.

## Gotchas

- _(noch keine — Symptom → Ursache → Fix)_

## Versionierung

Versionen und Änderungen: siehe [`CHANGELOG.md`](./CHANGELOG.md). Versionierung
läuft automatisch über Conventional Commits + release-please — Tags nicht von Hand setzen.
