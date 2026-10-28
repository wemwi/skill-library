# ci.md — Auto-Merge für alle PRs + CI sparsam

Zwei Regeln, die zusammengehören: **jeder PR mergt sich selbst**, sobald seine Prüfung
grün ist — und **die Prüfung kostet nur so viele Actions-Minuten wie nötig**.

## Warum Minuten zählen

Öffentliche Repos mit Standard-Runnern sind frei. Private Repos haben ein Monatskontingent
(GitHub Free 2.000, Pro 3.000 Minuten), danach wird pro Minute abgerechnet
(Linux 2-Core 0,006 $, Windows 2-Core 0,010 $, macOS ein Vielfaches). **Jeder Job wird auf
volle Minuten aufgerundet** — ein 5-Sekunden-Job kostet 1 Minute. Ist das Kontingent ohne
Budget aufgebraucht, blockiert GitHub alle Läufe.

Messwert (Okt. 2026, `first-commerce-import-*`): > 1.000 Läufe in drei Wochen je Repo;
größte Posten waren Windows-Tests bei jedem PR-Push, Doppelläufe nach dem Merge und ein
Automerge-Workflow, der nach jedem anderen Workflow und zusätzlich stündlich startete.

## Auto-Merge für alle PRs

- **Jeder PR wird gemergt (Squash), sobald seine Prüf-Jobs grün sind.** Release-PRs mergt
  `release-please.yml` selbst (`automation.md`).
- **Ausnahmen:** Entwürfe, PRs aus Forks, `renovate/*` (Renovate bleibt manuell,
  `automation.md`), `release-please--*` und PRs mit Label **`kein-automerge`**. Label
  entfernen → Merge läuft nach (`unlabeled`-Event).
- **Mechanik:** ein `automerge`-Job als **letzter Job im Prüf-Workflow**, `needs:` auf die
  Prüf-Jobs. Vorlage: `assets/automation/automerge.yml`. Merge per PAT `RELEASE_PLEASE`,
  damit release-please danach anläuft (`automation.md`, Stolperfalle 1).
- **Nicht** als eigener Workflow über `workflow_run` und **nicht** per Cron-Polling: Beides
  startet bei jedem anderen Workflow bzw. stündlich einen Lauf — jeder kostet mindestens
  eine Minute, fast immer ohne etwas zu tun.
- **Kein natives `--auto`**: braucht Required Checks bzw. in privaten Repos GitHub Pro
  (`automation.md`, Hinweis „Kein Allow auto-merge").
- Repo ohne PR-Prüfung: den `check`-Job der Vorlage weglassen, `needs:` streichen — der PR
  mergt dann direkt.

## CI-Sparregeln

**MUST** in privaten Repos, **SHOULD** in öffentlichen.

1. **`timeout-minutes` an jedem Job.** Default sind 360 Minuten — ein hängender Job frisst
   sonst sechs Stunden.
2. **`concurrency` mit `cancel-in-progress: true`** je PR/Branch. Ein neuer Push bricht den
   veralteten Lauf ab.
3. **Kein Doppellauf nach dem Merge.** Was auf dem PR grün war, läuft nach dem Squash-Merge
   nicht noch einmal auf `main`. Auf `push: main` laufen nur Deploy und release-please.
4. **Entwürfe prüfen nur schnell.** Die volle Suite läuft erst ab `ready_for_review` bzw.
   für Nicht-Entwürfe.
5. **Windows/macOS nur wo nötig** — und dann einmal vor dem Merge (nicht bei jedem Push)
   oder per `paths`-Filter nur bei plattformrelevanten Dateien.
6. **`paths`/`paths-ignore`**, damit reine Doku-Änderungen keine Tests starten.
7. **Ereignis statt Polling.** Kein Cron für etwas, das ein Event auslösen kann.
8. **Renovate bündeln:** montags vor 6 Uhr (`schedule`, `Europe/Berlin`) ein gebündelter
   Minor/Patch-PR je Repo; Major (und 0.x-Minor) erst nach Häkchen im Dependency
   Dashboard. So startet nicht jeder Einzel-Bump eine Suite. Vorlage:
   `assets/automation/renovate.json`, Details `automation.md`.

Kontrolle: Der monatliche Setup-Audit (`global-setup-audit`, Repo-Check) misst die Läufe je
Repo und meldet Verstöße gegen diese Regeln.
