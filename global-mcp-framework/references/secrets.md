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

**Outbound / Drittanbieter-Credential → `<AUSSTELLER>_<TYP>`.** Die Namensregel
(Suffix-Tabelle, „ein Credential = ein Name über alle Konsumenten", je Worker ein
Token, Cloudflare-interne Sonderfälle wie `R2_ACCESS_KEY_ID`) ist stack-weit und lebt
im Skill `global-credentials` (`references/secret-names.md`) — hier nicht duplizieren.

Konsistenz-Prinzip (gesamtes Framework): **infra-lesbar (Worker, KV, Secret) →
Anbieter/Aussteller rein. Modell-lesbar (Tool) → Anbieter raus.**

## Regeln

- Ablage, Rechte und Aufräumen der Credentials: Skill `global-credentials`.
- **Inbound-Hash vs. Outbound-Key:** Der Hash darf weitergezeigt werden — eine
  Einbahnstraße, bei einem Leak wertlos. Der Outbound-Key dagegen ist so
  schützenswert wie das Login-Passwort selbst.

## Bezug zu "Authorization failed" nach Consent

Wird das **Outbound-Secret am Worker nicht gesetzt**, wirft `buildServer` beim
Initialisieren — der Fehler erscheint *nach* dem Consent, *vor* den Tools. Secret am
richtigen Worker setzen. Siehe `diagnostics.md`.
