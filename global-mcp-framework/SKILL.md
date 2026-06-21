---
name: global-mcp-framework
description: >-
  Generisches Framework zum Erstellen von Custom-MCP-Servern als Cloudflare Worker
  mit @cloudflare/workers-oauth-provider (OAuth 2.1), stateless Streamable-HTTP und
  einer gemeinsamen Foundation als versionierte Git-Tag-Dependency. IMMER laden,
  sobald ein MCP-Server in diesem Stack erstellt, verdrahtet, auf eine neue
  Foundation gebumpt oder debuggt wird — auch wenn das Wort Skill nicht fällt.
  Trigger u.a.: Custom MCP-Server bauen, Cloudflare Worker MCP, workers-oauth-provider,
  OAUTH_KV, OAuth 2.1 inbound, /authorize Login, Provider-Wiring, stateless Transport,
  sessionIdGenerator, "Session terminated", "Server misconfigured", "Authorization
  failed" nach Consent, neuen Connector anlegen, Foundation-Tag bumpen,
  wrangler.jsonc für MCP, KV-Namespace MCP_OAUTH, scheduled purgeExpiredData,
  Discovery-Check well-known. Gilt für jeden neuen Custom-MCP-Server in diesem Stack.
metadata:
  version: "1.2.0"
---

# global-mcp-framework

Architektur-Wissen und Arbeitsabläufe zum Erstellen von Custom-MCP-Servern auf diesem
Stack. Jeder Server ist ein eigener Cloudflare Worker, der eine gemeinsame Foundation
(`<foundation-repo>`) als **versionierte Git-Dependency (Tag)** einbindet und nur
noch service-spezifisch verdrahtet: Tools + Login-Titel + Outbound-Secret.

**Betrieb ist web-only** — kein lokaler Rechner, kein VPS, kein Terminal. Alles läuft
über Claude Code (Git/PR), GitHub-Web (Merge/Tag) und das Cloudflare-Dashboard
(KV/Secrets/Logs). Bei jeder Anweisung gilt deshalb: keine `wrangler tail`-/SSH-
Schritte vorschlagen, sondern die Dashboard-Entsprechung.

## So findest du das richtige Detail

Diese SKILL.md ist der Einstieg. Die Tiefe liegt in `references/` — pro Sorge eine
Datei, damit ein Debug-Fall genau eine Datei lädt statt aller. Lies gezielt:

| Aufgabe / Symptom | Datei |
|---|---|
| OAuth-Provider verdrahten, `/authorize`-Login bauen, was der Provider selbst macht | `references/auth.md` |
| Transport-Setup, "Session terminated" beim Tool-Call | `references/transport.md` |
| KV-Binding/Namespace anlegen, KV-Hygiene, `purgeExpiredData`-Cron | `references/storage.md` |
| Inbound-Hash vs. Outbound-Key setzen, "Authorization failed" nach Consent | `references/secrets.md` |
| Repo-Layout, Workers-Builds Root directory, Deploy command, PR/Merge/Build, Foundation-Tag bumpen, Build-Cache-Falle | `references/deploy.md` |
| Repo-/Naming-Standard, Connector-URL, `login`-Config, README | `references/conventions.md` |
| Irgendein Fehlersymptom, Discovery-Check, Live-Logs, verifizierte CF-Fakten | `references/diagnostics.md` |

Vorlagen zum Kopieren liegen in `assets/`: `provider-wiring.ts`, `server.ts`,
`wrangler.jsonc`, `package.json.template`, `tsconfig.json.template`, `empty-ai.js`,
`README.template.md`, `hooks/`.

## Workflow: Neuen Custom-MCP-Server anlegen

Reihenfolge einhalten — Name verifizieren vor Anlegen, Secret vor Connector, Build
verifizieren vor Push, Connector-Test immer im frischen Chat. Primärquelle für den
Code ist immer das `server-template/` der Foundation; die Dateien in `assets/` sind
nur kommentierte Spiegel davon. Bei Abweichung gilt das `server-template/`.

0. **Name verifizieren** — Über den Cloudflare-MCP `workers_list` aufrufen. Existiert
   der Worker schon, exakt diesen Namen übernehmen; sonst den geplanten Namen
   festlegen. `name` in `wrangler.jsonc` = `name` in `package.json` = Repo = Cloudflare-
   Service. **Nie raten.** Details: `references/conventions.md`.
1. **KV** — KV-Namespace anlegen (per Cloudflare-MCP `kv_namespace_create` oder im
   Dashboard, Konvention `MCP_OAUTH_<SERVICE>`) und in `wrangler.jsonc` mit **Binding
   `OAUTH_KV`** verdrahten. Details: `references/storage.md`.
2. **Repo + Wiring** — `server-template/` der Foundation kopieren. `src/index.ts`
   (Provider-Wiring via `createOAuthWorker`, Spiegel: `assets/provider-wiring.ts`),
   `src/server.ts` (Tools + `TOOL_ALLOWLIST`, Spiegel: `assets/server.ts`),
   `wrangler.jsonc` (Spiegel: `assets/wrangler.jsonc`), `src/empty-ai.js` (Spiegel:
   `assets/empty-ai.js`). Foundation als Git-Tag in `package.json` (Spiegel:
   `assets/package.json.template`), `tsconfig.json` (Spiegel:
   `assets/tsconfig.json.template`). Konzepte: `references/auth.md`, `references/transport.md`.
   Repo-Layout (wrangler.jsonc im Build-Root): `references/deploy.md`.
3. **Secrets** — `MCP_AUTH_PASSWORD_HASH` (SHA-256-Hex) und das Outbound-Secret **am
   Worker** setzen. Outbound-Secret nicht zu setzen ist die häufigste Ursache für
   "Authorization failed" nach dem Consent. Details: `references/secrets.md`.
4. **Build verifizieren** — Vor dem Push: `npm run typecheck` und
   `npx wrangler deploy --dry-run` müssen grün sein. Das reproduziert die
   Cloudflare-Build-Fehler ("entry not found" / "static files") lokal. Die Gate-Hooks
   im `server-template` (`assets/hooks/`) erzwingen das. Details: `references/deploy.md`.
5. **Connector** — In claude.ai den Connector auf
   `https://<service>-mcp.<account>.workers.dev/mcp` zeigen lassen,
   Transport streamable-http, **kein Token-Feld** (OAuth). Vor dem Connect den
   Discovery-Check fahren (`references/diagnostics.md`).
6. **Test im frischen Chat** — Funktionstest NIE im Debug-Thread, immer in einem
   neuen Chat (klebende MCP-Sessions verfälschen sonst das Ergebnis). Erst wenn ein
   echter Tool-Call durchläuft, gilt der Server als verifiziert.

## Goldene Regeln (zeitlos)

- **Funktionstest immer im frischen Chat.** Das ist der einzige verlässliche
  Funktionstest — ein langer Debug-Thread kann eine alte MCP-Session festhalten.
- **Discovery-Check vor dem Connect.** Die beiden `.well-known`-Endpunkte im Browser
  öffnen; sauberes JSON heißt: Wiring ist live und öffentlich erreichbar.
- **Foundation-Bumps sind bewusst, nicht automatisch.** Eine neue Foundation-Version
  schlägt erst durch, wenn der Konsument seine `package.json` aktiv bumpt und neu baut.
- **Provider nicht nachbauen.** `/token`, `/register` und beide `.well-known`-Routen
  liefert `@cloudflare/workers-oauth-provider` selbst. Selbst gebaut wird nur die
  `/authorize`-Login-Seite.
- **Namen nie erfinden.** Vor dem Setzen von `name` `workers_list` (Cloudflare-MCP)
  fahren und den echten Service-Namen übernehmen. `name` muss in `wrangler.jsonc`,
  `package.json`, Repo und Cloudflare-Service identisch sein.
- **Tool-`name` ohne Punkt, ohne Prefix.** Jeder Tool-`name` und jeder
  `TOOL_ALLOWLIST`-Eintrag muss `^[a-zA-Z0-9_-]{1,64}$` erfüllen — kein Punkt, kein
  Leerzeichen, kein camelCase. Konvention `<verb>_<objekt>`, snake_case, **kein
  Service-Prefix** (z.B. `create_invoice`, `list_files`). Objekt nie weglassen
  (`list_files`, nicht `list`). Ein Punkt baut serverseitig durch, wird aber an der
  Frontend-Grenze abgewiesen (`FrontendRemoteMcpToolDefinition.name`) — fällt also erst
  beim Verbinden auf. Der Pre-Push-Gate-Hook erzwingt die Regel.
- **`name` ≠ `title`.** Der `name` ist die maschinenlesbare Aufruf-ID (snake_case,
  regex-streng). Der `title` ist der menschenlesbare Anzeigename im Connector
  (Title Case, Leerzeichen erlaubt: „Create Invoice", „Inspect URL"). Lesbarkeit lebt
  im `title`, deshalb braucht der `name` kein Prefix. Der `title` unterliegt der Regex
  NICHT und steht nie in der `TOOL_ALLOWLIST`.
- **Infra-Namen tragen den Anbieter, Tool-Namen nicht.** Worker, KV-Namespace und
  Secrets sind infra-lesbar → Anbieter/Aussteller im Namen (`google-sheets-mcp`,
  `MCP_OAUTH_GOOGLE_SHEETS`, `GOOGLE_SERVICE_ACCOUNT_JSON`). Tool-`name`s sind
  modell-lesbar → kurzes `<verb>_<objekt>` ohne Anbieter und ohne Service-Prefix
  (`append_row`, nicht `sheets_append_row`); die Server-Zuordnung macht der
  Connector-Namespace. Secret = `<AUSSTELLER>_<TYP>`, nicht nach Worker benannt
  (`GOOGLE_…`, nicht `GSC_…`). Details: `references/conventions.md`, `references/secrets.md`.
- **Build nie ungeprüft pushen.** `npm run typecheck` + `npx wrangler deploy --dry-run`
  müssen grün sein, bevor gepusht wird — der Cloudflare-Build wirft sonst dieselben
  Fehler erst nach dem Merge. Die Gate-Hooks (`assets/hooks/`) machen das verbindlich.
- **server-template ist die Wahrheit.** Die `assets/`-Dateien sind Spiegel; bei
  Abweichung gilt das `server-template/` der Foundation. Keine Asset-Drift dulden.
