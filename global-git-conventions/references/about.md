# about.md — GitHub About-Bereich

Der „About"-Block oben rechts im Repo (Description, Website, Topics) ist **kein Datei-Artefakt** — er wird über die GitHub-UI oder -API gesetzt, nicht per Commit. Trotzdem gehört er zum Standard, weil die Description in der Repo-Übersicht (`github.com/<OWNER>?tab=repositories`) erscheint und damit den „auf einen Blick"-Wert über *alle* Repos hinweg liefert.

## Description = README-Einzeiler

Die Description ist **derselbe Satz** wie der `>`-Einzeiler im README. Eine Aussage, zwei Orte, synchron gehalten. Nicht neu formulieren — kopieren.

## Website-Feld

- `*-mcp`: die **Worker-Live-URL** eintragen (`https://<repo>.wemwi.workers.dev/mcp`). So ist der Endpoint direkt aus der Repo-Übersicht erreichbar.
- `*-foundation`, `*-library`: leer lassen (oder Doku-Link, falls vorhanden).

## Topic-Schema je Typ

Basis-Topics (immer setzen), lowercase mit Bindestrichen:

| Typ | Basis-Topics |
|-----|--------------|
| `*-mcp` | `mcp`, `model-context-protocol`, `cloudflare-workers` |
| `*-foundation` | `mcp`, `model-context-protocol`, `cloudflare-workers`, `foundation` |
| `*-library` | `claude-skills`, `skills`, `library` |

**Repo-spezifische Topics** zusätzlich ergänzen, damit Filtern sinnvoll wird:
- `*-mcp`: der gekapselte Dienst, z.B. `google-sheets`, `telegram`, `lexware`.
- `*-library`: die Domäne, z.B. `shopify`, `liftr`.

## Setzen über Claude Code (gh CLI)

Da die Standardisierung über Claude Code läuft, kann der About-Block per `gh` mitgesetzt werden — kein manueller UI-Schritt nötig:

```bash
gh repo edit <OWNER>/<repo-name> \
  --description "<README-Einzeiler>" \
  --homepage "https://<repo-name>.wemwi.workers.dev/mcp" \
  --add-topic mcp --add-topic model-context-protocol --add-topic cloudflare-workers
```

`--homepage` bei `*-foundation`/`*-library` weglassen. Topics je nach Typ aus der Tabelle.
