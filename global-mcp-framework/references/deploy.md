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

## SDK-Dedup per `overrides` (Pflicht in jedem Consumer)

`agents` (liefert `createMcpHandler`) pinnt das MCP-SDK **exakt** auf eine ältere
Version als die, die der Consumer direkt nutzt. Ohne Gegenmaßnahme liegen zwei
SDK-Kopien im Baum → Typkonflikt (`McpServer` nominal inkompatibel) und möglicher
Runtime-Versions-Skew.

Jede Consumer-`package.json` braucht daher:

```jsonc
"overrides": { "@modelcontextprotocol/sdk": "$@modelcontextprotocol/sdk" }
```

Das zwingt den ganzen Baum (inkl. `agents`) auf die eine Version aus den eigenen
`dependencies`. Im `server-template` (Spiegel: `assets/package.json.template`) ist
das bereits gesetzt — beim Kopieren nicht entfernen.

## Foundation-Versionierung

Die Foundation ist eine **versionierte Git-Dependency (Tag)**. Es gibt **keinen
Auto-Push**: Eine neue Foundation-Version schlägt erst durch, wenn der Konsument seine
`package.json` bewusst auf den neuen Tag bumpt und neu baut. Das ist gewollt —
Kontrolle und gestaffelter Rollout.

Ablauf einer Framework-Änderung:
1. Foundation-PR → Merge. Der **Tag entsteht über release-please**, nicht von Hand —
   SemVer-Regel und Tag-Konvention stehen in `global-git-conventions`
   (`versioning.md`); bei Breaking Changes ist `feat!:` / `BREAKING CHANGE:` Pflicht,
   sonst ziehen Consumer unbemerkt inkompatibel nach.
2. Jeder Konsument bumpt `package.json` auf den neuen Tag → Merge → Cloudflare-Build.
   Den Wert in der `AUTO:foundation`-Zone des READMEs mitziehen (siehe
   `conventions.md`).
3. Konsumenten nacheinander nachziehen — kein Zwang, alle gleichzeitig zu heben.

## Build-Cache-Falle

Der Build-Cache kann eine **alte Foundation halten**, obwohl `package.json` bereits
einen neuen Tag nennt. Symptom: der Tag scheint nicht zu greifen.

Vorgehen: Cloudflare → Settings → Build → **Clear Cache**, dann neu deployen. Danach
im Deployments-Tab bestätigen, dass die neue Version aktiv ist.
