# <repo-name>

![Version](https://img.shields.io/github/v/release/<OWNER>/<repo-name>)

> <Einzeiler: welche gemeinsame Basis stellt dieses Repo für die Consumer bereit.>

## Zweck

<2–3 Sätze: Welche geteilte Funktionalität bündelt diese Foundation? Welche Repos
konsumieren sie und warum lohnt die Auslagerung in eine eigene Basis?>

## Bereitstellung

Wird als **Git-Tag-Dependency** konsumiert. Consumer pinnen einen Tag.

Exportierte Oberfläche:

| Export | Zweck |
|--------|-------|
| `<export>` | <was Consumer damit tun> |
| `<export>` | <was Consumer damit tun> |

**Aktueller Tag:** `<vX.Y.Z>` — Consumer-Repos pinnen diesen Tag in ihrer Dependency.

## Setup

<Wie wird die Foundation eingebunden? z.B. Tag-Pin in der Dependency-Deklaration
des Consumers. Welche Mindestversion ist nötig?>

> ⚠️ Breaking Changes MÜSSEN als `feat!:` / `BREAKING CHANGE:` markiert werden —
> Consumer ziehen sonst unbemerkt eine inkompatible Version.

## Gotchas

- _(noch keine — Symptom → Ursache → Fix)_

## Versionierung

Versionen und Änderungen: siehe [`CHANGELOG.md`](./CHANGELOG.md). Versionierung
läuft automatisch über Conventional Commits + release-please — Tags nicht von Hand setzen.
