---
name: global-git-conventions
description: >-
  Projektübergreifender Standard für GitHub-Repos — README-Aufbau,
  SemVer-Versionierung, CHANGELOG und Pflicht-Release-Automation via release-please.
  IMMER laden, sobald ein Repo angelegt, ein README geschrieben oder auditiert, eine
  Version gebumpt, ein Tag/Release gesetzt, ein CHANGELOG gepflegt oder die
  Release-Automation eingerichtet wird — auch wenn das Wort Skill oder Convention
  nicht fällt. Trigger u.a. README erstellen/überarbeiten, neues Repo bootstrappen,
  Version bumpen, SemVer-Entscheidung major/minor/patch, Git-Tag setzen, CHANGELOG
  anlegen/aktualisieren, Conventional Commits, release-please einrichten, Release-PR,
  Repo dokumentieren, Repo-Hygiene. Gilt für alle eigenen Repos der Typen
  *-library, *-mcp und *-foundation.
---

# global-git-conventions

Verbindlicher Standard für Doku und Versionierung aller eigenen GitHub-Repos. Dieser Skill definiert den **typ-übergreifenden** Standard. Typ-spezifische Details (z.B. die MCP-Secrets-Mechanik) leben in den jeweiligen Fach-Skills und werden von hier nur referenziert — nie dupliziert.

## Grundprinzipien

1. **Single Source of Truth pro Regel.** Jede Vorgabe lebt an genau einer Stelle. Dieser Skill = Standard. Fach-Skills (`global-mcp-framework` etc.) = Erweiterung. README-Templates sind nur die *Materialisierung* der Regel aus `references/conventions.md` — bei Konflikt gewinnt die Referenz.
2. **README passt auf einen Bildschirm.** Kein Handbuch. Was länger wird, kommt in eine separate Datei oder den passenden Fach-Skill.
3. **Automation ist Pflicht, nicht optional.** Jedes Repo bekommt release-please. Versionierung und CHANGELOG werden nicht von Hand gepflegt, sondern aus Conventional Commits generiert.
4. **Web-only-tauglich.** Alle Schritte funktionieren über GitHub Web + Cloudflare-Git-Build. Keine Annahme über lokales git/Terminal.
5. **READMEs auf Deutsch.**

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

## Referenzen — bei Bedarf lesen

- `references/conventions.md` — README-Pflichtsektionen, Längenlimit, Marker-Auto-Zonen, SSoT-Regel
- `references/versioning.md` — SemVer-Policy (wann major/minor/patch), Tag-Konvention
- `references/changelog.md` — CHANGELOG × release-please, Conventional-Commit-Mapping
- `references/automation.md` — release-please einrichten, Cloudflare-Interaktion, Token/Settings
- `references/about.md` — GitHub About-Block: Description, Website, Topic-Schema je Typ
- `references/types.md` — die drei Repo-Typen im Detail

## Assets — ins Ziel-Repo kopieren

- `assets/readme/{mcp,foundation,library}.md` — README-Templates
- `assets/CHANGELOG.template.md` — CHANGELOG-Startdatei
- `assets/automation/release-please.yml` — Workflow → `.github/workflows/`
- `assets/automation/config-{node,simple}.json` — → `release-please-config.json`
- `assets/automation/manifest.json` — → `.release-please-manifest.json`
