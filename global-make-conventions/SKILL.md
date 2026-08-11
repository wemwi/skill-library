---
name: global-make-conventions
description: >-
  Projektübergreifender Konventionsstandard und Audit-Maßstab für
  Make-Szenarien — Architektur-Grundprinzipien, Architektur-Muster
  (Dispatcher/Worker, native Subscenarios, Router-Fan-out u.a.) und eine
  MUST/SHOULD-Regelliste (Naming, Settings, Modul-Wahl, Trigger,
  Schleifenfreiheit, Webhook-Lebenszyklus, Idempotenz, Fehlerbehandlung,
  Datenlayer, Blueprint-Hygiene). IMMER laden, sobald ein Make-Szenario
  entworfen, gebaut, geprüft oder auditiert wird — auch ohne das Wort Skill.
  Ergänzt make-scenario-building/make-module-configuring (die WIE decken)
  um das WELCHE und dient als Prüfmaßstab für den Gesamt-Audit. Trigger u.a.:
  Szenario-Architektur, Dispatcher-Pattern, Trigger-Wahl, Webhook vs.
  Polling, Schleifenprävention, Watch-Feld, changeTypes, Idempotenz-Gate,
  dedupkey, Error-Handler-Konvention, Blueprint-Hygiene, Szenario-/Modul-
  Naming, native Modul vs. HTTP, Legacy-Modul, Make-Audit.
metadata:
  version: "1.1.0"
---

# global-make-conventions

Projektübergreifender Standard für Make-Szenarien — **kein Tutorial, kein
Modul-Nachschlagewerk**. Dieser Skill bezieht Position, wo Vendor-Docs nur
Tradeoffs auflisten, und macht die Regeln audit-tauglich: jede Vorgabe trägt
eine Severity (**MUST** = Audit-Fail, **SHOULD** = advisory) und einen
falsifizierbaren Check — woran ein Verstoß konkret erkennbar ist.

## Abgrenzung (SSoT pro Ebene)

- **make-scenario-building / make-module-configuring** (offizielle Make-Skills)
  = Bau-Mechanik: welches Modul, wie konfiguriert, Routing/Aggregation/
  Webhooks/IML/Error-Handler-Bedienung. Dieser Skill dupliziert das nie — er
  verweist darauf.
- **`<projekt>-operations-*`** (z.B. `selectedleafs-pos-operations-v2`) =
  Projektspezifisches: konkrete Base-IDs, Feldnamen, Store-Logik. Gehört
  NICHT hierher. Test pro Regel: *Gilt sie für jedes Make-Projekt?* → hierher.
  *Hängt sie an projektspezifischen Werten/Namen/IDs?* → Projekt-Skill.
- **Dieser Skill** = die normative Mitte: generische Architektur-Prinzipien,
  Muster-Wahl und Bau-Konventionen, die über jedes Make-Projekt hinweg gelten.

## Audit-Gebrauch

Beim Gesamt-Audit eines Szenario-Portfolios: erst **Teil A** (Architektur) je
Szenario/Szenario-Gruppe bewerten — passt die Topologie zur Aufgabe? —, dann
**Teil B** (Konventionen) als Checkliste durchgehen. Jeder MUST-Verstoß ist ein
Audit-Fail, jeder SHOULD-Verstoß eine notierte Empfehlung. Coarse-to-fine:
eine korrekt gebaute, aber falsch strukturierte Kette ist trotzdem ein Befund.

---

## Teil A · Grundlagen & Architektur

### A1 — Grundprinzipien

| # | Prinzip | Kurzfassung |
|---|---------|-------------|
| A1.1 | **Ein System-of-Record (SSoT) pro Entität** | Genau ein System schreibt die Wahrheit für ein Datum; alle anderen lesen oder spiegeln. Zwei Systeme, die dieselbe Entität schreiben, pingpongen Daten. |
| A1.2 | **Kanonische Keys statt Ad-hoc-Matching** | Jede Entität hat einen stabilen, eindeutigen Schlüssel, über den gesucht/verlinkt wird — nie Datumsnähe, nie Text-Fuzzy-Matching als Primärmechanik. |
| A1.3 | **Single Responsibility pro Szenario** | Ein Szenario hat eine Aufgabe. Wächst die Verantwortung, wird gesplittet — nicht ein Szenario mit Routern überladen, bis niemand mehr die Verzweigung überblickt. |
| A1.4 | **Kontrakt vor Bau** | Trigger-Payload, erwartete Felder und Fehlerfälle werden spezifiziert, bevor Module verdrahtet werden — nicht am gebauten Szenario abgelesen. |
| A1.5 | **Observability by Design** | Jede Kette ist nachvollziehbar: sprechende Namen, Statuslogging, sichtbare Fehlermeldung — nicht erst beim Debuggen nachgerüstet. |

Rationale, Bruchmuster aus der Praxis und Beispiele: `references/architecture.md`.

### A2 — Architektur-Muster

Muster-Katalog mit Wann/Tradeoff/Bruchmodus, plus die zentrale
Entscheidungsachse **team-intern (Scenarios-App: `Call a scenario`) vs.
Team-/Org-Grenze oder externer öffentlicher Trigger (Webhook)**. Der
sync/async-Modus ist dabei kein Konzept-Wechsel, sondern nur ein Toggle
(„Wait for the scenario to finish") *innerhalb* der Scenarios-App — Details,
Beispiele und die Herleitung: `references/architecture.md`.

Kurzreferenz der Muster: Linear (Trigger→Transform→Action) · Router-Fan-out ·
Batch/Aggregate · Dispatcher/Worker · Orchestrator + native Subscenarios ·
Data-Store-Queue (Producer/Consumer).

---

## Teil B · Bau-Konventionen

Jede Zeile: Regel · Severity · Check. Tiefe je Bereich in der verlinkten
Referenz.

### B1 — Naming & Lesbarkeit (`references/naming.md`)
- **MUST** Szenarien tragen handlungsbasierte, sprechende Namen (`Sync New Gmail Contacts to CRM`, nie eine ID oder ein generischer Platzhalter). Check: Name enthält Aktion + Objekt, nicht nur die App.
- **MUST** Module tragen sprechende Labels statt Default-Namen, sobald ein Szenario mehr als ~5 Module hat. Check: Blueprint-Diff zeigt keine unveränderten Default-Labels an entscheidenden Stellen (Router, Suche, Write).
- **SHOULD** Ordnerstruktur in Make spiegelt Projekt/Teilsystem, nicht Chronologie.

### B2 — Szenario-Settings (`references/settings.md`)
- **MUST** Webhook-getriggerte Szenarien laufen mit Scheduling-Typ `immediately`, nie `indefinitely`.
- **MUST** `Store incomplete executions` ist aktiviert, wo ein Fehler sonst spurlos verschwindet (jedes Szenario mit Write-Seiteneffekten).
- **SHOULD** Sequenzielle vs. parallele Ausführung ist eine bewusste Entscheidung (Datenintegrität bei geteiltem State vs. Durchsatz), nicht der Default.
- **SHOULD** Auto-Deaktivierung nach N Folgefehlern ist konfiguriert, wo ein durchlaufender Fehler sonst unbemerkt Buchungen anhäuft.

### B3 — Modul-Wahl (`references/modules.md`)
- **MUST** natives App-Modul vor generischem HTTP/API-Call — HTTP nur mit dokumentiertem Grund (fehlende native Funktion, z.B. Formatierungs-Parameter, Batch-Read ohne Aggregator). Check: jeder HTTP-Call im Blueprint hat einen Kommentar/eine Doku-Zeile, warum kein natives Modul reicht.
- **MUST** kein Legacy-/Deprecated-Modul im Neubau; bestehende Legacy-Module werden beim nächsten Umbau auf die aktuelle Version migriert, nicht kopiert. Check: `app_modules_list` zeigt für jedes verbaute Modul eine aktuelle, nicht als deprecated markierte Version.
- **MUST** team-interne Datenübergabe zwischen Szenarien läuft über die Scenarios-App (`Scenarios > Call a scenario` + `Start scenario` + `Return output`), nicht über HTTP+Webhook — der native-vor-HTTP-Grundsatz, angewandt auf Szenario-Verkettung. Der sync/async-Modus wird per „Wait for the scenario to finish"-Toggle gewählt, nicht durch die Wahl des Transports (auch entkoppelte, langlebige Worker laufen team-intern über `Call a scenario` im Async-Modus). Check: kein `gateway:CustomWebHook` als Ziel eines team-internen Szenario-zu-Szenario-Aufrufs; Ausnahme nur dokumentiert bei Team-/Org-Grenze oder externem öffentlichem Trigger. Rationale: definierte Inputs/Outputs, kein Credit-Verbrauch, kein öffentlicher Endpunkt.

### B4 — Trigger-Architektur (`references/triggers.md`)
- **MUST** Event-Trigger (Gateway-Webhook, Mailhook, natives App-Event) vor Polling, wo die Quelle es anbietet.
- **MUST** kein Airtable-„Watch Records"-Trigger — Gateway-Webhook auf die Airtable-Automation/den View-Wechsel stattdessen.
- **MUST** kein berechnetes Feld (Formel/Rollup) als Trigger-Cursor — feuert unzuverlässig, ggf. gar nicht bei Anlage.

### B5 — Schleifenfreiheit *(Flaggschiff)* (`references/loops.md`)
- **MUST** ein gelauschtes Watch-Feld ist nie ein Feld, das derselbe Trigger-Pfad nachgelagert zurückschreibt. Check: Diff aus Watch-Feldliste und den vom Szenario geschriebenen Feldern ist leer.
- **MUST** `changeTypes` (bzw. Äquivalent) ist bewusst minimal gesetzt — nur die Events, die wirklich einen neuen Lauf rechtfertigen sollen (typischerweise `add` allein für „reagiert nur auf Neuanlage"). Check: jeder aktivierte changeType ist begründet dokumentiert.
- **MUST** Guards/Schleifenwächter sind eingebaut, wo ein Szenario potenziell sein eigenes Trigger-Signal erzeugen kann.

### B6 — Webhook-Lebenszyklus (`references/webhooks.md`)
- **MUST** eine Spec-Änderung an einem bestehenden Webhook (Felder/changeTypes/Scope) wirkt erst nach Löschen + Neuanlage des Hooks — ein reiner „Refresh" behält die alte Spec. Check: nach jeder Spec-Änderung folgt ein Delete+Recreate-Schritt, nicht nur ein Update-Call.
- **MUST** eine Webhook-URL ist ein Bearer-Credential — nie durch den Chat-/Agent-Kontext holen und zurückspiegeln; die Person holt sie selbst aus der Make-UI oder per eigenem Tool-Call.

### B7 — Idempotenz & Dedup (`references/idempotency.md`)
- **MUST** jeder Trigger, der mehrfach für dasselbe Ereignis feuern kann (Status-Events, Retries, manuelle Replays), hat ein Idempotenz-Gate.
- **MUST** der Idempotenz-Key stammt aus stabilem Geschäftssinn (Event-ID, deterministischer Hash stabiler Felder, natürlicher Schlüssel) — nie aus Execution-ID oder Zeitstempel.
- **MUST** Schreib-Pfade nutzen Lookup-before-Write / Search-then-Create mit striktem Match statt blindem Create.
- **SHOULD** ein dedizierter „bereits verarbeitet"-Verdikt beendet die Route still (kein Write, keine Meldung), statt den Fehlerpfad zu missbrauchen.

### B8 — Fehlerbehandlung & Sichtbarkeit (`references/errors.md`)
- **MUST** kein globales Ignore/Resume ohne Logging — ein grüner Lauf muss heißen, dass die Arbeit tatsächlich passiert ist.
- **MUST** die Error-Handler-Direktive passt zum Modul (Break/Commit/Ignore/Resume/Rollback je nach Kritikalität) — kein pauschales Ignore auf einem Pflicht-Write.
- **MUST** Retry hat einen Cap und Backoff — kein unbegrenzter Retry-Loop.
- **SHOULD** ein DLQ/Incomplete-Executions-Eintrag wird aktiv abgearbeitet — er heilt nicht von selbst.

### B9 — Datenlayer (Airtable) *(gekapselt — nur bei Airtable-Backend relevant)* (`references/data-layer.md`)
- **MUST** Datum als reiner `YYYY-MM-DD`-String, kein `parseDate`, keine implizite Zeitzonen-Umrechnung.
- **MUST** REST-Reads gegen Airtable setzen `cellFormat`, `timeZone`, `userLocale` explizit über die Query-Parameter des HTTP-Moduls (nicht in die URL konkateniert) — sonst liefern Link-Felder inkonsistent Record-IDs oder Klartext.
- **MUST** `typecast: false` als Default bei Writes — `typecast: true` legt unbekannte Select-Optionen still neu an.
- **MUST** nie auf ein Formelfeld schreiben (führt zu 422) — Formelfelder sind reine Lesequellen.
- **MUST** `filterByFormula` bindet an Feldnamen, nicht IDs — jede Feldumbenennung ist potenziell eine Szenario-Änderung; vor jeder Umbenennung wird geprüft, welche Szenarien den alten Namen referenzieren.
- **SHOULD** ein Seitenlimit-Wächter degradiert hart in die Richtung, die keinen falschen Write erzeugen kann (z.B. „unklar" statt eines Treffers bei abgeschnittener Trefferliste).

### B10 — Blueprint- & Deploy-Hygiene (`references/blueprints.md`)
- **MUST** ein Blueprint wird immer als JSON-Datei geliefert/übergeben — nie als inline Text- oder Prosa-Beschreibung.
- **MUST** für ein bestehendes Szenario wird der UI-Export (⋯ → Export Blueprint) angefordert statt eines programmatischen Full-Fetch — kleiner, sauberer, ohne Laufzeit-Rauschen.
- **MUST** Aggregator-Module werden komplett per Blueprint oder komplett im UI bearbeitet — gemischtes Bearbeiten ist mapper-fragil.
- **MUST** nach jedem programmatischen Blueprint-Update werden die Connection-Bindings verifiziert, nicht angenommen — das Verhalten ist inkonsistent (mal bleiben sie gebunden, mal nicht).
- **SHOULD** Blueprint-Bytes laufen nie mehrfach durch einen Chat-/Agent-Kontext (Lesen ≠ wiederholtes Zurückschreiben) — siehe `global-workflow §5` für die Mechanik, hier nur als Prinzip referenziert.

---

## Referenzen — bei Bedarf lesen

- `references/architecture.md` — A1 Grundprinzipien vertieft (Skalierungs-Bruchmuster aus der Praxis) + A2 Muster-Katalog mit Wann/Tradeoff/Bruchmodus, inkl. der Dispatcher/Worker-vs-Subscenario-Entscheidung
- `references/naming.md` — B1 im Detail, Beispiele guter/schlechter Namen
- `references/settings.md` — B2 im Detail
- `references/modules.md` — B3 im Detail, Musterausnahme (Airtable-REST statt nativer Suche)
- `references/triggers.md` — B4 im Detail
- `references/loops.md` — B5 im Detail, dokumentierter Realfall (Phantom-Execution)
- `references/webhooks.md` — B6 im Detail
- `references/idempotency.md` — B7 im Detail
- `references/errors.md` — B8 im Detail
- `references/data-layer.md` — B9 im Detail
- `references/blueprints.md` — B10 im Detail

## Verwandte Skills

- **make-scenario-building** — WELCHE Module, Routing/Branching/Aggregation, Blueprint-Konstruktion
- **make-module-configuring** — WIE ein Modul konfiguriert wird, IML-Ausdrücke, Mapping
- **make-mcp-reference** — MCP-Server-Konfiguration, Scopes, Troubleshooting
- **global-workflow** — Byte-Routing-Prinzip für Blueprints/Skill-Updates (§5)
