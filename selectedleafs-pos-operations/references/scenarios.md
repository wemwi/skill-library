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
Übergabe-/Rückholprotokoll → schreibt **`Lieferungen`** + **`🟣 Lieferpositionen`** (stempelt `⚙ EK`). Notify **`delivery.booked`** / **`delivery.returned`**.

**`[Process] Upload PDF (Inventory)` · 6729541**
Bestandsprotokoll → schreibt **`Bestandsprüfungen`** + **`🟣 Bestandsprüfungspositionen`**. Notify **`inventory.checked`**.

**`[Process] Invoice (Store)` · 6633991**
Ausgangsrechnung → schreibt **`Umsätze`** + **`🟣 Umsatzpositionen`**; wählt `Konditionen` (eff-dated). Notify **`invoice.created` / `.paid` / `.voided` / `.written_off`**; **`task.terms_missing`** wenn keine passende Konditionen-Version.

**`[Process] Invoice (Sales)` · 6872651**
Eingangsrechnung (Provisionsrechnung des Vertrieblers) → schreibt **`Auszahlungen`** (Idempotenz über `⚙ Lexware ID`) + Gegen-`Beleg`. Notify **`payout.created` / `.settled`**; **`error.lexware_orphan`**.

**`[Process] Payment Reminder (Store)` · 6844567**
Trigger: **Mailhook**. Zahlungserinnerung/Mahnung → verknüpft `Beleg` mit dem `Umsatz` (Mahnstufe). Notify **`invoice.reminder_filed` / `.dunning_filed`**; **`error.reminder_unreadable` / `.reminder_unmatched`**.

## `[Notify]`

**`[Notify] Telegram` · 6862968** · Hub (on-demand child). Kontrakt + Mechanik: **[[notify]]**.

## `[Sync]` — Spiegel nach außen

**`[Sync] Inventory to Shopify` · 6805674**
Push der Bestände nach Shopify; danach die **City-Posts** aus `🟣 Bestände` (`⚙ Letzte Lieferung` = Belegdatum-Gate). Notify **`city.restock` / `city.strain_new`**; **`error.sync_aborted`**.

**`[Sync] Shopify Products to Airtable` · 6795533** · wöchentl. **So 04:00**
Upsert **`Produkte` / `Produktvarianten` / `Preise`** (Match über SKU). Notify **`sync.products`**; **`error.sync_aborted`**.

**`[Sync] Shopify Stores from Google Place API` · 6655783** · wöchentl. **So 05:00**
Aktualisiert **`Stores`** (Öffnungszeiten/Bewertung via Place API). Notify **`sync.stores`**.

**`[Sync] JTL Invoice to Lexware` · 6870495** · Ordner 377621
Trigger: **Mailhook**. JTL-Ausgangsrechnung → Lexware.

**`[Sync] Lexware Payments` · 6955541** · ohne Ordner
Trigger: **lexoffice `watchEvents` (`payment.changed`)**. Setzt den Zahlungsstatus auf **`Umsätze` / `Auszahlungen`** (inkl. **Teilzahlung**). Der definierte Sonderfall gegen die INSERT-only-Regel.

## `[Create]` — Onboarding

**`[Create] New Store Partner` · 6820980**
Trigger: **Formular** (personalisierter Link, `Akquise durch` vorbelegt; Eingangs-Guard Modul 2). Legt `Stores` + Shopify-Metaobjekt + Lexware-Kontakt an. Notify **`store.created`**; **`task.jtl_missing`**; **`error.store_failed` / `.store_partial`**.

**`[Create] New Sales Member` · 6821121**
Legt `Vertriebler` + Lexware-Kreditor + Provisions-Sheet an. Notify **`salesperson.created`**; **`task.telegram_missing`**; **`error.salesperson_failed`**. *(Emitter für `salesperson.onboarded` noch offen.)*

## `[Maintain]`

**`[Maintain] Airtable Webhooks` · 6830404** · Ordner 377621 · tägl. **04:30**
Hält die Airtable-Webhook-Registry frisch (Ablauf-Erneuerung).

---

## ⬜ Nicht gebaut: `[Scheduled] Daily Operations`

Der 07:00-Lauf fehlt noch. Er wäre der Emitter für **`inventory.due` · `invoice.overdue` · `task.digest` · `system.heartbeat`** — bis dahin sind diese vier Keys im Hub definiert, aber ohne Auslöser. Siehe [[operations]] / Audit-Remediation.

*Beziehungsgraph als Bild: `assets/diagrams/topology.html`.*
