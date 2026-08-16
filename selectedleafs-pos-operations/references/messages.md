# Nachrichten-Übersicht

> Zeigt pro Anlass, **was in welchen Channel gepostet wird** — mit **ausgefüllten Beispielwerten** statt Token, damit man die tatsächliche Nachricht sieht. Abgeleitet aus dem Live-Hub `[Notify] Telegram` (6862968); Emitter & Status aus Live-Inventar und Audit-Remediation, **Stand 15.08.2026**.
>
> Die **Wortlaut-Templates** (mit Token) sind die Text-SSoT in [[catalog]]; die **Mechanik** (Renderer, Token-Regeln, Channels, Empfänger-Logik) steht in [[notify]]. Hier steht keine Wahrheit, sondern die *Ansicht* — bei Textänderung: erst Modul 2 im `[Notify] Telegram`-Szenario, dann [[catalog]], dann bei Bedarf diese Datei.

**Beispieldaten (neutral, keine echten Partner-/Vertriebler-Daten):** Vertriebler `Max Berger` · Store `Kiosk Nordstern` · Stadtteil `Linden` · `30449 Hannover` · Rechnung `RG-10128-1` (12.08.2026, fällig 26.08.2026) · Nettoumsatz `312,40 €` · Provision `46,86 €` · offener Saldo `134,20 €`.

**Register:** **Operations** (Team-Forum, Topic) · **Vertriebler** (persönlicher Sales-Channel) · **City** (öffentlicher Stadt-Channel). Fehlt ein Register, gibt es dorthin keine Meldung — der Grund steht dann dabei.

**Status:** `live` = Emitter existiert und postet · `geplant` = hängt am noch nicht gebauten `[Scheduled] Daily Operations` · `offen` = Meldung definiert, Emitter (Klingel) im Szenario fehlt noch · `gestrichen` = nicht mehr aktiv.

---

## 📥 Vorgänge — ein Anlass, alle Register

### 🎉 `store.created` — Neuer Store
**Emitter** `[Create] New Store Partner` · **Status** `live`

**Operations** — 📥 Vorgänge · 586
```
🎉 Neuer Store aktiv
Kiosk Nordstern · Linden

Akquiriert durch Max Berger
```
**Vertriebler**
```
🎉 Neuer Store erfasst
Kiosk Nordstern · 30449 Hannover

Gute Arbeit Max.
```
**City** (mit Foto)
```
🎉 Neuer Partner: Kiosk Nordstern
Linden · Limmerstraße 12

🕒 Öffnungszeiten
Mo–Do    08:30–23:30
Fr–Sa    durchgehend
So       09:00–23:30

Google Maps öffnen → https://maps.google.com/…
```
**Begleitend** → 👉 `task.jtl_missing` ⚠ offen · 🛑 `error.store_failed` · 🛑 `error.store_partial`

### 🤝 `salesperson.created` — Neuer Vertriebler
**Emitter** `[Create] New Sales Member` · **Status** `live`

**Operations** — 📥 Vorgänge · 586
```
🤝 Neuer Vertriebler aktiv
Max Berger · Hannover

Besteuerung: Kleinunternehmer
```
**Vertriebler** — kein Kanal (existiert bei Anlage noch nicht)
**City** — —
**Begleitend** → 👉 `task.telegram_missing` ⚠ offen · 🛑 `error.salesperson_failed` · 🛑 `error.lexware_orphan`

### 👋 `salesperson.onboarded` — Onboarding
**Emitter** `Airtable-Webhook (⚙ Telegram ID)` · **Status** `offen`

**Operations** — —
**City** — —
**Vertriebler**
```
👋 Willkommen bei selectedleafs, Max

Dieser Chat hält dich ab sofort auf dem Laufenden. Wenn du Fragen hast, melde dich direkt bei Joscha.

Deine Konditionen
• 15 % Provision auf jeden bezahlten Store-Umsatz
• fairer 30 %-Kostensplit, abgezogen bei Lieferung

Deine Auszahlung
• jederzeit ab min. 250 € offenem Saldo
• Rechnung ausschließlich an invoice@selectedleafs.com

Deine einzige Pflicht
• mindestens eine Bestandsprüfung alle 14 Tage

Schön, dass du dabei bist.
```
*Schließt 👉 `task.telegram_missing`.*

### 📦 `delivery.booked` — Lieferung
**Emitter** `[Process] Upload PDF (Delivery)` · **Status** `live`

**Operations** — 📥 Vorgänge · 586
```
📦 Kommissionsware übergeben
Max Berger · Kiosk Nordstern

Nettowarenwert: 248,50 €
Gesamtkosten: 96,00 €
Anteil Max: 28,80 €

Protokoll ohne Unterschrift.

Geliefert am 12.08.2026
```
**Vertriebler**
```
📦 Lieferung erfasst
Kiosk Nordstern · 5 Sorten

Nettowarenwert: 248,50 €
Dein Kostenanteil: 28,80 €

Geliefert am 12.08.2026
```
**City** — Restock-Post (`city.restock`)
```
📦 Frisch aufgefüllt
Kiosk Nordstern · Linden

Indo Fusion (White), Suma Rush (White), Borneo Lift (Green)

Google Maps öffnen → https://maps.google.com/…
```
**City** — Neue-Sorte-Post (`city.strain_new`, je neuer Sorte ein eigener Post)
```
🌿 Neu: Java Spark (White)
Kiosk Nordstern · Linden

Google Maps öffnen → https://maps.google.com/…
```

### 📥 `delivery.returned` — Rückholung
**Emitter** `[Process] Upload PDF (Delivery)` · **Status** `live`

**Operations** — 📥 Vorgänge · 586
```
📥 Rückholung abgeschlossen
Max Berger · Kiosk Nordstern

Nettowarenwert: 248,50 €
Gesamtkosten: 96,00 €
Anteil Max: 28,80 €

Protokoll ohne Unterschrift.

Zurückgeholt am 12.08.2026
```
**Vertriebler**
```
📥 Rückholung erfasst
Kiosk Nordstern · 5 Sorten

Nettowarenwert: 248,50 €
Dein Kostenanteil: 28,80 €

Die Kosten wurden deinem Saldo gutgeschrieben.

Zurückgeholt am 12.08.2026
```
**City** — — (Leerbestand nie im Feed)

*Beträge werden hier ohne Vorzeichen gezeigt — Rückholungen buchen intern negativ (`{abs …}`).*

### 📋 `inventory.checked` — Bestandsprüfung
**Emitter** `[Process] Upload PDF (Inventory)` · **Status** `live`

**Operations** — 📥 Vorgänge · 586
```
📋 Bestandsprüfung abgeschlossen
Max Berger · Kiosk Nordstern

IST-Differenz: 12 Einheiten
Differenzwert: 41,00 €

Inventar nicht geprüft.
Protokoll ohne Unterschrift.

Geprüft am 12.08.2026
```
**Vertriebler**
```
📋 Bestandsprüfung erfasst
Kiosk Nordstern · 5 Sorten

IST-Differenz: 12 Einheiten
Differenzwert: 41,00 €

⚠️ Das Inventar wurde nicht geprüft.
⚠️ Das Protokoll ist nicht unterschrieben.

Geprüft am 12.08.2026
```
**City** — —

### ⏳ `inventory.due` — Prüfung fällig
**Emitter** `[Scheduled] Daily Operations` · **Status** `geplant`

**Operations** — 📥 Vorgänge · 586
```
⏳ Erinnerung zur Bestandsprüfung
Max Berger · Kiosk Nordstern

Zuletzt geprüft am 12.08.2026
```
**Vertriebler**
```
⏳ Bestandsprüfung fällig
Kiosk Nordstern · Zuletzt geprüft am 12.08.2026

Zeit für einen Besuch — Route öffnen → https://maps.google.com/…
```
**City** — —

### 🧾 `invoice.created` — Rechnung erstellt
**Emitter** `[Process] Invoice (Store)` · **Status** `live`

**Operations** — 📥 Vorgänge · 586
```
🧾 Rechnung RG-10128-1 erstellt
Kiosk Nordstern · Fällig am 26.08.2026

Nettoumsatz: 312,40 €
Ertrag nach Provision: 78,10 €
```
**Vertriebler**
```
🧾 Neue Rechnung RG-10128-1
Kiosk Nordstern · Fällig am 26.08.2026

Nettoumsatz: 312,40 €
Deine Provision: 46,86 €

Bitte leite die Rechnung an den Store weiter.
```
**City** — —
**Begleitend** → 👉 `task.terms_missing` · 👉 `task.invoice_unlinked` · 🛑 `error.checksum_mismatch`

### ✅ `invoice.paid` — Rechnung bezahlt
**Emitter** `[Process] Invoice (Store)` · **Status** `live`

**Operations** — 📥 Vorgänge · 586
```
✅ Zahlungseingang RG-10128-1
Kiosk Nordstern · pünktlich

Saldo Max (offen): 134,20 €
```
**Vertriebler**
```
✅ Zahlung für RG-10128-1
Kiosk Nordstern · pünktlich

Deine Provision: +46,86 €
Dein Saldo (offen): 134,20 €

Sauber. Genau so weiter.
```
**City** — —

### ⏰ `invoice.overdue` — Überfällig
**Emitter** `[Scheduled] Daily Operations` · **Status** `geplant`

**Operations** — 📥 Vorgänge · 586
```
⏰ RG-10128-1 noch nicht bezahlt
Kiosk Nordstern · Fällig seit 26.08.2026

Nettoumsatz: 312,40 €
```
**Vertriebler** — — (Ops-only)
**City** — —

### 📄 `invoice.reminder_filed` — Zahlungserinnerung
**Emitter** `[Process] Payment Reminder (Store)` · **Status** `live`

**Operations** — 📥 Vorgänge · 586
```
📄 Mahnstufe erreicht
Kiosk Nordstern · Zahlungserinnerung

RG-10128-1 vom 12.08.2026
```
**Vertriebler**
```
⏰ RG-10128-1 noch nicht bezahlt
Kiosk Nordstern · Fällig seit 26.08.2026

Nettoumsatz: 312,40 €
Deine Provision: 46,86 €

Bitte leite die Zahlungserinnerung weiter, um deine Provision zu sichern.
```
**City** — —
**Begleitend** → 🛑 `error.reminder_unmatched`

### 📮 `invoice.dunning_filed` — Mahnung
**Emitter** `[Process] Payment Reminder (Store)` · **Status** `live`

**Operations** — 📥 Vorgänge · 586
```
📄 Mahnstufe erreicht
Kiosk Nordstern · Mahnung

RG-10128-1 vom 12.08.2026
```
**Vertriebler**
```
📮 RG-10128-1 im Mahnlauf
Kiosk Nordstern · Fällig seit 26.08.2026

Nettoumsatz: 312,40 €
Deine Provision: 46,86 €

Die Mahnung geht per Post raus. Ein Besuch bringt trotzdem meist mehr.
```
**City** — —
**Begleitend** → 🛑 `error.reminder_unmatched`

### ❌ `invoice.written_off` — Ausgebucht
**Emitter** `[Process] Invoice (Store)` · **Status** `live`

**Operations** — 📥 Vorgänge · 586
```
❌ RG-10128-1 wurde ausgebucht
Kiosk Nordstern · Fällig seit 26.08.2026

Nettoumsatz: 312,40 €
Entgangener Ertrag: 78,10 €
```
**Vertriebler**
```
❌ RG-10128-1 wurde ausgebucht
Kiosk Nordstern · Fällig seit 26.08.2026

Entfallene Provision: −46,86 €

Der Betrag konnte leider nicht eingetrieben werden.
```
**City** — —

### ↩️ `invoice.voided` — Storniert
**Emitter** `[Process] Invoice (Store)` · **Status** `live`

**Operations** — 📥 Vorgänge · 586
```
↩️ RG-10128-1 wurde storniert
Kiosk Nordstern · Rechnung vom 12.08.2026

Nettoumsatz: 312,40 €
Entgangener Ertrag: 78,10 €
```
**Vertriebler**
```
↩️ RG-10128-1 wurde storniert
Kiosk Nordstern · Rechnung vom 12.08.2026

Entfallene Provision: −46,86 €
```
**City** — —

### 🧾 `payout.created` — Provisionsrechnung erfasst
**Emitter** `[Process] Invoice (Sales)` · **Status** `live`

**Operations** — 📥 Vorgänge · 586
```
🧾 Auszahlung beantragt
Max Berger · Voller Saldo

Betrag: 150,00 €

Rechnung RG-10128-1 vom 12.08.2026
```
**Vertriebler**
```
🧾 Rechnung RG-10128-1 erfasst

Betrag: 150,00 €

Auszahlung erfolgt in Kürze.
```
**City** — —

### 💶 `payout.settled` — Auszahlung abgeschlossen
**Emitter** `[Process] Invoice (Sales)` · **Status** `live`

**Operations** — 📥 Vorgänge · 586
```
💶 Auszahlung abgeschlossen
Max Berger · Voller Saldo

Betrag: 150,00 €

Saldo Max (offen): 134,20 €

Rechnung RG-10128-1 vom 12.08.2026
```
**Vertriebler**
```
💶 Auszahlung unterwegs
Rechnung RG-10128-1 vom 12.08.2026

Betrag: 150,00 €
Dein Saldo (offen): 134,20 €

Danke für deine Arbeit! :)
```
**City** — —

---

## 👉 Belege & Klassifikator

### 👉 `task.doctype_unclear` — Beleg — Typ unklar
**Emitter** `[Dispatch] Upload PDF` · **Status** `live`

**Operations** — 👉 Aufgaben · 585
```
👉 Belegtyp korrigieren
RG-10128-1 · Belegdatum: 12.08.2026

• Grund prüfen: Belegtyp nicht eindeutig erkannt
• Belegtyp in Airtable setzen — danach läuft der Prozess weiter
```
**Vertriebler** — — · **City** — —

---

## ⚙️ System & 07:00-Lauf
*Operations-only · alle Werte kommen fertig aus dem auslösenden Lauf (ctx).*

### ⚙️ `sync.products` — Produkt-Sync
**Emitter** `[Sync] Shopify Products to Airtable` · **Status** `live`

**Operations** — ⚙️ System · 583
```
⚙️ Produkt-Sync abgeschlossen
12 Produkte · 34 Varianten

Produkte: 2 angelegt · 3 geändert
Varianten: 5 angelegt · 4 geändert
Preise: 1 korrigiert
```
**Begleitend** → 🛑 `error.sync_aborted`

### ⚙️ `sync.stores` — Store-Sync
**Emitter** `[Sync] Shopify Stores from Google Place API` · **Status** `live`

**Operations** — ⚙️ System · 583
```
⚙️ Store-Sync abgeschlossen
8 Stores · 2 aktualisiert

Kiosk Nordstern: Öffnungszeiten, Bewertung
… und 1 weitere
```
**Begleitend** → 🛑 `error.sync_aborted`

### ⚙️ `sync.inventory` — Bestands-Push
**Emitter** `[Sync] Inventory to Shopify` · **Status** `gestrichen`
*Gestrichen — nur noch Störungen.*

**Operations** — ⚙️ System · 583
```
⚙️ Bestands-Push abgeschlossen
8 Stores · 3 mit Änderung

Kiosk Nordstern: +2 Sorten
… und 2 weitere

City-Posts: 1× 🌿 · 3× 📦
```
**Begleitend** → 🛑 `error.sync_aborted`

### 🗒 `task.digest` — Digest 07:00
**Emitter** `[Scheduled] Daily Operations` · **Status** `geplant`
*Postet nur bei ≥ 1 offenem Punkt.*

**Operations** — 👉 Aufgaben · 585
```
🗒 Offene Aufgaben (2)

3 T — JTL-Kunde anlegen · Kiosk Nordstern
1 T — Belegtyp korrigieren · BLG-00044
```

### ☀️ `system.heartbeat` — Systemcheck
**Emitter** `[Scheduled] Daily Operations` · **Status** `geplant`
*Die Meldung, deren Abwesenheit die Information ist.*

**Operations** — ⚙️ System · 583
```
☀️ Systemcheck
Stand 12.08.2026 · 15 Szenarien aktiv

Ohne Lauf: [Sync] Shopify Products
Unvollständige Ausführungen: 1 ([Process] Upload PDF (Inventory))
Webhooks: 3 aktiv · nächster Ablauf in 6 Tagen
```

---

## 🛑 Störungen — Referenz
*Alle im Topic 🛑 Störungen · 584. Werte kommen als ctx aus dem abbrechenden Lauf.*

### 🛑 `error.checksum_mismatch`
```
🛑 Rechnung ohne Positionen
Max Berger · Kiosk Nordstern

Grund: Positionssumme weicht vom Rechnungsbetrag ab
Folge: RG-10128-1 steht auf 0,00 € — Provision und Saldo sind falsch

Beleg in Lexware prüfen und erneut auf bezahlt setzen.
```

### 🛑 `error.reminder_unmatched`
```
🛑 Mahnschreiben nicht zuordenbar
Rechnung RG-10128-1 · Zahlungserinnerung

Grund: kein Umsatz mit dieser Nummer in Airtable
Folge: Beleg nicht abgelegt, keine Meldung an den Vertriebler
```

### 🛑 `error.lexware_orphan`
```
🛑 Lexware-ID nicht zurückgeschrieben
Max Berger · Hannover

Grund: HTTP 422 – Feld ungültig
Folge: der nächste Lauf legt eine Dublette an

a257b406-… von Hand in »⚙ Lexware ID« eintragen.
```

### 🛑 `error.sync_aborted`
```
🛑 Sync abgebrochen
[Sync] Inventory to Shopify · Abbruch bei: Belegdatum

Grund: HTTP 422 – Feld ungültig
Folge: kein Bestands-Push, keine City-Posts
```

### 🛑 `error.store_failed`
```
🛑 Store konnte nicht angelegt werden
Kiosk Nordstern · Abbruch bei: Kontakt anlegen

Grund: HTTP 422 – Feld ungültig
Folge: kein Metaobjekt, kein Lexware-Kontakt, kein Broadcast

Hinweis steht im Airtable-Datensatz.
```

### 🛑 `error.store_partial` · `offen`
```
🛑 Store nur teilweise angelegt
Kiosk Nordstern · Abbruch bei: Kontakt anlegen

Grund: HTTP 422 – Feld ungültig
Angelegt: Metaobjekt
Fehlt: Lexware-Kontakt
```

### 🛑 `error.salesperson_failed`
```
🛑 Vertriebler konnte nicht angelegt werden
Max Berger · Abbruch bei: Kontakt anlegen

Grund: HTTP 422 – Feld ungültig
Angelegt: Metaobjekt
Fehlt: Lexware-Kontakt
```

---

## 👉 Begleitende Aufgaben-Texte
*Werden zusammen mit dem auslösenden Vorgang in 👉 Aufgaben · 585 gepostet.*

### 👉 `task.jtl_missing`
```
👉 JTL-Kunde und Lager anlegen
Max Berger · Kiosk Nordstern

• Kunden anlegen, Max Berger als Erstkontakt
• Lager mit gleichem Namen und gleicher Adresse anlegen
• Kundennummer in Airtable unter »ID« eintragen
```

### 👉 `task.telegram_missing`
```
👉 Telegram-Channel anlegen
Max Berger · Hannover

• Channel anlegen: „selectedleafs.com · Max Berger"
• Max und „selectedleafs_sales_bot" einladen
• Chat-ID in »⚙ Telegram ID« eintragen
```

### 👉 `task.terms_missing`
```
👉 Konditionen prüfen
Max Berger · Kiosk Nordstern

• Leistungsdatum 31.07.2026 an der Rechnung prüfen
• Konditionen-Version mit »Gültig ab« ≤ Leistungsdatum anlegen

RG-10128-1 vom 12.08.2026
```

### 👉 `task.invoice_unlinked` / `task.beleg_no_pdf`
*Keine eigene Meldung — nur eine Zeile im Digest:*
```
Rechnung ohne Bestandsprüfung · RG-10128-1
Beleg ohne PDF · RG-10128-1
```

---

*Der öffentliche City-Channel hängt an genau zwei Anlässen: `delivery.booked` (→ `city.restock` / `city.strain_new`) und `store.created`. „geplant" hängt am noch nicht gebauten `[Scheduled] Daily Operations`; „offen" heißt: Meldung definiert, Emitter im Szenario fehlt noch.*
