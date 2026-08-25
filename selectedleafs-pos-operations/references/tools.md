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
- **Keine Make-Mapping-Klammern in einem Code-Modul** — auch nicht im Kommentar, auch nicht als Beispiel. Make parst das gesamte Codefeld als Template; `{{` + Zahl + `.` wird zur Modulreferenz. Fehlermeldung: `references inaccessible module [module ID 3]`. Trifft jeden Resolver und jedes Konsolidierungs-Modul. Wenn ein Mapping im Kommentar erklärt werden muss: Klammern auseinanderziehen oder in Worten beschreiben.
- **`scenarios_update` verlangt den vollständigen Blueprint als Inline-Parameter** — kein Dateipfad. Für ein reales Szenario sind das 80–150k Zeichen, die durch den Modell-Kontext abgetippt werden müssten; ein Übertragungsfehler landet direkt in Produktion. **Das ist der Grund hinter der Regel oben** („Lieferweg: Import-JSON"). Für kleine Eingriffe ist der Handweg im UI nicht die Notlösung, sondern der sicherste Weg.
- **Große Blueprints landen bei MCP-Überlauf als Datei** statt im Kontext. Sie sind dann gezielt per `jq` befragbar (`.blueprint.flow | .. | objects | select(has("module") and (.id==43))`) — das ist der Normalweg für alles ab ~30 Modulen, nicht der Ausnahmefall. Am Stück lesen ist weder nötig noch sinnvoll.
- **Ein von Hand im UI gespeichertes Modul ist nie byte-gleich zu einem aus dem Fetch.** Der Designer ergänzt beim Speichern `parameters: {}`, `metadata.expect` (Feldschema) und `metadata.restore` (Einklapp-Zustand). Kein Verhalten — aber beim Gegenlesen erwartbar, sonst wird eine saubere Änderung als Abweichung gemeldet.
- **Modulnamen verifizieren** (`app-modules_list` / `app-module_get`) — nie erfinden; ein `scenarios_create` mit unbekanntem Modul schlägt fehl.
- **Native Subszenarien.** Der Aufruf zwischen Szenarien läuft über **`scenario-service:StartSubscenario` / `CallSubscenario`** (nicht mehr über http-„Klingeln"). Der Notify-Hub ist ein `StartSubscenario`-Child (on-demand).
- **`__IMTCONN__` = feste Connection-IDs** je Baustein (Airtable 9136634 · Telegram Operations 9134912 · Sales 9664308 · Broadcast 9307335) — beim Reimport erhalten.
- **Interface-Blank beim Import — Ursache, nicht Zufall.** Der Blueprint aus `scenarios_get` trägt **keinen** top-level `io`-Block (2026-08-22 an 6677862 und 6729541 gemessen: `has("io") == false`). Wird er so importiert, ist das Szenario-Interface danach leer, und die Datenübergabe vom Eltern-Szenario bricht — **stumm**, jeder Lauf grün. Der **UI-Export** trägt `io`; deshalb überlebte der A8-Import am 2026-08-22 Interface *und* Scheduling. Der innere `blueprint.interface` reicht nachweislich **nicht**.
  - **Reimport nur aus dem UI-Export.** Geht das nicht: den `io`-Block vor dem Import aus dem UI-Export übernehmen.
  - **Fällt beides aus:** vorher `scenarios_interface` sichern, nachher `scenarios_set-interface` zurückschreiben. Die Spezifikation steht in der `metadata.interface` des Trigger-Moduls — **nie erfinden**.
  - **Bei winzigen Änderungen gar nicht importieren.** Ein Codefeld oder ein paar `mapper.input`-Zeilen gehören von Hand ins Modul; der Import ist dort reines Risiko ohne Gegenwert.
  - **Abbruchbedingung jedes Import-Skripts:** fehlender oder veränderter `io`-Block.
  - **Diagnose:** ein Kind mit `metadata.interface` am Trigger, aber leerem Szenario-Interface, ist **immer** defekt. Nicht „hat keins", sondern „hat seins verloren". Diese Lesart nicht wegargumentieren — genau das hat am 2026-08-22 zwei Tage Meldungsausfall gekostet.
- **`resolver_version` als Pflichtausgabe.** Jeder Resolver (`[Resolve] Store` 7049889 · `[Resolve] Salesperson & Conditions` 7048609 · `[Resolve] Positions`) gibt `ok` und `resolver_version` zurück. Der **Aufrufer** filtert hart darauf: kommt `resolver_version` leer an, hat das Kind nicht geantwortet — das ist eine Verdrahtungs-, keine Datenlage. Ohne diese Prüfung liest sich der Ausfall als sauberes „nicht gefunden".

## Namen & Werte, an denen Make zeichengenau hängt

`Stores.Name` (Restock-Match) · `Stores.ID`/`Produktvarianten.ID` (Bestands-/SKU-Schlüssel) · alle `Shopify GID` (voll inkl. Präfix) · die Dedup-Formeln `BLG-`/`BSP-`/`BST-` · die Select-Optionen, die Make als String schreibt (`Status`, `Belegtyp`). Ändern = stiller Bruch.
