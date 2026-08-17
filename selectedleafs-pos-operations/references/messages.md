# Nachrichten-Übersicht

> Zeigt pro Anlass, **was in welchen Channel gepostet wird** — mit **ausgefüllten Beispielwerten** statt Token. Abgeleitet aus dem finalisierten Wortlaut (Katalog Runde 24), **Stand 2026-08-16**.
>
> Die **Wortlaut-Templates** (mit Token) sind die Text-SSoT in [[catalog]]; die **Mechanik** (Renderer, Token-Regeln, Channels) steht in [[notify]]. Hier steht keine Wahrheit, sondern die *Ansicht*. **Achtung:** Katalog Runde 24 ist dem Hub-Modul 2 voraus — die Angleichung läuft als Import-JSON.

**Beispieldaten:** Vertriebler `Max Berger` · Store `Kiosk Nordstern` · Stadtteil `Linden` · `30449 Hannover` · `Limmerstraße 12` · Rechnung `RG-10128-1` (12.08.2026, fällig 26.08.2026) · Nettoverkaufswert `248,50 €` · Gesamtkosten `96,00 €` · Kostenanteil `28,80 €` · `60 Einheiten` · Bestandsdifferenz `12 Einheiten` / `41,00 €` · Nettoumsatz `312,40 €` · Provision `46,86 €` · Ertrag `78,10 €` · offener Saldo `134,20 €` · Auszahlung `150,00 €`.

**Register:** **Operations** (Team-Forum, Topic) · **Vertriebler** (persönlicher Sales-Channel) · **City** (öffentlicher Stadt-Channel).

**Status:** `live` = Emitter postet · `geplant` = hängt am noch nicht gebauten `[Scheduled] Daily Operations` · `offen` = Meldung definiert, Emitter fehlt · `gestrichen` = nicht aktiv.

---

## 📥 Vorgänge — ein Anlass, alle Register

### 🎉 `store.created` — Neuer Store · `live`
**Operations** — 📥 Vorgänge · 586
```
🎉 Neuer Store
Kiosk Nordstern · Linden

Akquiriert durch Max Berger
```
**Vertriebler**
```
🎉 Neuer Store erfasst
Kiosk Nordstern · 30449 Hannover
```
**City** (mit Foto)
```
🎉 Neuer Partner
Kiosk Nordstern · Limmerstraße 12

🕒 Öffnungszeiten
Mo–Do    08:30–23:30
Fr–Sa    durchgehend
So       09:00–23:30

Google Maps öffnen → https://maps.google.com/…
```
**Begleitend** → 👉 `task.jtl_missing` · 🛑 `error.store_failed` · 🛑 `error.store_partial`

### 🤝 `salesperson.created` — Neuer Vertriebler · `live`
**Operations** — 📥 Vorgänge · 586
```
🤝 Neuer Vertriebler
Max Berger · Hannover
```
**Vertriebler** — kein Kanal (existiert bei Anlage noch nicht) · **City** — —
**Begleitend** → 👉 `task.telegram_missing` · 🛑 `error.salesperson_failed` · 🛑 `error.lexware_orphan`

### 👋 `salesperson.onboarded` — Onboarding · `offen`
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

Dein Store-Formular
• neuen Partnerstore anlegen → https://…
• nur über diesen Link — er trägt deinen Namen

Schön, dass du dabei bist.
```
*Schließt 👉 `task.telegram_missing`.*

### 📦 `delivery.booked` — Lieferung · `live`
**Operations** — 📥 Vorgänge · 586
```
📦 Kommissionsware übergeben
Max Berger bei Kiosk Nordstern

Nettoverkaufswert: 248,50 €
Gesamtkosten: 96,00 €

⚠️ Protokoll ohne Unterschrift.

Geliefert am 12.08.2026
```
**Vertriebler**
```
📦 Lieferung erfasst
Kiosk Nordstern · 60 Einheiten

Nettoverkaufswert: 248,50 €
Dein Kostenanteil: 28,80 €

Geliefert am 12.08.2026
```
**City** — Restock (`city.restock`)
```
📦 Frisch aufgefüllt
Kiosk Nordstern · Linden

Indo Fusion (White), Suma Rush (White), Borneo Lift (Green)

Google Maps öffnen → https://maps.google.com/…
```
**City** — neue Sorte (`city.strain_new`, je Sorte ein Post)
```
🌿 Neue Sorte verfügbar
Kiosk Nordstern · Linden

Java Spark (White) ab sofort vor Ort erhältlich

Google Maps öffnen → https://maps.google.com/…
```

### 📥 `delivery.returned` — Rückholung · `live`
**Operations** — 📥 Vorgänge · 586
```
📥 Kommissionsware abgeholt
Max Berger bei Kiosk Nordstern

Nettoverkaufswert: 248,50 €
Gesamtkosten: 96,00 €

⚠️ Protokoll ohne Unterschrift.

Zurückgeholt am 12.08.2026
```
**Vertriebler**
```
📥 Rückholung erfasst
Kiosk Nordstern · 60 Einheiten

Nettoverkaufswert: 248,50 €
Dein Kostenanteil: 28,80 €

Die Kosten wurden deinem Saldo gutgeschrieben.

Zurückgeholt am 12.08.2026
```
**City** — — (Leerbestand nie im Feed)
*Beträge ohne Vorzeichen; Rückholungen buchen intern negativ (`{abs …}`).*

### 📋 `inventory.checked` — Bestandsprüfung · `live`
**Operations** — 📥 Vorgänge · 586
```
📋 Bestand geprüft
Max Berger bei Kiosk Nordstern

Differenz: 12 Einheiten
Nettoverkaufswert: 41,00 €

⚠️ Inventar nicht geprüft.
⚠️ Protokoll ohne Unterschrift.

Geprüft am 12.08.2026
```
**Vertriebler**
```
📋 Bestandsprüfung erfasst
Kiosk Nordstern · Linden

Differenz: 12 Einheiten
Nettoverkaufswert: 41,00 €

⚠️ Inventar nicht geprüft.
⚠️ Protokoll ohne Unterschrift.

Geprüft am 12.08.2026
```
**City** — —

### ⏳ `inventory.due` — Prüfung fällig · `geplant`
**Operations** — 📥 Vorgänge · 586
```
⏳ Bestandsprüfung fällig
Max Berger bei Kiosk Nordstern

Zuletzt geprüft am 12.08.2026
```
**Vertriebler**
```
⏳ Bestandsprüfung fällig
Kiosk Nordstern · Linden

Zeit für einen Besuch — Route öffnen → https://maps.google.com/…

Letzte Prüfung: 12.08.2026
```
**City** — —

### 🧾 `invoice.created` — Rechnung erstellt · `live`
*Beträge gültig, sobald die Klingel hinter die Positionsschreibung wandert (Szenario-Änderung 1b).*
**Operations** — 📥 Vorgänge · 586
```
🧾 Rechnung erstellt
Kiosk Nordstern · RG-10128-1

Nettoumsatz: 312,40 €
Ertrag nach Provision: 78,10 €

⚠️ Umsatz ohne Bestandsprüfung.

Fällig am 26.08.2026
```
**Vertriebler**
```
🧾 Neue Rechnung
Kiosk Nordstern · RG-10128-1

Nettoumsatz: 312,40 €
Deine Provision: 46,86 €

Bitte leite die Rechnung an den Store weiter.

Fällig am 26.08.2026
```
**Begleitend** → 👉 `task.terms_missing`

### ✅ `invoice.paid` — Rechnung bezahlt · `live`
**Operations** — 📥 Vorgänge · 586
```
✅ Zahlungseingang (pünktlich)
Kiosk Nordstern · RG-10128-1

Saldo Max (offen): 134,20 €
```
**Vertriebler**
```
✅ Zahlungseingang (pünktlich)
Kiosk Nordstern · RG-10128-1

Deine Provision: +46,86 €
Dein Saldo (offen): 134,20 €
```
*`{Zahlungsverlauf}`: pünktlich / nach Zahlungserinnerung / nach Mahnung.*

### ⏰ `invoice.reminder_filed` — Zahlungserinnerung · `live`
**Operations** — 📥 Vorgänge · 586
```
⏰ Rechnung überfällig
Kiosk Nordstern · RG-10128-1

Fällig seit 26.08.2026
```
**Vertriebler**
```
⏰ Rechnung überfällig
Kiosk Nordstern · RG-10128-1

Fällig seit 26.08.2026
```
**Begleitend** → 🛑 `error.reminder_unmatched`

### 📮 `invoice.dunning_filed` — Mahnung · `live`
**Operations** — 📥 Vorgänge · 586
```
📮 Mahnung erfasst
Kiosk Nordstern · RG-10128-1

Fällig seit 26.08.2026
```
**Vertriebler**
```
📮 Rechnung im Mahnlauf
Kiosk Nordstern · RG-10128-1

Fällig seit 26.08.2026
```

### ↩️ `invoice.voided` — Storniert · `live`
**Operations** — 📥 Vorgänge · 586
```
↩️ Rechnung storniert
Kiosk Nordstern · RG-10128-1

Nettoumsatz: 312,40 €
Entgangener Ertrag: −78,10 €

Erstellt am 12.08.2026
```
**Vertriebler**
```
↩️ Rechnung storniert
Kiosk Nordstern · RG-10128-1

Nettoumsatz: 312,40 €
Entfallene Provision: −46,86 €

Erstellt am 12.08.2026
```

### ❌ `invoice.written_off` — Ausgebucht · `live`
**Operations** — 📥 Vorgänge · 586
```
❌ Rechnung ausgebucht
Kiosk Nordstern · RG-10128-1

Nettoumsatz: 312,40 €
Entgangener Ertrag: −78,10 €

Fällig seit 26.08.2026
```
**Vertriebler**
```
❌ Rechnung ausgebucht
Kiosk Nordstern · RG-10128-1

Entfallene Provision: −46,86 €

Der Betrag konnte leider nicht eingetrieben werden.

Fällig seit 26.08.2026
```

### 💶 `payout.created` — Provisionsrechnung erfasst · `live`
**Operations** — 📥 Vorgänge · 586
```
💶 Auszahlung beantragt
Max Berger · RG-10128-1

Betrag: 150,00 €

Erstellt am 12.08.2026
```
**Vertriebler**
```
🧾 Rechnung erfasst
RG-10128-1 · Voller Saldo

Betrag: 150,00 €

Auszahlung erfolgt in Kürze.
```

### 💶 `payout.settled` — Auszahlung abgeschlossen · `live`
**Operations** — 📥 Vorgänge · 586
```
💶 Auszahlung abgeschlossen
Max Berger · RG-10128-1

Betrag: 150,00 €
Neuer Saldo: 134,20 €

Rechnung vom 12.08.2026
```
**Vertriebler**
```
💶 Auszahlung unterwegs
RG-10128-1 vom 12.08.2026

Betrag: 150,00 €
Neuer Saldo: 134,20 €

Danke für deine Arbeit! :)
```

*`invoice.overdue` gestrichen (16.08.2026) — der Überfällig-Hinweis läuft über `reminder_filed`.*

---

## 👉 Aufgaben · 585

### 👉 `task.jtl_missing` · `offen`
```
👉 JTL Datensatz anlegen
Kunde & Lager für Kiosk Nordstern

• Kunden anlegen, Erstkontakt: Max Berger
• Lager anlegen, Namen und Adresse wie Kunde
• Kundennummer in Airtable unter »ID« eintragen
```

### 👉 `task.telegram_missing` · `offen`
```
👉 Telegram-Channel anlegen
für Max Berger in Region Hannover

• Channel anlegen: „selectedleafs.com · Region Hannover"
• Max und „selectedleafs_sales_bot" einladen
• Chat-ID in »⚙ Telegram ID« eintragen
```

### 👉 `task.terms_missing` · `offen`
```
👉 Konditionen prüfen
Kiosk Nordstern · RG-10128-1

• Leistungsdatum 31.07.2026 an der Rechnung prüfen
• Konditionen-Version mit »Gültig ab« ≤ Leistungsdatum anlegen

Rechnung vom 12.08.2026
```

### 👉 `task.doctype_unclear` · `live`
```
👉 Belegtyp korrigieren
RG-10128-1 · Unbekannt

• Grund prüfen: Belegtyp nicht eindeutig erkannt
• Belegtyp in Airtable setzen — danach läuft der Prozess weiter

Beleg vom 12.08.2026
```

### 🗒 `task.digest` — Digest 07:00 · `geplant`
*Postet nur bei ≥ 1 offenem Punkt.*
```
🗒 Offene Aufgaben (2)

3 T — JTL-Kunde anlegen · Kiosk Nordstern
1 T — Belegtyp korrigieren · BLG-00044
```
*(`task.invoice_unlinked` / `task.beleg_no_pdf` — nur Zeile im Digest.)*

---

## ⚙️ System · 583

### ⚙️ `sync.products` — Produkt-Sync · `live`
*Postet nur bei materieller Änderung (Preis korrigiert / Sorte neu); No-Op-Lauf bleibt still.*
```
⚙️ Produkte aktualisiert
12 Produkte · 34 Varianten

Produkte: 2 angelegt · 3 geändert
Varianten: 5 angelegt · 4 geändert
Preise: 1 korrigiert
```
**Begleitend** → 🛑 `error.sync_aborted`

### `sync.stores` · `gestrichen` · `system.heartbeat` · `gestrichen` · `sync.inventory` · `gestrichen`
*System-/Sync-Bereich meldet nur noch Störungen (16.08.2026). Abbrüche → `error.sync_aborted`.*

---

## 🛑 Störungen · 584
*Alle im Topic 🛑 Störungen · 584. Werte als ctx aus dem abbrechenden Lauf.*

```
🛑 Mahnschreiben nicht verarbeitbar
Betreff: Zahlungserinnerung 10128

Grund: PDF nicht lesbar
Folge: kein Beleg angelegt, keine Meldung an den Vertriebler
```
```
🛑 Mahnschreiben nicht zuordenbar
Rechnung RG-10128-1 · Zahlungserinnerung

Grund: kein Umsatz mit dieser Nummer in Airtable
Folge: Beleg nicht abgelegt, keine Meldung an den Vertriebler
```
```
🛑 Lexware-ID nicht zurückgeschrieben
Max Berger · Hannover

Grund: HTTP 422 – Feld ungültig
Folge: der nächste Lauf legt eine Dublette an

a257b406-… von Hand in »⚙ Lexware ID« eintragen.
```
```
🛑 Sync abgebrochen
[Sync] Inventory to Shopify · Abbruch bei: Belegdatum

Grund: HTTP 422 – Feld ungültig
Folge: kein Bestands-Push, keine City-Posts
```
```
🛑 Store konnte nicht angelegt werden
Kiosk Nordstern · Abbruch bei: Kontakt anlegen

Grund: HTTP 422 – Feld ungültig
Folge: kein Metaobjekt, kein Lexware-Kontakt, kein Broadcast

Hinweis steht im Airtable-Datensatz.
```
```
🛑 Store nur teilweise angelegt
Kiosk Nordstern · Abbruch bei: Kontakt anlegen

Grund: HTTP 422 – Feld ungültig
Angelegt: Metaobjekt
Fehlt: Lexware-Kontakt
```
```
🛑 Vertriebler konnte nicht angelegt werden
Max Berger · Abbruch bei: Kontakt anlegen

Grund: HTTP 422 – Feld ungültig
Angelegt: Metaobjekt
Fehlt: Lexware-Kontakt
```

---

*City-Channel hängt an genau zwei Anlässen: `delivery.booked` (→ `city.restock` / `city.strain_new`) und `store.created`.*
