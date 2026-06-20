# Inbound-Auth: OAuth 2.1

Inbound-Authentifizierung läuft vollständig über OAuth 2.1 via
`@cloudflare/workers-oauth-provider`. OAuth ist gesetzt, weil claude.ai-Web und
Managed Agents ausschließlich OAuth sprechen.

## Was der Provider selbst implementiert (NICHT selbst bauen)

`/token`, `/register` (Dynamic Client Registration),
`/.well-known/oauth-authorization-server`,
`/.well-known/oauth-protected-resource`, PKCE-Validierung, Token-Lifecycle.

## Was selbst gebaut wird

Nur die `/authorize`-Login-Seite (der `defaultHandler`). Der Provider liefert
`/authorize` NICHT — er kennt den Endpoint nur für die Discovery-Metadaten.

## Provider-Wiring

Die kanonische Config steht als Vorlage in `assets/provider-wiring.ts`. Felder:

- `apiRoute: '/mcp'` — der streamable-http Endpoint.
- `apiHandler: mcpApiHandler` — erhält den authentifizierten User-Kontext über
  `ctx.props`. **Kein eigener Token-Check nötig** — der Provider hat vor dem
  `apiHandler` schon validiert.
- `defaultHandler` — die `/authorize`-Login-Seite (via `createLoginUiHandler`).
- `authorizeEndpoint: '/authorize'`, `tokenEndpoint: '/token'`,
  `clientRegistrationEndpoint: '/register'`.
- `scopesSupported: ['mcp']`.
- `allowPlainPKCE: false` — OAuth 2.1: nur S256.
- `refreshTokenTTL` — steuert, ob und wie lange claude.ai still erneuern kann. Die
  Provider-Semantik (`@cloudflare/workers-oauth-provider` 0.7+) ist kontraintuitiv und
  war Ursache eines stündlichen Re-Logins auf allen Servern gleichzeitig:

  | Wert | Verhalten im Provider |
  |---|---|
  | `undefined` | Refresh-Token wird ausgestellt, läuft **nie ab** — gewünscht für headless Agents |
  | `0` | **KEIN Refresh-Token** — nur der 1 h-Access-Token; nach Ablauf erzwungenes Re-Login |
  | `n > 0` | Refresh-Token läuft nach `n` Sekunden ab |

  Belegt in der Provider-Source: `useRefreshToken = refreshTokenTTL !== 0` überspringt
  bei `0` die komplette Token-Ausstellung; `expiresAt = refreshTokenTTL !== undefined
  ? now + refreshTokenTTL : undefined` macht `undefined` zu „unendlich". Gilt
  identisch in 0.7.0 und 0.8.1.

  ⚠️ **Falle:** `createOAuthWorker` hatte (Foundation ≤ v2.0.3) als Default
  `refreshTokenTTL: opts.refreshTokenTTL ?? 0`. Der `?? 0` kippt jeden nicht gesetzten
  oder als `undefined` übergebenen Wert auf `0` → kein Refresh-Token → claude.ai
  verliert die Session nach 1 h und verlangt Neu-Anmeldung. „Nie ablaufen" erreicht man
  nur, wenn `undefined` tatsächlich an den Provider durchgereicht wird (Default in
  `oauth.ts` auf `opts.refreshTokenTTL` ohne `?? 0`). **Folge für die KV-Hygiene**
  (siehe `storage.md`): Grants laufen dann nicht von selbst ab.
- `accessTokenTTL: 3600` — kurzlebiger Access-Token; der stille Refresh über das
  Refresh-Token (s. o.) ist der Mechanismus, der ein erneutes `/authorize` vermeidet.

## Login-Seite: `auth-ui.ts` (defaultHandler via `createLoginUiHandler`)

Es ist ein **Plain-Object-Handler** mit `async fetch(request, env, ctx)`. `env` kommt
als **zweiter Parameter** — KEINE `WorkerEntrypoint`-Klasse, kein `this.env`. Das war
eine der Debug-Fallen: in der Klassen-Form ist `env` nicht da, wo der Code es erwartet.

Der Code dieser Datei wird über den hier beschriebenen Verhaltens-Kontrakt gebaut bzw.
aus einem bestehenden Server der Foundation übernommen.

**`GET /authorize`:**
1. `parseAuthRequest()` auf den eingehenden Request.
2. CSRF-Token erzeugen.
3. Original-OAuth-Request als JSON in KV ablegen (kurze TTL, z.B. 600s).
4. Login-Formular rendern, CSRF-Token im `__Host-`-Cookie **und** als Hidden-Field.

**`POST /authorize`:**
1. CSRF prüfen (Cookie == Form).
2. Passwort-Hash gegen `env[passwordHashEnvVar]` (Default `MCP_AUTH_PASSWORD_HASH`)
   **timing-safe** vergleichen.
3. `completeAuthorization({ userId, scope, props })`.
4. 302-Redirect.

**Pflicht-Schutz (laut Cloudflare-Securing-Doc):**
- CSRF-Token im Cookie `__Host-CSRF` (HttpOnly, Secure, SameSite=Lax).
- State-Token (der zwischengeparkte OAuth-Request) in KV mit kurzer TTL.

## Übergabe des Kontexts

Der authentifizierte Kontext erreicht den `apiHandler` über `ctx.props` (das
`props`-Objekt aus `completeAuthorization`).
