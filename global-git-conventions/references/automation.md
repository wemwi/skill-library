# automation.md — Release-Automation (release-please) + Dependency-Automation (Renovate)

Zwei Automationen, beide Pflicht: **release-please** schneidet Releases (Tag, Changelog,
Release-PR), **Renovate** hält Dependencies aktuell (Bump-PRs). Beide öffnen nur PRs —
der Merge bleibt immer eine bewusste Entscheidung.

## Release-Automation: release-please

Jedes Repo bekommt release-please (`googleapis/release-please-action@v4`, Manifest-Modus).

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

## Dependency-Automation: Renovate

Renovate läuft als **Mend-GitHub-App** (web-only, kein lokales Setup) und öffnet
Bump-PRs für veraltete Dependencies. Kein Auto-Merge: PRs werden bewusst gemergt; das
Dependency Dashboard (ein Issue pro Repo) zeigt den Gesamt-Rückstand zentral.

### Setup (web-only)

1. Renovate-App aus dem Mend Developer Portal installieren und für die Repos
   autorisieren. Sie legt einen Onboarding-PR mit `renovate.json` an.
2. Die `renovate.json` aus `assets/automation/renovate.json` übernehmen (statt der
   generierten Default-Config). `config:recommended` liefert sinnvolle Defaults; **kein**
   Auto-Merge aktivieren.
3. Onboarding-PR mergen. Ab dann öffnet Renovate Bump-PRs nach Zeitplan.

### Foundation-Pin (`*-mcp`)

Der wichtigste Anwendungsfall: die `*-mcp` pinnen `mcp-foundation` als Git-Tag-Dependency
(`"mcp-foundation": "github:<org>/mcp-foundation#<tag>"`). Renovate verfolgt neue
Foundation-Tags und öffnet den Bump-PR automatisch — der manuelle Sechs-Repo-Nachzug
entfällt. Die MCP-spezifische Regel dazu (und ein `customManager`-Fallback, falls die
`github:#tag`-Form nicht out-of-the-box erkannt wird) steht in `global-mcp-framework`.

> [!NOTE]
> Beim Onboarding am Dependency Dashboard prüfen, ob `mcp-foundation` als Dependency
> erkannt wird. Falls nicht, greift der `customManager`-Regex aus `global-mcp-framework`.

### Verifikation vor Übernahme

`assets/automation/renovate.json` ist nach dem Stand der Renovate-Doku gebaut. Vor dem
Ausrollen gegen die aktuelle Doku prüfen: https://docs.renovatebot.com
