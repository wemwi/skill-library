# Secrets

## Übersicht

| Secret | Richtung | Form | Hinweis |
|---|---|---|---|
| `MCP_AUTH_PASSWORD_HASH` | inbound | SHA-256-Hex des Login-Passworts | NICHT Klartext. Ein Passwort für alle Server ist ok. |
| Outbound-Credential (`<AUSSTELLER>_<TYP>`, z.B. `GOOGLE_REFRESH_TOKEN`) | outbound | Klartext (zwingend, wird weitergereicht) | pro Server, beim Server-Aufbau (`buildServer`) gelesen |

## Naming

Zwei Töpfe, klar getrennt.

**Inbound / Framework-eigen → `MCP_`-Prefix, feste Namen.**
`MCP_AUTH_PASSWORD_HASH` ist das Türschloss des Frameworks selbst, kein
Drittanbieter-Credential. Auf jedem Worker gleich, nicht aussteller-basiert.

**Outbound / Drittanbieter-Credential → `<AUSSTELLER>_<TYP>`.**
- `<AUSSTELLER>` = wer das Credential ausstellt / wo es rotiert wird (die Marke, bei
  der man sich einloggt): `GOOGLE`, `LEXWARE`, `TELEGRAM`, `GITHUB` …
- `<TYP>` = die Credential-Art (Tabelle unten).
- **Nicht** den Worker/Service kodieren (kein `GSC_…`): ein Secret ist worker-scoped,
  der Worker ist also schon impliziter Kontext. Was zählt, ist *was* das Credential ist
  und *wo* man es rotiert → Aussteller + Typ. `GOOGLE_REFRESH_TOKEN` gilt damit
  für jeden Google-Worker, der denselben OAuth-Client mit einem eigenen scoped Refresh-
  Token nutzt (je Worker ein Token, je Worker ein Secret).
- Produkt-Qualifier nur zur Auflösung, wenn ein Worker zwei Credentials desselben
  Ausstellers UND Typs hält: `<AUSSTELLER>_<PRODUKT>_<TYP>` (Randfall).

| Typ | Suffix | Beispiel |
|---|---|---|
| API key | `_API_KEY` | `GOOGLE_API_KEY`, `LEXWARE_API_KEY` |
| Dienstkonto (JSON) | `_SERVICE_ACCOUNT_JSON` | `GITHUB_APP_SERVICE_ACCOUNT_JSON` |
| Bot-Token | `_BOT_TOKEN` | `TELEGRAM_BOT_TOKEN` |
| OAuth-Client (3-legged outbound) | `_OAUTH_CLIENT_ID` / `_OAUTH_CLIENT_SECRET` + `_REFRESH_TOKEN` | `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` |
| Personal Access Token | `_TOKEN` | `GITHUB_TOKEN` |
| Basic Auth | `_USERNAME` / `_PASSWORD` | `JTL_USERNAME` |
| Signing-/Webhook-Secret | `_SIGNING_SECRET` / `_WEBHOOK_SECRET` | `TELEGRAM_WEBHOOK_SECRET` |

Konsistenz-Prinzip (gesamtes Framework): **infra-lesbar (Worker, KV, Secret) →
Anbieter/Aussteller rein. Modell-lesbar (Tool) → Anbieter raus.**

## Regeln

- Secrets werden nur im Dashboard bzw. via `wrangler secret` gesetzt — nie im Repo.
- **Inbound-Hash vs. Outbound-Key:** Der Hash darf weitergezeigt werden — eine
  Einbahnstraße, bei einem Leak wertlos. Der Outbound-Key dagegen ist so
  schützenswert wie das Login-Passwort selbst.

## Bezug zu "Authorization failed" nach Consent

Wird das **Outbound-Secret am Worker nicht gesetzt**, wirft `buildServer` beim
Initialisieren — der Fehler erscheint *nach* dem Consent, *vor* den Tools. Secret am
richtigen Worker setzen. Siehe `diagnostics.md`.
