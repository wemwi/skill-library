# settings.md — Repo-Settings & Sicherheits-Standard

Der GitHub-seitige Grundzustand jedes Repos — unabhängig vom Typ. Während `automation.md` die Release-Mechanik beschreibt, definiert diese Datei, **wie das Repo selbst eingestellt ist**: Merge-Verhalten, Branch-Schutz, Actions-Härtung, Security-Features.

Alles web-only über die GitHub-Oberfläche setzbar. Ziel ist ein Solo-Betrieb, der den Auto-Merge-Workflow aus `automation.md` **nicht** blockiert — deshalb bewusst **keine** Required Reviews und **keine** Required Status Checks.

## Merge-Verhalten (*Settings → General → Pull Requests*)

| Setting | Wert | Warum |
|---------|------|-------|
| Allow squash merging | **an** | Eine Änderung = ein Commit auf `main`, lineare Historie. |
| Allow merge commits | **aus** | Verhindert Merge-Bubbles in der Historie. |
| Allow rebase merging | **aus** | Squash ist der einzige Pfad — eindeutig. |
| Default commit message (Squash) | **„Pull request title and description"** | **release-please-kritisch.** |
| Automatically delete head branches | **an** | Branch-Liste bleibt sauber, kollidiert nicht mit dem Workflow. |

> [!IMPORTANT]
> **„Default to pull request title" ist kein Kosmetik-Punkt.** release-please liest beim Squash-Merge den **PR-Titel** als Conventional Commit. Steht der Default auf „commit messages", landet schnell ein nicht-conventional Titel auf `main` → **kein Release-PR**. Symptom und Re-Run-Fix: `automation.md`, „Wenn ein Release-PR ausbleibt".

## Branch-Schutz für `main` (*Settings → Rules → Rulesets*)

Ruleset auf `main`, das schützt, **ohne** den Auto-Merge zu blockieren:

| Regel | Setzen? | Warum / Warum nicht |
|-------|---------|---------------------|
| Restrict deletions | **ja** | `main` darf nicht versehentlich gelöscht werden. |
| Block force pushes | **ja** | Schützt die Historie; release-please pusht regulär. |
| Require pull request before merging | optional | Solo: optional. Wenn aktiv → **0** Required Approvals, sonst blockiert sich der Workflow selbst. |
| Require status checks | **nein** | Würde den direkten `gh pr merge` blockieren (Cloudflare baut separat, nicht als PR-Check). |
| Require approvals | **nein** | Der Workflow mergt den Release-PR selbst — ein Pflicht-Review legt ihn lahm. |

> [!NOTE]
> Das Verbot von Required Reviews/Checks ist dieselbe Bedingung wie in `automation.md`, Setup-Schritt „Branch-Protection" — hier nur aus Settings-Sicht aufgeführt. Quelle der Mechanik bleibt `automation.md`.

**Tag-Schutz:** zusätzlich ein Ruleset auf `v*`-Tags mit *Restrict deletions* + *Block force pushes*. Die release-please-Tags (`vMAJOR.MINOR.PATCH`, siehe `versioning.md`) sind so vor versehentlichem Überschreiben/Löschen geschützt.

## Actions-Härtung (*Settings → Actions → General*)

| Setting | Wert | Warum |
|---------|------|-------|
| Actions permissions | **nur erlaubte Actions** | Allowlist statt „alles". Mindestens `googleapis/release-please-action`, `actions/checkout` zulassen. |
| Workflow permissions | **Read repository contents (read-only)** als Default | Least Privilege. Schreibrechte setzt der Workflow selbst per `permissions:`-Block (so im Asset). |

> [!NOTE]
> **Zwei release-kritische Actions-Settings liegen in `automation.md`, nicht hier** (SSoT): das Repo-Setting „Allow GitHub Actions to create and approve pull requests" und das Secret `RELEASE_PLEASE`. Diese Datei verweist nur darauf.

**Actions auf Commit-SHA pinnen** statt auf bewegliche Tags (`@v5` → `@<sha>`). Tags lassen sich verschieben, ein SHA nicht — Supply-Chain-Schutz. Renovate verfolgt SHA-gepinnte Actions und bumpt sie als regulären PR; passt also in die bestehende Dependency-Automation (`automation.md`).

## Security-Features (*Settings → Code security*)

| Feature | Wert | Warum |
|---------|------|-------|
| Secret scanning | **an** | Findet versehentlich committete Secrets. |
| Push protection | **an** | Blockt das Secret **vor** dem Push auf `main` — wichtigste Einzelmaßnahme bei diesem Token-lastigen Stack (PATs, OAuth-KV, Worker-Secrets). |
| Dependabot alerts | **an** | Nur die Vulnerability-Advisories — ergänzt Renovate, kollidiert nicht. |
| Dependabot security updates | **aus** | Version-Bumps macht **Renovate** (`automation.md`). Kein zweiter Bot auf denselben Dependencies. |

## Secret- & Token-Lifecycle

Anlage, Scopes und Pflicht des `RELEASE_PLEASE`-PAT stehen in `automation.md` (Setup-Schritt + Stolperfalle 1). Hier nur die **Lifecycle-Seite**:

> [!WARNING]
> **Stiller Bruch bei PAT-Ablauf.** Fine-grained PATs haben ein Ablaufdatum. Läuft `RELEASE_PLEASE` ab, bricht der Auto-Merge **lautlos** — die Version wird gebumpt, aber kein Tag, kein Release. Erneuerung terminieren (Kalender/Reminder), bevor der Token ausläuft.

**Optional — GitHub App statt PAT.** Wer den Ablauf-Stolperstein dauerhaft loswerden will: eine GitHub App liefert granularere Rechte ohne hartes Ablaufdatum. Für ein Solo-Setup Overkill, solange die PAT-Erneuerung im Blick bleibt — als Eskalationspfad notiert, nicht als Pflicht.
