---
name: global-credentials
description: >-
  Stack-weite Regeln für Zugangsdaten (API-Tokens, PATs, API-Keys, Secrets) in Worker,
  Web-App, CI und MCP-Server: anlegen, beim Aussteller benennen, Secret-Namen im Code,
  minimale Rechte, Ablage, Aufräumen. IMMER laden, sobald ein Token oder Secret angelegt,
  benannt, gesetzt, rotiert oder gelöscht wird. Trigger: wrangler secret, GitHub-Secret,
  .dev.vars, Env-Variable, Scopes, neuer Worker, Make-Schlüssel, Make-Verbindung.
metadata:
  version: "1.1.0"
---

# global-credentials

Stack-weite Regeln für Zugangsdaten (API-Tokens, Personal Access Tokens, API-Keys,
sonstige Secrets): anlegen, benennen, Rechte, Ablage, aufräumen. Gilt für jede
Anwendung — Worker, Web-App, CI, MCP-Server.

Bewusst **kein Inventar** konkreter Tokens: das wäre volatil. Maßgeblich ist das
Token-Dashboard des jeweiligen Anbieters; dieser Skill regelt nur, wie es dort
aussehen soll.

## Abgrenzung

- `global-mcp-framework` — nur die MCP-eigene Secret-Mechanik
  (`MCP_AUTH_PASSWORD_HASH`, Inbound vs. Outbound, „Authorization failed" nach
  Consent). Secret-Namen und Token-Regeln kommen von hier.
- `global-git-conventions` — Einrichtung von release-please samt Secret
  `RELEASE_PLEASE` (`references/automation.md`); Zuschnitt des Tokens nach Regel 1
  und 4.

## Regeln

### 1. Ein Credential je Anwendung und Zweck

Build, Laufzeit und CI bekommen je ein eigenes Credential, nie zwischen Anwendungen
geteilt. Das gilt ausdrücklich auch für Cloudflare-Workers-Builds: je Worker ein
eigener Build-Token. Grund: Nur so lässt sich ein Token gezielt rotieren oder löschen,
ohne eine fremde Anwendung zu brechen, und „Last used" bleibt einer Anwendung
zuordenbar.

In Make ist die Anwendung die Aufgabe, nicht das einzelne Szenario: Szenarien mit
derselben Aufgabe (z. B. „Rechnungs-PDF an den Beleg hängen") teilen sich ein
Credential, jede andere Aufgabe bekommt ein eigenes.

### 2. Name beim Aussteller: `<Zweck> · <Anwendung>`

| Zweck | Name beim Aussteller |
|---|---|
| Build (Cloudflare Workers Builds) | `Workers Builds · selectedleafs-app` |
| CI (GitHub Actions) | `GitHub Actions · first-commerce-import-dashboard` |
| Laufzeit (Worker liest Airtable) | `Worker · selectedleafs-app · Airtable` |
| Make-Aufgabe (Szenarien schreiben in Airtable) | `make.com · Sync Invoice` |

Ein dritter Teil `· <Ziel>` (das angesprochene System) ist optional, wenn der Zweck
allein nicht eindeutig ist. Wird eine Anwendung umbenannt, die Token-Namen bei allen
Ausstellern mitziehen.

**Name beim Konsumenten:** Liegt ein Credential beim Nutzer unter eigenem Namen
(Make-Schlüssel, Make-Verbindung mit API-Key oder Token), heißt es
`<Aussteller> · <Anwendung>` — spiegelbildlich zum Namen beim Aussteller: vorn steht
jeweils die Gegenseite, der zweite Teil ist auf beiden Seiten gleich.

| Beim Aussteller | Beim Konsumenten |
|---|---|
| Airtable-PAT `make.com · Sync Invoice` | Make-Schlüssel `Airtable · Sync Invoice` |
| Google-API-Key `make.com · Store Places` | Make-Schlüssel `Google · Store Places` |

So zeigt jeder Name, wo das Credential rotiert wird, und das Gegenstück ist per Name
zu finden. Vorn nie die Datenquelle des Ablaufs (`Lexware · …` für einen
Airtable-Token) und nie die eigene Plattform (`make.com · …` in Make); hinten nie der
Produkt- oder API-Name statt der Anwendung (`Google Place (New)`). OAuth-Verbindungen,
die ein Konto autorisieren, fallen nicht darunter.

### 3. Secret-Namen im Code: `<AUSSTELLER>_<TYP>`

- `<AUSSTELLER>` = wo das Credential ausgestellt und rotiert wird; `<TYP>` = die
  Credential-Art. Nie die Anwendung im Secret-Namen — die steht nur im Namen beim
  Aussteller (Regel 2).
- **Ein Credential = ein Name über alle Konsumenten:** jede Anwendung hat ihr eigenes
  Credential (Regel 1), aber denselben Env-Namen. Bestehende Namen zeichengenau
  übernehmen — ein falscher Name ist zur Laufzeit still `undefined`.
- API-Key immer `_API_KEY`; `_TOKEN` nur für Personal Access Tokens.
- Beispiele: Airtable-PAT `AIRTABLE_TOKEN`, Resend `RESEND_API_KEY`, Google-API-Key
  `GOOGLE_API_KEY` (Produkt-Qualifier nur zur Auflösung eines echten Doppels).

Suffix-Tabelle, Sonderfälle (Cloudflare-intern, GitHub-Secrets) und Begründung:
`references/secret-names.md`.

### 4. Minimale Rechte

Nur die betroffene Base, das betroffene Repo, das betroffene Konto. Typische
Mindest-Scopes:

| Credential | Mindestrechte | Ressource |
|---|---|---|
| Airtable-PAT | `data.records:read`, bei Schreibzugriff zusätzlich `data.records:write` | nur die eine Base |
| GitHub fine-grained PAT für release-please | `Contents` + `Pull requests`, je Read and write | nur die Repos der Anwendung |
| Cloudflare-Build-Token (Workers Builds) | Standardrechte von Workers Builds; zusätzlich „Account · D1 · Edit", wenn der Deploy-Befehl D1-Migrationen anwendet | nur das eine Konto |

Workers Builds unterstützt derzeit (Stand 25.10.2026) nur User-Tokens, keine
Account-Tokens.

### 5. Ablage

- Nie im Chat, nie im Repo, nie in Commit-Messages.
- Nur als Secret im Worker (Dashboard oder `wrangler secret put <NAME>`) bzw. als
  GitHub-Repository-Secret.
- `.dev.vars.example` enthält nur Namen, keine Werte.
- Öffentliche Browser-Schlüssel (z. B. Google Maps) sind kein Secret: als Variable
  setzen und beim Aussteller auf die Domain beschränken. Sie stehen ohnehin im
  ausgelieferten Code; Schutz ist die Domain-Beschränkung.

### 6. Aufräumen

- Löschen: Tokens mit „Last used" älter als 90 Tage oder ohne zuordenbare Anwendung.
- Keine Tokens mit Rechten auf „alle Konten", wenn ein Konto reicht.

## Checklisten

**Neue Anwendung**
1. Zwecke festlegen (Build, Laufzeit, CI) — je Zweck ein eigenes Credential.
2. Beim Aussteller anlegen: Name nach Regel 2, Rechte nach Regel 4; Make-Schlüssel
   oder Make-Verbindung mit dem Spiegelnamen (Regel 2).
3. Secret-Namen nach Regel 3; vorhandene Namen anderer Konsumenten übernehmen.
4. Wert direkt als Worker- bzw. Repository-Secret setzen; `.dev.vars.example` nur mit
   Namen.
5. Ersten Build und ersten Lauf prüfen.

**Umbenennung einer Anwendung**
1. Alle Tokens der Anwendung bei jedem Aussteller umbenennen, Spiegelnamen beim
   Konsumenten mit.
2. Secrets am Ziel prüfen — ein unter neuem Namen neu angelegter Worker hat keine.
3. Ersetzte Tokens löschen.

**Rückbau einer Anwendung**
1. Alle Tokens der Anwendung beim Aussteller löschen, nicht nur das Secret.
2. Worker- und Repository-Secrets entfernen.
3. Anbieter-Dashboards gegenprüfen: kein Token mehr mit dem Anwendungsnamen.
