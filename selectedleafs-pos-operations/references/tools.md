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
- **Interface-Blank — nicht nur beim Import.** Ein importiertes Subszenario verliert leicht sein Interface (`key/id/ctx`). **Live verifiziert 2026-08-21:** auch **`scenarios_update` leert `blueprint.interface` restlos**, selbst wenn man es im Payload mitschickt. Regel: **nach *jedem* `scenarios_update` das Interface mit `scenarios_set-interface` neu setzen und mit `scenarios_interface` gegenlesen.** Bei einem Notify-Kind kostet ein leeres Interface eine Meldung; bei einem Resolver liefert es **still leere Identitäten** — deshalb tragen die Resolver `ok` + `resolver_version` als Pflicht-Outputs, auf die der Aufrufer hart filtert.
- **Array-of-Objects im Szenario-Interface.** Für `type: "array"` mit Objekt-Items muss `spec` eine **flache Feldliste** sein (`"spec": [{name,type,required}, …]`) — **nicht** ein verschachteltes `{type:"collection", spec:[…]}`. Achtung: **`validate_scenario_interface` behauptet das Gegenteil** („Expected type 'object', got type 'array'") und akzeptiert die Form, die die API mit `refVal2 is not defined` ablehnt. **Die API gewinnt**, das Validierungs-Tool ist hier falsch.
- **In einer Positionsschleife nie `airtable:ActionSearchRecords`.** Es erzeugt **pro Treffer** ein Bundle — und bei **null** Treffern **gar keines**. Die Zeile fällt dann still aus der Schleife, landet in keinem „nicht gefunden"-Zweig, und eine Vollständigkeitsprüfung meldet trotzdem „alles da". **`airtable:makeApiCall` liefert immer genau ein Bundle**, auch bei leerer Trefferliste — das ist in einer Schleife die Sicherung gegen eine still verschwundene Position. (Alternative, wenn das Search-Modul bleiben soll: direkt dahinter ein Array-Aggregator auf dieses Modul als Feeder.)

## Namen & Werte, an denen Make zeichengenau hängt

`Stores.Name` (Restock-Match) · `Stores.ID`/`Produktvarianten.ID` (Bestands-/SKU-Schlüssel) · alle `Shopify GID` (voll inkl. Präfix) · die Dedup-Formeln `BLG-`/`BSP-`/`BST-` · die Select-Optionen, die Make als String schreibt (`Status`, `Belegtyp`). Ändern = stiller Bruch.
