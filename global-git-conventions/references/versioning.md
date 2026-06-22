# versioning.md — SemVer & Tags

Eine einheitliche Versionierungsregel für alle Repos — egal ob Foundation-Tag, Worker oder Skill-Library.

## SemVer

Format `MAJOR.MINOR.PATCH`. Entscheidung, welche Stelle springt:

| Stelle | Wann | Conventional-Commit-Auslöser |
|--------|------|------------------------------|
| **MAJOR** | Breaking Change — Consumer müssen etwas anpassen | `feat!:` oder Footer `BREAKING CHANGE:` |
| **MINOR** | Neues Feature, rückwärtskompatibel | `feat:` |
| **PATCH** | Bugfix, interne Änderung, rückwärtskompatibel | `fix:`, `perf:` |

`chore:`, `docs:`, `refactor:`, `test:` lösen standardmäßig **keinen** Versionssprung aus (erscheinen je nach Config nicht oder nur als Notiz im Changelog).

## Tags

- Format: `vMAJOR.MINOR.PATCH`, z.B. `v2.0.4`.
- Tags werden **ausschließlich von release-please** gesetzt — nie von Hand. Manuelles Taggen umgeht den Changelog und das Manifest und führt zu Drift.
- Pre-1.0: Solange ein Repo unreif ist, bleibt es bei `0.x.y`. In `0.x` darf `minor` auch Breaking sein — Konvention, kein Sonderfall in der Config.

## Besonderheit `*-foundation`

Die Foundation ist eine **Git-Tag-Dependency**: Die `*-mcp`-Repos pinnen einen Foundation-Tag. Konsequenzen:
- Foundation-Tags müssen besonders diszipliniert sein — ein Breaking Change MUSS `feat!:` / `BREAKING CHANGE:` sein, sonst ziehen Consumer unbemerkt eine inkompatible Version.
- Bumpt die Foundation, ziehen die Consumer **nicht automatisch durch** — es gibt kein Auto-Merge. Renovate öffnet pro `*-mcp` automatisch einen Bump-PR auf den neuen Foundation-Tag; der Merge bleibt eine bewusste Entscheidung. Den Rückstand zur neuesten Foundation zeigt Renovates Dependency Dashboard zentral (siehe `automation.md`). Der gepinnte Tag lebt allein in der `package.json` des Consumers — keine zusätzliche README-Zone.

## Besonderheit `*-library` — zwei entkoppelte Versionsebenen

Eine Skill-Library hat **zwei** Versionsbegriffe, die bewusst getrennt bleiben:

1. **Repo-Version** — das ganze Library-Repo, von release-please versioniert
   (`release-type: simple`, ein Tag, ein CHANGELOG). Das ist die „harte" Versionierung
   über Git; sie deckt das Repo als Sammlung ab.
2. **Skill-Version** — `metadata.version` im Frontmatter des einzelnen `SKILL.md`. Sie
   wird **von Hand** gepflegt, release-please rührt sie **nicht** an (kein
   `extra-files`-Eintrag, kein Monorepo-Setup pro Skill).

Warum getrennt und warum überhaupt eine Skill-Version: `metadata.version` ist die vom
Skill-Format empfohlene Konvention und — weil ein `.skill`-Paket die installierte
Version stumpf überschreibt — der **einzige** Indikator, an dem nach der Installation
ablesbar ist, welche Iteration eines Skills läuft. Bei den `*-mcp`/`*-foundation`-Repos
übernimmt das der Git-Tag; bei Skills gibt es nur das Frontmatter.

**Kein** Monorepo-release-please pro Skill: Der Mehrwert (eigene Tags/Changelogs je
Skill) zahlt sich nur aus, wenn diese Tags konsumiert werden — Skills werden aber als
`.skill`-Paket verteilt, nicht per Tag gepinnt. Der Pflegeaufwand (jeder Skill in
`config` + `manifest`, generischer Updater fürs Frontmatter) lohnt nicht.

**Skill-Versionssemantik** (pragmatisch, kein striktes SemVer für ein Doku-Artefakt):

| Stelle | Wann beim Skill |
|--------|-----------------|
| **MINOR** | neue Regel/Section/Asset dazu, Anwendung bleibt kompatibel (Normalfall) |
| **PATCH** | Korrektur, Klarstellung, Tippfehler, Thinning ohne Regeländerung |
| **MAJOR** | Umbau, der ändert, *wie* der Skill angewandt wird (selten) |

Der Bump des Skill-Frontmatters gehört in **denselben** Commit wie die Skill-Änderung;
der Commit-Title trägt den Skill als Scope (siehe `changelog.md`).

## Erstinitialisierung bei bereits existierender Version

Hat ein Repo schon eine Version (z.B. Foundation bei `v2.0.4`), wird diese **einmalig** ins Manifest eingetragen, damit release-please ab dort weiterzählt:

```json
{ ".": "2.0.4" }
```

Neue Repos starten mit `{ ".": "0.0.0" }` — der erste `feat:` macht daraus `0.1.0`.
