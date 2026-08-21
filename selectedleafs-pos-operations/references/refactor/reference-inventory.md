# Referenz-Inventur — was beim Entschlacken umgehängt werden muss

> **Datiertes Review-Artefakt · Stand 2026-08-21 · verify-live.** Erzeugt aus den Live-Blueprints
> (Make-MCP `scenarios_get`) der drei Kern-Worker. Die „heute"-Spalte zitiert den Blueprint
> **wörtlich** — das ist hier der Zweck, nicht ein gepflegter Fakt. Feld-IDs sind zusätzlich mit
> `Tabelle.Feld` benannt. Wer nach dem Stand-Datum umbaut: **vorher gegenlesen.**
>
> Ergänzt [[refactor/duplication-map]]: die Landkarte sagt **was** extrahiert wird, diese Datei sagt
> **was dabei bricht, wenn man es übersieht.** Auch dieses Dokument baut nichts.

---

## 1 · Warum es diese Datei braucht

Ein Resolver-Aufruf ersetzt drei bis fünf Module. Jede nachgelagerte Stelle zeigt aber per
**Modul-ID** dorthin (`{{34.result.number}}`, `{{7.fldjVBRtbovK3Ky92}}`). Wird eine davon übersehen,
**wirft Make nicht** — der Ausdruck liefert leer. Ergebnis: eine Lieferung ohne Vertriebler, eine
Position mit EK 0. Genau die Fehlerklasse, gegen die der ganze Umbau antritt.

Diese Datei zählt jede dieser Stellen einmal auf.

---

## 2 · Methode

Gezählt werden **funktionale** Referenzen im Blueprint-Baum: alles unter `mapper`, `filter` und
`parameters` eines Modules, plus die strukturelle `parameters.feeder`-Bindung von Aggregatoren.
**Nicht** gezählt: `metadata.restore` und `metadata.expect` — reine Editor-Kosmetik, die beim Import
neu entsteht. Referenzen **innerhalb** eines Blocks sind ausgeschlossen: sie verschwinden mit dem
Block.

Deshalb liegt die Summe hier (**70**) unter der groben Vorabzählung (~88): die hatte
Block-interne Verweise mitgezählt.

| Worker | B5 Positionen | B1 Store | B2/B3 Vertriebler+Konditionen | B8 Archiv | Σ |
|---|---:|---:|---:|---:|---:|
| `[Process] Upload PDF (Delivery)` | 18 | 7 | 7 | **0** | **32** |
| `[Process] Upload PDF (Inventory)` | 6 | 13 | 1 | **0** | **20** |
| `[Process] Invoice (Store)` | 6 | 8 | 4 | — | **18** |

**B8 Archiv hat in beiden Uploadern null ausgehende Referenzen.** Nichts im Szenario liest von den
drei Modulen. Das bestätigt den Schnitt aus der Landkarte auf die härteste Weise: dieser Block kann
herausgelöst werden, ohne dass irgendetwas anderes angefasst wird.

---

## 3 · Drei Kontrakt-Korrekturen (das eigentliche Ergebnis)

Die Inventur widerlegt drei Annahmen aus den Kontrakt-Skizzen der Landkarte. Ohne diese Korrekturen
wäre der erste Resolver unbrauchbar gebaut worden.

### K1 `[Resolve] Positions` — vier Felder fehlen

Die Aggregatoren lesen mehr aus den drei Suchen, als K1 zurückgibt:

| fehlt in K1 | wird gelesen von | Quelle |
|---|---|---|
| `product_type` | Delivery „Bundle rows" — **in einer Filterbedingung**, nicht nur im Mapping | `Produktvarianten.Typ` |
| `product_rec` | Delivery „Bundle rows" | `Produktvarianten.Produkt` (Link) |
| `product_name` | Delivery „Bundle rows" | `Produktvarianten.Name` |
| `stock_target` | Inventory „Bundle rows" | `Bestände.SOLL` |

`product_type` ist der kritische: er steht in einer **Filterbedingung** der Zeilen-Vollständigkeit.
Fehlt er, fällt jede Zeile still durch das Gate — kein Fehler, nur keine Positionen.

### K2 `[Resolve] Store` — ein Feld fehlt, vier sind tot

- **Fehlt:** `model` (`Stores.Modell`). `[Process] Invoice (Store)` filtert in „Umsatz auflösen
  (Gate)" darauf. War in der Landkarte nicht im Output-Kontrakt.
- **Tot:** Delivery „Assign store" berechnet `place_id`, `chat_id`, `district_id` und `shopify_gid` —
  und **kein einziges Modul liest sie**. Die Landkarte hatte den Kontrakt auf „Delivery und
  `[Sync] Inventory to Shopify` lesen dieselben sechs Store-Felder" gestützt; tatsächlich liest
  `[Sync] Inventory to Shopify` sie **selbst aus dem Record**, und Delivery rechnet sie ins Leere.
  Vermutlich ein Rest aus der Zeit, als Delivery die City-Posts selbst gemacht hat.

Der tatsächlich konsumierte Output ist deutlich schmaler: `ok` · `store_id` · `store_number` ·
`store_name` · `model` · `error` · `warning`.

**Nebenbefund zum Aufräumen:** die vier toten Ausgaben in Delivery „Assign store" können unabhängig
vom Refactor weg.

### K3 `[Resolve] Salesperson & Conditions` — schmaler als skizziert

Konsumiert wird nur: `salesperson_ok` · `salesperson_id` · `salesperson_error` · `condition_id` ·
`condition_error` · `date`. Weder `salesperson_name` noch `condition_name` noch `taxation` werden
heute irgendwo gelesen — `taxation` entsteht in Delivery nur als Zwischenschritt im selben Modul.
`provision` / `cost_share` braucht ausschließlich `[Create] New Sales Member` für seine
Onboarding-Meldung.

---

## 4 · Die Durchreich-Frage (entscheidet die Migrationskosten von B5)

Jeder Aggregator mischt **zwei** Sorten Schlüssel:

| Sorte | Delivery „Bundle rows" | Inventory „Bundle rows" | Invoice (Store) „Zeilen bündeln" |
|---|---|---|---|
| **aus den Suchen** (→ Resolver) | `price` `stock` `product` `purchase` `gross_price` `product_rec` `product_name` `product_type` | `price` `stock` `product` `stock_target` | `preis` `bestand` `produkt` |
| **aus der Positionszeile** (Durchreiche) | `pos` `no` `qty` `kg` `grams` | `pos` `no` `actual` `target` | `pos` `nr` `kg` `netto` `stueck` |

Die Schreib-Module lesen **ausschließlich** aus dem Aggregator-Array, mit dessen Schlüsselnamen —
und die sind pro Worker verschieden, in `[Process] Invoice (Store)` sogar deutsch (`preis`,
`bestand`, `produkt`, `stueck`).

Daraus folgen zwei Wege:

**(a) Der Resolver reicht die Zeilenfelder durch.** K1 deklariert die Vereinigung aller
Durchreich-Felder als optional. Dann ändert das Schreib-Modul gar nichts und der Iterator zeigt nur
auf `{{R1.resolved}}`. **Kosten:** der Kontrakt trägt worker-spezifisches Vokabular (`actual`/`target`
gibt es nur beim Bestandsprotokoll, `netto`/`stueck` nur bei der Rechnung) — und beim ersten neuen
Nutzer wächst er wieder.

**(b) Der Resolver gibt nur `pos` + aufgelöste Referenzen zurück, der Aufrufer joint selbst.**
Ein kleines Code-Modul beim Aufrufer verbindet die eigene Zeilenliste mit `resolved[]` über `pos` und
gibt **exakt die Schlüsselnamen aus, die das Schreib-Modul heute schon erwartet**.

**Empfehlung: (b).** Grund ist nicht Eleganz, sondern das fehlende Testbett: bei (b) bleiben
`[10] Create delivery line`, `[19] Create line` und `[82] Umsatzposition anlegen`
**byte-unverändert** — die Module, die tatsächlich in die Geldtabellen schreiben, werden gar nicht
angefasst. Der Preis ist ein Code-Modul je Aufrufer; die Netto-Ersparnis bleibt (Delivery: 5 Module
raus, 2 rein).

---

## 5 · Referenzen im Einzelnen

`R1` = Aufrufmodul `[Resolve] Positions` · `R2` = `[Resolve] Store` ·
`R3` = `[Resolve] Salesperson & Conditions` · `J` = Join-Modul beim Aufrufer (Variante b).

### 5.1 `[Process] Upload PDF (Delivery)` · 6677862

**B5 Positionen** — ersetzt „Resolve product variant" · „Price at service date" · „Find stock" ·
„Bundle stock matches" · „Create or match stock". **Alle 18 Referenzen sitzen in genau einem Modul:**
„Bundle rows". Das Modul entfällt vollständig und wird durch `J` ersetzt.

| Modul | Pfad | heute | wird zu |
|---|---|---|---|
| Bundle rows | `filter[0][0].a` | `{{7.id}}` | entfällt — Gate wandert in `R1.complete` |
| Bundle rows | `filter[0][1].a` | `{{27.id}}` | entfällt |
| Bundle rows | `filter[0][2].a` | `{{30.id}}` | entfällt |
| Bundle rows | `filter[0][3].a` | `{{join(7.fld6i3bS5YerX40fq)}}` · `Produktvarianten.Typ` | entfällt — **muss in `R1` als `product_type` erhalten bleiben** |
| Bundle rows | `filter[1][0..3]` | zweite Bedingungsgruppe, gleiche vier | entfällt |
| Bundle rows | `mapper.price` | `{{27.id}}` | `J.price` ← `R1.resolved[].price_id` |
| Bundle rows | `mapper.stock` | `{{30.id}}` | `J.stock` ← `R1.resolved[].stock_id` |
| Bundle rows | `mapper.product` | `{{7.id}}` | `J.product` ← `R1.resolved[].variant_id` |
| Bundle rows | `mapper.purchase` | `{{if(4.result.kind = "Rückholung"; 29.array[1].fldyfjs6US0Xd8kON; 7.fldjVBRtbovK3Ky92)}}` · `Bestände.Ø EK (netto)` vs. `Produktvarianten.EK (netto)` | `J.purchase` ← `R1.resolved[].purchase_net`, Zweig über `purchase_source` **im Resolver** |
| Bundle rows | `mapper.gross_price` | `{{27.fldrvbwTvTBGatH9M}}` · `Preise.VK (brutto)` | `R1.resolved[].gross_price` |
| Bundle rows | `mapper.product_rec` | `{{7.fld0KMcyfc7pSJupr}}` · `Produktvarianten.Produkt` | `R1.resolved[].product_rec` |
| Bundle rows | `mapper.product_name` | `{{7.fldzdSc2JoqkpRT09}}` · `Produktvarianten.Name` | `R1.resolved[].product_name` |
| Bundle rows | `mapper.product_type` | `{{7.fld6i3bS5YerX40fq}}` · `Produktvarianten.Typ` | `R1.resolved[].product_type` |
| Bundle rows | `mapper.pos/no/qty/kg/grams` | `{{6.*}}` | Durchreiche → `J` (Variante b) |

Der Rückhol-Zweig (`purchase`) ist die Stelle, an der die geplante Rückholung hängt: er ist heute
eine IML-Bedingung im Aggregator und wird zum `purchase_source`-Eingang des Resolvers.

**B1 Store** — ersetzt „Load stores" · „Bundle store candidates" · „Assign store".

| Modul | Pfad | heute | wird zu |
|---|---|---|---|
| Consolidate verdict | `input[5]` | `{{34.result.ok}}` | `{{R2.ok}}` |
| Consolidate verdict | `input[6]` | `{{34.result.error}}` | `{{R2.error}}` |
| Consolidate verdict | `input[7]` | `{{34.result.warning}}` | `{{R2.warning}}` — trägt künftig die **A1-Pflichtwarnung** |
| Find stock | `mapper.formula` | `{{34.result.number}}` | **entfällt**, wenn B5 vorher migriert ist |
| Create or match stock | `record.…` · `Bestände.Store` | `{{34.result.id}}` | **entfällt**, wenn B5 vorher migriert ist |
| Finalize delivery | `record.…` · `Lieferungen.Store` | `{{34.result.id}}` | `{{R2.store_id}}` |
| Trigger inventory push | `data.store_id` | `{{34.result.id}}` | `{{R2.store_id}}` |

**Zwei der sieben verschwinden von selbst, wenn B5 zuerst läuft** — netto bleiben fünf.

**B2/B3 Vertriebler + Konditionen** — ersetzt „Load salesperson" · „Load conditions" ·
„Identity + condition at service date".

| Modul | Pfad | heute | wird zu |
|---|---|---|---|
| Consolidate verdict | `input[8]` | `{{23.result.salesperson_ok}}` | `{{R3.ok}}` |
| Consolidate verdict | `input[9]` | `{{23.result.salesperson_error}}` | `{{R3.salesperson_error}}` |
| Consolidate verdict | `input[10]` | `{{23.result.condition_id}}` | `{{R3.condition_id}}` |
| Consolidate verdict | `input[11]` | `{{23.result.condition_error}}` | `{{R3.condition_error}}` |
| Price at service date | `mapper.formula` | `{{23.result.date}}` | **entfällt** mit B5 — das Leistungsdatum geht dann als `service_date` in `R1` |
| Finalize delivery | `record.…` · `Lieferungen.Konditionen` | `{{23.result.condition_id}}` | `{{R3.condition_id}}` |
| Finalize delivery | `record.…` · `Lieferungen.Vertriebler` | `{{23.result.salesperson_id}}` | `{{R3.salesperson_id}}` |

**Achtung Reihenfolge:** „Price at service date" gehört zu B5, liest aber aus B2/B3. Wird B2/B3
zuerst migriert, muss diese eine Referenz zwischenzeitlich auf `R3.date` zeigen. Migriert man B5
zuerst, entfällt sie ersatzlos. **Also B5 zuerst.**

**B8 Archiv** — ersetzt „Compress archive copy" · „Upload archive copy" ·
„Replace original with archive copy". **Null Referenzen.** Eingänge sind `{{38.data}}` (Download),
`{{4.result.ul}}` (Belegnummer) und `{{100.record_id}}` — alle bleiben stehen.

---

### 5.2 `[Process] Upload PDF (Inventory)` · 6729541

**B1 Store ist hier der große Brocken (13), nicht B5 (6)** — umgekehrt zu Delivery. Grund: das Modul
„Consolidate store resolution" bildet zusätzlich den Dedup-Schlüssel, und der wird sechsmal gelesen.

**B5 Positionen** — ersetzt „Resolve product variant" · „Price at service date" · „Find stock row".
Alle 6 Referenzen in „Bundle rows".

| Modul | Pfad | heute | wird zu |
|---|---|---|---|
| Bundle rows | `filter[0][0].a` / `[0][1].a` | `{{14.id}}` / `{{15.id}}` | entfällt — Gate → `R1.complete` |
| Bundle rows | `mapper.product` | `{{14.id}}` | `R1.resolved[].variant_id` |
| Bundle rows | `mapper.price` | `{{103.id}}` | `R1.resolved[].price_id` |
| Bundle rows | `mapper.stock` | `{{15.id}}` | `R1.resolved[].stock_id` |
| Bundle rows | `mapper.stock_target` | `{{15.fld8OepBzfJSL0xyt}}` · `Bestände.SOLL` | `R1.resolved[].stock_target` — **K1-Korrektur** |

**B1 Store** — ersetzt „Store by customer no." · „Bundle store matches" ·
„Store by commissioner name" · „Bundle name matches" · „Consolidate store resolution".

| Modul | Pfad | heute | wird zu |
|---|---|---|---|
| Dedup: customer no. + date exists? | `mapper.formula` (2×) | `{{37.result.dedupkey}}` | **Dedup-Schlüssel — siehe unten** |
| Consolidate verdict | `input[3]` | `{{37.result.noteText}}` | `{{R2.warning}}` |
| Consolidate verdict | `input[4]` | `{{37.result.errorText}}` | `{{R2.error}}` |
| Consolidate verdict | `input[5]` | `{{37.result.dupText}}` | Aufrufer baut den Text — hängt am Dedup-Schlüssel |
| Consolidate verdict | `input[7]` | `{{37.result.store_id}}` | `{{R2.store_id}}` |
| Store assortment | `filter[0][1].a` | `{{37.result.dedupkey}}` | Dedup-Schlüssel |
| Store assortment | `mapper.formula` | `{{37.result.store_number}}` | `{{R2.store_number}}` |
| Find stock row | `mapper.formula` | `{{37.result.store_number}}` | **entfällt** mit B5 |
| Trigger inventory push | `data.store_id` | `{{37.result.store_id}}` | `{{R2.store_id}}` |
| Compress archive copy | `output_filename` | `{{37.result.dedupkey}}` | Dedup-Schlüssel |
| Upload archive copy | `jsonStringBodyContent` | `{{37.result.dedupkey}}` | Dedup-Schlüssel |
| Replace original with archive copy | `mapper.body` | `{{get(map(24.data.fields.…; "filename"; 37.result.dedupkey + ".pdf"); 1)}}` | Dedup-Schlüssel |

**Der Dedup-Schlüssel ist die Kernfrage dieses Workers.** Er wird **sechsmal** gelesen und heute im
Store-Resolver gebildet (`BSP-<Store-Nr>-<Datum>`). Die Landkarte sagt zu Recht: er gehört
architektonisch nicht dorthin (B1 Punkt 5). Zwei Wege:

- **Sauber:** Aufrufer bildet ihn aus `{{R2.store_number}}` + Belegdatum in einem kleinen Modul.
  Sechs Stellen zeigen dann darauf statt auf den Resolver. Der Schlüssel muss **zeichengleich** zur
  Formel in `Bestandsprüfungen.ID` bleiben — das ist die eigentliche Bruchgefahr, nicht die
  Umverdrahtung.
- **Bequem:** `R2` gibt ihn optional mit zurück. Spart sechs Umhängungen, zieht aber die
  Schichtvermischung in den geteilten Baustein — und `[Process] Upload PDF (Delivery)` bräuchte ihn
  nie.

**Empfehlung: sauber.** Sechs Umhängungen an einer Stelle, die ohnehin angefasst wird, sind billiger
als ein Kontrakt, der für einen von drei Nutzern gebaut ist.

**B2 Vertriebler** — ersetzt „Salesperson by inspector name" · „Bundle inspector matches".
Eine einzige Referenz: `Consolidate verdict` `input[10]` = `{{31.array[1].id}}` → `{{R3.salesperson_id}}`.
Dieser Worker hat **keine** Konditionen-Auflösung (kein Geld) — hier reicht der Vertriebler-Teil von
`R3`, oder ein `mode`, der die Konditionen überspringt.

**B8 Archiv** — null ausgehende Referenzen (die drei Module *lesen* den Dedup-Schlüssel, siehe B1).

---

### 5.3 `[Process] Invoice (Store)` · 6633991

Besonderheit: hier hängen die drei Blöcke **in einer Kette** — Store → Vertriebler → Konditionen.

**B1 Store** — ersetzt „Store (by Lexware ID)". Eingang ist die Lexware-`contactId`, nicht die
Kunden-Nr.

| Modul | Pfad | heute | wird zu |
|---|---|---|---|
| Vertriebler (by Name) | `filter[0][0].a` | `{{7.id}}` | **entfällt** mit B2 |
| Umsatz anlegen | `record.…` · `Umsätze.Store` | `{{7.id}}` | `{{R2.store_id}}` |
| ctx bauen | `input[1]` | `{{7.fld7fbRS1BHvrqJrj}}` · `Stores.Name` | `{{R2.store_name}}` |
| Bestand suchen | `mapper.formula` | `{{7.fldL1YaDEswIZNnNP}}` · `Stores.ID` | **entfällt** mit B5 |
| Push Inventory (→ 6805674) | `data.store_id` | `{{7.id}}` | `{{R2.store_id}}` |
| Umsatz auflösen (Gate) | `filter[0][0].a` | `{{7.fld8C3tgNKcDqBgdP}}` · `Stores.Modell` | `{{R2.model}}` — **K2-Korrektur** |
| Bestandsprüfungen des Stores | `qs[5]` | `{{7.fldL1YaDEswIZNnNP}}` · `Stores.ID` | `{{R2.store_number}}` |
| Positionen der Bestandsprüfungen | `qs[5]` | `{{7.fldL1YaDEswIZNnNP}}` · `Stores.ID` | `{{R2.store_number}}` |

**B2 Vertriebler** — ersetzt „Vertriebler (by Name)".

| Modul | Pfad | heute | wird zu |
|---|---|---|---|
| Umsatz existiert? | `filter[0][0].a` | `{{50.id}}` | `{{R3.salesperson_id}}` |
| Konditionen (Besteuerung + eff-dated) | `mapper.formula` | `{{if(length(ifempty(50.fldF4idsFUiCgAX1A; …)))}}` · `Vertriebler.⚙ Regelbesteuerung ab` | **entfällt** — die Besteuerungs-Ableitung wandert komplett in `R3` |
| Umsatz anlegen | `record.…` · `Umsätze.Vertriebler` | `{{50.id}}` | `{{R3.salesperson_id}}` |

**B3 Konditionen** — ersetzt „Konditionen (Besteuerung + eff-dated)". Eine Referenz:
`Umsatz anlegen` · `Umsätze.Konditionen` = `{{11.id}}` → `{{R3.condition_id}}`.

Weil B2 und B3 in einem Resolver zusammenfallen, lösen sich hier **zwei** Referenzen in Luft auf
(der Filter auf `{{7.id}}` und die IML-Besteuerungsformel). Von den 12 Referenzen der drei Blöcke
bleiben **acht** echte Umhängungen.

**B5 Positionen** — alle 6 Referenzen in „Zeilen bündeln", deutsche Schlüsselnamen
(`preis`/`bestand`/`produkt`) → Variante (b) hält `[82] Umsatzposition anlegen` unverändert.

---

## 6 · Migrationsreihenfolge

Innerhalb **jedes** Workers gilt dieselbe Ordnung, und sie ist nicht beliebig:

**B5 → B8 → B1 → B2/B3**

- **B5 zuerst**, weil es Referenzen aus B1 und B2/B3 mitnimmt: in Delivery fallen dadurch 2 (B1) + 1
  (B2/B3) Umhängungen weg, in Inventory 1, in Invoice (Store) 1. Umgekehrt müsste man sie zweimal
  anfassen.
- **B8 als zweites**, weil es null Referenzen hat — der billigste echte Produktionslauf des neuen
  Mechanismus.
- **B1 vor B2/B3**, weil in `[Process] Invoice (Store)` die Vertriebler-Suche auf den Store filtert.

Über die Worker hinweg bleibt die Reihenfolge der Landkarte:

| # | Worker | Block | echte Umhängungen | warum hier |
|---|---|---|---|---|
| 1 | `[Process] Upload PDF (Inventory)` | B5 | **6** | liest nur, schreibt nichts — billigster Testfall |
| 2 | `[Process] Invoice (Store)` | B5 | 6 | liest nur |
| 3 | `[Process] Upload PDF (Delivery)` | B5 | 18 | schreibt (`upsert` Bestand) + Rückhol-EK |
| 4 | beide Uploader | B8 | 0 | Fehlerpfad üben |
| 5 | alle drei | B1 | 5 · 12 · 6 | erst nach A1-Umsetzung |
| 6 | Delivery, Invoice (Store) | B2/B3 | 6 · 2 | erst nach A5 |

---

## 7 · Was der Umbau nicht anfasst

Bewusst festgehalten, damit es beim Bau nicht doch passiert:

- **Die Schreib-Module in die Geldtabellen** — „Create delivery line", „Create line",
  „Umsatzposition anlegen", „Finalize delivery", „Umsatz anlegen". Bei Variante (b) bleiben ihre
  Mappings byte-gleich; nur die Quelle des Iterators darüber ändert sich.
- **Die Anker-Module** („Create delivery", „Create inventory check") und das Verdikt-Muster (B6).
- **Die Transkriptions-Kette** (B4) — Download, LLM-Aufruf, Validator bleiben, wo sie sind.
- **Die Klingeln** an `[Notify] Telegram` — sie zeigen auf Ereignis-Record-IDs, nicht auf die
  Resolver.
- **`[Notify] Telegram` und `[Sync] Inventory to Shopify`** lesen Store/Vertriebler weiterhin selbst.
  Sie sind trotz Landkarten-Eignung **keine** Migrationskandidaten (Härtung H5 bzw. eigene
  Feldauswahl).

---

## 8 · Restrisiko nach dieser Inventur

Was die Inventur **nicht** abdeckt, ehrlich benannt:

1. **Sie zählt statisch.** Ein Ausdruck, der einen Modulverweis zur Laufzeit zusammensetzt, wäre
   unsichtbar. Im gescannten Bestand ist mir keiner begegnet — Make bietet dafür auch keinen
   üblichen Weg — aber bewiesen ist es nicht.
2. **Reihenfolge-Effekte innerhalb eines Blueprints.** Module laufen in Flow-Reihenfolge; ein
   Resolver-Aufruf muss vor seinem ersten Konsumenten stehen. Das prüft kein Referenzzähler, das
   muss beim Bau je Worker im Designer nachgesehen werden.
3. **`metadata.restore` bewusst ausgeklammert.** Für die Funktion irrelevant, aber `[[tools]]` warnt:
   fehlende `restore`-Objekte lassen den Blueprint-Import Module verwerfen. Ein
   `scenario-service:CallSubscenario` trägt keine Connection und hat in allen 39 Bestands-Vorkommen
   ein schlankes `restore` mit dem Szenario-Label — dieses Muster ist beim Bau zu übernehmen.
4. **Kein Testbett.** Jede Umhängung landet direkt im Geldpfad. Pro Worker gehört der alte Stand als
   Rückfall-Blueprint gesichert, bevor der neue scharf geht.
