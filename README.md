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

| Skill | Version | Zweck |
|-------|---------|-------|
| `global-agent-framework` | `1.4.1` | Build-Time-Framework für Claude Managed Agents (Config, Deploy, Cron-Trigger, Permissions, Debug). |
| `global-git-conventions` | `1.6.0` | Repo-Standard: README, SemVer, CHANGELOG, release-please. |
| `global-mcp-framework` | `1.7.0` | Custom-MCP-Server als Cloudflare Worker (OAuth 2.1, Foundation-Tag). |
| `global-workflow` | `1.0.0` | Universelles Arbeitsprotokoll: Task-Analyse, Modell-Routing, Nachfragen, Planung. |
| `selectedleafs-brand` | `–` | Style-Kit der selectedleafs-Marke (Farben, Typo, Mockups, Icons). |
| `selectedleafs-city-content` | `–` | Content-Strategie für lokale City Landing Pages. |
| `selectedleafs-pos-restock` | `–` | Runtime-Anleitung an den `pos-restock`-Agent: Übergabeprotokoll auswerten & in Drive ablegen. |
| `selectedleafs-telegram` | `–` | Posting-Playbook für lokale Telegram City-Channels. |
| `tailwind-4-docs` | `–` | Tailwind CSS v4 Doku-Snapshot + Migrations-Workflow. |

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
