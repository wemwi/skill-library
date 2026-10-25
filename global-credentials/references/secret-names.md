# Secret-Namen im Code

Gilt **stack-weit**: für jede Anwendung, die ein Drittanbieter-Credential liest —
MCP-Server, Webhook-Brücken, Adapter, Web-Apps, CI. Framework-eigene Secrets mit
festen Namen (z. B. `MCP_AUTH_PASSWORD_HASH` in `global-mcp-framework`) regelt der
jeweilige Fach-Skill.

## Drittanbieter-Credential → `<AUSSTELLER>_<TYP>`

- `<AUSSTELLER>` = wer das Credential ausstellt / wo es rotiert wird (die Marke, bei
  der man sich einloggt): `GOOGLE`, `LEXWARE`, `TELEGRAM`, `GITHUB`, `AIRTABLE`,
  `RESEND` …
- `<TYP>` = die Credential-Art (Tabelle unten).
- **Nicht** die Anwendung/den Worker kodieren (kein `GSC_…`): ein Secret ist
  anwendungs-scoped, die Anwendung ist also schon impliziter Kontext. Was zählt, ist
  *was* das Credential ist und *wo* man es rotiert → Aussteller + Typ.
  `GOOGLE_REFRESH_TOKEN` gilt damit für jeden Google-Worker, der denselben OAuth-Client
  mit einem eigenen scoped Refresh-Token nutzt (je Worker ein Token, je Worker ein
  Secret).
- Produkt-Qualifier nur zur Auflösung, wenn eine Anwendung zwei Credentials desselben
  Ausstellers UND Typs hält: `<AUSSTELLER>_<PRODUKT>_<TYP>` (Randfall).

| Typ | Suffix | Beispiel |
|---|---|---|
| API key | `_API_KEY` | `GOOGLE_API_KEY`, `LEXWARE_API_KEY`, `RESEND_API_KEY` |
| Dienstkonto (JSON) | `_SERVICE_ACCOUNT_JSON` | `GITHUB_APP_SERVICE_ACCOUNT_JSON` |
| Bot-Token | `_BOT_TOKEN` | `TELEGRAM_BOT_TOKEN` |
| OAuth-Client (3-legged outbound) | `_OAUTH_CLIENT_ID` / `_OAUTH_CLIENT_SECRET` + `_REFRESH_TOKEN` | `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` |
| Personal Access Token | `_TOKEN` | `GITHUB_TOKEN`, `AIRTABLE_TOKEN` |
| Basic Auth | `_USERNAME` / `_PASSWORD` | `JTL_USERNAME` |
| Signing-/Webhook-Secret | `_SIGNING_SECRET` / `_WEBHOOK_SECRET` | `TELEGRAM_WEBHOOK_SECRET` |
| S3-Credential (R2 presign) | `_ACCESS_KEY_ID` / `_SECRET_ACCESS_KEY` | `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY` |

Produkt-Qualifier bei Google: Ein Google-API-Key heißt `GOOGLE_API_KEY`, auch wenn er
nur für ein Produkt (Maps, PageSpeed …) freigeschaltet ist. `GOOGLE_<PRODUKT>_API_KEY`
erst, wenn dieselbe Anwendung wirklich zwei Google-API-Keys hält.

## Ein Credential = ein Name, über alle Konsumenten hinweg

Der Env-Name gehört zum *Credential* (Aussteller + Typ), nicht zur lesenden
Anwendung. Nutzen mehrere Dienste dasselbe Provider-Credential, tragen sie
**denselben** Namen — ein neuer Konsument übernimmt den etablierten Namen, statt einen
eigenen zu erfinden. Diese Konvention ist **stack-weit, nicht MCP-only**: auch
Nicht-MCP-Worker (Webhook-Brücken, Adapter, Web-Apps) erben sie, weil sie dasselbe
Credential lesen. Ein Lexware-API-Key heißt also überall `LEXWARE_API_KEY`, nie
`LEXWARE_API_TOKEN` — ein API-Key trägt **immer** `_API_KEY` (das Suffix `_TOKEN` ist
für Personal Access Tokens reserviert, nicht für API-Keys). Warum das strikt sein muss:
`env.<falscher Name>` ist zur Laufzeit still `undefined` — ein Name-Mismatch scheitert
**nicht** laut beim Deploy, sondern verändert stumm das Verhalten (z. B. ein
fail-open-Gate, ein nicht gesetzter Header). Darum beim Mitnutzen eines bestehenden
Credentials den Namen zeichengenau gegen die Tabelle oben abgleichen, nie neu erfinden.

„Derselbe Name" heißt nicht „derselbe Wert": Jede Anwendung hat ihr eigenes Token
(SKILL.md, Regel 1), gesetzt unter demselben Env-Namen.

## Sonderfälle

**Cloudflare-interne Credentials** (R2-S3 für presigned URLs): kein externer
Aussteller, daher steht der **Produktname** (`R2`) vorn statt einer Marke. Es ist das
S3-kompatible Access-Key-Paar — **nicht** der Bearer-Token-*Value* desselben
R2-API-Tokens (der ist für die native REST-API; `aws4fetch` signiert nur mit dem
Key-Paar). Mechanik: `global-mcp-framework`, `references/storage.md`.

**GitHub-Actions-Secrets:** Namen mit dem Präfix `GITHUB_` sind von GitHub reserviert
und als Repository-Secret nicht anlegbar. Das release-please-Secret behält seinen
etablierten Namen `RELEASE_PLEASE` (`global-git-conventions`,
`references/automation.md`).
