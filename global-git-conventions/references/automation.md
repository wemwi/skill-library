# automation.md — Release-Automation (release-please) + Dependency-Automation (Renovate)

Zwei Automationen, beide Pflicht: **release-please** schneidet Releases (Tag, Changelog,
Release-PR), **Renovate** hält Dependencies aktuell (Bump-PRs).

- **Release-PRs werden automatisch gemergt** (alle Repo-Typen). Jeder releasbare Merge auf
  `main` → release-please öffnet den Release-PR → der Workflow mergt ihn sofort → Tag,
  GitHub-Release und (bei `*-mcp`/`*-foundation`) Cloudflare-Deploy laufen ohne Handgriff.
  Der Merge ist kein Gate mehr. Mechanik und die dafür nötige PAT-Pflicht: Abschnitt
  „Auto-Merge" unten.
- **Renovate-Bump-PRs bleiben manuell.** Bewusst nicht auto-gemergt — ein Major-Bump auf
  einem Produktions-Worker soll eine Entscheidung bleiben. Das Dependency Dashboard zeigt
  den Rückstand zentral.

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
4. **Repo-Setting aktivieren:** *Settings → General →* „Allow auto-merge" anhaken. Ohne das schlägt der `gh pr merge --auto`-Schritt fehl.
5. **PAT-Secret hinterlegen:** Einen Personal Access Token (Scopes: `contents:write` + `pull-requests:write`, fine-grained reicht) als Repo-Secret `RELEASE_PLEASE_TOKEN` anlegen. Pflicht, nicht optional — Begründung unter „Stolperfalle 1". Ein org-weites Secret deckt alle Repos auf einmal ab.
6. **Branch-Protection:** `main` darf keine Pflicht-Reviews verlangen, sonst kann der Workflow den Release-PR nicht selbst mergen (Solo-Repo: kein Problem).
7. Fertig. Ab dem nächsten releasbaren Merge auf `main` öffnet release-please den Release-PR und mergt ihn automatisch.

## Auto-Merge — wie der Release-PR ohne Handgriff durchläuft

Der Workflow (`assets/automation/release-please.yml`) hat nach der release-please-Action
einen zweiten Step, der den gerade geöffneten Release-PR sofort mergt:

```yaml
- name: Release-PR automatisch mergen
  if: ${{ steps.release.outputs.pr }}
  env:
    GH_TOKEN: ${{ secrets.RELEASE_PLEASE_TOKEN }}
  run: gh pr merge --squash --auto "${{ fromJson(steps.release.outputs.pr).number }}"
```

Ablauf: feat/fix landet auf `main` → **Run 1** öffnet den Release-PR und mergt ihn →
der Merge ist ein PAT-Push auf `main` → **Run 2** sieht den gemergten Release-PR und setzt
Tag + GitHub-Release → Cloudflare deployt (reagiert ohnehin auf den Branch-Push).

**Kein Loop:** Der Merge-Commit ist ein `chore(main): release …` (kein releasbarer Unit),
also öffnet Run 2 keinen neuen Release-PR — der `pr`-Output ist leer, der Merge-Step wird
übersprungen.

## Stolperfalle 1 — Token (PAT ist Pflicht)

Standardmäßig nutzt release-please das eingebaute `GITHUB_TOKEN`. Bekannte Eigenheit: Events, die mit diesem Token erzeugt werden, triggern **keine weiteren GitHub-Action-Workflows** (Schutz gegen Endlosschleifen).

Beim Auto-Merge ist das **fatal**: release-please braucht nach dem Merge des Release-PR einen **zweiten Run**, um Tag + GitHub-Release zu erstellen. Mergt der Workflow den PR mit `GITHUB_TOKEN`, bleibt dieser zweite Run aus → Version wird gebumpt, aber **kein Tag, kein Release** (Label hängt auf `autorelease: pending`). Das Cloudflare-Deploy liefe trotzdem (Branch-Push), aber ohne Tag/Changelog-Abschluss — also ein halbfertiger Release.

Deshalb: **PAT als `RELEASE_PLEASE_TOKEN` ist Pflicht, sobald Auto-Merge aktiv ist** (war früher nur für CI auf PRs nötig). Der PAT-Push triggert den zweiten Run, der Release sauber abschließt.

## Stolperfalle 2 — Cloudflare-Deploy-Interaktion

- release-please arbeitet über PRs, nicht über direkte Pushes. Der **Auto-Merge des Release-PR** ist ein normaler Push auf `main` → Cloudflare deployt die neue Version. Mit Auto-Merge heißt das: jeder releasbare Merge auf `main` führt automatisch zu einem Deploy — der Merge ist kein bewusstes Gate mehr. Wenn mehrere Änderungen als ein Release rausgehen sollen, müssen sie **vor** dem Merge auf `main` gebündelt werden (z.B. über einen Feature-Branch/Sammel-PR), nicht erst auf `main`.
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
   Auto-Merge aktivieren. `"mode": "full"` ist Pflicht (siehe Silent-Falle unten).
3. Onboarding-PR mergen. Ab dann öffnet Renovate Bump-PRs nach Zeitplan.

> [!WARNING]
> **Silent-Falle.** Wird Renovate mit „All repositories" installiert, defaulten alle
> Repos in den **Silent-Modus** (`dryRun=lookup`): Renovate scannt, öffnet aber keine
> PRs/Issues — Ergebnisse nur im Mend Developer Portal. Symptom: Repos zeigen „onboarded",
> aber es kommen keine PRs. Fix: `"mode": "full"` in der `renovate.json` (überschreibt den
> Default pro Repo, versioniert) oder im Portal die Engine-Setting von „Silent" auf
> „Interactive" stellen. Bei „Selected repositories"-Installation tritt das nicht auf —
> die gewählten Repos starten direkt interaktiv.

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
