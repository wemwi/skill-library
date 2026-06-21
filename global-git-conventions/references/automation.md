# automation.md — Release-Automation mit release-please

Automation ist Pflicht. Jedes Repo bekommt release-please (`googleapis/release-please-action@v4`, Manifest-Modus).

## Drei Dateien pro Repo

| Datei | Ziel-Pfad im Repo | Quelle |
|-------|-------------------|--------|
| Workflow | `.github/workflows/release-please.yml` | `assets/automation/release-please.yml` |
| Config | `release-please-config.json` (Repo-Wurzel) | `config-node.json` oder `config-simple.json` |
| Manifest | `.release-please-manifest.json` (Repo-Wurzel) | `assets/automation/manifest.json` |

`release-type` nach Repo-Typ: `node` für `*-mcp` und `*-foundation`, `simple` für `*-library` (siehe `types.md`).

## Setup-Schritte (web-only, über GitHub Web)

1. Die drei Dateien ins Repo committen (Config mit passendem `release-type`).
2. Im Manifest die aktuelle Version eintragen, falls das Repo schon released wurde (z.B. `{ ".": "2.0.4" }`), sonst `{ ".": "0.0.0" }`.
3. **Repo-Setting aktivieren:** *Settings → Actions → General →* „Allow GitHub Actions to create and approve pull requests" anhaken. Ohne das kann release-please keinen Release-PR öffnen.
4. Fertig. Ab dem nächsten Merge auf `main` läuft die Action und öffnet bei releasbaren Commits einen Release-PR.

## Stolperfalle 1 — Token

Standardmäßig nutzt release-please das eingebaute `GITHUB_TOKEN`. Bekannte Eigenheit: Tag und Release-PR, die mit diesem Token erstellt werden, triggern **keine weiteren GitHub-Action-Workflows**.

Für dieses Setup ist das **unkritisch**, weil der Deploy über die Cloudflare-Git-Build-Pipeline läuft (reagiert auf Branch-Push, nicht auf GitHub Actions). Ein PAT ist nur nötig, wenn auf den Release-PRs zusätzlich GitHub-Actions-CI laufen soll — das ist hier nicht der Fall.

## Stolperfalle 2 — Cloudflare-Deploy-Interaktion

- release-please arbeitet über PRs, nicht über direkte Pushes. Der **Merge des Release-PR** ist ein normaler Push auf `main` → Cloudflare deployt die neue Version. Gewünschtes Verhalten: Deploy genau dann, wenn eine Version getaggt wird.
- Die von release-please erstellten **Tags** triggern keinen zusätzlichen Cloudflare-Build, da Cloudflare auf Branch-Push baut, nicht auf Tag-Push. Kein doppelter Deploy.
- release-please ändert deinen Deploy-Trigger nicht — es legt nur Tag + Changelog + GitHub-Release obendrauf.

## Wenn ein Release-PR ausbleibt

Hat ein gemergter PR eine releasbare Änderung, aber es erscheint kein Release-PR: den fehlgeschlagenen Workflow-Run suchen und erneut ausführen (re-run). Häufigste Ursache: PR-Titel war nicht conventional (siehe `changelog.md`).

## Verifikation vor Übernahme

Die Configs in `assets/automation/` sind nach dem Stand der release-please-v4-Doku gebaut. Bei größeren Versionssprüngen der Action vor dem Ausrollen die aktuelle Doku gegenprüfen: https://github.com/googleapis/release-please-action
