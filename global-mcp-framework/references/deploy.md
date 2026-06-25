# Deploy-Pipeline

## Ablauf

Claude Code → PR gegen `main` → **manueller Merge im GitHub-Web** → Cloudflare baut
automatisch von `main`. Kein Terminal, kein `wrangler deploy` von Hand.

Dieser Cloudflare-Build ist **unabhängig** von der Release-Automation: Tags,
CHANGELOG und GitHub-Release erzeugt release-please (Standard in
`global-git-conventions`), und zwar auf einem Branch-Push. Cloudflare baut ebenfalls
auf Branch-Push (`main`), nicht auf Tag-Push — der Merge des release-please-Release-PR
ist so ein `main`-Push und löst genau einen Deploy aus. Kein Doppel-Deploy, keine
Verzahnung nötig.

## Repo-Layout & Workers-Builds (häufigste Build-Fehler)

Die `wrangler.jsonc` muss im **Build-Root** liegen — dem Verzeichnis, das Workers
Builds als Arbeitsverzeichnis nimmt. Zwei konsistente Layouts, eines wählen:

- Repo-Root = die Server-Dateien direkt (`wrangler.jsonc`, `package.json`, `src/`).
  In Workers Builds bleibt **Root directory** leer.
- Server-Dateien in einem Unterordner `<service>-mcp/`. Dann **Root directory**
  in Workers Builds (Settings → Build → Git configuration) exakt auf diesen Ordner
  setzen.

**Deploy command** muss `npx wrangler deploy` sein (nicht `wrangler pages deploy`).

Zwei Symptome, beide = Layout/Root-Problem (siehe auch `diagnostics.md`):
- `The entry-point file at "src/index.ts" was not found` — wrangler findet die Config,
  aber `src/` fehlt relativ dazu → Root zeigt eine Ebene daneben.
- `Could not detect a directory containing static files` — wrangler findet **keine**
  `wrangler.jsonc` und fällt in den Static-Assets-Modus → Root zeigt auf einen Ordner
  ohne `wrangler.jsonc`.

## Verifikation vor dem Push (Gate-Hooks)

Beide Fehler oben schlagen ohne Vorprüfung erst im Cloudflare-Build auf (nach dem
Merge). Deshalb VOR dem Push lokal in Claude Code:

```
npm run typecheck            # tsc --noEmit
npx wrangler deploy --dry-run  # reproduziert Entry-/Config-/Bundling-Fehler lokal
```

Das `server-template` bringt dafür Gate-Hooks mit (`assets/hooks/` → `.claude/`):
ein PreToolUse-Hook fängt `git push` ab und blockiert (Exit 2), solange Typecheck
oder Dry-Run fehlschlagen oder keine `wrangler.jsonc` im Root liegt. So wird die
Prüfung erzwungen statt nur empfohlen.

## `wrangler.jsonc`-Pflicht pro Repo

Vorlage: `assets/wrangler.jsonc`. Pflichtbestandteile:

- `ai`-Alias auf `src/empty-ai.js`.
- Worker-Name = Cloudflare-Service-Name = Repo-Name.
- **KEIN** `durable_objects`, **KEIN** `migrations` (stateless, kein DO — siehe
  `transport.md`).
- `kv_namespaces` mit `"binding": "OAUTH_KV"` (siehe `storage.md`).
- `nodejs_compat`.
- **KEIN** `triggers`/`crons` — der Cloudflare Free Plan limitiert Cron Triggers,
  stack-weit keine Cron Jobs. Der `scheduled`-Handler (`purgeExpiredData`) bleibt in der
  Foundation, wird aber nicht getriggert; die Folge ist bewusst akzeptiert (siehe
  `storage.md`).

## Ausnahme: Mehrere Worker aus einem Repo (Environments)

Standard ist ein Repo = ein Worker = eine `wrangler.jsonc` mit festem `name` und einer
KV-ID. Ausnahme: Wenn mehrere Services fast den gesamten Code teilen und sich nur in der
Verdrahtung unterscheiden (z.B. `telegram-mcp` → `mcp-telegram-operations` +
`mcp-telegram-broadcast`), werden sie über **Wrangler Environments** aus einem Repo
gespeist — nicht über zwei `wrangler.jsonc` und nicht über das CI-Name-Override.

Warum nicht das CI-Override: Workers Builds überschreibt nur den Worker-**Namen**, nicht
die Bindings. Zwei Builds auf dieselbe top-level `wrangler.jsonc` zielen damit auf
**dieselbe** KV — das verletzt „pro Server ein eigener Namespace" (`storage.md`) und
failt, sobald die eine ID nicht (mehr) existiert.

Mechanik:
- Top-level trägt nur die **inheritable** Keys (`main`, `compatibility_date`,
  `compatibility_flags`/`nodejs_compat`, `ai`-Alias). Der top-level `name` bleibt der
  Repo-Name und wird real nie deployt.
- Pro Service ein `env.<name>`-Block mit eigenem `name` (= existierender Cloudflare-
  Service) und eigener `OAUTH_KV`-Binding (eigene KV-ID). So bleibt „pro Server ein
  eigener Namespace" erfüllt — die Isolation wandert in den env-Block.
- **Bindings und `vars` sind non-inheritable** und müssen in **jeden** env-Block
  gespiegelt werden. Was nur top-level steht, fehlt im deployten Worker (baut durch,
  fällt zur Laufzeit aus).
- Deploy command je Workers-Builds-Connection: `npx wrangler versions upload --env <name>`.
  **Nie ohne `--env` deployen** — das legt einen verwaisten top-level-Service an.

```jsonc
{
  "name": "telegram-mcp",            // Basis; real deployt wird nur per --env
  "main": "src/index.ts",
  "compatibility_date": "…",
  "compatibility_flags": ["nodejs_compat"],
  "env": {
    "operations": {
      "name": "mcp-telegram-operations",
      "kv_namespaces": [{ "binding": "OAUTH_KV", "id": "<operations-kv-id>" }]
      // + jede top-level vars/Binding hier spiegeln
    },
    "broadcast": {
      "name": "mcp-telegram-broadcast",
      "kv_namespaces": [{ "binding": "OAUTH_KV", "id": "<broadcast-kv-id>" }]
      // + jede top-level vars/Binding hier spiegeln
    }
  }
}
```

`name` und KV divergieren hier bewusst (vgl. `conventions.md`, „vier Stellen identisch") —
die Identitäts-Regel gilt für den Standardfall, der env-Block ist die benannte Ausnahme.
Verifikation vor dem Push dann pro Environment: `npx wrangler deploy --dry-run --env <name>`.

## SDK-Dedup per `overrides` (Pflicht in jedem Consumer)

`agents` (liefert `createMcpHandler`) pinnt das MCP-SDK **exakt** auf eine bestimmte
Version. Ohne Gegenmaßnahme liegen zwei SDK-Kopien im Baum → Typkonflikt (`McpServer`
nominal inkompatibel) und möglicher Runtime-Versions-Skew. Das gilt auch jetzt noch,
wo der Consumer das SDK nicht mehr direkt in seinen `dependencies` führt: `agents` zieht
seine eigene SDK-Kopie transitiv mit, die gegen die der Foundation deduppt werden muss.

Jede Consumer-`package.json` braucht daher:

```jsonc
"overrides": { "@modelcontextprotocol/sdk": "1.29.0" }
```

`npm`-overrides wirken **nur vom Consumer-Root** — deshalb steht der override im
Consumer, nicht in der Foundation. Anders als früher steht hier eine **explizite
Version** statt der Self-Reference `"$@modelcontextprotocol/sdk"`: Das SDK ist nicht
mehr in den Consumer-`dependencies` (es kommt über die Fassade `mcp-foundation/sdk`),
also gibt es keinen eigenen `dependencies`-Eintrag mehr, auf den `$…` zeigen könnte.
Die Version muss exakt die sein, die `agents` erwartet. Im `server-template` (Spiegel:
`assets/package.json.template`) ist das bereits gesetzt — beim Kopieren nicht entfernen.

## Foundation-Versionierung

Die Foundation ist eine **versionierte Git-Dependency (Tag)**. Es gibt **kein
Auto-Merge**: Eine neue Foundation-Version schlägt erst durch, wenn der Bump-PR bewusst
gemergt und neu gebaut wird. Den PR öffnet **Renovate** automatisch — der manuelle
Sechs-Repo-Nachzug entfällt, die Merge-Entscheidung bleibt bei dir.

Ablauf einer Framework-Änderung:
1. Foundation-PR → Merge. Der **Tag entsteht über release-please**, nicht von Hand —
   SemVer-Regel und Tag-Konvention stehen in `global-git-conventions`
   (`versioning.md`); bei Breaking Changes ist `feat!:` / `BREAKING CHANGE:` Pflicht,
   sonst ziehen Consumer unbemerkt inkompatibel nach.
2. Renovate erkennt den neuen Tag und öffnet pro `*-mcp` einen Bump-PR auf
   `package.json`. Mergen → Cloudflare-Build. Den Rückstand über alle Server zeigt das
   Renovate Dependency Dashboard zentral — keine README-Zone mehr.
3. Konsumenten nacheinander mergen — kein Zwang, alle gleichzeitig zu heben. Bei einem
   Breaking-/Major-Bump zuerst ein Repo als Kanarienvogel durchziehen.

### Renovate erkennt den Foundation-Pin

Renovates npm-Manager verfolgt GitHub-Tags meist out-of-the-box. Falls die
`github:<org>/mcp-foundation#<tag>`-Form beim Onboarding **nicht** als Dependency im
Dependency Dashboard auftaucht, einen `customManager` in der `renovate.json` ergänzen
(`<org>` aus dem bestehenden Pin übernehmen):

```json
{
  "customManagers": [
    {
      "customType": "regex",
      "fileMatch": ["^package\\.json$"],
      "matchStrings": ["\"mcp-foundation\":\\s*\"github:<org>/mcp-foundation#(?<currentValue>v[0-9.]+)\""],
      "depNameTemplate": "mcp-foundation",
      "packageNameTemplate": "<org>/mcp-foundation",
      "datasourceTemplate": "github-tags"
    }
  ]
}
```

Die Renovate-Basis-Config und das Setup stehen in `global-git-conventions`
(`assets/automation/renovate.json`, `references/automation.md`).

## Build-Cache-Falle

Der Build-Cache kann eine **alte Foundation halten**, obwohl `package.json` bereits
einen neuen Tag nennt. Symptom: der Tag scheint nicht zu greifen.

Vorgehen: Cloudflare → Settings → Build → **Clear Cache**, dann neu deployen. Danach
im Deployments-Tab bestätigen, dass die neue Version aktiv ist.
