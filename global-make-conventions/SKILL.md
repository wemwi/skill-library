---
name: global-make-conventions
description: >-
  Projektübergreifender Konventionsstandard und Audit-Maßstab für
  Make-Szenarien — Architektur-Grundprinzipien, Architektur-Muster
  (Dispatcher/Worker, native Subscenarios, Router-Fan-out u.a.) und eine
  MUST/SHOULD-Regelliste (Naming, Settings, Modul-Wahl, Trigger,
  Schleifenfreiheit, Webhook-Lebenszyklus, Idempotenz, Fehlerbehandlung,
  Datenlayer, Variablen/State, Blueprint-Hygiene). IMMER laden, sobald ein Make-Szenario
  entworfen, gebaut, geprüft oder auditiert wird — auch ohne das Wort Skill.
  Ergänzt make-scenario-building/make-module-configuring (die WIE decken)
  um das WELCHE und dient als Prüfmaßstab für den Gesamt-Audit. Trigger u.a.:
  Szenario-Architektur, Dispatcher-Pattern, Trigger-Wahl, Webhook vs.
  Polling, Schleifenprävention, Watch-Feld, changeTypes, Idempotenz-Gate,
  dedupkey, Error-Handler-Konvention, Blueprint-Hygiene, Szenario-/Modul-
  Naming, native Modul vs. HTTP, Legacy-Modul, Set/Get Variables,
  Set Multiple Variables, Variablen-Scope, Scenario- vs. Custom-Variable,
  Data Store, Make-Audit.
metadata:
  version: "1.6.0"
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
- **MUST** Alle Bezeichner sind englisch und projektweit einheitlich — Szenario-Namen, Modul-Labels, Ordner, Variablennamen (die IML-Referenz) und Doku/Kommentare. Check: kein nicht-englischer oder gemischtsprachiger Bezeichner im Blueprint.
- **MUST** Szenarien tragen handlungsbasierte Namen: Verb + Objekt (+ Ziel-App, wenn nicht eindeutig), nie eine ID oder ein generischer Platzhalter (`Sync New Gmail Contacts to CRM`, nicht `Scenario 3`). Check: Name enthält Aktion + Objekt, nicht nur die App.
- **MUST** Modul-Labels tragen nur das Delta zum Default — das Icon (beim Trigger auch die Position) zeigt den Typ bereits, also kein Typ-Wort im Label (kein `Webhook:`/`Watch:`/`Router:`/`Var:`/`Error:`-Präfix). Verb + Objekt ist der Default; Trigger = Event, Router-Zweig = Fall, Filter = Bedingung sind die begründeten Ausnahmen. Je-Typ-Tabelle in der Referenz. Check: kein Typ-Präfix und kein unverändertes Default-Label an den Knoten, die das Delta tragen sollen.
- **MUST** Trigger, Router-Zweige, Write- und Fehlerrouten werden immer gelabelt, unabhängig von der Modulzahl; alle übrigen Module spätestens ab ~5 Modulen im Szenario. Check: Blueprint-Diff zeigt keine unveränderten Default-Labels an diesen Stellen.
- **SHOULD** Ordnerstruktur in Make spiegelt Projekt/Teilsystem, nicht Chronologie.
- **SHOULD** Das führende Verb eines Szenario-Namens darf als `[Rolle]`-Präfix in eckige Klammern gezogen werden, um Szenarien im UI nach Rolle zu gruppieren — aber nur aus einer geschlossenen, **einachsigen** (Rolle, nicht Trigger/Kadenz), projektweit einmal definierten Menge; das Präfix *ersetzt* das Verb, es tritt nicht neben eins (`[Sync] Inventory to Shopify`, nicht `[Scheduled] Sync …`). Ein Präfix wird erst eingeführt, wenn ein Szenario dieser Rolle live existiert; das konkrete Set gehört in den `<projekt>-operations-*`-Skill. Check: kein Präfix-Set mit mehr als einer Achse (ein Trigger-/Kadenz-Präfix wie `[Scheduled]` neben Rollen-Präfixen ist ein Befund), jedes verwendete Präfix ist im Projekt-Skill definiert und hat ≥1 lebendes Mitglied.
- **SHOULD** Die Szenario-Beschreibung (`description`) trägt den Trigger-Kontrakt in einer Zeile — wer/was triggert, welche Inputs, was zurückgegeben wird —, nicht die Wiederholung des Namens. Check: bei `Call a scenario`-Zielen (on-demand) ist die Beschreibung nicht leer, dort ist der Kontrakt die einzige Inline-Doku.

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
- **MUST** Select-Writes setzen den Wert als Options-**ID** (`{ "fld…": { "id": "sel…" } }`), nicht als Options-Namen — `sel…`-IDs sind permanent, ein namensbasierter Write bricht bei Options-Rename still (Airtable zieht Optionen nicht nach). Check: kein Select-Write mit Klartext-Options-Namen als Wert; jeder referenziert eine `sel…`-ID (direkt oder über eine sichtbare Name→ID-Mapping-Quelle).
- **MUST** nie auf ein Formelfeld schreiben (führt zu 422) — Formelfelder sind reine Lesequellen.
- **MUST** `filterByFormula` bindet an Feldnamen, nicht IDs — jede Feldumbenennung ist potenziell eine Szenario-Änderung; vor jeder Umbenennung wird geprüft, welche Szenarien den alten Namen referenzieren.
- **SHOULD** ein Seitenlimit-Wächter degradiert hart in die Richtung, die keinen falschen Write erzeugen kann (z.B. „unklar" statt eines Treffers bei abgeschnittener Trefferliste).
- **SHOULD** namensreferenzierende Prädikate gehören nach *innen* (Airtable-Formelfeld/View, beim Feld-Rename automatisch nachgezogen), nicht als `filterByFormula`-String ins Blueprint. Reihenfolge im Blueprint, oberste greifende Sprosse gewinnt: GET-by-Record-ID → Link-Traversal → View → `RECORD_ID()`-Filter → als letzter Fallback eine eingedämmte namensbasierte `filterByFormula`. Check: kein `filterByFormula`/code-gebauter Filter-String mit Feldnamen, wo eine obere Sprosse greift.

### B10 — Blueprint- & Deploy-Hygiene (`references/blueprints.md`)
- **MUST** ein Blueprint wird immer als JSON-Datei geliefert/übergeben — nie als inline Text- oder Prosa-Beschreibung.
- **MUST** für ein bestehendes Szenario wird der UI-Export (⋯ → Export Blueprint) angefordert statt eines programmatischen Full-Fetch — kleiner, sauberer, ohne Laufzeit-Rauschen.
- **MUST** Aggregator-Module werden komplett per Blueprint oder komplett im UI bearbeitet — gemischtes Bearbeiten ist mapper-fragil.
- **MUST** nach jedem programmatischen Blueprint-Update werden die Connection-Bindings verifiziert, nicht angenommen — das Verhalten ist inkonsistent (mal bleiben sie gebunden, mal nicht).
- **MUST** ein `Start scenario`-Blueprint (Call-a-scenario-Ziel) behält beim Import seinen top-level `io`-Block (`input_spec`/`output_spec`) — das Interface ist eine eigene Szenario-Einstellung, kein Teil des Flows; ein Import ohne den Block wischt es leer. Nie auf `name`/`flow`/`metadata` reduzieren; Felder zusätzlich in `trigger.metadata.interface`. Nur Call-a-scenario-Ziele betroffen, `CustomWebHook` ist immun. Check: importiertes Blueprint hat einen nicht-leeren top-level `io`-Block.
- **MUST** nach jedem `Start scenario`-Import wird das Interface aktiv geprüft (`scenarios_interface`) und bei Leerbefund über `validate_scenario_interface` → `scenarios_set-interface` restauriert — nicht annehmen, es sei durchgekommen. Check: Ziel-Interface listet nach dem Import die erwarteten Felder.
- **SHOULD** Blueprint-Bytes laufen nie mehrfach durch einen Chat-/Agent-Kontext (Lesen ≠ wiederholtes Zurückschreiben) — siehe `global-workflow §5` für die Mechanik, hier nur als Prinzip referenziert.

### B11 — Variablen & State (`references/variables.md`)
- **MUST** ein `Get variable`/`Get multiple variables` liest nur aus einer Set-Quelle, die im selben Ausführungspfad/Cycle tatsächlich vorher lief — ein Get auf eine nicht-nachgelagerte oder nie durchlaufene Set-Quelle liefert still leer. Check: jede Get-Referenz hat eine Set-Quelle auf demselben Pfad/Cycle.
- **MUST** der Variablen-Scope ist bewusst gewählt: `One cycle` für Pro-Bundle-Werte (Default für laufflüchtige Zwischenwerte), `Whole execution` nur für absichtlich über Cycles hinweg getragene/akkumulierte Werte. Check: kein `Whole execution`-Scope auf einem Pro-Datensatz-Wert — der leckt Werte zwischen Bundles.
- **MUST** Scenario-Variablen tragen nur laufflüchtigen State (ein Lauf, ein Szenario). Werte, die über Läufe oder Szenarien hinweg leben müssen, gehören in Custom Variables (Konfiguration/Business-Logik) bzw. einen Data Store (State/Dedup/Cache) — nie in eine Scenario-Variable „gemerkt". Check: keine Scenario-Variable, die Persistenz über das Laufende hinaus annimmt.
- **SHOULD** mehrere Werte an einem Punkt laufen über ein `Set multiple`/`Get multiple` statt einer Kette einzelner `Set variable`/`Get variable` — ein Multiple-Modul ist eine Operation, N Einzelmodule sind N. Ergänzend: Werte, die mehrere Router-Zweige brauchen, werden **vor** dem Router gesetzt und in den Zweigen direkt referenziert, statt sie per `Get variable` über Zweiggrenzen zu holen (spart die Get-Operationen ganz).
- **SHOULD** ein `Set multiple variables` bündelt opake, tief verschachtelte oder fragile Outputs (Code-/AI-Ergebnisobjekte, Array-Index-Zugriffe, Attachment-URLs) als **benannten Kontrakt**, bevor mehrere nachgelagerte Module sie konsumieren — der fragile IML-Ausdruck steht dann an genau einer Stelle statt dupliziert über jeden Consumer.

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
- `references/variables.md` — B11 im Detail, inkl. Picker-Symptomatik, Scope-Mechanik und der Scenario-/Custom-Variable-/Data-Store-Entscheidungsachse

## Verwandte Skills

- **make-scenario-building** — WELCHE Module, Routing/Branching/Aggregation, Blueprint-Konstruktion
- **make-module-configuring** — WIE ein Modul konfiguriert wird, IML-Ausdrücke, Mapping
- **make-mcp-reference** — MCP-Server-Konfiguration, Scopes, Troubleshooting
- **global-workflow** — Byte-Routing-Prinzip für Blueprints/Skill-Updates (§5)
