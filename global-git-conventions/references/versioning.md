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

## Erstinitialisierung bei bereits existierender Version

Hat ein Repo schon eine Version (z.B. Foundation bei `v2.0.4`), wird diese **einmalig** ins Manifest eingetragen, damit release-please ab dort weiterzählt:

```json
{ ".": "2.0.4" }
```

Neue Repos starten mit `{ ".": "0.0.0" }` — der erste `feat:` macht daraus `0.1.0`.
