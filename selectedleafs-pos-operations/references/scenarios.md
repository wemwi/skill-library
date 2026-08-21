# Szenarien

> **Vertrag, nicht Innereien.** Je Szenario: Aufgabe · Trigger · gelesene/geschriebene Tabellen · Aufrufe · Notify-Keys. Die Modulketten leben ausschließlich im **Live-Szenario** (SSoT der Innereien) — bei Bedarf per Make-MCP `scenarios_get(<id>)` ziehen; diese Datei dupliziert sie bewusst nicht. Stand **2026-08-15**, Team **2174024** (eu1). Präfix = Rolle (nicht Trigger).

## Topologie in einem Satz

Eingang (Mail/Webhook/Watch/Scheduled) → **`[Dispatch]`** klassifiziert → **`[Process]`** schreibt die Ereignis-/Positionszeilen → **`[Sync]`** spiegelt nach Shopify/Lexware → **jedes** Szenario „klingelt" bei **`[Notify] Telegram`** (6862968) per `StartSubscenario(key,id,ctx)`. `[Maintain]` hält die Airtable-Webhooks frisch.

---

## `[Dispatch]` — Eingang & Klassifikation

**`[Dispatch] Upload PDF` · 6836167** · Ordner 370442
Trigger: **Gateway-Webhook** (Airtable-Automation auf der Belege-View). Aufgabe: Belegtyp klassifizieren und an den passenden `[Process]` weiterreichen (native Call).
Liest `Belege`; bei `Belegtyp = Unbekannt` → Notify **`task.doctype_unclear`**. → ruft `[Process] Upload PDF (Delivery|Inventory)` / `[Process] Invoice (Store)`.

**`[Dispatch] Lexware Voucher` · 6872775** · Ordner 370442
Trigger: **lexoffice `watchEvents`**. Aufgabe: Voucher-Events aufnehmen, per **A2-Guard** (Modul 2) filtern und weiterleiten (Eingangsrechnung → Sales, Zahlung → Payments).

## `[Process]` — Ereigniszeilen schreiben

**`[Process] Upload PDF (Delivery)` · 6677862**
Übergabe-/Rückholprotokoll → schreibt **`Lieferungen`** + **`Lieferpositionen`** (stempelt `EK`). Notify **`delivery.booked`** / **`delivery.returned`**.

**`[Process] Upload PDF (Inventory)` · 6729541**
Bestandsprotokoll → schreibt **`Bestandsprüfungen`** + **`Bestandsprüfungspositionen`**. Notify **`inventory.checked`**.

**`[Process] Invoice (Store)` · 6633991**
Ausgangsrechnung → schreibt **`Umsätze`** + **`Umsatzpositionen`**; wählt `Konditionen` (eff-dated). Notify **`invoice.created` / `.paid` / `.voided` / `.written_off`**; **`task.terms_missing`** wenn keine passende Konditionen-Version.

**`[Process] Invoice (Sales)` · 6872651**
Eingangsrechnung (Provisionsrechnung des Vertrieblers) → schreibt **`Auszahlungen`** (Idempotenz über `Lexware ID`) + Gegen-`Beleg`. Notify **`payout.created` / `.settled`**; **`error.lexware_orphan`**.

**`[Process] Payment Reminder (Store)` · 6844567**
Trigger: **Mailhook**. Zahlungserinnerung/Mahnung → verknüpft `Beleg` mit dem `Umsatz` (Mahnstufe). Notify **`invoice.reminder_filed` / `.dunning_filed`**; **`error.reminder_unmatched`** (R26: `error.reminder_unreadable`-Zweig entfernt).

## `[Notify]`

**`[Notify] Telegram` · 6862968** · Hub (on-demand child). Kontrakt + Mechanik: **[[notify]]**.

## `[Resolve]` — geteilte Bausteine (synchron)

Neue Achse seit **2026-08-21**. Ein Resolver ist ein **Kind mit Rückgabe**: `Start scenario`
(`scenario-service:StartSubscenario`) → Auflösung → `Return output` (`scenario-service:ReturnData`),
aufgerufen mit **`Wait for the scenario to finish` = true**. Er löst nur auf und gibt zurück; was mit
Lücken passiert, entscheidet der Aufrufer. Ordner **382196 (`Resolver`)**.

**`[Resolve] Positions` · 7039710**
Löst je Positionszeile **Produktvariante · Preis am Leistungsdatum · Bestandszeile** auf —
**ein Aufruf je Beleg**, nicht je Zeile (Batch: `lines[]` rein, `resolved[]`/`unresolved[]` raus).
Liest `Produktvarianten` / `Preise` / `Bestände`; schreibt **nur** bei `create_missing_stock = true`
eine Bestandszeile (`airtable:upsertRecord`) — das darf ausschließlich
`[Process] Upload PDF (Delivery)`, weil nur eine Lieferung ein Sortiment eröffnet.
`purchase_source` schaltet den Einkaufswert: `variant` = `Produktvarianten.EK (netto)` (Übergabe) ·
`stock_avg` = `Bestände.Ø EK (netto)` (Rückholung).
Kein Notify — ein Baustein klingelt nicht, der Aufrufer meldet.
Geplante Nutzer: `[Process] Upload PDF (Inventory)` → `[Process] Invoice (Store)` →
`[Process] Upload PDF (Delivery)`. Kontrakt + Umhäng-Liste: [[refactor/reference-inventory]].

**`[Archive] Document PDF` · 7042723**
Ersetzt den Original-Anhang eines Belegs durch eine komprimierte Archivkopie: lädt selbst über
`document_url`, `ilovepdf:compressPdf`, Upload nach `content.airtable.com`, dann PATCH auf
`Belege.Beleg`. Eingaben `record_id` · `document_url` · `filename` (**ohne** `.pdf`) — Binärdaten
passen durch kein Szenario-Interface, deshalb lädt das Kind statt sie übergeben zu bekommen.
Nutzer: `[Process] Upload PDF (Delivery)` (Dateiname = Belegnummer) und
`[Process] Upload PDF (Inventory)` (Dateiname = Dedup-Schlüssel).
**Der Aufruf trägt beim Aufrufer `onerror: builtin:Ignore`** — der Block darf ausfallen, ohne den
Lauf zu kippen; das war schon vor der Extraktion so und muss so bleiben.
**Ausfall erkennen:** Kind-Lauf mit **2 statt 4 Operations** und der Beleg behält seine
Originaldatei (iLovePDF fällt intermittierend aus). **Nachträgliches Archivieren mit demselben
Dateinamen ist ein No-op** — siehe [[refactor/duplication-map]].

**Pflicht-Outputs jedes Resolvers:** `ok` (der Baustein lief) und `resolver_version`. Sie sind die
Gegenmaßnahme gegen ein beim Schreiben geleertes Interface ([[tools]]) — der Aufrufer **muss** hart
darauf filtern, sonst bucht er still auf leeren Identitäten.

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

## ⬜ Nicht gebaut: `[Scheduled] Daily Operations`

Der 07:00-Lauf fehlt noch. Er wäre der Emitter für **`invoice.overdue` · `task.digest` · `system.heartbeat`** — bis dahin sind diese Keys im Hub definiert, aber ohne Auslöser. (`inventory.due` hat seit 18.08. einen eigenen Auslöser → `[Maintain] Overdue Inventory Checks`.) Siehe [[operations]] / Audit-Remediation.

*Beziehungsgraph als Bild: `assets/diagrams/topology.html`.*
