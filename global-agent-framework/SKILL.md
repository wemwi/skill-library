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
  Sessions, Vault für Agent-Secrets, Permission-Policy, Least-Privilege, Allowlist/
  Denylist, Tool-Oberfläche minimieren, enabled:false vs permission_policy, Agent-
  Version bumpen, Agent debuggen, neuen Agent ins Portfolio aufnehmen. Gilt für jeden
  Managed Agent in diesem Stack.
metadata:
  version: "1.5.0"
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
| `tools` | Toolset-Einträge. Eingebaut via `agent_toolset_20260401` (Bash, File-Ops, Web Search/Fetch). **Jeder** in `mcp_servers` deklarierte Server braucht hier zusätzlich einen eigenen `mcp_toolset`-Eintrag (`mcp_server_name` = Server-`name`), sonst erscheinen seine Tools nicht. Gating je Toolset über `enabled`/`permission_policy` (Abschnitte 5+7). |
| `mcp_servers` | Die MCP-Server *dieses* Agenten — je `{type: url, name, url}` (Abschnitt 5). |
| `skills` | Domänen-Kontext mit Progressive Disclosure (optional, Abschnitt 3). |

Dazu optional `description`, `metadata` (Abschnitt 4) und `callable_agents`
(Research Preview).

**Template (kanonischer Startpunkt).** Die Config wird als YAML geschrieben; die
Console/Platform-API akzeptiert YAML. Zwei Vorlagen liegen unter `assets/`:

- `assets/agent-config.blank.yaml` — kommentiertes Skeleton zum Kopieren. Jedes Feld
  trägt einen Verweis auf den zuständigen Abschnitt; die `mcp_servers`/`mcp_toolset`-
  Verdrahtung ist als auskommentiertes Muster hinterlegt.
- `assets/agent-config.example.yaml` — ausgefüllter `rechnungs-agent` als lebendes
  Vorbild: Drei-Ebenen-`system`, `mcp_servers` als URL-Objekt, ein `mcp_toolset` mit
  Allowlist (`enabled`) und `permission_policy`-Gate auf dem Schreib-Tool, gefülltes
  `metadata`. Referenz zum Abgucken, **nicht** garantiert deploybar — die Beta kann
  Feldnamen und erlaubte Modelle verschieben.

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

**Leitfrage vor jeder Verdrahtung: Hängt die Eigenschaft, die du kontrollieren willst,
am CREDENTIAL/an der VERBINDUNG — oder am einzelnen TOOL-CALL?** Daraus folgt, *wo* die
Grenze sitzt:

- **Am Call** (welches Tool, ob es überhaupt läuft) → in der **Config** lösen:
  `enabled: false` (Tool weg) oder `permission_policy` (Tool gegated, Abschnitt 7). **Ein
  Connector** genügt.
- **Am Credential/an der Verbindung** → **strukturell trennen**: eigener Connector /
  eigenes Deployment / eigenes Credential / eigenes Environment.

Credential-gebundene Eigenschaften sind mehr als nur „darf kommunizieren": Absender-
**Identität**, Berechtigungs-**Scope**, **Blast-Radius** bei Kompromittierung,
**Rotation/Widerruf**, **Audit-Zurechenbarkeit**, **Rate-Limit/Quota**,
**Daten-Mandantentrennung**. Sobald *eine* davon getrennt sein muss, reicht Config nicht —
es braucht zwei Verbindungen.

- **Telegram = Identität** → Sende- und Lese-Bot sind token-gebunden: **zwei Bots, zwei
  Deployments**, nicht ein Bot mit gegateten Tools.
- **Shopify = Scope** → eine Identität genügt, aber Rechte begrenzen über das
  **read-only-Token** (Credential + `enabled`), nicht über zwei Stores.
- **Lexware = read-vs-write-Scope** → hängt am Token: über das **Credential** trennen,
  nicht allein über `enabled`.

Darauf aufbauend die zeitlosen Server-Regeln:

- **MCP pro Agent, nicht global.** In `mcp_servers` nur die Server eintragen, die
  *dieser* Agent wirklich braucht. Ein `rechnungs-agent` bekommt `lexware-mcp` — nicht
  `telegram-mcp`, nicht `shopify-mcp`.
- **Jeder Agent nur seine Teilmenge.** Die Server-Liste ist Teil der
  Least-Privilege-Grenze — zusammen mit Vaults (Abschnitt 6) und Permission-Policy
  (Abschnitt 7).
- **Netzwerk muss an sein.** MCP- und externe Calls brauchen das in der
  Environment-Config aktivierte Netzwerk. **Default ist: aus.**
- **Nicht jeder Job braucht MCP.** Die Sandbox bringt Bash + Python/Node u.a. mit;
  einfache Datei-Arbeit (z.B. PDF umbenennen oder komprimieren) erledigt der Agent direkt
  in der Sandbox, statt dafür einen Custom-MCP zu bauen.

### Tool-Oberfläche minimieren — mit `enabled: false`, nicht mit `permission_policy`

Default für jedes MCP-Toolset ist die **Allowlist**: alles aus, nur das Benötigte an.
`enabled: false` entfernt ein Tool **strukturell** — es ist für den Agenten weder
auffindbar noch aufrufbar (**harte Wand**: „weg", nicht „gegated"). Das ist die saubere
Methode, nicht benötigte oder gefährliche Tools loszuwerden; nebenbei spart es
Kontext-Ballast.

> **Merksatz: Fähigkeit *entfernen* → `enabled: false`. Fähigkeit *gaten* →
> `permission_policy` (Abschnitt 7). Nicht verwechseln.** Eine `always_ask`-Policy lässt
> das Tool im Modell sichtbar und aufrufbar und pausiert nur davor — sie ist **kein**
> Ersatz fürs Entfernen. Wer ein Schreib-Tool gar nicht braucht, gated es nicht, sondern
> nimmt es weg.

- **Allowlist** (Standard): `default_config.enabled: false` + pro Tool `enabled: true`.
  Nur die freigeschalteten Tools erreichen das Modell.
- **Denylist** (Ausnahme): `default_config` weglassen, `enabled: false` nur auf einzelne
  gefährliche Tools.
- **Präzedenz:** per-Tool-`configs` > `default_config` > System-Default.

Mini-Beispiel — von einem schreibmächtigen Server nur die read-only-Abfrage freischalten:

```yaml
# tools[]: Allowlist auf dem MCP-Toolset — alles aus, nur graphql_query an
- type: mcp_toolset
  mcp_server_name: shopify
  default_config:
    enabled: false
  configs:
    - name: graphql_query   # read-only
      enabled: true
```

(Das YAML-Grundgerüst der Agent-Config steht im Template `assets/agent-config.*.yaml` —
hier nur das Least-Privilege-Muster, nicht die ganze Config-Mechanik.)

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

**`enabled` vs. `permission_policy` — die zentrale Unterscheidung.** `enabled: false` ist
die **strukturelle** Grenze (Tool weg, Abschnitt 5). `permission_policy` ist die
**Laufzeit**-Grenze für Tools, die *bleiben*:

| Policy | Verhalten |
|---|---|
| `always_allow` | Tool läuft ohne Rückfrage. |
| `always_ask` | Session pausiert vor **jedem** Aufruf und wartet auf Freigabe. |

**Defaults bewusst kennen — sie sind nicht symmetrisch:**

- **agent_toolset** (`agent_toolset_20260401`) → Default `always_allow`. Bash, Write,
  Edit, web_fetch laufen also **ungefragt**, sobald das Toolset drin ist.
- **mcp_toolset** → Default `always_ask`. Auch neu hinzukommende Tools eines MCP-Servers
  führen so nichts ungefragt aus. Für einen vertrauten read-only-Server auf
  `always_allow` heben; Schreib-Tools auf `always_ask` lassen.

Override pro Toolset über `default_config.permission_policy`, pro Tool über die
`configs`-Liste — gleiche Präzedenz wie bei `enabled` (per-Tool > default > System).

**Daraus die HITL-Praxis:**

- **Default bewusst wählen.** Für **headless** Betrieb (Cron, Webhook) ist `always_allow`
  eine echte Entscheidung, kein Selbstläufer: ohne menschliches Gate führt der Agent jeden
  erlaubten Tool-Call sofort aus.
- **Lesen vs. Schreiben trennen.** Für rein lesende/ableitende Agents ist `always_allow`
  meist okay. **Schreibende oder geldrelevante** Aktionen (Lexware-Rechnung finalisieren,
  Bestellung anlegen, öffentlich posten) brauchen ein Gate.
- **„Erst vorschlagen, dann schreiben".** Sensible Agents zuerst einen **Entwurf** erzeugen
  lassen (Artefakt/Nachricht); der irreversible Schreib-Schritt erfordert eine
  Bestätigung — per `permission_policy` auf den Schreib-Tools oder durch Aufteilen des
  Workflows (Agent liefert Entwurf, Mensch löst den Commit aus). Dieses Verhalten
  zusätzlich im System-Prompt verankern (Abschnitt 3).

### Drei-Schichten-Schutz für schreibmächtige MCPs

Bei einem Server, der schreiben oder Geld bewegen kann, staffelt man drei **unabhängige**
Wände — jede hält für sich, und Schicht 2 hält sogar dann, wenn Config oder Modell
versagen:

1. **`enabled: false`** (Abschnitt 5) → die Schreib-Fähigkeit **existiert nicht** für den
   Agenten. Harte Wand in der Config.
2. **scope-/read-only-Credential im Vault** (Abschnitt 6) → der Server lehnt
   serverseitig ab, selbst bei Fehlverhalten; das Secret sieht die Sandbox nie. Harte Wand
   **unabhängig vom Agentenverhalten** — deshalb die belastbarste Schicht.
3. **`permission_policy: always_ask`** in der Testphase, später `always_allow`, wenn
   vertraut. Weiche Wand, Laufzeit-Gate.

Beispiel Shopify: nur `graphql_query` aktiviert (Schicht 1), read-only-Token im Vault
(Schicht 2), in der Testphase `always_ask` (Schicht 3). Zum Read-only-Agenten wird er
schon durch Schicht 1+2 — Schicht 3 ist die Sicherung beim Einfahren.

**Sonderfall: ein nötiger Write, aber nur ein generisches Mutation-Tool.** Manchmal braucht
der Agent **genau eine** schmale Schreibaktion, der MCP-Server bietet dafür aber nur ein
**generisches** Tool an (z.B. ein `graphql_mutation`, das *jede* Mutation abdeckt, nicht nur
die gewünschte). Dann lässt sich **Schicht 1 nicht halten**: Du musst das generische Tool
`enabled: true` setzen und gewährst damit *alle* Writes, nicht nur den einen. Die tragende
Wand wandert in dem Moment auf **Schicht 2** — der **Credential-Scope** muss aufs Minimum
des tatsächlich nötigen Writes begrenzt werden (server-seitige Ablehnung von allem anderen,
unabhängig vom Agentenverhalten). Besonders brisant, wenn der Agent auf **ungeprüftem
Input** operiert (OCR aus fremd gelieferten Dateien, eingehende Nachrichten): generisches
Write-Tool + weiter Token-Scope + `always_allow` = der Input steuert potenziell *jeden*
erlaubten Write. Sauberste Gegenmaßnahme, wenn du Schicht 1 zurückwillst: ein
**Single-Purpose-Custom-MCP**, das nur die eine Aktion kann — das generische Tool bleibt
aus. Passt in den `*-mcp`-Stack und ist strukturell richtig; Credential-Scope ist der
pragmatische Zwischenschritt.

**Wo `always_ask` tatsächlich freigegeben wird.** Eine `always_ask`-Policy pausiert die
Session im Zustand `requires_action` — *wie* du freigibst, hängt am **Session-Start**:
**interaktiv** gestartet siehst du den Entwurf und bestätigst auf dem Schirm; **per
API/Webhook** gestartet gibt es keinen Schirm → die Freigabe ist ein **API-Call**, der
`requires_action` auflöst (= Job der Webhook-Brücke, Abschnitt 8). Konsequenz: `always_ask`
für einen **headless** Agenten setzt einen Freigeber voraus (Brücke oder manueller
API-Aufruf). Ohne ihn **stallt** die Session am Gate — es erscheint kein Popup. Wer headless
fährt und (noch) keinen API-Freigeber hat, lehnt sich daher auf Schicht 1+2 statt auf
Schicht 3.

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

## 10. Modellwahl

`model` wird bei **jedem** Agent gesetzt — entscheide es bewusst, nicht per Default.
Die Wahl läuft über **vier Achsen**, die sich nicht ändern, wenn Anthropic neue Modelle
bringt:

| Achse | Frage | Richtung |
|---|---|---|
| **Komplexität** | Mehrstufiges Reasoning, Tool-Orchestrierung, Code? | komplex → stärker; schematische Transformation → kleiner reicht |
| **Kosten × Frequenz** | Wie oft feuert der Agent (Abschnitt 8)? | hochfrequent + einfach → klein; selten + komplex → groß vertretbar |
| **Autonomie/Risiko** | Headless `always_allow` mit Schreibrechten (Abschnitt 7)? | kein Mensch liest gegen → eher stärker, trotz Kosten |
| **Latenz** | Wartet ein Auslöser auf Antwort? | Webhook/interaktiv → schnell; Cron nachts → egal |

**Relative Tier-Logik statt absoluter Liste.** Anthropic staffelt Modelle von
„klein/schnell/günstig" bis „groß/fähig/teuer". Mappe die Achsen auf **relative** Tiers,
nicht auf eine festgenagelte Spitze:

- Hochfrequente Cron-Transformation (PDF umbenennen, Zeile ins Sheet) → **kleinstes
  tragfähiges** Tier.
- Standard-Agent mit Tool-Arbeit und Urteilsbedarf → **mittleres** Tier.
- Headless Schreib-/Geld-Agent ohne menschliches Gate → **stärkstes in der Beta
  verfügbares** Tier.

**Keine harten Modell-IDs hier.** Die Tier-Landschaft verschiebt sich aktiv (oberhalb der
bisherigen Spitze sind weitere Ebenen entstanden, Zugang teils eingeschränkt), und
Managed Agents ist Beta — die erlaubte Modell-Teilmenge kann von der normalen API
abweichen. Welche konkrete ID welchem Tier entspricht und welche die Beta zulässt:
**zum Bauzeitpunkt gegen die Console-Doku prüfen,** nicht aus diesem Skill ableiten.

## 11. Environment-Strategie

Das **Environment** ist der Laufzeit-Kontext der Sandbox — **Netzwerk** und **Pakete**. Es
ist **keine Sicherheits-/Isolationsgrenze** zwischen Agenten: Wer was darf, entscheiden
Credential-Scope (Abschnitt 6) und Tool-Config (Abschnitte 5+7), nicht das Environment.
Greife fürs Härten also dorthin, nicht ins Environment.

**Trennen nach Bedarf, nicht zur Isolation.** Environments separiert man nach
**Paket-/Netzbedarf** — zwei Agenten mit denselben Paketen und demselben Netzprofil teilen
sich eins; ein Agent mit Sonderpaketen bekommt ein eigenes. Mehr Environments „zur
Sicherheit" bringen nichts (die Grenze sitzt woanders) und kosten nur Pflege.

**Netzwerk — so eng wie möglich, Default ist aus.** Wähle die engste Stufe, die noch trägt:

- **Limited** statt **Full**, wenn der Agent kein freies Web braucht. **Erlaubte Hosts leer
  lassen** ist das sichere Minimum — jeder Eintrag *weitet* den Egress. Hosts nur eintragen,
  wenn der Agent eine konkrete externe Domain wirklich braucht (z.B. `web_fetch` auf eine
  feste API).
- **MCP-Egress** nur an, wenn der Agent MCP-Server nutzt. **Paketmanager-Egress** nur an,
  wenn Pakete deklariert sind (siehe ungültige Kombi unten).

**Pakete deklarieren + pinnen.** Was der Agent an Bibliotheken/Tools braucht, gehört in die
Environment-Pakete — **nicht** ins Skill, **nicht** in den System-Prompt. **Versionen
pinnen**: reproduzierbarer Build, kein stiller Supply-Chain-Wechsel, kostet keine
Funktionalität. Liste minimal halten, weil der Paketmanager-Egress eine Angriffsfläche ist,
die du bei deklarierten Paketen **nicht** schließen kannst (siehe unten).

**Die ungültige Kombi.** „**Limited + Paketmanager-Egress AUS + deklarierte Pakete**" ist
**ungültig**: Das Provisioning braucht Repo-Egress (PyPI/apt), um die Pakete zu ziehen —
ohne ihn schlägt der Build fehl. Wer Pakete deklariert, **muss** den Paketmanager-Egress
anlassen. Du sparst also keine Sicherheit, indem du ihn abschaltest; der Hebel ist eine
**minimale, gepinnte** Paketliste, nicht „aus".

**Egress-Kopplung durch Tool-Design.** Wenn ein Agent per Tool einen externen HTTP-Aufruf auslöst (z. B. `curl PUT` an eine Upload-URL), entsteht eine Egress-Abhängigkeit, auch wenn der MCP-Server selbst Limited-Egress betreibt. Die URL ist dabei oft dynamisch (Session-spezifisch, host-verifiziert erst zur Laufzeit). Regel: Jeden solchen Host **einmalig per isoliertem Testaufruf** aus der zurückgegebenen URL ablesen und dann build-time in die Allowed-Hosts-Liste des Environments eintragen — nicht raten, nicht hardcoden im Skill. Erst nach dem Eintrag die Kette scharf stellen.

**Beispiel:** `create_upload_session` im google-drive-mcp gibt `uploadUrl` zurück. Der Agent liest den Hostnamen, Betreiber trägt ihn in die Allowed-Hosts ein, dann erst wird der `curl PUT`-Schritt verdrahtet.

**Environment-Naming.** §4 regelt nur Agent-Namen — Umgebungen brauchen ihr eigenes Muster,
weil sie nach Profil **geteilt** werden (oben): Der Name benennt das **Profil**, nie den
Agenten (sonst lügt er, sobald ein zweiter Agent dasselbe Profil mitbenutzt). Muster,
kebab-case, lowercase, keine Version im Namen (Umgebungen sind per ID versioniert):

```
<capability>[-<variante>][-<netz-ausnahme>]
```

- **capability** (Pflicht): der **Zweck** des Paket-/Tool-Profils, nie die Paketliste —
  z.B. `ocr-pdf`, `node-build`, `headless-chrome`; `plain`, wenn keine Sonderpakete.
- **variante** (optional): nur wenn ein Sub-Detail den **Paketsatz selbst** ändert (Locale,
  Runtime-Version, Toolchain-Variante) — z.B. `ocr-pdf-de` vs. `ocr-pdf-en`.
- **netz-ausnahme** (nur die riskante Abweichung): `-open` (Full/Unrestricted), `-offline`
  (kein Netz). **Limited = sicherer Default = stilles Weglassen.** Das Sichere schweigt, das
  Gefährliche wird zum Token.

Was **nicht** in den Namen kommt: Config-Werte und harmlose Toggles. Maßgeblich die
**Egress-Regel** — eine Egress-Achse bekommt nur dann ein Token, wenn ihr „An" die
**Exfil-/Angriffsfläche spürbar weitet**: freies Web ja (`-open`); **MCP-Egress nein**
(harmlose Obermenge — erreicht nur die ohnehin selektiv genutzten MCP-Endpoints, macht einen
Nicht-MCP-Agenten nicht unsicherer); **Paketmanager-Egress nein** (durch „hat Pakete"
impliziert). Auch der Compute-Typ (in der Beta nur Cloud) ist kein Differenzierer. Käme
später eine echte Share-Achse dazu (GPU, Region), wäre *die* ein neuer optionaler Slot — das
Muster bleibt.

Beispiele: `plain` · `plain-offline` · `node-build` · `headless-chrome-open` ·
`ocr-pdf-de` / `ocr-pdf-en` · `data-science`.

**Environment-Metadaten.** Sparsam. **Native Config-Felder nicht spiegeln** (Netz-Typ und
Pakete stehen schon sichtbar in der Console). Bei kleinem Portfolio meist leer lassen. Der
einzige Eintrag mit eigenständigem Wert wäre ein **Reverse-Index** `consumers` (welche
Agenten die Umgebung nutzen — für „wer bricht, wenn ich sie ändere/lösche"); er ist aber
**manuell gepflegt und driftet** — ein veralteter Eintrag führt in die Irre, also nur mit
Pflege-Disziplin, sonst leer lassen und auf die Agent-Seite verlassen (jeder Agent nennt
seine Env-ID). Keine Logik, keine Secrets.

---

## 12. Tool-Datenfluss & Sandbox-Grenze

**Grundregel: Bytes nie durch den Kontext routen.** Der Modell-Kontext ist kein Datenpuffer für binäre oder große Nutzlasten. Alles, was der Agent als Tool-Argument konstruieren muss, zahlt aus seinem Output-Budget — bei binären oder langen Dateien ist dieses Budget erschöpft, bevor der Inhalt vollständig ist.

**Drei Klassen, drei Wege:**

| Klasse | Größenordnung | Weg |
|---|---|---|
| Strukturierte Daten / kurze Texte | < ~10 KB | Direkt als Argument (inline) — kein Problem |
| Mittlere Dateien (Textdokumente, kleine JSONs) | 10–100 KB | Abhängig vom Agenten; kritisch prüfen |
| Binäre oder gescannte PDFs, Bilder, Archivdateien | > ~100 KB | **Referenz-Pfad zwingend**: Tool holt/speichert, Bytes laufen nie durch Kontext |

**Referenz-Pfad — Muster:**
1. **Session holen** — das Tool initiiert eine Upload-Session serverseitig (Credential bleibt auf MCP-Server-Seite), gibt nur eine kurzlebige URL/Referenz zurück.
2. **Bytes direkt transportieren** — Sandbox führt `curl PUT` (oder äquivalent) aus, Bytes fließen direkt zwischen Sandbox und Ziel. Kein Modell-Kontext involviert.

**Tool-Kontrakt vor der Verdrahtung prüfen.** Bevor ein neues Tool in eine Kette eingebaut wird: Welche Argumente konstruiert der Agent? Welche sind binär/groß? Kann das realistische Payload-Volumen als Argument produziert werden? Ein Tool, das Datei-Bytes inline als base64-Argument erwartet, ist für Dateien > ~100 KB in einer Agenten-Kette nicht einsetzbar — das ist ein Architektur-Mismatch, kein Laufzeit-Fehler.

**Fehlerbild, das auf diesen Abschnitt zeigt:** Der Agent produziert ein abgeschnittenes oder leeres Argument, versucht alternative Wege (liest andere Credentials, fragt nach Hilfsmitteln, ruft interne Endpunkte ab), oder bricht in einer Schleife ab — ohne dass ein offensichtlicher Fehler im Fachcode liegt.

## 13. Fail-closed als Default

**Headless Agenten ohne menschliches Gate müssen bei Fehler abbrechen, nicht improvisieren.**

**Warum Improvisation gefährlicher ist als Abbruch:** Ein Agent, der bei einem Tool-Fehler weiterläuft und alternative Wege sucht, kann:
- Credentials anderer Tools lesen (Scope-Überschreitung, selbst wenn unbeabsichtigt)
- Interne Infrastruktur erkunden (Metadata-Endpunkte, LAN-Hosts)
- Einen Post absetzen, obwohl eine vorgelagerte Prüfung fehlschlug
- In einer Wiederholungsschleife externe APIs mit Anfragen fluten

**Regel — Fail-closed-Verhalten ist kein Konfigurationswunsch, sondern Architektur-Default:**
- Jeder Schritt, der eine Voraussetzung für Nachfolgeschritte bildet (Idempotenz-Check, Upload, Daten-Schreiben), ist eine Abbruch-Barriere: schlägt er fehl, folgt kein Nachfolgeschritt.
- **Kein stiller Weiter-Lauf.** Der Fehler wird mit konkretem Kontext ins Status-Topic geschrieben, der Lauf endet.
- **Kein Off-Surface-Verhalten.** Schlägt ein Tool fehl, sucht der Agent keine alternativen Wege, die außerhalb der deklarierten Tool-Oberfläche liegen — der System-Prompt muss das explizit verbieten.

**Im System-Prompt verankern (Formulierungsvorlage):**
```
Wenn ein Tool-Aufruf fehlschlägt oder ein unerwartetes Ergebnis liefert,
brichst du sofort ab und schreibst einen konkreten Fehler-Status ins Topic.
Du suchst keine alternativen Wege außerhalb deiner Tool-Oberfläche.
Du postest nie öffentlich, wenn ein vorgelagerter Schritt nicht erfolgreich war.
```

**Kombination mit §9 (Idempotenz):** Der Dedup-Schlüssel schützt vor Doppel-Ausführung bei Retry — Fail-closed schützt vor Halbzuständen (Post ohne Ablage, Ablage ohne Idempotenz-Eintrag). Beide gemeinsam ergeben eine robuste Kette.

---
Observability-Tiefe, restliches Kostenmodell (Token-Budgets, Caching), Lifecycle-Details,
Anti-Pattern-Katalog.
