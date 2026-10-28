---
name: global-git-conventions
description: >-
  Standard für eigene GitHub-Repos (*-library, *-mcp, *-foundation): README, SemVer,
  CHANGELOG, release-please, Conventional Commits, Auto-Merge, CI-Sparregeln,
  Branch-Hygiene. IMMER laden bei Repo anlegen, README schreiben, Version bumpen,
  Release/Tag, Commit- oder PR-Titel formulieren, Actions-Workflow schreiben oder prüfen.
  Trigger: Release-PR, Actions-Minuten, Branches aufräumen.
metadata:
  version: "2.0.2"
---

# global-git-conventions

Verbindlicher Standard für Doku und Versionierung aller eigenen GitHub-Repos. Dieser Skill definiert den **typ-übergreifenden** Standard. Typ-spezifische Details (z.B. die MCP-Secrets-Mechanik) leben in den jeweiligen Fach-Skills und werden von hier nur referenziert — nie dupliziert.

## Grundprinzipien

1. **Single Source of Truth pro Regel.** Jede Vorgabe lebt an genau einer Stelle. Dieser Skill = Standard. Fach-Skills (`global-mcp-framework` etc.) = Erweiterung. README-Templates sind nur die *Materialisierung* der Regel aus `references/conventions.md` — bei Konflikt gewinnt die Referenz.
2. **README passt auf einen Bildschirm.** Kein Handbuch. Was länger wird, kommt in eine separate Datei oder den passenden Fach-Skill.
3. **Automation ist Pflicht, nicht optional.** Jedes Repo bekommt release-please (Releases) und Renovate (Dependency-Bumps). Versionierung und CHANGELOG werden nicht von Hand gepflegt, sondern aus Conventional Commits generiert; Dependency-Updates kommen als Renovate-PRs, nicht von Hand. **Alle PRs werden automatisch gemergt**, sobald ihre Prüfung grün ist; Release-PRs mergt release-please selbst → Release + Deploy ohne Handgriff (Mechanik: `references/ci.md`, PAT-Pflicht: `references/automation.md`). Renovate-Bump-PRs bleiben bewusst manuell.
4. **Einrichtung web-tauglich.** Repo-Settings und Secrets lassen sich komplett über GitHub Web setzen. Änderungen am Repo macht Claude über einen git-Klon (Branch → PR), nie per Datei-Upload durch den Chat (`global-workflow`).
5. **READMEs auf Deutsch.**
6. **Jede Repo-Änderung läuft als PR mit Conventional-Commit-Titel.** Der Titel wird beim Squash-Merge zur Commit-Message auf `main`. Nur wenn Claude keinen Schreibzugriff hat, kommt stattdessen ein fertiger Commit-Block zum Einfügen. Format: Abschnitt unten + `references/changelog.md`.
7. **CI sparsam.** In privaten Repos kostet jede Minute; jeder Workflow folgt den Sparregeln in `references/ci.md` (Timeout, Abbruch veralteter Läufe, kein Doppellauf, Windows/macOS nur wo nötig). Gemergte Branches werden automatisch gelöscht (`references/settings.md`).

## Repo-Typ am Suffix erkennen

Der Repo-Name bestimmt Template und Konfiguration:

| Suffix | Beispiel | README-Template | release-type |
|--------|----------|-----------------|--------------|
| `*-mcp` | `google-sheets-mcp` | `assets/readme/mcp.md` | `node` |
| `*-foundation` | `mcp-foundation` | `assets/readme/foundation.md` | `node` |
| `*-library` | `skill-library` | `assets/readme/library.md` | `simple` |

Details je Typ: siehe `references/types.md`.

## Workflow — neues oder bestehendes Repo standardisieren

1. **Typ bestimmen** am Suffix (Tabelle oben).
2. **README** aus dem passenden `assets/readme/*.md` ableiten. Platzhalter `<...>` ersetzen. Pflichtsektionen nicht entfernen — Regel in `references/conventions.md`.
3. **CHANGELOG** anlegen: `assets/CHANGELOG.template.md` kopieren (minimaler Header, den release-please füllt). NICHT von Hand mit `[Unreleased]` pflegen — Begründung in `references/changelog.md`.
4. **Automation** einrichten: Workflow + Config + Manifest aus `assets/automation/` kopieren, `release-type` nach Typ wählen. Setup-Schritte und die zwei Stolperfallen (Repo-Setting, Token) in `references/automation.md`.
5. **Commit-Konvention** einhalten: Conventional Commits, auch im PR-Titel bei Squash-Merge. Mapping in `references/changelog.md`.
6. **About-Block** setzen: Description (= README-Einzeiler), Website (Live-URL bei `*-mcp`) und Topics je Typ. Kein Datei-Artefakt — per `gh repo edit` mitsetzen. Schema in `references/about.md`.

## Commit- und PR-Titel

Jede Änderung in einem dieser Repos (Datei geändert, Skill/Asset geliefert, Config
angepasst) bekommt einen Conventional-Commit-Titel — als PR-Titel, wenn Claude den PR
selbst öffnet, sonst als copy-paste-fähiger Commit-Block am Ende der Antwort. Title und,
wenn die Änderung es wert ist, ein kurzer Body.

- **Auslöser:** echte Repo-Änderung (geänderte/neue Datei, geliefertes Artefakt). Reine
  Fragen, Debugging ohne Dateiänderung oder Erklärungen brauchen keinen Titel.
- **Format:** Conventional Commit, release-please-tauglich. Bei Squash-Merge zählt der
  PR-Titel — derselbe Text passt für beides. Mapping, Body-Format und Beispiele:
  `references/changelog.md`. SemVer-Stelle: `references/versioning.md`.
- **Scope = die berührte Komponente** (z.B. der Skill-Name in einer `*-library`). In
  Monorepo-Setups ordnet release-please über den **Dateipfad** zu, nicht über den Scope
  — einen Commit also nie quer über zwei Komponenten ziehen.
- **Mehrere unabhängige Änderungen:** getrennte Commit-Vorschläge (sauberer Changelog),
  nicht alles in einen quetschen. Gehört es logisch zusammen, ein Commit mit Footer.
- **Skill-Version mitführen:** Ändert sich ein Skill in einer `*-library`, gehört der
  passende `metadata.version`-Bump im SKILL.md zur selben Änderung — Regel in
  `references/versioning.md`.

## Referenzen — bei Bedarf lesen

- `references/conventions.md` — README-Pflichtsektionen, Längenlimit, SSoT-Regel
- `references/versioning.md` — SemVer-Policy (wann major/minor/patch), Tag-Konvention
- `references/changelog.md` — CHANGELOG × release-please, Conventional-Commit-Mapping
- `references/automation.md` — release-please + Renovate einrichten, Cloudflare-Interaktion, Token/Settings
- `references/ci.md` — Auto-Merge aller PRs, CI-Sparregeln (Actions-Minuten)
- `references/settings.md` — Repo-Settings: Merge-Verhalten, Branch-Hygiene, Actions-Härtung, Security
- `references/protection.md` — Repo-Härtung: Branch-Protection, Secret Scanning, Dependabot, 2FA (GitHub Free, public vs. private)
- `references/about.md` — GitHub About-Block: Description, Website, Topic-Schema je Typ
- `references/types.md` — die drei Repo-Typen im Detail

## Assets — ins Ziel-Repo kopieren

- `assets/readme/{mcp,foundation,library}.md` — README-Templates
- `assets/CHANGELOG.template.md` — CHANGELOG-Startdatei
- `assets/automation/release-please.yml` — Workflow → `.github/workflows/`
- `assets/automation/automerge.yml` — Prüf-Workflow mit Auto-Merge-Job → `.github/workflows/`
- `assets/automation/config-{node,simple}.json` — → `release-please-config.json`
- `assets/automation/manifest.json` — → `.release-please-manifest.json`
- `assets/automation/renovate.json` — Renovate-Config (Mend-App), → Repo-Wurzel
