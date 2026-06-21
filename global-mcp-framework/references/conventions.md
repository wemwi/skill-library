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

Jedes Tool trägt **zwei** Bezeichner, die nie vermischt werden: `name` (Aufruf-ID,
strikt) und `title` (Anzeige, frei).

| Feld | Form | Zweck | Restriktion |
|---|---|---|---|
| `name` | `<verb>_<objekt>` · snake_case | Aufruf-ID (Agent/Client) | **`^[a-zA-Z0-9_-]{1,64}$`** — kein Punkt, kein Leerzeichen, kein camelCase |
| `title` | `<Verb> <Objekt>` · Title Case | Anzeige im Connector-UI | keine (Leerzeichen/Großschreibung erlaubt) |

Beispiel: `register("create_invoice", { title: "Create Invoice", … }, handler)`.

**1. Kein Service-Prefix.** Die Zuordnung Tool → Server übernimmt der Connector-
Namespace, den der Client anzeigt (`Lexware: Create Invoice`). Ein Prefix wie
`lexware_` würde nur wiederholen, was der Server-Name schon sagt. Vorbild ist Shopify
(`create-product`) / PubMed (`search_articles`), nicht Cloudflare — dessen `d1_`/`kv_`/
`r2_` trennt Sub-Produkte *innerhalb eines* Servers, was hier (ein Worker = ein Service)
nicht zutrifft.

| Worker | Beispiel-Tool (`name`) | `title` |
|---|---|---|
| `google-sheets-mcp` | `append_row` | Append Row |
| `google-drive-mcp` | `list_files` | List Files |
| `google-pagespeed-mcp` | `get_full_audit` | Get Full Audit |
| `google-search-console-mcp` | `inspect_url` | Inspect URL |
| `lexware-mcp` | `create_invoice` | Create Invoice |
| `telegram-mcp` | `post_message` | Post Message |

**2. Lesbarkeit lebt im `title`, nicht im `name`.** Da der `title` die menschen-
lesbare Anzeige übernimmt (Title Case, Akronyme groß: „Inspect URL", „Render Invoice
PDF"), muss der `name` nichts Kosmetisches mehr leisten — er bleibt kurz und
maschinenlesbar.

**3. Verb-first mit festem Verb-Set.** `<verb>_<objekt>`, Verb zuerst.
Kanonische Verben: `list`, `get`, `read`, `create`, `update`, `delete`, `append`, `move`,
`rename`, `search`, `analyze`. **Objekt nie weglassen** — ohne Prefix wäre `list` zu
nackt, also `list_files`. Generische Einzelwörter (`list`, `read`, `move`) sind verboten.

**4. Eindeutigkeit ohne Prefix.** Innerhalb eines Servers sind Namen ohnehin eindeutig.
Über mehrere Server hinweg garantiert sie der Connector-Namespace. Nur falls ein
Managed Agent mehrere Server in *eine flache* Tool-Liste zieht, vor dem Anbinden auf
namensgleiche Tools prüfen.

**5. Identisch in `register(...)` und `TOOL_ALLOWLIST`.** Der `name` (nicht der `title`)
steht an beiden Stellen exakt gleich. Der `title` steht nur im `register`-Config-Objekt.

**Warum die Punkt-Falle:** Ein Punkt (`append.row`) wird vom Server-SDK akzeptiert,
aber vom Konsumenten/Frontend abgewiesen — Fehler
`tools.N.FrontendRemoteMcpToolDefinition.name: String should match pattern '^[a-zA-Z0-9_-]{1,64}$'`.
Fällt erst beim Verbinden auf, nicht beim Build. Der Pre-Push-Gate-Hook prüft die
`TOOL_ALLOWLIST` (= `name`-Werte) gegen die Regex und blockiert den Push bei Verstoß
(siehe `deploy.md` / `assets/hooks/`). Der `title` unterliegt der Regex NICHT und darf
Leerzeichen/Großschreibung tragen — er taucht nie in der Allowlist auf.

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
Foundation. Pflicht ist außerdem der `overrides`-Eintrag für die SDK-Dedup (siehe
`deploy.md`). Versionen pro Repo gegen die Foundation pinnen.

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
