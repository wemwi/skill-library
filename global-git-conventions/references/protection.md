# protection.md — Repo-Härtung (GitHub Free, Solo-Account)

Checkliste, gegen die jedes eigene Repo geprüft wird. Stand: GitHub **Free**, gemischt
public/private, Solo-Account. Höhere Pläne schalten mehr frei — hier steht nur, was auf
Free real verfügbar ist.

> [!IMPORTANT]
> **Du sperrst dich als Admin nie selbst aus.** Branch-Protection läuft so, dass du im
> Notfall weiter direkt pushen kannst: klassische *Branch protection rule* OHNE „Do not
> allow bypassing" angehakt, oder *Ruleset* mit dir auf der **Bypass-Liste**. Nur der
> Release-Bot-Flow und versehentliche Zerstörung werden geblockt, nie dein Owner-Zugriff.

> [!NOTE]
> Datei NICHT mit `SECURITY.md` verwechseln. `SECURITY.md` ist ein Repo-Artefakt
> (Vulnerability-Disclosure-Policy: „wie meldet man mir eine Lücke"). Diese
> `protection.md` ist die **Härtungs-Anleitung** für den Skill. Zwei verschiedene Dinge.

## Account-Ebene (einmalig, gilt für alle Repos)

| Punkt | Wo |
|-------|-----|
| **2FA aktiviert** | *Account → Settings → Password and authentication* |
| **Push Protection für User** an (Default) | *Account → Settings → Code security* — schützt dich beim Push in public Repos automatisch vor committeten Secrets, repo-unabhängig |

## Pro Repo — public (Free)

| Punkt | Wo / Wert |
|-------|-----------|
| **Dependabot Alerts** an | *Repo → Settings → Advanced Security* |
| **Secret Scanning** an (gratis für public) | *Repo → Settings → Advanced Security* |
| **Push Protection** (repo-weit) an (gratis für public) | *Repo → Settings → Advanced Security* |
| **Branch-Protection auf `main`:** Block force pushes + Restrict deletions, **keine** Required Reviews/Checks | *Repo → Settings → Branches* (oder Ruleset) |
| **Actions-PR-Recht** nur wo nötig | *Repo → Settings → Actions → General* — „Allow GitHub Actions to create and approve pull requests" nur an, wo release-please läuft (siehe `automation.md`) |
| **`SECURITY.md`** (Disclosure-Policy) | empfohlen bei sichtbaren/genutzten Repos |

## Pro Repo — private (Free)

Auf Free sind Secret Scanning + repo-weite Push Protection für private Repos **nicht
verfügbar** (brauchen GitHub Secret Protection → Team/Enterprise). Dafür greifen:

| Punkt | Wo / Wert |
|-------|-----------|
| **Dependabot Alerts** an (frei, auch private) | *Repo → Settings → Advanced Security* |
| **Branch-Protection auf `main`:** wie public (Block force pushes + Restrict deletions, keine Required Reviews/Checks) | *Repo → Settings → Branches* (oder Ruleset) |
| **Actions-PR-Recht** nur wo nötig | wie public |
| **Secrets-Disziplin** | Keys via `.gitignore` draußen halten + als Repo-Secret hinterlegen — Secret Scanning fängt hier NICHT, also manuell sauber sein |

> [!WARNING]
> **Ein public-Repo nicht „zur Sicherheit" auf private umstellen.** Beim Wechsel auf
> private fallen auf Free Secret Scanning + Push Protection (repo-weit) WEG — das Repo
> wird dadurch nicht sicherer, sondern verliert Schutz.

## Branch-Protection — Minimal-Variante im Detail

Setzt genau zwei Dinge, mehr nicht:

- **Block force pushes** — niemand überschreibt die `main`-Historie.
- **Restrict deletions** — `main` lässt sich nicht versehentlich löschen.
- **KEINE** Required Reviews, **KEINE** Required Status Checks, **KEIN** Review-Zwang über
  „Require a pull request before merging". Diese würden den selbst-mergenden Release-PR
  (`gh pr merge --squash`) blockieren — Begründung in `automation.md`.

Damit ist GitHubs „your main branch isn't protected"-Warnung erledigt, ohne die
Release-Automation zu brechen.

Umsetzung wahlweise:
- **Branch protection rule** (zwei Häkchen, „Do not allow bypassing" NICHT anhaken) —
  reicht für Solo. Owner behält Notfall-Push.
- **Ruleset** (`Block force pushes` + `Restrict deletions`, Bypass-Liste = du selbst) —
  moderner, erlaubt später feingranulares Bypass, falls doch mal Required Checks dazukommen.
