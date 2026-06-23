---
name: global-agent-framework
description: >-
  Build-Time-Framework zum Bauen, Konfigurieren, Deployen und Debuggen von Claude
  Managed Agents (Claude Platform / Anthropic Console) in diesem Stack — Anleitung
  für die Arbeit AM Agenten, kein Skill der einem laufenden Agent angehängt wird.
  IMMER laden, sobald ein Managed Agent erstellt, konfiguriert, verdrahtet, deployed,
  versioniert oder gedebuggt wird — auch wenn das Wort Skill nicht fällt. Trigger u.a.:
  Managed Agent anlegen, Agent-Config (system/tools/mcp_servers/skills), Session
  starten, Scheduled Deployment / Cron-Trigger, Webhook-Brücke zum Starten von
  Sessions, Vault für Agent-Secrets, Permission-Policy, Agent-Version bumpen, Agent
  debuggen, neuen Agent ins Portfolio aufnehmen. Gilt für jeden Managed Agent in
  diesem Stack.
metadata:
  version: "1.0.0"
---

# global-agent-framework

Architektur- und Konfig-Wissen zum **Bauen, Verdrahten, Deployen und Debuggen von
Claude Managed Agents** (Claude Platform / Anthropic Console). Dieser Skill begleitet
die Bau-/Konfig-Arbeit *am* Agenten — analog zu `global-mcp-framework` für MCP-Server.
Er wird **nicht** einem laufenden Agent als dessen Skill angehängt.

**Betrieb ist web-only** — kein lokaler Rechner, kein VPS, kein Terminal. Agent-Config,
Sessions, Scheduled Deployments und Vaults laufen über Console/Platform-API; die
Webhook-Brücke (Abschnitt 8) ist ein Cloudflare Worker auf demselben Stack wie die
MCP-Server.

**Stand:** Managed Agents sind **Beta** (`managed-agents-2026-04-01`). Felder und Limits
können sich ändern — bei Abweichung gewinnt die offizielle Doku, nicht dieser Skill.

**Abgrenzung:** MCP-Server-Mechanik → `global-mcp-framework`. Repo-Doku/SemVer/Release →
`global-git-conventions`. Hier geht es ausschließlich um den Agenten selbst.

## 1. Scope & Trigger

Greift, sobald ein Managed Agent in diesem Stack **erstellt, konfiguriert, verdrahtet,
deployed, versioniert oder gedebuggt** wird — auch ohne das Wort „Skill". Typische
Auslöser: Agent-Config schreiben (`system` / `tools` / `mcp_servers` / `skills`),
Session starten, Scheduled Deployment / Cron einrichten, Webhook-Brücke bauen, Vault
anbinden, Permission-Policy wählen, Agent-Version bumpen, neuen Agent ins Portfolio
aufnehmen.

**Kein Trigger:** die Arbeit *innerhalb* eines Agent-Laufs — die regeln die eigenen
Skills des Agenten plus die User-Message, nicht dieser Skill.

## 2. Agent-Anatomie

**Vier Kernkonzepte** — gemeinsames Vokabular:

| Konzept | Bedeutung |
|---|---|
| **Agent** | Versionierte, wiederverwendbare Config. Per ID referenziert. Update → neue Version. Archive ist terminal. |
| **Environment** | Laufzeit-Kontext der Sandbox (u.a. Netzwerk an/aus). |
| **Session** | Ein konkreter Lauf in einer provisionierten Sandbox. |
| **Events** | Nachrichten in eine Session (v.a. `user.message`). **Kein Event = keine Arbeit.** |

**Fünf Config-Felder** (Kern, gemeinsames Vokabular für die Verdrahtung):

| Feld | Inhalt |
|---|---|
| `name` | Aufruf-/Tracking-ID des Agenten (Abschnitt 4). |
| `model` | Claude 4.5 oder neuer. |
| `system` | Persona / Dauerverhalten (Abschnitt 3). |
| `tools` | Eingebaut: Bash, File-Ops, Web Search/Fetch, MCP. Toolset-Typ `agent_toolset_20260401`. |
| `mcp_servers` | Die MCP-Server *dieses* Agenten (Abschnitt 5). |
| `skills` | Domänen-Kontext mit Progressive Disclosure (optional, Abschnitt 3). |

Dazu optional `description`, `metadata` (Abschnitt 4) und `callable_agents`
(Research Preview).

## 3. Drei-Ebenen-Regel (Herzstück)

Jede Information gehört auf **genau eine** Ebene. Falsche Platzierung macht den Agenten
entweder starr (Lauf-Auftrag im System-Prompt) oder unzuverlässig (Domänenwissen in der
User-Message).

| Ebene | Was hier hingehört | Test |
|---|---|---|
| **System-Prompt** (`system`) | Dauerverhalten, Persona, Leitplanken, Tonfall — gilt in **jedem** Lauf. | „Gilt das für jeden Lauf dieses Agenten?" |
| **Skill** (`skills`) | Wiederverwendbares **Domänenwissen** (Regeln, Formate, Verfahren). Umfangreich, on-demand geladen. | „Gilt das für eine Aufgabenklasse, aber nicht jeden Lauf — und ist es zu groß für den System-Prompt?" |
| **User-Message** (`user.message`) | Der **konkrete Auftrag dieses Laufs** mit seinen Daten. | „Ist das genau die Arbeit von *jetzt*?" |

**Beispiel — ein `rechnungs-agent`:**

- **System:** „Du bist ein sorgfältiger Buchhaltungs-Agent. Du schreibst **nie** ohne
  ausdrückliche Bestätigung in Lexware; du legst zuerst einen Entwurf vor."
- **Skill** (z.B. ein global-Lexware-Skill): Pflichtfelder einer Rechnung, USt-Logik,
  Nummernkreis-Regeln — gilt für *jede* Rechnung, aber nicht für jeden Lauf des Agenten.
- **User-Message:** „Erstelle die Rechnung zu Auftrag #4711, Kunde Müller GmbH, 3 Posten
  laut Anhang."

Faustregel: **Persona → System. Domäne → Skill. Auftrag → User-Message.** Secrets gehören
auf **keine** dieser Ebenen (→ Abschnitt 6).

## 4. Naming & Metadata

**Agent-Name (wemwi-Konvention):** kebab-case, Suffix `-agent`, benennt den
**wiederkehrenden Job**, nicht den einzelnen Lauf — z.B. `rechnungs-agent`,
`pos-manager-agent`, `telegram-poster-agent`. Stabil über Versionen hinweg; die Version
steckt **nie** im Namen. Reiht sich in die Suffix-Familie ein: `*-mcp` / `*-foundation` /
`*-library` / `*-agent`.

**Versionierung:** Jedes Config-Update erzeugt anbieterseitig **automatisch** eine neue
Agent-Version (per ID referenziert, Archive terminal). Spiegle den Stand zusätzlich als
SemVer im `metadata`-Feld und — wenn die Config als Code im Repo liegt — als Commit nach
`global-git-conventions`. So bleibt nachvollziehbar, welche Repo-Version welcher
Agent-Version entspricht.

**`metadata`-Felder fürs Tracking (Vorschlag):** `version` (SemVer-Spiegel), `owner`,
`repo` (Quelle der Config), `domain` / `purpose`, optional `runbook`. Reines Tracking —
keine Secrets, keine Logik.

## 5. MCP-Verdrahtung & Least-Privilege

- **MCP pro Agent, nicht global.** In `mcp_servers` nur die Server eintragen, die
  *dieser* Agent wirklich braucht. Ein `rechnungs-agent` bekommt `lexware-mcp` — nicht
  `telegram-mcp`, nicht `shopify-mcp`.
- **Minimale Tool-Oberfläche.** Auch innerhalb eines Servers die Tool-Menge so klein wie
  möglich halten; jedes zusätzliche Schreib-Tool vergrößert den Schaden bei
  Fehlverhalten.
- **Jeder Agent nur seine Teilmenge.** Die Server-Liste ist Teil der
  Least-Privilege-Grenze — zusammen mit Vaults (Abschnitt 6) und Permission-Policy
  (Abschnitt 7).
- **Netzwerk muss an sein.** MCP- und externe Calls brauchen das in der
  Environment-Config aktivierte Netzwerk. **Default ist: aus.**
- **Nicht jeder Job braucht MCP.** Die Sandbox bringt Bash + Python/Node u.a. mit;
  einfache Datei-Arbeit (z.B. PDF umbenennen oder komprimieren) erledigt der Agent direkt
  in der Sandbox, statt dafür einen Custom-MCP zu bauen.

## 6. Secrets via Vaults

- **Nie hardcoden** — nicht im System-Prompt, nicht im Skill, nicht in der User-Message.
- **Vaults statt Klartext.** Bei der **Session-Erstellung** die passenden `vault_ids`
  übergeben; Anthropic übernimmt den Token-Refresh.
- **Credential-Isolation pro Agent.** Ein Agent erhält nur die `vault_ids`, die er für
  seine Server/Aufgaben braucht — gleiche Logik wie die MCP-Teilmenge. Ein
  `telegram-poster-agent` sieht keine Lexware-Credentials.
- **Konsequenz für Trigger:** Weil `vault_ids` **pro Session** gesetzt werden, müssen
  Scheduler **und** Webhook-Brücke (Abschnitt 8) bei jeder Session die richtigen
  Vault-IDs mitliefern.

## 7. Permission-Policies & Human-in-the-Loop

- **Default bewusst wählen.** `always_allow` ist als Default möglich — für **headless**
  Betrieb (Cron, Webhook) ist das eine echte Entscheidung, kein Selbstläufer: ohne
  menschliches Gate führt der Agent jeden erlaubten Tool-Call sofort aus.
- **Lesen vs. Schreiben trennen.** Für rein lesende/ableitende Agents ist `always_allow`
  meist okay. Für **schreibende oder geldrelevante** Aktionen (Lexware-Rechnung
  finalisieren, Bestellung anlegen, öffentlich posten) braucht es ein Gate.
- **„Erst vorschlagen, dann schreiben".** Sensible Agents so bauen, dass sie zuerst einen
  **Entwurf** erzeugen (Artefakt/Nachricht) und der irreversible Schreib-Schritt eine
  Bestätigung erfordert — entweder per Permission-Policy, die auf Schreib-Tools eine
  Bestätigung verlangt, oder durch Aufteilen des Workflows (Agent liefert Entwurf, Mensch
  löst den Commit aus). Dieses Verhalten zusätzlich im System-Prompt verankern
  (Abschnitt 3).

## 8. Trigger-Muster

Zwei Wege, einen Agent zu starten:

**A) Cron — Scheduled Deployment (einziger eingebauter autonomer Trigger).**

- Cron-Expression **+ IANA-Timezone**, **Minutengranularität**, **Jitter bis 10 s**,
  max. **1000 Deployments/Org**.
- **DST:** Wall-Clock-Matching. Nicht existierende Zeiten (Spring-Forward) feuern
  **nicht**, doppelte (Fall-Back) feuern **zweimal**. Deshalb **01–03 Uhr lokal meiden**
  oder gleich in **UTC** planen.
- **Lifecycle:** pause / unpause / archive. **Manual-Run-Endpoint** zum Testen, ohne auf
  den Zeitplan zu warten.

**B) Webhook-Brücke (für „eingehende Nachricht weckt Agent").**

- Es gibt **keinen** nativen „Message-startet-Agent"-Trigger. Das baut man selbst: ein
  **Cloudflare Worker** nimmt das externe Event entgegen und ruft die **Sessions-API** —
  erst Session **create** (Agent-ID + Environment-ID + `vault_ids`), dann **`user.message`**
  senden.
- Zweistufig denken: **kein Event = keine Arbeit.** Die Brücke liegt auf demselben
  web-only Stack wie die MCP-Server.

**Wahl:** planbar/wiederkehrend → Cron. Ereignisgetrieben/extern angestoßen →
Webhook-Brücke.

## 9. Idempotenz & irreversible Aktionen

Trigger können **doppelt** feuern: Fall-Back-DST (zweimal), Webhook-Redelivery, Retries.
Ohne Schutz heißt das doppelte Rechnung, doppelter Post, doppelte Bestellung.

- **Dedup-Schlüssel für jede Schreib-/Geld-Aktion.** Vor dem Schreiben prüfen, ob der
  Schlüssel schon verarbeitet wurde; nur dann handeln.
- **Schlüssel aus der fachlichen Identität bilden,** nicht aus Zeit/Zufall:
  `rechnungs-agent` → Auftrags-ID; `telegram-poster-agent` → (Channel, Datum, Typ).
- **Reversibles braucht keinen Dedup.** Der Aufwand skaliert mit dem Schaden
  (Blast Radius).
- **Mit Abschnitt 7 kombinieren:** Der Entwurf ist idempotent unkritisch — der Commit
  braucht den Schlüssel.

---

**Geplant für v1.1** (hier bewusst noch nicht ausgeführt): Environment-Strategie im
Detail, Datenresidenz/ZDR, Observability-Tiefe, Kostenmodell, Lifecycle-Details,
Anti-Pattern-Katalog.
