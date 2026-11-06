# Szenarien

> **Vertrag, nicht Innereien.** Je Szenario: Aufgabe · Trigger · gelesene/geschriebene Tabellen · Aufrufe · Notify-Keys. Die Modulketten leben ausschließlich im **Live-Szenario** (SSoT der Innereien) — bei Bedarf per Make-MCP `scenarios_get(<id>)` ziehen; diese Datei dupliziert sie bewusst nicht. Stand **2026-08-25**, Team **2174024** (eu1). Präfix = Rolle (nicht Trigger). Seit 22.08. ist die Auflösung aus den `[Process]`-Workern in native Subscenarios ausgezogen: **`[Resolve]`** (Beleg lesen, Store/Vertriebler/Kondition/Positionen) + **`[Archive]`** (PDF-Sicherung).

## Topologie in einem Satz

Eingang (Mail/Webhook/Watch/Scheduled) → **`[Dispatch]`** klassifiziert → **`[Process]`** orchestriert: ruft die **`[Resolve]`**-Kinder (Beleg lesen, Store/Vertriebler/Kondition/Positionen auflösen) als native Subscenarios, schreibt dann die Ereignis-/Positionszeilen und lässt **`[Archive]`** das PDF sichern → **`[Sync]`** spiegelt nach Shopify/Lexware → **jedes** Szenario „klingelt" bei **`[Notify] Telegram`** (6862968) per `StartSubscenario(key,id,ctx)`. `[Maintain]` hält die Airtable-Webhooks frisch.

---

## `[Dispatch]` — Eingang & Klassifikation

**`[Dispatch] Upload PDF` · 6836167** · Ordner 370442
Trigger: **Gateway-Webhook** (Airtable-Automation auf der Belege-View). Aufgabe: Belegtyp klassifizieren und an den passenden `[Process]` weiterreichen (native Call).
Liest `Belege`; bei `Belegtyp = Unbekannt` → Notify **`task.doctype_unclear`**. → ruft `[Process] Upload PDF (Delivery|Inventory)` / `[Process] Invoice (Store)`. Seit 05.11.2026 erkennt der Kopf-Leser auch **Lieferschein** (Titel „Lieferschein AF-…", Kunden-Nr., Datum) → Delivery; Lieferscheine laufen nie in den Gemini-Kopfzweig.

**`[Dispatch] Lexware Voucher` · 6872775** · Ordner 370442
Trigger: **lexoffice `watchEvents`**. Aufgabe: Voucher-Events aufnehmen, per **A2-Guard** (Modul 2) filtern und weiterleiten (Eingangsrechnung → Sales, Zahlung → Payments).

## `[Process]` — Ereigniszeilen schreiben

**`[Process] Upload PDF (Delivery)` · 6677862** · Ordner 382128 · chainingRole bridge
**Übergabeprotokoll (Kommission) und Lieferschein (Eigenbestand, seit 05.11.2026)** (Rückhol ist ausgezogen → `[Process] Upload PDF (Return)`). Orchestriert (verifiziert 25.08.): `[Resolve] Protocol` (Beleg lesen) → Validator (Code, liest nicht mehr, prüft nur) → `[Resolve] Store` → `[Resolve] Salesperson & Conditions` → Dedup (`ID`) → Verdikt; bei sauberem Verdikt `[Resolve] Positions` (`purchase_source = variant`, `create_missing_stock = true`), schreibt **`Lieferungen`** + **`Lieferpositionen`**, triggert `[Sync] Inventory to Shopify` (restock) und `[Archive] Document PDF`. Notify **`delivery.booked`** · **`delivery.note_booked`** (Lieferschein) · **`delivery.equipment`** · **`task.jtl_stock`** (nicht bei Lieferscheinen: JTL liefert aus dem eigenen Lager).
**Lieferschein-Zweig:** keine Unterschriftsprüfung, Nummer `AF-…-…-…` = `Lieferungen.ID`, Vertriebler aus „Vertrieb und Betreuung". Vor der Buchung `Read store model` → `Model switch?`: Lieferschein auf einem Kommission-Store setzt **`Stores.Modell` = Eigenbestand** und meldet **`store.model_changed`**; nur diese Richtung, ein zweiter Lieferschein ändert nichts. Am Ende verteilt der Router „Task + archive" Lager-Aufgabe (Filter „Not for delivery notes") und Archiv auf getrennte Zweige — ein Filter direkt vor dem Archiv würde es für Lieferscheine mit anhalten (Stand 05.11.2026).

**`[Process] Upload PDF (Return)` · 7062902**
Rückholprotokoll (Gegenstück zu Delivery, `dry_run`-fähig) → nutzt `[Resolve] Positions` mit `purchase_source = stock_avg` (Rückhol-Zweig, Bewertung zum gleitenden Ø-EK aus `Bestände`); schreibt die Rückhol-Zeilen. Notify **`inventory.checked`** + **`task.jtl_inventory_date`** (nur wenn die Bestandsprüfung neu ist) · **`delivery.returned`** + **`task.jtl_return`** (nur wenn die Negativlieferung neu ist) · **`error.return_failed`** (Gate blockiert). Die Meldungen hängen in einem Router „Meldungen / Abschluss" vor Rest-Sortiment, Offboarding und Archiv, damit ein Wiederanlauf mit vorhandener Bestandsprüfung bis zum Archiv durchläuft (Stand 05.11.2026). Bei `Stores.Modell = Eigenbestand` setzt „Kein Rest-Sortiment?" den Store **nicht** inaktiv und ruft kein `remove` (Rückholung der Kommissionsware beim Modellwechsel). *Exakte Aufruf-Kette live prüfen (`scenarios_get 7062902`).*

**`[Process] Upload PDF (Inventory)` · 6729541**
Bestandsprotokoll → schreibt **`Bestandsprüfungen`** + **`Bestandsprüfungspositionen`**. In: `record_id`, `document_date`, `document_url`, `customer_no?`, `store_name?`, `document_type?`, **`protocol_layout?`** (gesetzt von `[Dispatch] Upload PDF`; entfällt mit P5). Verzweigt nach Layout:
- **`table` oder leer** (JTL-Druck) — Bestand-Zweig von `[Resolve] Protocol` (Gemini-Raster + mehrstufige Reconciliation), wie bisher.
- **`grid`** (freies Formular, seit P3) — liest über **`[Resolve] Protocol (Inventory)`**; SOLL kommt nicht vom Blatt, sondern aus der Base: lädt Vertriebler („Load salespeople“: `Name`, `Stores`, `Stores 2`), Bestände (inkl. `Store`), die Lieferungen seit der letzten Prüfung („Load deliveries since last check“, `filterByFormula` über die 🟣-Felder von `Lieferpositionen`) und die Rechnungspositionen ab dem Vortag des Prüftags („Load invoices since check day“, `filterByFormula` über 🟣 `Umsatzpositionen.Bestand` + `CREATED_TIME()`). Schreibt zusätzlich `Bestandsprüfungen.Poster im Schaufenster` und `Bestandsprüfungen.Nachtrag` (Modul „Write poster and amendment“, über die Feld-ID).
  - **SOLL-Abgleich (grid-1.2.0, seit 06.11.2026):** Eine schon einmal gezählte Kratom-Sorte wird nur gebucht, wenn **SOLL laut Zählung** (`Bestände.IST` − Lieferungen ab Prüftag) gleich **SOLL laut Rechnungen am Prüftag** (`Bestände.SOLL` − Lieferungen ab Prüftag + Rechnungsmenge ab Prüftag, ohne Storniert) ist. Sonst bleibt die Zeile offen („mehr berechnet als gezählt“ = Zählstand veraltet, „Rechnung fehlt“ = Verkäufe noch nicht berechnet); richtig ist immer der **kleinere** Wert. Nie gezählte Sorten, Display und Vitrine: kein Abgleich. Rechnungsliste über 100 Zeilen → SOLL nicht bestimmbar.
  - **Vorbelegung:** Jede offene Kratom-Zeile (Abgleich, Mehrbestand, leer mit SOLL > 0, unlesbar) geht als `Pos N · Sorte (SKU) · SOLL x · IST y` in `Nachtrag`, beim Abgleich mit dem kleineren SOLL; `SOLL ?`, wenn nicht bestimmbar. Beleg-Problem → keine Vorbelegung.
  - „Guard + status“ unverändert: keine Kratom-Zeile gebucht → **Ungültig**, auch wenn Display/Vitrine gebucht sind.

Notify **`inventory.checked`**. *Genaue Resolver-Kette live.*

**`[Process] Inventory Amendment` · 8413130** · Ordner 382128 · seit 06.11.2026
Trigger: Airtable-Webhook **„Inventory amendment“** (View „Korrektur (make.com)“, nur `add`, beobachtet `Nachtrag buchen`; registriert über `[Maintain] Airtable Webhooks`), sofort, sequenziell. Bucht offene Zählzeilen aus `Bestandsprüfungen.Nachtrag` nach: „Load checks to amend“ (View, bis 10 Prüfungen je Lauf) → „Load booked lines“ (`Bestandsprüfungspositionen` per `RECORD_ID()`-Filter) → Code „Parse amendment“ → `[Resolve] Positions` (`purchase_source = variant`, `create_missing_stock = false`, Leistungsdatum = Prüfdatum) → „Join resolver result“ (Code von `Resolver-Ergebnis anjoinen`, wörtlich) → „Close amendment“ → schreibt **`Bestandsprüfungspositionen`** wie „Create line“, setzt `Status`, hängt den Block „NACHTRAG <Datum>“ an `Hinweis`, nimmt `Nachtrag buchen` zurück und stößt `[Sync] Inventory to Shopify` (`inventory-check`) an.
- **Regeln je Zeile:** Artikelnummer in Klammern (Pos optional, Name nur zum Lesen, Trenner frei). Gebucht nur bei ganzen Zahlen mit 0 ≤ IST ≤ SOLL; Ausstattung, doppelte Zeile, fehlender SOLL/IST, Mehrbestand → nicht gebucht mit Grund; Sorte mit Position in dieser Prüfung → übersprungen (Idempotenz). Belegte oder fehlende Pos → nächste freie ab 21.
- **Status:** angenommen bei Teilgebucht, Abgeschlossen, Ungültig; „In Bearbeitung“ abgelehnt. Nichts offen → Abgeschlossen; sonst Teilgebucht; Ungültig ohne angelegte Zeile bleibt Ungültig.
- **Fehler:** Fehlerweg an `[Resolve] Positions` und „Create line“ schreibt den Fehler in den `Hinweis` und hält die Ausführung als unvollständig (2 Wiederholungen, 15 Min.). Keine Telegram-Meldung (Joscha löst selbst aus).
- Spec: Projekt „selectedleafs.com · Technik“, `claude/spec-soll-abgleich-nachtrag.md`.

**`[Process] Invoice (Store)` · 6633991**
Ausgangsrechnung → löst über die `[Resolve]`-Kinder auf (Salesperson-Input = `partner` aus dem Lexware-Beleg; `[Resolve] Positions`-plus-Join produktiv) und schreibt **`Umsätze`** + **`Umsatzpositionen`**; wählt `Konditionen` (eff-dated). Notify **`invoice.created` / `.paid` / `.voided` / `.written_off`**; **`task.terms_missing`** wenn keine passende Konditionen-Version. *Genaue Resolver-Kette live.*

**`[Process] Invoice (Sales)` · 6872651**
Eingangsrechnung (Provisionsrechnung des Vertrieblers) → schreibt **`Auszahlungen`** (Idempotenz über `Lexware ID`) + Gegen-`Beleg`. Notify **`payout.created` / `.settled`**; **`error.lexware_orphan`**.

**`[Process] Invoice Reminder (Store)` · 6844567**
*(In der Doku lief das Szenario lange als `[Process] Payment Reminder (Store)`. Maßgeblich ist
der Name in Make — beim Suchen den alten Namen mitdenken.)*
Trigger: **Mailhook**. Zahlungserinnerung/Mahnung → verknüpft `Beleg` mit dem `Umsatz` (Mahnstufe). Notify **`invoice.reminder_filed` / `.dunning_filed`**; **`error.reminder_unmatched`** (R26: `error.reminder_unreadable`-Zweig entfernt).

## `[Resolve]` — Auflösung (native Subscenarios)

On-demand-Kinder (`Call a scenario` / `CallSubscenario`, synchron), je **eine** Auflösungs-Aufgabe, aufgerufen von den `[Process]`-Workern. Gemeinsamer Kontrakt:

- **Weiches Verdikt statt Wurf.** Jedes Kind gibt `*_ok` + `*_error` zurück und wirft **nie** einen ValidationError — ein harter Wurf würde den Eltern-Lauf killen, *bevor* dessen Verdikt geschrieben ist. Eingaben sind darum bewusst optional/tolerant.
- **`resolver_version` ist Pflicht-Output.** Kommt sie leer an, ist das Kind-Interface geleert (Import-Falle, → [[operations]]/B10) — der Eltern-Guard meldet dann **Verdrahtungsfehler**, nicht Datenfehler (INCIDENT-2026-08-22).
- **Datum immer Text `YYYY-MM-DD`**, nie Datumstyp (Zeitzone kippt den Tag).
- **Reader-Output wird am Modell schema-gebunden**, nicht per Make-Data-Structure: jeder LLM-Reader nutzt natives Structured-Output (Claude `json_schema`, Gemini `responseSchema`/`responseMimeType`), nullable für Unlesbares (`set null, do not guess`).

**`[Resolve] Protocol` · 7054448** · Ordner 382196 — **LLM-Reader**. In: `document_type`, `document_url`. Lädt den Beleg, verzweigt nach Belegtyp: Claude (`claude-haiku-4-5`) für den Übergabe-Einspalter; Gemini (`gemini-3.1-pro`) als Raster-Leser für Bestand, inkl. mehrstufiger Reconciliation (Cross-check → Zweitlese „only on doubt" → Reconcile). Out: `ok`, `read_ok`, `read_error`, `person`, `checked_by`, `doc_number`, `commission_agent`, `signature_consignor`, `signature_commission_agent`, `positions[]` (`pos`/`no`/`label`/`qty`/`kg`/`grams`), `resolver_version`. Die Vereinheitlichung der drei Zweig-Formen macht je ein Code-`Normalize`/`Assemble` vor `ReturnData` — kein Schema kann das. Seit 05.11.2026 ein Zweig **Lieferschein** (Claude, „Read delivery note"): Nummer, Vertriebler aus „Vertrieb und Betreuung", Positionen; gleicher Ausgangsvertrag, keine Unterschriften. Der Name bleibt trotz Lieferschein- und Inventory-Aufrufern (Joscha 05.11.2026).

**`[Resolve] Protocol (Inventory)` · 8329417** — **LLM-Reader** für das freie Bestandsprotokoll (grid-Zweig von `[Process] Upload PDF (Inventory)`). In: `document_url` (lädt selbst). Out: `ok`, `read_ok`, `read_error`, `checked_by`, `customer_no_read`, `date_read`, `poster`, `signature_consignor`, `signature_commission_agent`, `positions[]` (`pos`/`no`/`actual`/`uncertain`/`empty`), `notes[]` (`kat`/`pos`/`no`/`text`), `noteText`, `second_reading_ran`, `disputed_total`, `decided`, `open`, `resolver_version`. Liest nur IST — SOLL rechnet der Aufrufer aus der Base.

**`[Resolve] Store` · 7049889** — Store über Kunden-Nr. **dann** Name (Kaskade). In: `customer_no?`, `store_name?` (beide optional; beide leer → `store_error`). Out: `store_ok`, `store_id`, `store_number`, `store_name`, `store_error`, `store_note`, `via`, `resolver_version`.

**`[Resolve] Salesperson & Conditions` · 7048609** — Vertriebler + eff-datierte Kondition. In: `person_name?`, `service_date?` (Text). Leerer Name → `salesperson_error`, fehlendes Datum → `condition_error`. Out: `salesperson_ok`, `salesperson_id`, `salesperson_error`, `taxation`, `condition_id`, `condition_error`, `date`, `resolver_version`.

**`[Resolve] Positions` · 7039710** — Positionszeilen gegen Produkt/Preis/Bestand auflösen. In: `lines[{pos,sku}]`, `service_date` (Text), `store_number`, `store_record_id?`, `create_missing_stock`, `purchase_source`: `variant` = `Produktvarianten.EK` (netto, Übergabe-Zweig) · `stock_avg` = `Bestände.Ø EK` (netto, Rückhol-Zweig). `create_missing_stock: true` **nur** bei Delivery (nur eine Lieferung darf ein Sortiment eröffnen). Durchreichfelder (`qty`/`kg`/`grams`) bleiben beim Aufrufer und werden über `pos` angejoint; das Auflöse-Gate sitzt **beim Aufrufer** (Code `anjoinen`), nicht im Kind.

## `[Archive]` — PDF-Sicherung

**`[Archive] Document PDF` · 7042723** — lädt das Original selbst (Binärdaten passen durch kein Interface) und ersetzt den Anhang `Belege.Anhang` durch eine mit iLovePDF komprimierte Kopie namens `<filename>.pdf`. In: `document_url`, `filename` (ohne `.pdf`), `record_id`. Out: `ok`, `archiver_version`, `filename`. Aufrufer übergeht einen Fehler via `Ignore`.

## `[Notify]`

**`[Notify] Telegram` · 6862968** · Hub (on-demand child). Kontrakt + Mechanik: **[[notify]]**.

## `[Sync]` — Spiegel nach außen

**`[Sync] Inventory to Shopify` · 6805674**
Push der Bestände nach Shopify; danach die **City-Posts** aus `Bestände` (`Letzte Lieferung` = Belegdatum-Gate). Notify **`sync.inventory`** (R26, Erfolgs-Report) · **`city.restock` / `city.strain_new`**; **`error.sync_aborted`**. Liest `Stores.Modell`: bei **Eigenbestand** fügt `restock` die Sorten des Belegs zur Shop-Liste hinzu, alle anderen Typen ändern nichts; Kommission unverändert (seit 05.11.2026).

**`[Sync] Shopify Products to Airtable` · 6795533** · wöchentl. **So 04:00**
Upsert **`Produkte` / `Produktvarianten` / `Preise`** (Match über SKU). Notify **`sync.products`**; **`error.sync_aborted`**.

**`[Sync] Shopify Stores from Google Place API` · 6655783** · wöchentl. **So 05:00**
Aktualisiert **`Stores`** (Öffnungszeiten/Bewertung via Place API). Notify **`sync.stores`**.

**`[Sync] JTL Invoice to Lexware` · 6870495** · Ordner 382407 (POS · Sync)
Trigger: **Mailhook**. JTL-Ausgangsrechnung → Lexware. „Dokument wählen" nimmt nie ein PDF mit „lieferschein" oder „deliverynote" im Namen; ist es das einzige, endet der Lauf ohne Upload (Schutz, Stand 05.11.2026).

**`[Sync] JTL Delivery Note to Airtable` · 8392806** · Ordner 382407 (POS · Sync) · seit 05.11.2026
Trigger: **Mailhook** (eigene Adresse; JTL schickt den Lieferschein beim Anlegen). Prüft nur: Absender `kontakt@selectedleafs.com` (fremde Post still verwerfen), genau ein PDF, Dateiname beginnt mit „Lieferschein" oder „DeliveryNote" (JTL liefert `DeliveryNote AF-….pdf`) — sonst Make-Fehler. Legt **`Belege`** an (Belegtyp „Unbekannt") und hängt das PDF über den Airtable-Upload-Endpunkt an `Anhang` (Schlüssel „Airtable · Sync Delivery Note"). Lesen und Buchen macht der bestehende Eingang (Inbox-View → `[Dispatch] Upload PDF`). Sequenziell: eine offene unvollständige Ausführung hält weitere Lieferscheine an, bis sie gelöst ist. Scheitert der Upload, bleibt ein Beleg ohne PDF zurück.

**`[Sync] Lexware Payments` · 6955541** · ohne Ordner
Trigger: **lexoffice `watchEvents` (`payment.changed`)**. Setzt den Zahlungsstatus auf **`Umsätze` / `Auszahlungen`** (inkl. **Teilzahlung**). Der definierte Sonderfall gegen die INSERT-only-Regel. Notify **`error.payment_unmatched`** (R26, No-Match-Zweig).

## `[Create]` — Onboarding

**`[Create] New Store Partner` · 6820980**
Trigger: **Formular** (personalisierter Link, `Akquise durch` vorbelegt; Eingangs-Guard Modul 2). Legt `Stores` + Shopify-Metaobjekt + Lexware-Kontakt an. Notify **`store.created`**; **`task.jtl_missing`**; **`error.store_failed` / `.store_partial`**.

**`[Create] New Sales Member` · 6821121**
Legt `Vertriebler` + Lexware-Kreditor + Provisions-Sheet an. Notify **`salesperson.created` / `.onboarded`**; **`error.salesperson_failed`**.

## `[Maintain]`

**`[Maintain] Airtable Webhooks` · 6830404** · Ordner 377621 · tägl. **04:30**
Hält die Airtable-Webhook-Registry frisch (Ablauf-Erneuerung).

**`[Maintain] Overdue Inventory Checks` · ID nach Import** · tägl. **~07:00**
Trigger: **Schedule**. Scannt aktive Stores (`Status` ∈ Aktiv/Probezeit · `Modell` = Kommission), bestimmt je Store die jüngste `Bestandsprüfung` und meldet Überfällige (heute − letzte Prüfung > 30 Tage). Liest `Stores` + `Bestandsprüfungen`; schreibt den Marker `Fällig gemeldet am`. Notify **`inventory.due`**. Idempotenz über den Marker (wöchentliches Re-Nag).

---

## ❌ Gestrichen: `[Scheduled] Daily Operations`

Der 07:00-Lauf ist **gestrichen, nicht aufgeschoben** — und die drei Schlüssel, die er hätte auslösen sollen, **existieren im Hub nicht**. Am Live-Hub gemessen (2026-08-22, Ereignis-Landkarte in Modul `[2]`, 33 Schlüssel): weder `invoice.overdue` noch `task.digest` noch `system.heartbeat` steht dort. [[notify]] führt alle drei folgerichtig als in Runde 26 gestrichen. (`inventory.due` hat seit 18.08. einen eigenen Auslöser → `[Maintain] Overdue Inventory Checks`.)

> ⚠ **Korrigiert am 2026-08-22.** Hier stand das Gegenteil: „bis dahin sind diese Keys im Hub definiert, aber ohne Auslöser". Diese Zeile hat einen Eintrag in einer offenen Liste erzeugt, der nie offen war — sie war nie gegen das laufende System geprüft, und sie widersprach [[notify]] im selben Skill. **Widersprechen sich Skill und Live-System, gewinnt das Live-System; korrigiert wird der Skill, nicht die Messung.** Und: widersprechen sich zwei Referenzen dieses Skills, ist eine davon falsch — nicht beide gültig.

**Folge, entschieden am 2026-08-22:** `task.invoice_unlinked` und `task.beleg_no_pdf` waren als Zeilen im Digest vorgesehen. Sie bekommen **keine** Zeile in der Ereignis-Landkarte — der Verzicht ist entschieden, nicht offen. Beide Schlüssel sind damit tot; wer sie in einem Kommentar findet, findet einen Rest aus einem verworfenen Plan und darf ihn löschen.

**Bewusst in Kauf genommen:** schlägt in `[Process] Invoice Reminder (Store)` der PDF-Upload fehl, gibt Modul `[12]` in **beiden** Zweigen den Erfolgsschlüssel (`invoice.reminder_filed` / `.dunning_filed`) zurück und sendet nur `key`/`id`/`ctx` — der dort gebaute Warntext geht nirgendwohin. Telegram meldet also „abgelegt", obwohl das PDF fehlt. Der Beleg steht dann ohne PDF in Airtable, das PDF nur in der Mail.

*Beziehungsgraph als Bild: `assets/diagrams/topology.html`.*
