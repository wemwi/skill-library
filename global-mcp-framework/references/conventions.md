# Repo-Standard / Konvention

Ziel: alle MCP-Repos einheitlich.

## Naming

### Worker-Name: `<service>-mcp`

`<service>` wird aus dem **vollen Produktnamen inklusive Anbieter** abgeleitet:
lowercase, mit Bindestrich getrennt, **keine Abkürzung**. Lange Produktnamen
pragmatisch kürzen, aber den Anbieter behalten.

| Dienst | Worker-Name |
|---|---|
| Google Sheets | `google-sheets-mcp` |
| Google Drive | `google-drive-mcp` |
| Google Search Console | `google-search-console-mcp` |
| Google PageSpeed Insights | `google-pagespeed-mcp` (gekürzt, nicht `…-insights-mcp`) |
| Lexware Office | `lexware-mcp` |
| Telegram | `telegram-mcp` |

`<service>-mcp` ist Repo = Worker = Cloudflare-Service-Name — **kein zusätzliches
Org-/Projekt-Suffix.** Der Name muss an vier Stellen identisch sein: `name` in
`wrangler.jsonc`, `name` in `package.json`, der Repo-Name und der Cloudflare-
Service-Name. Ein Mismatch deployt entweder einen falsch benannten Zweit-Worker
oder lässt den Build den falschen Service treffen.

**Vor dem Setzen des Namens verifizieren, nicht raten:** über den Cloudflare-MCP
`workers_list` die existierenden Worker abrufen. Existiert der Ziel-Worker bereits,
exakt dessen Namen übernehmen.

Platzhalter: `<service>` = der angebundene Dienst (Produktname inkl. Anbieter,
abgeleitet wie oben), `<account>` = die workers.dev-Subdomain des Cloudflare-
Accounts, `<foundation-repo>` = die gemeinsame Foundation, `<user-id>` = der Single-
User der Installation.

## Tool-Naming

Tool-Namen müssen dem Muster `^[a-zA-Z0-9_-]{1,64}$` folgen: Buchstaben, Ziffern,
`_`, `-` — **kein Punkt, kein Leerzeichen, kein Doppelpunkt**. Format
`<prefix>_<verb>_<objekt>`, durchgehend **snake_case** (kein camelCase).

**1. Prefix ist Pflicht — und aus dem Worker-Namen abgeleitet.**
Worker-Namen nehmen, `provider-` vorne und `-mcp` hinten streichen, snake_case → das
ist der Prefix. So ist die Zuordnung Tool → Worker mechanisch erkennbar. Gilt für
**jeden** Server, auch Single-Provider — kein nacktes `post_message`, kein `createInvoice`.

| Worker | Prefix | Beispiel-Tool |
|---|---|---|
| `google-sheets-mcp` | `sheets_` | `sheets_append_row` |
| `google-drive-mcp` | `drive_` | `drive_list_files` |
| `google-pagespeed-mcp` | `pagespeed_` | `pagespeed_get_full_audit` |
| `google-search-console-mcp` | `search_console_` (Ausnahme `gsc_`, siehe 4) | `search_console_inspect_url` |
| `lexware-mcp` | `lexware_` | `lexware_create_invoice` |
| `telegram-mcp` | `telegram_` | `telegram_post_message` |

**2. Der Prefix ist NICHT der Worker-Name.** Worker-Name = infra-/menschen-lesbar,
lang ok, Anbieter drin (`google-sheets-mcp`). Tool-Name = modell-lesbar in einer
flachen, server-übergreifenden Liste → **kurzer** Token ohne Anbieter (`sheets_`, nicht
`google_sheets_`). Anbieter rein in Infra-Namen, raus aus Tool-Namen.

**3. Verb-first mit festem Verb-Set.** `<prefix>_<verb>_<objekt>`, Verb zuerst.
Kanonische Verben: `list`, `get`, `read`, `create`, `update`, `delete`, `append`, `move`,
`rename`, `search`. Objekt nicht weglassen, wenn es sonst unklar ist
(`drive_list_files`, nicht `drive_list`).

**4. Abkürzungen nur als dokumentierte Ausnahme.** Default ist die volle Ableitung
(`search_console_`). Eine Abkürzung ist nur zulässig, wenn sie ein etablierter
Branchenbegriff ist UND hier in der Ausnahmeliste steht.
**Ausnahmeliste:** `gsc_` = Google Search Console.

**5. Identisch in `register(...)` und `TOOL_ALLOWLIST`.** Beide Stellen tragen exakt
denselben Namen.

**Warum die Punkt-Falle:** Ein Punkt (`sheets.append_row`) wird vom Server-SDK
akzeptiert, aber vom Konsumenten/Frontend abgewiesen — Fehler
`tools.N.FrontendRemoteMcpToolDefinition.name: String should match pattern '^[a-zA-Z0-9_-]{1,64}$'`.
Fällt erst beim Verbinden auf, nicht beim Build. Der Pre-Push-Gate-Hook prüft die
`TOOL_ALLOWLIST` gegen die Regex und blockiert den Push bei Verstoß
(siehe `deploy.md` / `assets/hooks/`).

## Struktur

Diese Dateien liegen direkt im **Build-Root** (Repo-Root oder das in Workers Builds
gesetzte Root directory) — **nicht** in einem zusätzlichen Wrapper-Ordner. Liegt die
`wrangler.jsonc` nicht im Build-Root, schlägt der Cloudflare-Build fehl (siehe
`deploy.md`).

```
<service>-mcp/              # = Build-Root
├── src/index.ts        # Provider-Wiring + login-Config (siehe auth.md, assets/provider-wiring.ts)
├── src/server.ts       # Tools + TOOL_ALLOWLIST (siehe assets/server.ts)
├── src/empty-ai.js     # leerer Stub für den ai-Alias (siehe assets/empty-ai.js)
├── wrangler.jsonc      # MUSS im Build-Root liegen (siehe deploy.md, assets/wrangler.jsonc)
├── package.json        # Foundation-Dependency auf einen Git-Tag, name == Worker-Name (siehe assets/package.json.template)
├── tsconfig.json       # siehe assets/tsconfig.json.template
└── .claude/            # Gate-Hooks (settings.json + hooks/), siehe assets/hooks/
```

Die `package.json` bindet die Foundation als **Git-Tag-Dependency** ein
(`"mcp-foundation": "github:<org>/<foundation-repo>#<git-tag>"`), `name` == Worker-Name,
und braucht das `typecheck`-Script (der Gate-Hook ruft `npm run typecheck`). Direkte
Dependencies sind nur, was der Code wirklich importiert (`mcp-foundation`,
`@modelcontextprotocol/sdk`, `zod`) — der OAuth-Provider kommt transitiv über die
Foundation. Versionen pro Repo gegen die Foundation pinnen.

## Connector-URL

`https://<service>-mcp.<account>.workers.dev/mcp` — Transport
streamable-http, OAuth. **Kein Token-Feld** im Connector.

## `login`-Config je Server

```ts
login: { userId: "<user-id>", title: "<Service> MCP — Login" }
```

## README

Template: `assets/README.template.md`. Struktur:
- Service-Logo oben (offizielle Logo-Asset-URL des jeweiligen Dienstes als
  Markdown-Image — konkrete URL pro Repo eintragen).
- Titel + Einzeiler (was der Server tut).
- Endpoint-URL + Transport (streamable-http, OAuth).
- Tool-Liste (Kurzbeschreibung je Tool).
- Eingebundene Foundation-Version.
- Deploy-Hinweis (PR → Merge → Cloudflare baut; KV + Secrets im Dashboard).
