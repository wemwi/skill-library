# Szenarien

> **Vertrag, nicht Innereien.** Je Szenario: Aufgabe · Trigger · gelesene/geschriebene Tabellen · Aufrufe · Notify-Keys. Die Modulketten leben ausschließlich im **Live-Szenario** (SSoT der Innereien) — bei Bedarf per Make-MCP `scenarios_get(<id>)` ziehen; diese Datei dupliziert sie bewusst nicht. Stand **2026-08-25**, Team **2174024** (eu1). Präfix = Rolle (nicht Trigger). Seit 22.08. ist die Auflösung aus den `[Process]`-Workern in native Subscenarios ausgezogen: **`[Resolve]`** (Beleg lesen, Store/Vertriebler/Kondition/Positionen) + **`[Archive]`** (PDF-Sicherung).

## Topologie in einem Satz

Eingang (Mail/Webhook/Watch/Scheduled) → **`[Dispatch]`** klassifiziert → **`[Process]`** orchestriert: ruft die **`[Resolve]`**-Kinder (Beleg lesen, Store/Vertriebler/Kondition/Positionen auflösen) als native Subscenarios, schreibt dann die Ereignis-/Positionszeilen und lässt **`[Archive]`** das PDF sichern → **`[Sync]`** spiegelt nach Shopify/Lexware → **jedes** Szenario „klingelt" bei **`[Notify] Telegram`** (6862968) per `StartSubscenario(key,id,ctx)`. `[Maintain]` hält die Airtable-Webhooks frisch.

---

## `[Dispatch]` — Eingang & Klassifikation

**`[Dispatch] Upload PDF` · 6836167** · Ordner 370442
Trigger: **Gateway-Webhook** (Airtable-Automation auf der Belege-View). Aufgabe: Belegtyp klassifizieren und an den passenden `[Process]` weiterreichen (native Call).
Liest `Belege`; bei `Belegtyp = Unbekannt` → Notify **`task.doctype_unclear`**. → ruft `[Process] Upload PDF (Delivery|Inventory)` / `[Process] Invoice (Store)`.

**`[Dispatch] Lexware Voucher` · 6872775** · Ordner 370442
Trigger: **lexoffice `watchEvents`**. Aufgabe: Voucher-Events aufnehmen, per **A2-Guard** (Modul 2) filtern und weiterleiten (Eingangsrechnung → Sales, Zahlung → Payments).

## `[Process]` — Ereigniszeilen schreiben

**`[Process] Upload PDF (Delivery)` · 6677862** · Ordner 382128 · chainingRole bridge
**Nur Übergabeprotokoll** (Rückhol ist ausgezogen → `[Process] Upload PDF (Return)`). Orchestriert (verifiziert 25.08.): `[Resolve] Protocol` (Beleg lesen) → Validator (Code, liest nicht mehr, prüft nur) → `[Resolve] Store` → `[Resolve] Salesperson & Conditions` → Dedup (`ID`) → Verdikt; bei sauberem Verdikt `[Resolve] Positions` (`purchase_source = variant`, `create_missing_stock = true`), schreibt **`Lieferungen`** + **`Lieferpositionen`**, triggert `[Sync] Inventory to Shopify` (restock) und `[Archive] Document PDF`. Notify **`delivery.booked`** · **`task.jtl_stock`**.

**`[Process] Upload PDF (Return)` · 7062902**
Rückholprotokoll (Gegenstück zu Delivery, `dry_run`-fähig) → nutzt `[Resolve] Positions` mit `purchase_source = stock_avg` (Rückhol-Zweig, Bewertung zum gleitenden Ø-EK aus `Bestände`); schreibt die Rückhol-Zeilen. *Exakte Aufruf-Kette live prüfen (`scenarios_get 7062902`).*

**`[Process] Upload PDF (Inventory)` · 6729541**
Bestandsprotokoll → schreibt **`Bestandsprüfungen`** + **`Bestandsprüfungspositionen`**. Der Bestand-Zweig von `[Resolve] Protocol` (Gemini-Raster + mehrstufige Reconciliation) gehört zu diesem Weg. Notify **`inventory.checked`**. *Genaue Resolver-Kette live.*

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

**`[Resolve] Protocol` · 7054448** · Ordner 382196 — **LLM-Reader**. In: `document_type`, `document_url`. Lädt den Beleg, verzweigt nach Belegtyp: Claude (`claude-haiku-4-5`) für den Übergabe-Einspalter; Gemini (`gemini-3.1-pro`) als Raster-Leser für Bestand, inkl. mehrstufiger Reconciliation (Cross-check → Zweitlese „only on doubt" → Reconcile). Out: `ok`, `read_ok`, `read_error`, `person`, `checked_by`, `doc_number`, `commission_agent`, `signature_consignor`, `signature_commission_agent`, `positions[]` (`pos`/`no`/`label`/`qty`/`kg`/`grams`), `resolver_version`. Die Vereinheitlichung der drei Zweig-Formen macht je ein Code-`Normalize`/`Assemble` vor `ReturnData` — kein Schema kann das.

**`[Resolve] Store` · 7049889** — Store über Kunden-Nr. **dann** Name (Kaskade). In: `customer_no?`, `store_name?` (beide optional; beide leer → `store_error`). Out: `store_ok`, `store_id`, `store_number`, `store_name`, `store_error`, `store_note`, `via`, `resolver_version`.

**`[Resolve] Salesperson & Conditions` · 7048609** — Vertriebler + eff-datierte Kondition. In: `person_name?`, `service_date?` (Text). Leerer Name → `salesperson_error`, fehlendes Datum → `condition_error`. Out: `salesperson_ok`, `salesperson_id`, `salesperson_error`, `taxation`, `condition_id`, `condition_error`, `date`, `resolver_version`.

**`[Resolve] Positions` · 7039710** — Positionszeilen gegen Produkt/Preis/Bestand auflösen. In: `lines[{pos,sku}]`, `service_date` (Text), `store_number`, `store_record_id?`, `create_missing_stock`, `purchase_source`: `variant` = `Produktvarianten.EK` (netto, Übergabe-Zweig) · `stock_avg` = `Bestände.Ø EK` (netto, Rückhol-Zweig). `create_missing_stock: true` **nur** bei Delivery (nur eine Lieferung darf ein Sortiment eröffnen). Durchreichfelder (`qty`/`kg`/`grams`) bleiben beim Aufrufer und werden über `pos` angejoint; das Auflöse-Gate sitzt **beim Aufrufer** (Code `anjoinen`), nicht im Kind.

## `[Archive]` — PDF-Sicherung

**`[Archive] Document PDF` · 7042723** — lädt das Original selbst (Binärdaten passen durch kein Interface) und ersetzt den Anhang `Belege.Beleg`. In: `document_url`, `filename` (ohne `.pdf`), `record_id`. Out: `ok`, `archiver_version`, `filename`. Aufrufer übergeht einen Fehler via `Ignore`.

## `[Notify]`

**`[Notify] Telegram` · 6862968** · Hub (on-demand child). Kontrakt + Mechanik: **[[notify]]**.

## `[Sync]` — Spiegel nach außen

**`[Sync] Inventory to Shopify` · 6805674**
Push der Bestände nach Shopify; danach die **City-Posts** aus `Bestände` (`Letzte Lieferung` = Belegdatum-Gate). Notify **`sync.inventory`** (R26, Erfolgs-Report) · **`city.restock` / `city.strain_new`**; **`error.sync_aborted`**.

**`[Sync] Shopify Products to Airtable` · 6795533** · wöchentl. **So 04:00**
Upsert **`Produkte` / `Produktvarianten` / `Preise`** (Match über SKU). Notify **`sync.products`**; **`error.sync_aborted`**.

**`[Sync] Shopify Stores from Google Place API` · 6655783** · wöchentl. **So 05:00**
Aktualisiert **`Stores`** (Öffnungszeiten/Bewertung via Place API). Notify **`sync.stores`**.

**`[Sync] JTL Invoice to Lexware` · 6870495** · Ordner 377621
Trigger: **Mailhook**. JTL-Ausgangsrechnung → Lexware.

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
