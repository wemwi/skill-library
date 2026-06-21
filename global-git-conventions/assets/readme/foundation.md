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

Consumer pinnen den **jeweils neuesten Release-Tag** — die aktuelle Version steht
im Badge oben und unter „Releases". KEINE feste Versionsnummer in diesen Fließtext
schreiben, sie driftet beim nächsten Release.

## Setup

Im Consumer-Repo als Git-Dependency mit festem Tag einbinden (neuesten Tag einsetzen,
nicht aus dem README abschreiben — siehe Badge):

```jsonc
// package.json des Consumers
"dependencies": {
  "<repo-name>": "github:<OWNER>/<repo-name>#<neuester-tag>"
}
```

> [!WARNING]
> Breaking Changes MÜSSEN als `feat!:` / `BREAKING CHANGE:` markiert werden —
> Consumer ziehen sonst unbemerkt eine inkompatible Version.

## Gotchas

- _(noch keine — Symptom → Ursache → Fix)_

## Versionierung

Versionen und Änderungen: siehe [`CHANGELOG.md`](./CHANGELOG.md). Versionierung
läuft automatisch über Conventional Commits + release-please — Tags nicht von Hand setzen.
