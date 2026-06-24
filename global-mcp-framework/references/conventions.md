# MCP-Naming & Struktur

Diese Datei regelt die **MCP-spezifische** Mechanik: Naming (Worker/Tool/Secret),
Folder-Struktur der Repo-Typen und Connector-Wiring. Der **typ-übergreifende**
Repo-Standard (README-Pflichtsektionen, Versionierung, CHANGELOG, Release-Automation,
About-Block) lebt in `global-git-conventions` und wird hier nur referenziert.
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

> **Ausnahme Multi-Worker:** Speist ein Repo mehrere Services über Wrangler Environments
> (z.B. `telegram-mcp` → `mcp-telegram-operations` + `…-broadcast`), divergieren `name`
> und KV bewusst pro `env`-Block; der Repo-/Paket-`name` bleibt der gemeinsame Basisname.
> Mechanik in `deploy.md`.

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

Zwei Repo-Typen, beide hier dokumentiert, weil die Folder-Struktur typ-spezifisch
ist (anders als der Doku-/Release-Standard, der in `global-git-conventions` wohnt).

### `*-mcp` — der MCP-Server (Cloudflare Worker)

Diese Dateien liegen direkt im **Build-Root** (Repo-Root oder das in Workers Builds
gesetzte Root directory) — **nicht** in einem zusätzlichen Wrapper-Ordner. Liegt die
`wrangler.jsonc` nicht im Build-Root, schlägt der Cloudflare-Build fehl (siehe
`deploy.md`).

```
<service>-mcp/                  # = Build-Root
├── src/
│   ├── index.ts            # Provider-Wiring + login-Config (siehe auth.md, assets/provider-wiring.ts)
│   ├── server.ts           # Tools + TOOL_ALLOWLIST (siehe assets/server.ts)
│   └── empty-ai.js         # leerer Stub für den ai-Alias (siehe assets/empty-ai.js)
├── .claude/                # Gate-Hooks (settings.json + hooks/), siehe assets/hooks/
├── docs/                   # optional — nur bei repo-spezifischer Tiefe, die das README sprengt
├── wrangler.jsonc          # MUSS im Build-Root liegen (siehe deploy.md, assets/wrangler.jsonc)
├── package.json            # Foundation-Dependency auf einen Git-Tag, name == Worker-Name (siehe assets/package.json.template)
├── tsconfig.json           # siehe assets/tsconfig.json.template
├── README.md               # Template + Pflichtsektionen: global-git-conventions (assets/readme/mcp.md)
├── CHANGELOG.md            # von release-please gepflegt — global-git-conventions
└── .github/ + release-please-*.json   # Release-Automation — global-git-conventions
```

Die `package.json` bindet die Foundation als **Git-Tag-Dependency** ein
(`"mcp-foundation": "github:<org>/<foundation-repo>#<git-tag>"`), `name` == Worker-Name,
und braucht das `typecheck`-Script (der Gate-Hook ruft `npm run typecheck`). Die
**einzige Laufzeit-Dependency ist `mcp-foundation`** (plus repo-eigene Libs, die nur
dieses Repo importiert, z.B. `unpdf`). `zod` und `@modelcontextprotocol/sdk` stehen
**NICHT** mehr in den Consumer-`dependencies`: Fremdimporte laufen ausschließlich über
die Fassade — `z` aus `mcp-foundation/schema`, `McpServer` aus `mcp-foundation/sdk`.
Die Foundation (ab v2.4.0) führt SDK, zod, `agents` und den OAuth-Provider als eigene
`dependencies` und re-exportiert sie über diese Subpaths. Pflicht bleibt der
`overrides`-Eintrag (`"@modelcontextprotocol/sdk": "1.29.0"`, explizite Version) für die
SDK-Dedup gegen den `agents`-Pin (siehe `deploy.md`). Versionen pro Repo gegen die
Foundation pinnen.

> `README.md`, `CHANGELOG.md` und die `.github/`-/`release-please-*`-Dateien folgen
> dem typ-übergreifenden Standard und den Templates aus `global-git-conventions` —
> hier nicht erneut beschrieben.

### `*-foundation` — die gemeinsame Basis

Die Foundation ist **kein deploybarer Worker**, sondern eine Bibliothek, die per
Git-Tag von den `*-mcp`-Repos konsumiert wird — daher kein Build-Root-Zwang und keine
`wrangler.jsonc` auf Repo-Ebene. Zwei Aufgaben: (1) die geteilte Laufzeit-Oberfläche
exportieren, (2) das `server-template/` bereitstellen, das beim Anlegen eines neuen
`*-mcp` 1:1 kopiert wird.

```
mcp-foundation/
├── src/                    # exportierte Oberfläche (Aufteilung als Vorschlag, Exports sind verbindlich)
│   └── index.ts            # exportiert: createOAuthWorker, createLoginUiHandler, buildServer, purgeExpiredData
├── server-template/        # wird beim Anlegen eines *-mcp kopiert (= Primärquelle, assets/ sind nur Spiegel)
│   ├── src/{index.ts, server.ts, empty-ai.js}
│   ├── .claude/{settings.json, hooks/pre-push-gate.sh}
│   ├── wrangler.jsonc
│   ├── package.json
│   └── tsconfig.json
├── docs/                   # optional
├── package.json            # name == foundation-repo, type module, exports-Feld, typecheck-Script
├── tsconfig.json
├── README.md               # Template: global-git-conventions (assets/readme/foundation.md)
├── CHANGELOG.md            # von release-please gepflegt — global-git-conventions
└── .github/ + release-please-*.json   # Release-Automation — global-git-conventions
```

**Verbindlich** (in Servern belegt) ist die exportierte Oberfläche — die vier
Funktionen `createOAuthWorker` (Provider-Wiring, `auth.md`),
`createLoginUiHandler` (`/authorize`-Login, `auth.md`), `buildServer`
(Server-Aufbau, liest das Outbound-Secret, `secrets.md`) und `purgeExpiredData`
(KV-Cron-Hygiene, `storage.md`) — sowie das `server-template/` als Primärquelle.
Die interne Datei-Aufteilung unter `src/` (z.B. ob `oauth.ts`/`auth-ui.ts` getrennt
liegen) ist ein **Vorschlag** und beim Bauen frei wählbar, solange `src/index.ts`
die vier Exports stabil nach außen gibt.

> [!IMPORTANT]
> Der `refreshTokenTTL`-Default in `createOAuthWorker` darf **nicht** `?? 0` sein —
> `0` heißt „kein Refresh-Token" und erzwingt stündliches Re-Login. `undefined`
> durchreichen (= nie ablaufen). Belegt in `auth.md`.

## Connector-URL

`https://<service>-mcp.<account>.workers.dev/mcp` — Transport
streamable-http, OAuth. **Kein Token-Feld** im Connector.

## `login`-Config je Server

```ts
login: { userId: "<user-id>", title: "<Service> MCP — Login" }
```

## README & Release

Aufbau, Pflichtsektionen und das Template stehen in `global-git-conventions`
(`assets/readme/mcp.md`) — hier nicht duplizieren. Ein `*-mcp`-README füllt nur die
typ-spezifischen Felder: Live-URL (Connector-Config), Tool-Liste und die
Secrets/Bindings-Tabelle (nur Namen + Pflicht-Flag; Mechanik bleibt hier im Skill).
CHANGELOG, Tags und der About-Block laufen ebenfalls über `global-git-conventions`.

### Foundation-Aktualität (kein README-Eintrag)

Der gepinnte Foundation-Tag lebt ausschließlich in der `package.json`
(`"mcp-foundation": "github:<org>/<foundation-repo>#<git-tag>"`). Er wird **nicht** ins
README gespiegelt — den Rückstand zur neuesten Foundation und die Bump-PRs übernimmt
Renovate (Dependency Dashboard). Setup und die Foundation-spezifische Renovate-Regel
stehen in `deploy.md` bzw. `global-git-conventions` (`references/automation.md`).
