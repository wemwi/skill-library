# Duplikations-Landkarte — Fundament für den DRY-Resolver-Umbau

> **Datiertes Review-Artefakt · Stand 2026-08-21 · verify-live.** Alle Befunde stammen aus einem
> Vollscan der **17 produktiven Szenarien** in Team **2174024** (eu1), live gelesen per Make-MCP
> `scenarios_list` + `scenarios_get(<id>)`. Formeln und Feld-IDs stehen hier als **Beweismittel für
> eine Divergenz**, nicht als gepflegte Fakten — Zuhause bleibt das Live-Szenario ([[scenarios]])
> bzw. `airtable/<tabelle>.md`. Wer nach dem Stand-Datum daraus baut: **vorher gegenlesen.**
>
> **Dieses Dokument baut nichts.** Es kartiert und empfiehlt einen Schnitt. Bau erst nach Review.
>
> **Schwesterdatei:** [[refactor/reference-inventory]] — jede Stelle, die beim Entschlacken umgehängt
> werden muss (70 Referenzen über die drei Kern-Worker). Sie hat die Kontrakt-Skizzen in §5 an drei
> Stellen korrigiert; die Korrekturen sind hier bereits eingearbeitet.

---

## 1 · Inventur (Scope des Scans)

`scenarios_list(2174024)` liefert **17** produktive Szenarien, alle `isActive`. Diag-Szenarien
existieren im Team nicht mehr (die beiden `[Diag] Lexware …` tauchen nur noch als MCP-Tool-Namen
auf, nicht in der Team-Liste) — es gab also nichts zu ignorieren.

| Szenario | ID | Rolle im Scan |
|---|---|---|
| `[Dispatch] Upload PDF` | 6836167 | Klassifikator · Beleg-Leser |
| `[Dispatch] Lexware Voucher` | 6872775 | Store-/Vertriebler-Auflösung über Lexware-ID |
| `[Process] Upload PDF (Delivery)` | 6677862 | **Kern-Duplikator** (Store · Vertriebler · Konditionen · Positionen) |
| `[Process] Upload PDF (Inventory)` | 6729541 | **Kern-Duplikator** (Store · Vertriebler · Positionen) |
| `[Process] Invoice (Store)` | 6633991 | **Kern-Duplikator** (Store · Vertriebler · Konditionen · Positionen) |
| `[Process] Invoice (Sales)` | 6872651 | bekommt Identitäten fertig vom Dispatcher |
| `[Process] Payment Reminder (Store)` | 6844567 | Dedup · Beleg anlegen · PDF anhängen |
| `[Notify] Telegram` | 6862968 | **bereits geteilter Baustein** — und selbst Nutzer der Store-/Vertriebler-Lesung |
| `[Sync] Inventory to Shopify` | 6805674 | **bereits geteilter Baustein** (3 Aufrufer) · Store-Lesung |
| `[Sync] Shopify Products to Airtable` | 6795533 | keine Kandidaten-Blöcke |
| `[Sync] Shopify Stores from Google Place API` | 6655783 | keine Kandidaten-Blöcke |
| `[Sync] JTL Invoice to Lexware` | 6870495 | keine Kandidaten-Blöcke |
| `[Sync] Lexware Payments` | 6955541 | Dedup-/Match-Muster |
| `[Create] New Store Partner` | 6820980 | Fehler-ctx-Muster (9×) |
| `[Create] New Sales Member` | 6821121 | **Konditionen eff-dated** (dritte Variante) |
| `[Maintain] Airtable Webhooks` | 6830404 | keine Kandidaten-Blöcke |
| `[Maintain] Inventory Check Reminder` | 7001118 | Store-Scan (keine Auflösung) |

Base durchgehend `appiIkOaz1ID1FjfE`, Airtable-Connection durchgehend **9136634**.

**Legende Extraktions-Eignung**
🟢 **sauber extrahierbar** — deckungsgleich, kann so wie es ist herausgezogen werden ·
🟡 **erst angleichen** — gleiche Absicht, divergente Logik; ein geteilter Baustein bräche still einen Nutzer ·
🔴 **szenariospezifisch** — nicht teilen, nur das Muster dokumentieren

---

## 2 · Blöcke

### B1 · Store-Auflösung 🟡 erst angleichen

**Vorkommen**

| Szenario | Module (Designer-Label) | Eingang | Mechanik |
|---|---|---|---|
| `[Process] Upload PDF (Delivery)` | „Load stores" → „Bundle store candidates" → **„Assign store"** | Kunden-Nr. + Store-Name vom Beleg | **alle** Stores laden (`maxRecords 500`), Match in JS |
| `[Process] Upload PDF (Inventory)` | „Store by customer no." → „Bundle store matches" · „Store by commissioner name" → „Bundle name matches" → **„Consolidate store resolution"** | Kunden-Nr. + Kommissionär-Name vom Beleg | **zwei gezielte** Airtable-Suchen, Konsolidierung in JS |
| `[Process] Invoice (Store)` | „Store (by Lexware ID)" | Lexware `contactId` | eine Suche `{Lexware ID} = …` |
| `[Dispatch] Lexware Voucher` | „Store zum Kontakt" | Lexware `contactId` | eine Suche `{Lexware ID} = …` |
| `[Sync] Inventory to Shopify` | „Store lesen (cellFormat=string)" | Record-ID | `makeApiCall`, **sechs** Felder |
| `[Notify] Telegram` | „Store nachlesen · Klartext" | Record-ID / Link | `makeApiCall` |
| `[Maintain] Inventory Check Reminder` | „Aktive Stores – überfällig & fällig-meldbar" | — | Filter-Scan, **keine** Auflösung |

**Deckungsgleich oder divergiert — divergiert, an vier Stellen, davon eine gefährlich:**

1. **Fallback-Semantik (die gefährliche) — ✅ entschieden 2026-08-21.** Kunden-Nr. gelesen, aber
   **kein Store dazu**:
   - Delivery bricht heute **hart** ab — Kommentar im Modul: *„Nummer gelesen, aber kein Store dazu:
     nicht still auf den Namen ausweichen — eine unbekannte Kunden-Nr. ist ein eigener Befund."*
   - Inventory **fällt auf den Namen zurück** und schreibt einen Hinweis.

   **Entscheidung (Joscha): Name-Fallback für beide.** Damit gilt künftig die Inventory-Semantik —
   Inventory bleibt unverändert, **`[Process] Upload PDF (Delivery)` ändert sein Verhalten**: eine
   unbekannte Kunden-Nr. blockt dort nicht mehr, sondern versucht den Namen.

   Zwei Auflagen, damit der neue Zweitweg nicht still wird:
   - Der Fallback erzeugt **immer** eine Warnung, die im Verdikt landet — so wie Inventory es heute
     schon tut („Store über den Namen aufgelöst, Kunden-Nr. … nicht in Stores gefunden"). Der
     Beleg läuft durch, aber die unbekannte Kunden-Nr. bleibt sichtbar.
   - Mehrdeutigkeit bleibt **hart**: >1 Namenstreffer ist ein Fehler, kein Ratespiel — hier gewinnt
     die Delivery-Haltung (siehe Punkt 3).

2. **Namens-Normalisierung — drei verschiedene Formen.** Delivery normalisiert in JS aggressiv
   (Anführungszeichen, Interpunktion, Binde-/Gedankenstriche → Leerzeichen, Mehrfach-Leerzeichen
   kollabiert). Inventory sucht in Airtable per `LOWER({Name}) = LOWER("…")` und quervergleicht in JS
   mit einer **anderen** Funktion (`lean()`, nur `a-z0-9äöüß`). Ein Store „Kiosk – die Ecke" trifft in
   Delivery, in Inventory nicht.

3. **Mehrdeutigkeit.** Delivery: >1 Treffer (Nummer oder Name) → **Fehler**. Inventory: Namenssuche
   mit `maxRecords 2`, >1 → kein Ergebnis + Hinweis; Nummernsuche `maxRecords 1` → eine doppelte
   Kunden-Nr. bliebe **unentdeckt**.

4. **Rückgabe-Umfang.** Delivery liefert zusätzlich `Stores.⚙ Google Place ID`,
   `Stores.⚙ Telegram ID (Stadt)`, `Stores.Stadtteil`, `Stores.⚙ Shopify GID` — Inventory nur
   `id`/`name`/`number`. Delivery und `[Sync] Inventory to Shopify` lesen dabei **exakt dieselben
   sechs Felder** (`Stores.ID`, `.Name`, `.Stadtteil`, `.⚙ Google Place ID`, `.⚙ Shopify GID`,
   `.⚙ Telegram ID (Stadt)`) — das ist der natürliche Output-Kontrakt.

5. **Schichtvermischung.** Inventory bildet den Dedup-Schlüssel `BSP-<Nr>-<Datum>` **im
   Store-Resolver**. Das gehört nicht in die Store-Auflösung (→ B6).

**Abhängigkeiten:** Base `appiIkOaz1ID1FjfE` · Tabelle `Stores` · Felder `Stores.ID` (Primary,
JTL-Nr.), `.Name`, `.Lexware ID`, `.Stadtteil`, `.⚙ Google Place ID`, `.⚙ Shopify GID`,
`.⚙ Telegram ID (Stadt)` · Connection 9136634.

**Eignung:** 🟡 — nach Angleich von (1) und (2) gut extrahierbar. Der Lexware-ID-Weg ist **kein
zweiter Baustein**, sondern ein dritter Eingang desselben.

---

### B2 · Vertriebler-Auflösung 🟡 erst angleichen

**Vorkommen**

| Szenario | Modul | Vergleich |
|---|---|---|
| `[Process] Upload PDF (Delivery)` | „Load salesperson" → **„Identity + condition at service date"** | alle Vertriebler laden, JS-`norm()`, **exakt** |
| `[Process] Upload PDF (Inventory)` | „Salesperson by inspector name" → „Bundle inspector matches" | `LOWER({Name}) = LOWER("…")`, `maxRecords 1` |
| `[Process] Invoice (Store)` | „Vertriebler (by Name)" | `LOWER(TRIM({Name})) = LOWER(TRIM("…"))`, `maxRecords 1` |
| `[Dispatch] Lexware Voucher` | „Vertriebler zum Kontakt" | `{Lexware ID} = contactId` |
| `[Notify] Telegram` | „Vertriebler nachlesen" | Record-ID |
| `[Process] Invoice (Sales)` | — | bekommt `salesmember_id` **fertig** vom Dispatcher |

**Divergiert — drei verschiedene Namensvergleiche für denselben money-kritischen Match:**

- JS-`norm()` (Delivery) — trimmt, kollabiert Mehrfach-Leerzeichen, entfernt Interpunktion.
- `LOWER({Name})` (Inventory) — **kein Trim**, kein Interpunktions-Handling.
- `LOWER(TRIM({Name}))` (Invoice (Store)) — trimmt, sonst nichts.

Ein Vertriebler mit einem Leerzeichen zu viel im Airtable-Namen löst in Delivery und Invoice (Store)
auf, in Inventory nicht. Die Kette ist **Vertriebler → Besteuerung → Kondition → Kostenanteil**; eine
Fehl-Auflösung dreht Geld.

Zweite Divergenz: Delivery blockt bei **0 und >1** Treffern hart und nennt die Kandidaten im
Fehlertext. Inventory und Invoice (Store) laufen auf `maxRecords 1` — **>1 wird still zum ersten
Treffer.**

**Abhängigkeiten:** Tabelle `Vertriebler` · Felder `Vertriebler.Name`, `.⚙ Regelbesteuerung ab`,
`.Lexware ID` · Connection 9136634.

**Eignung:** 🟡 — die Angleichung ist der eigentliche Gewinn, die Extraktion nur ihre Konsequenz.

---

### B3 · Konditionen eff-dated 🟡 erst angleichen

**Vorkommen — drei Implementierungen, drei Semantiken:**

| Szenario | Modul | Besteuerung kommt aus | Versionswahl | Gleichstand `Gültig ab` | Kein Treffer |
|---|---|---|---|---|---|
| `[Process] Upload PDF (Delivery)` | „Load conditions" → **„Identity + condition at service date"** | **abgeleitet**: `Vertriebler.⚙ Regelbesteuerung ab` ≤ Leistungsdatum | JS-Sortierung desc | **blockt** — zwei Versionen ab demselben Datum sind „nicht entscheidbar" | Fehler → Verdikt „Fehlerhaft" |
| `[Process] Invoice (Store)` | „Konditionen (Besteuerung + eff-dated)" | **abgeleitet**, inline in IML aus `⚙ Regelbesteuerung ab` vs. `voucherDate` | Airtable `sort Gültig ab desc`, `maxRecords 1` | **still** — erster Treffer gewinnt | Notify `task.terms_missing` |
| `[Create] New Sales Member` | „Airtable: Konditionen (eff-dated)" | **gelesen**: `Vertriebler.Besteuerung` (Select), Stand *heute* | Airtable `sort Gültig ab desc`, `maxRecords 1` | **still** | `builtin:Resume`, **komplett still** |

**Divergiert, an drei Stellen:**

1. **Datumsvergleich.** Invoice (Store) filtert `{Gültig ab} <= "YYYY-MM-DD"` — ein
   **String-Vergleich gegen ein Datumsfeld**. Create New Sales Member nutzt
   `NOT(IS_AFTER({Gültig ab}, DATETIME_PARSE("…", 'YYYY-MM-DD')))`. Das sind nicht garantiert
   dieselben Prädikate; die Datumsfelder stehen auf **EU-`D/M/YYYY`** ([[tools]]), und genau hier
   sitzt der dokumentierte Vortag-Fallstrick. **Vor der Extraktion auf eine Form bringen.**

2. **Besteuerungs-Quelle.** Delivery und Invoice (Store) leiten die Besteuerung **ereignisdatiert**
   aus `Vertriebler.⚙ Regelbesteuerung ab` ab. Create New Sales Member liest das
   `Besteuerung`-Select — richtig für eine Onboarding-Vorschau („gibt es überhaupt eine passende
   Version?"), **falsch** für jeden rückdatierten Geldvorgang. Beide Wege sind legitim, aber es sind
   **zwei Kontrakte**, nicht einer.

3. **Gleichstand-Guard.** Nur Delivery hat ihn. Zwei Konditions-Versionen mit identischem
   `Gültig ab` sind heute in Invoice (Store) ein **stiller Münzwurf** über Provision und
   Kostenanteil.

**Abhängigkeiten:** Tabelle `Konditionen` · Felder `Konditionen.ID`, `.Gültig ab`, `.Gültig für`,
`.Provision`, `.Kostenanteil` · Tabelle `Vertriebler` (`.⚙ Regelbesteuerung ab`, `.Besteuerung`).

**Eignung:** 🟡 — und zwar mit der **Delivery-Variante als Vorlage**, weil sie als einzige den
Gleichstand behandelt. `[Create] New Sales Member` bleibt ein eigener, nicht-eff-dated Aufruf
(anderer Kontrakt, siehe Kontrakt-Skizze K3).

---

### B4 · Positions-Transkription 🔴 szenariospezifisch

**Vorkommen**

| Szenario | Module | Vendor / Modell | Form |
|---|---|---|---|
| `[Dispatch] Upload PDF` | „Fetch document PDF" → „Read document type + date" → „Verdict: check type + date" | Claude Haiku 4.5, `temperature 0`, JSON-Schema | nur Kopf (Belegart + Datum) |
| `[Process] Upload PDF (Delivery)` | „Download document" → „Read protocol (positions + header)" → „Validator" | Claude Haiku 4.5, `max_tokens 4000` | **ein** Call für Kopf **und** Positionen |
| `[Process] Upload PDF (Inventory)` | „Download document" → „Read header" (Claude Sonnet 5) → „Upload document to Gemini" → „Transcribe positions" (Gemini 3.1 Pro) → „Cross-check + booking decision" → „Re-read disputed cells" → „Reconcile second read" | **zwei** Vendoren | zwei Pässe + Zweitlesung strittiger Zellen |
| `[Process] Invoice (Store)` | „extract_voucher_positions" | `mcp-client:CallTool` | gar kein LLM-Leser — MCP-Tool gegen Lexware |

**Deckungsgleich? Nein — nur die *Form* wiederholt sich**, nicht der Inhalt: Download → Leser mit
JSON-Schema → Validator → Verdikt. Die Prompts sind je Belegart aufgebaut (Handschrift-Erkennung,
Strich-vs-Null, Spalten-Vorlauf beim Bestandsprotokoll; Vorzeichen aus der Belegart beim
Übergabe-/Rückholprotokoll). Ein geteilter Leser müsste alle Prompts tragen und per Schalter wählen —
das ist keine Extraktion, das ist eine Sammelstelle.

**Eignung:** 🔴 — nicht teilen. Ein geteilter *Kopf*-Leser für Delivery + Inventory wäre denkbar,
kostet Delivery aber einen **zweiten** LLM-Call (dort steckt der Kopf im selben Aufruf wie die
Positionen). Nicht empfohlen.

---

### B5 · Produkt / Preis / Bestand je Position 🟢 sauber extrahierbar

**Der stärkste Kandidat des ganzen Scans.** Dreimal derselbe Dreiklang, in einer Positionsschleife:

| Schritt | `[Process] Upload PDF (Delivery)` | `[Process] Upload PDF (Inventory)` | `[Process] Invoice (Store)` |
|---|---|---|---|
| Variante | „Resolve product variant" | „Resolve product variant" | „Produktvariante auflösen" |
| Preis | „Price at service date" | „Price at service date" | „Preis am Leistungsdatum" |
| Bestand | „Find stock" | „Find stock row" | „Bestand suchen" |

**Deckungsgleich** — bis auf Mapping-Referenzen und Modul-Labels sind die Mapper identisch:

- Variante: `{ID} = "<SKU>"` auf `Produktvarianten`, `maxRecords 1`, `useColumnId true`.
- Preis: `AND(ARRAYJOIN({Produkt}) = "<SKU>", NOT(IS_AFTER({Gültig ab}, DATETIME_PARSE("<Datum>", 'YYYY-MM-DD'))))`,
  Sortierung `Gültig ab` desc, `maxRecords 1` — in allen drei Szenarien **zeichengleich**.
  (Nebenbefund: das ist die *saubere* Datumsform — dieselben drei Szenarien, die hier korrekt
  vergleichen, vergleichen bei den Konditionen in B3 uneinheitlich.)
- Bestand: `{ID} = "BST-<Store-Nr>-<SKU>"`, `maxRecords 1`.

**Zwei bewusste Abweichungen — als Schalter erhalten, nicht wegvereinheitlichen:**

1. **Nur Delivery legt fehlende Bestandszeilen an** („Bundle stock matches" → „Create or match stock",
   `airtable:upsertRecord`). Inventory und Invoice (Store) lesen nur. Das ist richtig so: nur eine
   Lieferung darf ein Sortiment eröffnen. → Kontrakt-Flag `create_missing_stock`.
2. **Nur Delivery liest `Bestände.Ø EK (netto)`** — und nur im Rückhol-Zweig: der Einkaufswert kommt
   bei einer **Rückholung** aus dem Durchschnitts-EK des Bestands, bei einer **Übergabe** aus
   `Produktvarianten.⚙ EK (netto)`. Genau dieser Zweig ist das, was die geplante Rückholung braucht.
   → Kontrakt-Flag `purchase_source`.

**Abhängigkeiten:** `Produktvarianten.ID`, `.⚙ EK (netto)` · `Preise.Produkt`, `.Gültig ab` ·
`Bestände.ID`, `.Ø EK (netto)`, `.Produktvariante`, `.Store` · Connection 9136634.

**Eignung:** 🟢 — kein Angleich nötig, nur zwei Flags. Erster Baustein.

---

### B6 · Beleg-Verdikt / Dedup-Muster 🔴 szenariospezifisch (Muster dokumentieren)

**Das Muster (Anchor-first), sichtbar in beiden Upload-Workern:**
Ereigniszeile mit Status „In Bearbeitung" **anlegen** → auflösen → Dedup suchen → „Consolidate
verdict" (JS) → Verdikt zurückschreiben. Der Anker existiert, bevor irgendetwas schiefgehen kann —
ein gescheiterter Lauf hinterlässt eine sichtbare Zeile statt Stille.

**Vorkommen und Schlüssel**

| Szenario | Dedup-Modul | Schlüssel |
|---|---|---|
| `[Process] Upload PDF (Delivery)` | „Dedup: document number exists?" | `Lieferungen.ID = <Belegnummer>` |
| `[Process] Upload PDF (Inventory)` | „Dedup: customer no. + date exists?" | `Bestandsprüfungen.ID = BSP-<Nr>-<Datum>` **+ `RECORD_ID() != <eigener Anker>`** |
| `[Process] Invoice (Store)` | „Umsatz existiert?" | `Umsätze.ID = <voucherNumber>` |
| `[Process] Invoice (Sales)` | „Auszahlung schon da?" | `Auszahlungen.⚙ Lexware ID = <resource_id>` |
| `[Process] Payment Reminder (Store)` | „Dublette suchen" | `AND(Belege.Belegtyp, Belege.Datum, Belege.Umsatz)` |
| `[Sync] Lexware Payments` | „Umsatz suchen (by ID)" / „Auszahlung suchen (by Lexware ID)" | dito |

**Divergenz:** nur Inventory schließt den **eigenen Anker** aus der Dedup-Suche aus. Delivery kommt
heute ohne aus, weil der Anker noch keine Belegnummer trägt und deshalb nicht in die
Formel-ID-Suche fällt — das ist ein **impliziter** Schutz, kein expliziter. Wenn `Lieferungen.ID`
je zu einer Formel wird, die früher greift, bricht Delivery still an dieser Stelle.

**Eignung:** 🔴 — Tabelle, Feld-Map und Statuswerte sind je Ereignistyp verschieden; ein geteilter
Baustein wäre eine Konfigurations-Wolke. **Aber:** den Anker-Ausschluss in Delivery nachziehen und
das Muster in [[operations]] als verbindliche Form festschreiben.

---

### B7 · Notify-Klingeln 🟢 bereits extrahiert

**39** `scenario-service:CallSubscenario`-Aufrufe insgesamt, **36** davon an `[Notify] Telegram`
(6862968), 3 an `[Sync] Inventory to Shopify` (6805674). Nutzlast durchgehend
`data.{ key, id?, ctx? }`.

**Deckungsgleich** bis auf zwei Kleinigkeiten:

- Der `onerror`-Zweig ist mal `builtin:Resume` („Klingel-Fehler übergehen"), mal `builtin:Ignore`
  („Meldung darf ausfallen") — gleiche Absicht, zwei Formen.
- Mehrere Aufrufe tragen im `restore`-Label noch den alten Namen „[Dispatch] Telegram
  Notifications". Kosmetisch, aber irreführend beim Lesen.

**Eignung:** 🟢 — der Hub **ist** der geteilte Baustein, hier ist nichts mehr zu extrahieren. Nur
angleichen. Bemerkenswert: `[Notify] Telegram` liest Store und Vertriebler selbst nach („Store
nachlesen · Klartext", „Vertriebler nachlesen") — der Hub wird damit **Nutzer** von B1/B2, nicht nur
deren Nachbar.

---

### B8 · Archiv-Kopie des Belegs 🟢 sauber extrahierbar *(nicht im Auftrag — gefunden)*

**Vorkommen:** `[Process] Upload PDF (Delivery)` („Compress archive copy" → „Upload archive copy" →
„Replace original with archive copy") und `[Process] Upload PDF (Inventory)` („Compress archive
copy" → „Upload archive copy" → „Replace original with archive copy").

**Deckungsgleich** — `ilovepdf:compressPdf` (`compression_level: recommended`, `try_pdf_repair: true`)
→ `http:MakeRequest POST content.airtable.com/…/<record>/…/uploadAttachment` → `PATCH Belege/<record>`
mit der neuen Attachment-ID. Unterschiede: **Zeilenenden** im Body-Template (CRLF vs. LF) und die
Quelle des Dateinamens (Belegnummer vs. Dedup-Schlüssel). Sonst zeichengleich.

**Abhängigkeiten:** `Belege.Beleg` (Anhangfeld) · Keychain-API-Key 204951 · ilovepdf-Connection.

**Eignung:** 🟢 — klein, klar begrenzt, **kein Geld daran**. Damit der ideale zweite Baustein: er übt
den Fehlerpfad (der Block darf ausfallen, ohne den Lauf zu kippen), ohne etwas zu riskieren.

---

### B9 · PDF an einen Beleg hängen 🟡 erst angleichen *(nicht im Auftrag — gefunden)*

**Vorkommen:** `[Process] Invoice (Sales)` („PDF an Beleg hängen") · `[Process] Payment Reminder
(Store)` („PDF an den Beleg haengen") · `[Process] Invoice (Store)` („Airtable: Beleg anhängen") ·
plus die beiden Archiv-Uploads aus B8. Alle gegen dasselbe Feld `Belege.Beleg` über
`content.airtable.com`.

**Divergiert** in der Fehlerhaltung: `stopOnHttpError` mal `true` mal `false`, `parseResponse`
uneinheitlich, `timeout` mal 60 s mal Default. Payment Reminder wertet das Ergebnis aus und meldet
„Beleg angelegt, PDF fehlt" — die anderen hängen ein `builtin:Ignore` dran und schweigen.

**Eignung:** 🟡 — die *Fehlerhaltung* angleichen (Payment Reminder ist die richtige: Datensatz nie
zurückrollen, aber sagen, dass das PDF fehlt). Danach ist es ein **Zwei-Modul-Muster**, kein
Subszenario wert — es sei denn, es wird mit B8 zusammen geschnitten.

---

### B10 · Fehler-ctx + `error.*`-Klingel + Break 🟡 erst angleichen *(nicht im Auftrag — gefunden)*

**Vorkommen:** `[Create] New Store Partner` (9× „Fehler-ctx bauen") · `[Sync] Inventory to Shopify`
(5×) · `[Sync] Shopify Products to Airtable` · `[Sync] Shopify Stores from Google Place API` ·
`[Create] New Sales Member`.

**Teilweise deckungsgleich:** In `[Create] New Store Partner` sind **6 der 9** Module
**byte-identisch** — sie nehmen die Stufe als `input.stufe`. Die anderen 3 (an GATE 1/2/3) und die
5 in `[Sync] Inventory to Shopify` unterscheiden sich **ausschließlich** im hartcodierten
Stufen-Literal.

**Eignung:** 🟡 — die abweichenden auf die parametrisierte Form ziehen (`Stufe` als Input). Danach
ist es ein Ein-Modul-Muster; **kein** Subszenario. Aufwand klein, Wirkung: 8 Module weniger, die bei
einer Textänderung einzeln angefasst werden müssten.

---

## 3 · Querschnitt-Befunde (gelten über alle Blöcke)

Drei Befunde, die kein einzelner Block trägt, die aber den Umbau bestimmen:

1. **Die Synchron-Mechanik ist im ganzen Team noch nie benutzt worden.** Alle **39**
   Subszenario-Aufrufe laufen mit `shouldWaitForExecutionEnd: false`. Es gibt **kein einziges**
   `Return outputs`-Modul, und **alle** Szenario-Interfaces haben `output: []`. Der Resolver-Layer
   setzt genau den Mechanismus voraus, für den es hier noch keinen einzigen Präzedenzfall gibt.

2. **Ein Baustein-Präzedenzfall existiert trotzdem:** `[Sync] Inventory to Shopify` wird von
   Delivery, Inventory und Invoice (Store) aufgerufen — aber fire-and-forget, ohne Rückgabe. Er zeigt,
   dass der Fan-in organisatorisch funktioniert, nicht, dass die Rückgabe funktioniert.

3. **Zwei Datumsvergleichsformen koexistieren in derselben Base.** Die Preis-Auflösung (B5) nutzt
   dreimal identisch `NOT(IS_AFTER(…, DATETIME_PARSE(…)))`; die Konditionen-Auflösung (B3) nutzt
   einmal genau das und einmal einen String-Vergleich. Für eine Base, deren Datumsfelder auf
   EU-`D/M/YYYY` stehen, ist das eine offene Flanke — unabhängig vom Refactor.

---

## 4 · Schnitt-Empfehlung (priorisiert)

### Stufe 0 — Beweis der Mechanik (vor jeder Extraktion, wegwerfbar)

Ein Wegwerf-Paar aus Dummy-Resolver (**Start scenario** `scenario-service:StartSubscenario` →
konstante Werte → **Return output** `scenario-service:ReturnData`) und Dummy-Aufrufer
(**Call a scenario** `scenario-service:CallSubscenario` mit *„Wait for the scenario to finish"* =
**true**). Die Output-Felder kommen dabei aus dem am Szenario deklarierten `interface.output` — das
`Return output`-Modul mappt nur hinein. Das Feature ist im Tarif frei (Org-Lizenz `scenarioIO: true`),
es ist hier schlicht nie benutzt worden. Zu beweisen sind genau vier Dinge:

1. Das Output-Interface kommt als Bundle beim Aufrufer an.
2. Es **überlebt einen Blueprint-Import** — [[tools]] warnt ausdrücklich vor „Interface-Blank beim
   Import"; bei einem Notify-Kind kostet das eine Meldung, bei einem Resolver liefert es **still
   leere Identitäten**.
3. Ein Fehler im Kind erreicht das Elternteil auf einem Weg, den der Aufrufer filtern kann.
4. Ein Aufruf **innerhalb eines Iterators** verhält sich pro Bundle wie erwartet.

Ohne Stufe 0 ist alles Weitere Spekulation. Sie kostet einen Nachmittag und kann komplett verworfen
werden.

### Stufe 1 — `[Resolve] Positions` (aus B5) — ✅ **gebaut 2026-08-21**

**Szenario 7039710**, Ordner `Resolver` (382196), on-demand, aktiv. Kontrakt K1 wie unten, Testlauf
gegen echte Daten verifiziert (Store 10031 · SKU `10004-002` aufgelöst, unbekannte SKU sauber in
`unresolved[]`, `complete = false`). Nächster Schritt ist der erste Aufrufer, nicht ein weiterer
Baustein.

Erster echter Baustein: dreimal deckungsgleich, kein Angleich nötig, nur zwei Flags. Schreibt nichts
außer der optionalen Bestandszeile. **Als Batch-Resolver bauen** (Array rein, Array raus, Schleife im
Kind) — nicht pro Zeile, siehe Engpass unten.
Migrationsreihenfolge der Nutzer: Inventory (liest nur) → Invoice (Store) (liest nur) → Delivery
(schreibt und braucht den Rückhol-EK).

### Stufe 2 — `[Archive] Document PDF` (aus B8, optional mit B9)

Zwei Nutzer, byte-gleich, kein Geld. Der Baustein, an dem der **Fehlerpfad** geübt wird: er darf
ausfallen, ohne den Lauf zu kippen — genau die Eigenschaft, die die späteren Resolver *nicht* haben.

### Stufe 3 — `[Resolve] Store` (aus B1)

Fünf potenzielle Nutzer (Delivery, Inventory, Invoice (Store), `[Sync] Inventory to Shopify`,
`[Notify] Telegram`) plus die Rückholung als sechsten. **Erst nach den Angleichungen A1 und A2.**

### Stufe 4 — `[Resolve] Salesperson & Conditions` (aus B2 + B3)

Zuletzt, weil hier das Geld hängt und weil drei Namensvergleiche und zwei Datumsvergleiche zuerst auf
je eine Form müssen (A3–A5).
**Ehrliche Einschränkung:** heute hat dieser Baustein nur **zwei** echte Nutzer im Geldpfad (Delivery,
Invoice (Store)) — `[Create] New Sales Member` ist ein anderer Kontrakt (K3). Bei zwei Nutzern wäre
ein Subszenario grenzwertig; er lohnt, **weil die Rückholung der dritte wird**. Kommt die Rückholung
nicht, ist die Angleichung (A3–A5) trotzdem der Gewinn und die Extraktion verzichtbar.

### Vor der Extraktion anzugleichen

| # | Was | Betrifft | Entscheidung nötig? |
|---|---|---|---|
| **A1** | Store-Fallback bei unbekannter Kunden-Nr. | B1 | ✅ **entschieden 2026-08-21: Name-Fallback für beide**, mit Pflicht-Warnung im Verdikt · Delivery ändert Verhalten |
| **A2** | Eine Namens-Normalisierung für `Stores.Name` | B1 | nein (Delivery-`norm()` übernehmen) |
| **A3** | Ein Namensvergleich für `Vertriebler.Name` + hartes Verhalten bei 0/>1 | B2 | nein (Delivery übernehmen) |
| **A4** | Ein Datumsvergleich für `Konditionen.Gültig ab` + Gleichstand-Guard | B3 | nein (Delivery/`IS_AFTER` übernehmen) |
| **A5** | Besteuerung: Datum vs. Select | B3 | ✅ **entschieden 2026-08-21: `⚙ Regelbesteuerung ab` ist alleinige Maschinenwahrheit**, das Select ist Eingang/Anzeige · Regel steht in [[airtable/vertriebler]] |
| **A6** | Klingel-`onerror`: `Resume` **oder** `Ignore`, nicht beides | B7 | nein |
| **A7** | Fehler-ctx: `Stufe` überall als Input | B10 | nein |
| **A8** | Anker-Ausschluss (`RECORD_ID() != …`) auch in Delivery | B6 | nein |
| **A9** | `[Create] New Sales Member`: Modul „Airtable: Konditionen (eff-dated)" referenziert `{{3.result.heute}}` — **das Feld gibt Modul 3 gar nicht zurück**. Das Datumsprädikat läuft leer; gezogen wird faktisch nur „neueste Version mit passender Besteuerung". Heute zufällig richtig (Onboarding-Vorschau), in einem Geldpfad ein Fehler. | B3 | nein — mit Stufe 4 fixen |

A2–A4 und A6–A8 sind **eigenständig nützlich**: sie beheben stille Divergenzen, auch wenn nie ein
Resolver gebaut wird. Sie sind der risikoarme Teil und können vor Stufe 1 laufen.

---

## 5 · Kontrakt-Skizzen (Skizze, kein Blueprint)

### K1 · `[Resolve] Positions`

```
IN   lines[]        : { sku, qty, pos }        — Positionszeilen, roh
     store_number   : Stores.ID (JTL-Nr.)      — für den BST-Schlüssel
     service_date   : YYYY-MM-DD               — Leistungsdatum, nie now()
     store_record_id: rec…                     — nur bei create_missing_stock
     create_missing_stock : bool               — nur [Process] Upload PDF (Delivery)
     purchase_source: "variant" | "stock_avg"  — Übergabe vs. Rückholung

OUT  ok             : bool                     — Pflichtfeld, siehe Härtung H2
     resolver_version : text                   — Pflichtfeld, siehe Härtung H2
     resolved[]      : { pos, sku,
                         variant_id, price_id, stock_id,
                         purchase_net,          — aus Variante oder Ø EK
                         gross_price,           — Preise.VK (brutto)
                         product_rec,           — Produktvarianten.Produkt (Link)
                         product_name,          — Produktvarianten.Name
                         product_type,          — Produktvarianten.Typ  ⚠ steht in einer
                                                  Filterbedingung, nicht nur im Mapping
                         stock_target }         — Bestände.SOLL
     unresolved[]    : { pos, sku, reason }
     complete        : bool                    — alle Zeilen aufgelöst
```

Wichtig: **ein** Aufruf je Beleg, nicht je Zeile. Der Aufrufer entscheidet weiterhin selbst, was er
bei `complete = false` tut (Delivery markiert „Fehlerhaft", Inventory bucht Teilmengen).

Die vier zusätzlichen Felder stammen aus [[refactor/reference-inventory]] §3 — ohne sie lassen sich
Delivery und Inventory nicht migrieren. **Die Durchreich-Felder der Positionszeile** (`qty`, `kg`,
`grams`, `actual`, `target`, `netto`, `stueck`) gehören **nicht** in den Kontrakt: der Aufrufer joint
seine eigene Zeilenliste über `pos` mit `resolved[]`. Damit bleiben die Module, die in die
Geldtabellen schreiben, byte-unverändert — Begründung in [[refactor/reference-inventory]] §4.

### K2 · `[Resolve] Store`

```
IN   (genau einer der drei Eingänge)
     record_id      : rec…                     — [Sync] Inventory to Shopify, [Notify] Telegram
     lexware_id     : text                     — [Dispatch] Lexware Voucher, [Process] Invoice (Store)
     customer_no    : text  + name_hint : text — die beiden Upload-Worker
                                                 (A1: Nummer zuerst, dann Name — kein Schalter)

OUT  ok, resolver_version
     store_id       : rec…
     store_number   : Stores.ID
     store_name     : Stores.Name
     model          : Stores.Modell            — Gate in [Process] Invoice (Store)
     via            : "number" | "name" | "lexware" | "record"
     warning        : text                     — blockt nicht; bei via="name" nach erfolgloser
                                                 Nummer PFLICHT (A1-Auflage)
     error          : text                     — 0 Treffer, oder >1 Namenstreffer (hart)
```

Der Dedup-Schlüssel (`BSP-…`) gehört **nicht** hierher — er bleibt beim Aufrufer (Entflechtung aus B1
Punkt 5). Er wird in `[Process] Upload PDF (Inventory)` sechsmal gelesen; die Umhängung ist in
[[refactor/reference-inventory]] §5.2 aufgeschlüsselt.

Gegenüber der ersten Skizze **korrigiert** (Quelle: [[refactor/reference-inventory]] §3): `model` ist
dazugekommen, und `place_id` / `chat_id` / `district_id` / `shopify_gid` sind **raus** — Delivery
berechnet sie zwar, aber kein Modul liest sie. `[Sync] Inventory to Shopify` und `[Notify] Telegram`
lesen ihre Store-Felder selbst aus dem Record.

### K3 · `[Resolve] Salesperson & Conditions`

```
IN   person_name    : text                     — Name vom Beleg
     service_date   : text (YYYY-MM-DD)        — Leistungsdatum, nie now(); BEWUSST text,
                                                 ein date-Typ kippt DATETIME_PARSE (siehe K1)

OUT  ok, resolver_version
     salesperson_id
     condition_id
     taxation       : "Kleinunternehmer" | "Regelbesteuerung"
     service_date   : YYYY-MM-DD               — Echo, ersetzt 23.result.date in Delivery
     salesperson_error, condition_error        — getrennt: das Verdikt unterscheidet sie
     provision, cost_share                     — nur [Create] New Sales Member; nie gerechnet
```

Schmaler als die erste Skizze (Quelle: [[refactor/reference-inventory]] §3): `salesperson_name` und
`condition_name` werden heute **nirgends** gelesen.

**A5 ist entschieden — `mode` entfällt.** Der Resolver kennt genau einen Weg: Besteuerung
ereignisdatiert aus `Vertriebler.⚙ Regelbesteuerung ab`. `[Create] New Sales Member` ruft ihn
**nicht** auf; es prüft beim Onboarding nur, ob für den neuen Vertriebler überhaupt eine
Konditions-Version existiert, und behält dafür seinen eigenen Griff — inklusive A9-Fix.

### K4 · `[Archive] Document PDF`

```
IN   document_record_id : rec…                 — Belege-Record
     file_data          : buffer
     file_name          : text                 — ohne .pdf
OUT  ok, attachment_id, error
```

Darf scheitern; der Aufrufer läuft weiter (`builtin:Ignore` bleibt, wie heute).

---

## 6 · Stress-Test des vorgeschlagenen Schnitts

### Verdikt
**Trägt mit Auflagen.** Die Reihenfolge ist richtig (deckungsgleiche und geldferne Blöcke zuerst),
aber sie steht auf einem Mechanismus, der in diesem Team noch nie gelaufen ist, und zwei der vier
Bausteine setzen eine Entscheidung voraus, die noch nicht getroffen ist.

### Bruchstellen (priorisiert)

1. **Interface-Blank beim Import — still.** [[tools]] dokumentiert, dass ein importiertes
   Subszenario sein Interface verlieren kann. Bei `[Notify] Telegram` kostet das eine Meldung. Bei
   einem Resolver liefert es **leere Identitäten ohne Fehler** — der Aufrufer schreibt dann eine
   Lieferung ohne Vertriebler oder mit `purchase_net = 0`. Kein Alarm, keine Spur.
2. **Fan-in ohne Rückfallebene.** Heute bricht ein Fehler in der Store-Auflösung genau einen Worker.
   Nach Stufe 3 bricht er fünf. Es gibt **keine Testbase** und keinen Rollback-Pfad außer dem
   Blueprint-Reimport.
3. **Der A1-Fallback macht Delivery durchlässiger — mit Ansage.** Entschieden ist er (Name-Fallback
   für beide), aber die Bruchstelle bleibt benennbar: eine Lieferung, deren Kunden-Nr. nicht in
   `Stores` steht, läuft künftig über den Namen durch statt zu blocken. Trifft der Name den falschen
   Store, wird auf den falschen Bestand gebucht. Die Pflicht-Warnung im Verdikt macht das sichtbar,
   sie verhindert es nicht — **beim Migrieren von Delivery gezielt gegenprüfen**, ob in den letzten
   Läufen Kunden-Nummern auftauchten, die heute blocken.
4. **Gekoppelte Fehlerbudgets.** Alle Szenarien laufen mit `maxErrors: 3` und DLQ. Ein synchroner
   Aufruf koppelt Eltern- und Kind-Lauf: ein Kind, das dreimal scheitert, parkt den Eltern-Lauf mit.
   Bei einem Batch-Resolver in der Positionsschleife ist das der plausibelste Weg in eine volle DLQ.
5. **`[Notify] Telegram` als Nutzer von `[Resolve] Store`** wäre ein Kind, das ein Kind ruft.
   Machbar, aber es koppelt den Meldeweg an den Resolver — und der Meldeweg ist das, was schreit,
   wenn der Resolver bricht. **Empfehlung: den Hub bewusst außen vor lassen**, auch wenn er
   technisch Nutzer wäre.

### Engpass
**Volumen → die Positionsschleife.** Delivery und Inventory laufen heute pro Positionszeile durch
drei Airtable-Suchen. Ein Resolver *pro Zeile* legt auf jede Zeile zusätzlich eine
Subszenario-Startzeit — bei 20 Zeilen × 3 Workern ist das der erste Ort, an dem die 40-Minuten-Grenze
und `maxErrors` gemeinsam zubeißen. Deshalb ist K1 als **Batch**-Kontrakt geschnitten: ein Aufruf je
Beleg, Schleife im Kind. Das ist die einzige Stelle im ganzen Entwurf, an der die Lastrichtung die
Form des Kontrakts diktiert.

Die anderen drei Lastrichtungen sind unkritisch: *Zeit* — Konditionen und Preise wachsen um wenige
Versionen im Jahr; *Breite* — der einzige Ort, der mit der Store-Zahl wächst, ist „Load stores" in
Delivery (`maxRecords 500`, heute ~8 Stores), und genau den räumt der Resolver ab; *Ränder* —
Gleichzeitigkeit ist durch „ein Bearbeiter" und die Ereignis-Trigger faktisch ausgeschlossen.

**Gegengewicht (YAGNI):** Für `[Resolve] Salesperson & Conditions` wird hier auf drei Nutzer gebaut,
von denen einer noch nicht existiert. Das ist bewusst, aber es ist eine Wette. Fällt die Rückholung
aus, bleibt A3–A5 der Gewinn und die Extraktion ist überflüssiger Aufwand — dann Stufe 4 streichen,
nicht trotzdem bauen.

### Blinde Winkel

- **Ungenanntes Non-Goal:** Der Resolver zentralisiert die Feld-**IDs**, nicht die
  Umbenennungs-Bruchgefahr. `filterByFormula` arbeitet weiter mit Feld-**Namen**; ein umbenanntes
  `Stores.Name` bricht danach genau eine Stelle statt fünf — aber es bricht immer noch still.
  „Nach dem Refactor kann man gefahrlos umbenennen" wäre die falsche Erwartung.
- **Ungenanntes Non-Goal:** Der Umbau macht die Worker **nicht** billiger. Die Module wandern nur ins
  Kind; die Operations zählen dort genauso. Der Gewinn ist Konsistenz, nicht Credits.
- **Nicht abgesuchte Alternative — Airtable statt Make.** Steelman: `Belege` bekommt per
  Airtable-Automation eine Verknüpfung zum Store, dann bräuchten beide Upload-Worker gar keine
  Store-Auflösung. **Fällt**, weil die Kunden-Nr. nur im PDF steht und erst durch die Transkription
  entsteht — die Auflösung kann Airtable also nicht vor Make erledigen. Für `[Dispatch] Lexware
  Voucher` (Lexware-ID liegt vor) wäre sie denkbar, dort ist es aber schon nur eine Suche.
- **Nicht abgesuchte Alternative — nur angleichen, nicht extrahieren.** Für B2/B3 mit zwei Nutzern
  ist das ernsthaft im Rennen (siehe Gegengewicht). Für B5 nicht: dreimal identisch ist genau der
  Fall, für den es Bausteine gibt.

### Falsifizierbare Annahmen

| Annahme | Woran man merkt, dass sie falsch ist |
|---|---|
| Synchrone Subszenarien mit `Return outputs` funktionieren hier | Stufe 0 scheitert an einem der vier Punkte — dann fällt der gesamte Entwurf, nicht nur eine Stufe |
| Die drei Positions-Resolver sind semantisch gleich | Ein Nutzer braucht eine vierte Suche oder ein anderes `maxRecords` — dann ist K1 zu eng geschnitten |
| Ein Batch-Aufruf je Beleg hält die Laufzeit | Delivery-Läufe überschreiten nach der Migration ihre heutige Laufzeit spürbar |
| Der Fan-in ist beherrschbar, weil inkrementell migriert wird | Zwei Nutzer werden im selben Release umgestellt — dann ist die Annahme praktisch aufgegeben |

### Härtung (nach Wirkung/Aufwand)

- **H1 — A5 vor Stufe 4 entscheiden** (A1 ist ✅ entschieden). Eine Frage, kein Bau. Höchste Wirkung,
  kein Aufwand.
- **H2 — Jeder Resolver liefert `ok` und `resolver_version` als Pflichtfelder; jeder Aufrufer filtert
  hart darauf.** Das ist die einzige Gegenmaßnahme gegen das stille Interface-Blank: ein geleertes
  Interface liefert `ok = leer`, der Filter greift, der Lauf blockt sichtbar statt leise falsch zu
  buchen. Kleiner Aufwand, verhindert die zweitschwerste Bruchstelle.
- **H3 — Ein Nutzer pro Release.** Alter Pfad bleibt stehen (deaktiviert, nicht gelöscht), bis der
  neue eine Woche grün läuft. Deckt sich mit „Fundament-First, inkrementell".
- **H4 — K1 als Batch-Kontrakt festschreiben**, nicht pro Zeile. Adressiert den Engpass direkt.
- **H5 — `[Notify] Telegram` nicht an die Resolver hängen**, obwohl er Nutzer wäre. Der Meldeweg
  bleibt unabhängig von dem, worüber er meldet.
- **H6 — A2, A3, A4, A6, A7, A8 vorziehen**, unabhängig vom Resolver-Bau. Sie beheben stille
  Divergenzen, die heute schon da sind, und verkleinern jede spätere Extraktion.

---

## 7 · Entscheidungen und offene Fragen

**Entschieden am 2026-08-21 (Joscha):**

- **A1 — Store-Fallback:** Name-Fallback für **beide** Worker. Inventory bleibt, Delivery wird
  durchlässiger; Auflagen siehe B1 Punkt 1.
- **Rückholung:** fest eingeplant. Damit bleibt **Stufe 4** im Plan (`[Resolve] Salesperson &
  Conditions` bekommt seinen dritten Nutzer) und der Rückhol-Zweig aus B5 —
  `Bestände.Ø EK (netto)` statt `Produktvarianten.⚙ EK (netto)` — ist Pflichtteil von K1.

**Noch offen — A5, Besteuerung.** `Vertriebler` trägt zwei Felder dazu:

| Feld | Typ | sagt |
|---|---|---|
| `Besteuerung` | singleSelect | Stand **heute** (Kleinunternehmer / Regelbesteuerung) |
| `⚙ Regelbesteuerung ab` | date | **ab wann** Regelbesteuerung gilt |

`[Process] Upload PDF (Delivery)` und `[Process] Invoice (Store)` **rechnen** die Besteuerung aus dem
Datum: Leistungsdatum ≥ `⚙ Regelbesteuerung ab` → Regelbesteuerung, sonst Kleinunternehmer. Das
Select lesen sie gar nicht. `[Create] New Sales Member` liest **nur** das Select.

**Frage:** Ist `⚙ Regelbesteuerung ab` die alleinige Wahrheit überall, wo Geld dranhängt, und das
Select damit reine Anzeige? Falls ja, bekommt K3 nur **einen** Weg, der `mode`-Schalter entfällt, und
`[Create] New Sales Member` ruft den Resolver gar nicht auf — der prüft ja nur, ob für diesen
Vertriebler überhaupt eine Konditions-Version existiert.

---

*Nächster Schritt laut Auftrag: Review dieser Landkarte — erst danach Bau des ersten
Resolver-Subszenarios. Vorgelagert und unabhängig davon empfohlen: Stufe 0 und die Angleichungen aus
H6.*
