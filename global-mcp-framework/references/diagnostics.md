# Betriebs- & Diagnose-Landkarte

Symptom → Ursache → Vorgehen. Diese Datei routet zu den vertiefenden References.

## "Server misconfigured" (HTTP 500 auf `/authorize`-POST)

Der Passwort-Hash-Guard feuert — `env[passwordHashEnvVar]` ist leer/undefined.
Ursachen: Secret fehlt, oder `env` enthält die Secrets nicht (z.B. `WorkerEntrypoint`-
Klassen-Form statt Plain-Object-Handler, siehe `auth.md`).

Diagnose: temporär `log?.info("authorize env keys", { keys: Object.keys(env ?? {}) })`
vor der Hash-Zeile committen → in den Live-Logs prüfen, ob der erwartete Schlüssel
überhaupt in den env-Keys auftaucht. Den Log danach wieder entfernen.

→ `auth.md`, `secrets.md`

## "Session terminated" (JSON-RPC 32600 beim Tool-Call)

(a) Transport läuft stateful ohne State-Backing → auf stateless umstellen
(`sessionIdGenerator: undefined`).
(b) Klebende MCP-Session in einem langen Debug-Thread → **im frischen Chat testen**,
das ist der verlässliche Funktionstest.

→ `transport.md`

## "Authorization … failed" / Fehler nach Consent, vor Tools

Outbound-Secret am Worker nicht gesetzt. `buildServer` wirft beim Initialisieren.
Secret am richtigen Worker setzen.

→ `secrets.md`

## "Client not found" / Error 1101 auf `/authorize`

Die DCR-Client-Registrierung ist aus dem KV verschwunden — typisch 90 Tage nach dem
Erst-Connect, wenn der Worker auf einer Foundation ≤ v3.0.3 läuft (Provider-Default
`clientRegistrationTTL`). `/token` meldet `Client not found`, `GET /authorize` wirft
unbehandelt (1101), „Neu autorisieren" im Client scheitert, weil er die tote Client-ID
wiederverwendet.

Vorgehen: Foundation auf ≥ v3.0.4 bumpen und deployen, dann die Verbindung im Client
**neu anlegen** (nicht neu autorisieren) — erzwingt eine frische `/register`-Registrierung
ohne Ablauf.

→ `auth.md`

## Deploy greift scheinbar nicht

Version-live-Indikator prüfen (z.B. ob ein entfernter Diagnose-Log noch erscheint) →
Build-Cache leeren → Version im Deployments-Tab als aktiv bestätigen.

→ `deploy.md`

## Build: "entry-point file at src/index.ts was not found"

wrangler findet die `wrangler.jsonc`, aber die `main`-Datei nicht relativ dazu. Das
Build-Root/Workers-Builds Root directory zeigt eine Ebene daneben. Layout prüfen.

→ `deploy.md`

## Build: "Could not detect a directory containing static files"

wrangler findet **keine** `wrangler.jsonc` im Build-Verzeichnis und fällt in den
Static-Assets-Modus (Pages-artiger Deploy). Ursache: Root directory zeigt auf einen
Ordner ohne `wrangler.jsonc`, oder der Deploy command ist `wrangler pages deploy`.
Root directory auf den Ordner mit `wrangler.jsonc` setzen, Deploy command auf
`npx wrangler deploy`.

→ `deploy.md`

## Discovery-Check (vor dem Connect)

Im Browser öffnen:
- `…/.well-known/oauth-authorization-server`
- `…/.well-known/oauth-protected-resource/mcp`

Sauberes JSON = Wiring live und öffentlich erreichbar (kein Token nötig).

## Live-Logs

Cloudflare → Worker → Observability → Logs (Live oder Events der letzten Stunde).
Das ist der web-only-Ersatz für `wrangler tail`.

## Grundregel

Funktionstest immer im **frischen Chat**, nie im Debug-Thread.

---

# Verifizierte Cloudflare-Fakten (Referenz)

Gegen die Cloudflare-Docs (`@cloudflare/workers-oauth-provider` v0.7.x,
MCP-SDK 1.26.0, Stand Juni 2026) verifiziert bzw. in produktiven Servern belegt.

- Der Provider implementiert `/token`, `/register` und beide `/.well-known/*` selbst;
  nur `/authorize` baut die App.
- `OAUTH_KV` ist der erwartete Binding-Name (hardcodiert).
- Stateless: `sessionIdGenerator: undefined`, frische `McpServer`-Instanz pro Request
  (SDK-1.26.0-Guard).
- `/token` muss `Content-Type: application/x-www-form-urlencoded` akzeptieren und bei
  ungültigen Tokens RFC-konforme Codes (`invalid_grant`) liefern — macht der Provider
  von Haus aus.
- Protected-Resource-Metadata liegt bei Pfad-Servern unter
  `/.well-known/oauth-protected-resource/mcp`.
