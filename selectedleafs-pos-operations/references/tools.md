# Werkzeuge & Fallstricke

Projektspezifische Fallen von Airtable-MCP und Make in **dieser** Base/diesem Team. **Generisches** (Modulwahl, Blueprint-Hygiene, Error-Handler-Konvention) steht in **`global-make-conventions`** — hier nur, was in POS-Operations konkret beißt.

## Airtable

- **`list_tables_for_base` vs `get_table_schema`.** Ersteres gibt die **Feldliste** (Name·Typ·`fld…`) — gut für den Feld-Block. **Formel-/Rollup-Strings** liefert nur `get_table_schema` (pro Tabelle). Für jede Formel-Aussage → `get_table_schema`, nie raten.
- **Die Zwei-Lese-Mechanik** (aus `[Notify] Telegram`, gilt überall):
  - `returnFieldsByFieldId=true` → Felder unter `fld…`-Keys; **Link-Felder liefern Record-IDs** (`rec…`), Zahlen/Datum **roh**.
  - `cellFormat=string` (+ `timeZone=Europe/Berlin`, `userLocale`) → Link-Felder als **Klartext**, aber Zahlen/Datum **formatiert** (nicht ISO).
  - Faustregel: **Zahlen/Datum aus der JSON-Lesung, Links aus der Klartext-Lesung.**
- **Link-Feld druckt den Primärwert.** `Stores` hat als Primärfeld die **JTL-Nummer** — ein Link auf Stores liefert im Klartext „10009", nicht den Namen. Deshalb wird `Stores.Name` separat gelesen (der `{Store}`-Fallstrick, [[notify]]).
- **`filterByFormula` nutzt Feld-**Namen** (oder `RECORD_ID()`).** By-ID-Lookup: `RECORD_ID()="rec…"`. Der Dedup-Match läuft `filterByFormula {ID} = dedupkey` gegen ein Formelfeld.
- **EU-Datum.** Datumsfelder stehen auf **`D/M/YYYY`** (european). `cellFormat=string` gibt das **angezeigte** Format, nicht ISO; ISO + Zeitzone kann beim Schreiben auf den **Vortag** kippen. Zeitzone/Locale bewusst setzen.
- **`typecast`.** `create/update_records_for_table` nur mit `typecast:true`, wenn String→Option/Zahl gewandelt werden soll — sonst Default `false` (Integrität).
- **Make-/Formel-Felder & Match-Schlüssel nie anfassen** (Namen, Optionswerte, GID-Präfixe) — Bruchmodi in [[model]].

## Make

- **`scenarios_update` ersetzt den Blueprint komplett** (kein Merge): erst `scenarios_get`, das JSON editieren, das **vollständige** Ergebnis senden. Reine `scheduling`-Änderungen gehen **ohne** Blueprint. Tool-Szenarien (aus `tools_create`) lassen sich damit **nicht** editieren → `tools_update`.
  *Lieferweg in diesem Projekt: Szenario-Änderungen als **Import-JSON** (Blueprint zum Reimport), nicht per `scenarios_update`.*
- **Modulnamen verifizieren** (`app-modules_list` / `app-module_get`) — nie erfinden; ein `scenarios_create` mit unbekanntem Modul schlägt fehl.
- **Native Subszenarien.** Der Aufruf zwischen Szenarien läuft über **`scenario-service:StartSubscenario` / `CallSubscenario`** (nicht mehr über http-„Klingeln"). Der Notify-Hub ist ein `StartSubscenario`-Child (on-demand).
- **`__IMTCONN__` = feste Connection-IDs** je Baustein (Airtable 9136634 · Telegram Operations 9134912 · Sales 9664308 · Broadcast 9307335) — beim Reimport erhalten.
- **Interface-Blank — nicht nur beim Import.** Ein importiertes Subszenario verliert leicht sein Interface (`key/id/ctx`). **Live verifiziert 2026-08-21:** auch **`scenarios_update` leert `blueprint.interface` restlos**, selbst wenn man es im Payload mitschickt. Regel: **nach *jedem* `scenarios_update` das Interface mit `scenarios_set-interface` neu setzen und mit `scenarios_interface` gegenlesen.** Bei einem Notify-Kind kostet ein leeres Interface eine Meldung; bei einem Resolver liefert es **still leere Identitäten** — deshalb tragen die Resolver `ok` + `resolver_version` als Pflicht-Outputs, auf die der Aufrufer hart filtert. **Dasselbe nach jedem Blueprint-Import** — am 2026-08-21 stand `interface.input` an `[Process] Upload PDF (Inventory)` nach dem Import auf `[]`, während das Szenario **aktiv** war; der Dispatcher hätte seine drei Eingaben nicht mehr übergeben können. Beim Wiederherstellen: **leere `help`-Strings weglassen**, die API weist `help: ""` mit „should NOT be shorter than 1 characters" zurück (alte Interfaces tragen sie, neu setzen geht nur ohne).
- **Der Blueprint-Import kippt auch das Scheduling** (2026-08-21 an `[Process] Upload PDF (Inventory)` passiert): `on-demand` wurde zu `immediately, 100/min`. Das ist doppelt bösartig — es ändert das Laufverhalten **und** blockiert die Reparatur: `scenarios_set-interface` weist Pflicht-Eingaben mit „You can only use required inputs with on demand schedule setting" ab. **Reihenfolge nach jedem Import: erst Scheduling mit `scenarios_update` zurücksetzen (ohne Blueprint), dann das Interface setzen** — umgekehrt leert das Update das Interface gleich wieder.
- **Array-Inputs an ein Subszenario funktionieren** (verifiziert 2026-08-21): ein ganzes Array lässt sich als `data.<name>` mappen (`{{2.result.lines}}`), die Item-Schlüssel müssen zur Spec passen. Der Kind-Lauf erscheint in `executions_list` mit `parent`-Block.
- **✅ Der synchrone Subszenario-Aufruf funktioniert — aber das Kind braucht `metadata.expect` an seinem `Return output`.** (Ursache am 2026-08-21 isoliert, Wert-verifiziert.) `scenario-service:ReturnData` liest die zu sendenden Felder **nicht** aus `interface.output` des Szenarios, sondern aus dem eigenen `metadata.expect`. Fehlt der Block, sendet das Kind eine **leere Nutzlast**: der Aufrufer bekommt genau **ein** Bundle, in dem **jedes** Feld `null` ist — auch `executionId`. Der Nachfolger läuft, sieht aber nichts. Der Designer schreibt den Block beim Speichern automatisch; **jedes per API oder Blueprint gebaute Kind muss ihn selbst mitbringen**, Feld für Feld deckungsgleich mit `interface.output` (bei `type: "array"` inklusive `spec`).
  ```
  {"id": 11, "module": "scenario-service:ReturnData", "version": 2,
   "mapper": {"ok": "{{10.result.ok}}", …},
   "metadata": {"designer": {…},
     "expect": [{"name":"ok","type":"boolean","label":"ok","required":true},
                {"name":"resolved","type":"array","label":"resolved","required":true,
                 "spec":[{"name":"pos","type":"number","required":true}, …]}]}}
  ```
- **Rückgabe lesen:** `{{<modul-id>.<output-name>}}`, flach — nicht `.data.`, nicht `.result.`. **Arrays von Objekten kommen als echte Arrays an** (verifiziert: `istArray=true`, Inhalt vollständig, `length()` funktioniert). **`executionId` ist beim wartenden Aufruf `null`** — es ist die Ausgabe der *nicht* wartenden Form und taugt nicht als Lebenszeichen.
- **`shouldWaitForExecutionEnd` gehört in den `mapper`** des Aufrufmoduls (Geschwister von `data`), und das Aufrufmodul braucht die Kind-Outputs in `metadata.interface`. Beides lässt sich gegen Make selbst prüfen:
  `rpc_execute scenario-service@2 GetInputInterface {scenario:"SCN_<id>", teamId:…, withWaitParameter:"true"}` → liefert den Schalter (`default: true`, `editable: false`; **der Flag-Wert muss ein String `"true"` sein**, als Boolean ignoriert der RPC ihn still).
  `rpc_execute scenario-service@2 GetOutputInterface {scenario:"SCN_<id>", teamId:…, shouldWaitForExecutionEnd:true}` → liefert exakt den `metadata.interface`-Block für das Aufrufmodul; **ohne** den Schalter nur `executionId`.
- **⚠️ Falschdiagnose vom 2026-08-21, als Warnung stehengelassen:** aus „Kind-Lauf endet nach dem Eltern-Lauf" wurde geschlossen, `Wait for the scenario to finish` sei in diesem Team wirkungslos. Das war falsch — gewartet wurde immer, die Nutzlast war leer. Die Zeitstempel waren echt, die Schlussfolgerung nicht. **Ein Negativbefund über eine Plattform-Funktion braucht einen Minimalversuch** (Kind mit zwei Modulen, Konstante zurück), bevor er ausgesprochen wird.
- **Modul-Ausgaben sind über den MCP nicht lesbar** (`executions_get-detail` liefert nur den Status). Brauchbare Ersatz-Messtechnik: ein `code:ExecuteCode` hinter dem Aufruf, das bei unerwartetem Wert **wirft** und den Rohwert in die Fehlermeldung schreibt — die Meldung steht dann im `scenarios_run`-Ergebnis. Das ist die einzige Methode hier, die echte Werte zeigt.
  **⚠️ Nicht über die Operations-Zahl schließen.** Ob `CallSubscenario` als Operation zählt, ist ungeklärt — dadurch ist „N Operations" zwischen „Sonde lief" und „Sonde lief nicht, dafür zählte der Aufruf" **nicht unterscheidbar**. Genau diese Mehrdeutigkeit hat am 2026-08-21 zu einer falschen Erfolgsmeldung geführt: aus 2 Operations wurde „das Folgemodul lief und bekam Werte" gelesen, tatsächlich lief es gar nicht. Zeitstempel aus `executions_list` (Eltern-Ende vs. Kind-Ende) sind belastbar, Operations-Zählungen nicht.
- **Array-of-Objects im Szenario-Interface.** Für `type: "array"` mit Objekt-Items muss `spec` eine **flache Feldliste** sein (`"spec": [{name,type,required}, …]`) — **nicht** ein verschachteltes `{type:"collection", spec:[…]}`. Achtung: **`validate_scenario_interface` behauptet das Gegenteil** („Expected type 'object', got type 'array'") und akzeptiert die Form, die die API mit `refVal2 is not defined` ablehnt. **Die API gewinnt**, das Validierungs-Tool ist hier falsch.
- **In einer Positionsschleife nie `airtable:ActionSearchRecords`.** Es erzeugt **pro Treffer** ein Bundle — und bei **null** Treffern **gar keines**. Die Zeile fällt dann still aus der Schleife, landet in keinem „nicht gefunden"-Zweig, und eine Vollständigkeitsprüfung meldet trotzdem „alles da". **`airtable:makeApiCall` liefert immer genau ein Bundle**, auch bei leerer Trefferliste — das ist in einer Schleife die Sicherung gegen eine still verschwundene Position. (Alternative, wenn das Search-Modul bleiben soll: direkt dahinter ein Array-Aggregator auf dieses Modul als Feeder.)

## Namen & Werte, an denen Make zeichengenau hängt

`Stores.Name` (Restock-Match) · `Stores.ID`/`Produktvarianten.ID` (Bestands-/SKU-Schlüssel) · alle `Shopify GID` (voll inkl. Präfix) · die Dedup-Formeln `BLG-`/`BSP-`/`BST-` · die Select-Optionen, die Make als String schreibt (`Status`, `Belegtyp`). Ändern = stiller Bruch.
