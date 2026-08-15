# Nachrichtenkatalog

> **Runde 23** · **generiert aus `[Notify] Telegram` (6862968), Stand 2026-08-14.**
> **Der Hub (Modul 2 „Ereignis-Landkarte") ist die Wahrheit.** Diese Datei ist die lesbare, datierte Spiegelung der Texte. **Bei Textänderung: erst Modul 2 im Szenario ändern, dann diese Datei neu ziehen.** Die Mechanik (Renderer, Token, Channels, Empfänger-Logik) steht in [[notify]] — hier nur die Wortlaute.

**Register je Meldung:** `text` → Operations · `vtext` → Vertriebler · `ctext` → City. Fehlt ein Register, gibt es dorthin keine Meldung. Token-Regeln (`{abs}`, `{Vorname}`, `{Maps-URL}`, `{Saldoabruf}`, `{leer …}`/`{gesetzt …}`) siehe [[notify]].

---

## 📥 Vorgänge · Topic 586

### `store.created`
**Operations**
```
🎉 Neuer Store aktiv
{Store} · {Stadtteil}

Akquiriert durch {Vertriebler}
```
**Vertriebler**
```
🎉 Neuer Store erfasst
{Store} · {Postleitzahl} {Stadt}

Gute Arbeit {Vorname}.
```
**City** (mit Foto)
```
🎉 Neuer Partner: {Store}
{Stadtteil} · {Straße / Nr.}

🕒 <b>Öffnungszeiten</b>
{Öffnungszeiten}

<a href="{Maps-URL}">Google Maps öffnen</a>
```

### `salesperson.created`
**Operations**
```
🤝 Neuer Vertriebler aktiv
{Vertriebler} · {Ort}

Besteuerung: {Besteuerung}
```

### `salesperson.onboarded`
**Vertriebler**
```
👋 Willkommen bei selectedleafs, {Vorname}

<i>Dieser Chat hält dich ab sofort auf dem Laufenden. Wenn du Fragen hast, melde dich direkt bei Joscha.</i>

Deine Konditionen
• {Provision} % Provision auf jeden bezahlten Store-Umsatz
• fairer {Kostenanteil}-Kostensplit, abgezogen bei Lieferung

Deine Auszahlung
• jederzeit ab min. {Schwelle} offenem Saldo
• Rechnung ausschließlich an invoice@selectedleafs.com

Deine einzige Pflicht
• mindestens eine Bestandsprüfung alle {Intervall} Tage

Dein Store-Formular
• <a href="{Formularlink}">neuen Partnerstore anlegen</a>
• nur über diesen Link — er trägt deinen Namen

Schön, dass du dabei bist.
```

### `delivery.booked`
**Operations**
```
📦 Kommissionsware übergeben
{Vertriebler} · {Store}

Nettowarenwert: {Nettoverkaufswert}
Gesamtkosten: {Kosten}
Anteil {Vorname}: {Kostenanteil}

{leer Unterschrieben}Protokoll ohne Unterschrift.

<i>Geliefert am {Datum}</i>
```
**Vertriebler**
```
📦 Lieferung erfasst
{Store} · {Positionen} Sorten

Nettowarenwert: {Nettoverkaufswert}
Dein Kostenanteil: <b>{Kostenanteil}</b>

<i>Geliefert am {Datum}</i>
```

### `delivery.returned`
**Operations**
```
📥 Rückholung abgeschlossen
{Vertriebler} · {Store}

Nettowarenwert: {abs Nettoverkaufswert}
Gesamtkosten: {abs Kosten}
Anteil {Vorname}: {abs Kostenanteil}

{leer Unterschrieben}Protokoll ohne Unterschrift.

<i>Zurückgeholt am {Datum}</i>
```
**Vertriebler**
```
📥 Rückholung erfasst
{Store} · {Positionen} Sorten

Nettowarenwert: {abs Nettoverkaufswert}
Dein Kostenanteil: <b>{abs Kostenanteil}</b>

Die Kosten wurden deinem Saldo gutgeschrieben.

<i>Zurückgeholt am {Datum}</i>
```

### `inventory.checked`
**Operations**
```
📋 Bestandsprüfung abgeschlossen
{Vertriebler} · {Store}

IST-Differenz: {⚙ Differenz (Gesamt)} Einheiten
Differenzwert: {⚙ Nettoverkaufswert}

{leer Inventar geprüft}Inventar nicht geprüft.
{leer Unterschrieben}Protokoll ohne Unterschrift.

<i>Geprüft am {Datum}</i>
```
**Vertriebler**
```
📋 Bestandsprüfung erfasst
{Store} · {Positionen} Sorten

IST-Differenz: {⚙ Differenz (Gesamt)} Einheiten
Differenzwert: <b>{⚙ Nettoverkaufswert}</b>

{leer Inventar geprüft}⚠️ Das Inventar wurde nicht geprüft.
{leer Unterschrieben}⚠️ Das Protokoll ist nicht unterschrieben.

<i>Geprüft am {Datum}</i>
```

### `inventory.due`
**Operations**
```
⏳ Erinnerung zur Bestandsprüfung
{Vertriebler} · {Store}

Zuletzt geprüft am {Datum}
```
**Vertriebler**
```
⏳ Bestandsprüfung fällig
{Store} · Zuletzt geprüft am {Datum}

Zeit für einen Besuch — <a href="{Maps-URL}">Route öffnen</a>
```

### `invoice.created`
**Operations**
```
🧾 Rechnung {ID} erstellt
{Store} · Fällig am {⚙ Fällig am}


{gesetzt Hinweis}⚠️ Umsatz ohne Bestandsprüfung.
```
**Vertriebler**
```
🧾 Neue Rechnung {ID}
{Store} · Fällig am {⚙ Fällig am}


Bitte leite die Rechnung an den Store weiter.
```

### `invoice.paid`
**Operations**
```
✅ Zahlungseingang {ID}
{Store} · {Zahlungsverlauf}

Saldo {Vorname} (offen): {Offen}

{gesetzt Hinweis}⚠️ Umsatz ohne Bestandsprüfung.
```
**Vertriebler**
```
✅ Zahlung für {ID}
{Store} · {Zahlungsverlauf}

Deine Provision: +{Provision}
Dein Saldo (offen): <b>{Offen}</b>

Sauber. Genau so weiter.
```

### `invoice.overdue`
**Operations**
```
⏰ {ID} noch nicht bezahlt
{Store} · Fällig seit {⚙ Fällig am}

Nettoumsatz: {Nettoumsatz}
```

### `invoice.reminder_filed`
**Operations**
```
📄 Mahnstufe erreicht
{Store} · {Belegtyp}

<i>{ID} vom {Datum}</i>
```
**Vertriebler**
```
⏰ {ID} noch nicht bezahlt
{Store} · Fällig seit {⚙ Fällig am}

Nettoumsatz: {Nettoumsatz}
Deine Provision: <b>{Provision}</b>

Bitte leite die Zahlungserinnerung weiter, um deine Provision zu sichern.
```

### `invoice.dunning_filed`
**Operations**
```
📄 Mahnstufe erreicht
{Store} · {Belegtyp}

<i>{ID} vom {Datum}</i>
```
**Vertriebler**
```
📮 {ID} im Mahnlauf
{Store} · Fällig seit {⚙ Fällig am}

Nettoumsatz: {Nettoumsatz}
Deine Provision: <b>{Provision}</b>

Die Mahnung geht per Post raus. Ein Besuch bringt trotzdem meist mehr.
```

### `invoice.voided`
**Operations**
```
↩️ {ID} wurde storniert
{Store} · Rechnung vom {Datum}

Nettoumsatz: {Nettoumsatz}
Entgangener Ertrag: {Nettoertrag}

{gesetzt Hinweis}⚠️ Umsatz ohne Bestandsprüfung.
```
**Vertriebler**
```
↩️ {ID} wurde storniert
{Store} · Rechnung vom {Datum}

Entfallene Provision: <b>−{Provision}</b>
```

### `invoice.written_off`
**Operations**
```
❌ {ID} wurde ausgebucht
{Store} · Fällig seit {⚙ Fällig am}

Nettoumsatz: {Nettoumsatz}
Entgangener Ertrag: {Nettoertrag}

{gesetzt Hinweis}⚠️ Umsatz ohne Bestandsprüfung.
```
**Vertriebler**
```
❌ {ID} wurde ausgebucht
{Store} · Fällig seit {⚙ Fällig am}

Entfallene Provision: <b>−{Provision}</b>

Der Betrag konnte leider nicht eingetrieben werden.
```

### `payout.created`  · `saldo: created`
**Operations**
```
🧾 Auszahlung beantragt
{Vertriebler} · {Saldoabruf}

Betrag: {Betrag}

<i>Rechnung {Rechnungsnummer} vom {Datum}</i>
```
**Vertriebler**
```
🧾 Rechnung {Rechnungsnummer} erfasst

Betrag: <b>{Betrag}</b>

Auszahlung erfolgt in Kürze.
```

### `payout.settled`  · `saldo: settled`
**Operations**
```
💶 Auszahlung abgeschlossen
{Vertriebler} · {Saldoabruf}

Betrag: {Betrag}

Saldo {Vorname} (offen): {Offen}

<i>Rechnung {Rechnungsnummer} vom {Datum}</i>
```
**Vertriebler**
```
💶 Auszahlung unterwegs
Rechnung {Rechnungsnummer} vom {Datum}

Betrag: {Betrag}
Dein Saldo (offen): <b>{Offen}</b>

Danke für deine Arbeit! :)
```

### `city.restock` · City
```
📦 Frisch aufgefüllt
{Store} · {Stadtteil}

{Sorten}

<a href="{Maps-URL}">Google Maps öffnen</a>
```

### `city.strain_new` · City (ein Post je neuer Sorte)
```
🌿 Neu: {Sorte} ({Vein})
{Store} · {Stadtteil}

<a href="{Maps-URL}">Google Maps öffnen</a>
```

### `city.hours` · City · ⚠️ NEU (C6 — noch nicht im Hub)
> **Entwurf, provisorisch.** Copy gegen `selectedleafs-city-content` (Voice + Compliance) prüfen. Key im Hub Modul 2 noch anzulegen.
```
🕒 {Store} · Öffnungszeiten
{Stadtteil}

{Öffnungszeiten}

<a href="{Maps-URL}">Google Maps öffnen</a>
```

### `city.teach` · City · ⚠️ NEU (C7 „Lücke melden" — noch nicht im Hub)
> **Entwurf, provisorisch.** Intent des Teach-Posts mit dir schärfen; Copy gegen `selectedleafs-city-content` prüfen. Key im Hub Modul 2 noch anzulegen.
```
📣 {Store} · Deine Sorte fehlt?
{Stadtteil}

Sag dem Team vor Ort Bescheid — wir füllen zeitnah nach.

<a href="{Maps-URL}">Google Maps öffnen</a>
```

---

## 👉 Aufgaben · Topic 585

### `task.doctype_unclear`
**Operations**
```
👉 Belegtyp korrigieren
{ID} · Belegdatum: {Datum}

• Grund prüfen: {Hinweis}
• Belegtyp in Airtable setzen — danach läuft der Prozess weiter
```

### `task.terms_missing`
**Operations**
```
👉 Konditionen prüfen
{Vertriebler} · {Store}

• Leistungsdatum {Leistungsdatum} an der Rechnung prüfen
• Konditionen-Version mit »Gültig ab« ≤ Leistungsdatum anlegen

<i>{ID} vom {Rechnungsdatum}</i>
```

### `task.jtl_missing`
**Operations**
```
👉 JTL-Kunde und Lager anlegen
{Vertriebler} · {Store}

• Kunden anlegen, {Vertriebler} als Erstkontakt
• Lager mit gleichem Namen und gleicher Adresse anlegen
• Kundennummer in Airtable unter »ID« eintragen
```

### `task.telegram_missing`
**Operations**
```
👉 Telegram-Channel anlegen
{Vertriebler} · {Ort}

• Channel anlegen: „selectedleafs.com · {Vertriebler}"
• {Vorname} und „selectedleafs_sales_bot" einladen
• Chat-ID in »⚙ Telegram ID« eintragen
```

### `task.digest`  · 07:00-Lauf
**Operations**
```
🗒 Offene Aufgaben ({n})

{Zeilen}
```
*(`task.invoice_unlinked` / `task.beleg_no_pdf` haben bewusst keine eigene Meldung — sie erscheinen nur als Zeile hier.)*

---

## ⚙️ System · Topic 583
*(alle Token ctx; wiederholte Blöcke liefert der Emitter fertig als `{Zeilen}`.)*

### `sync.products`
**Operations**
```
⚙️ Produkt-Sync abgeschlossen
{n} Produkte · {m} Varianten

Produkte: {a} angelegt · {b} geändert
Varianten: {c} angelegt · {d} geändert
Preise: {e} korrigiert
```

### `sync.stores`
**Operations**
```
⚙️ Store-Sync abgeschlossen
{n} Stores · {m} aktualisiert

{Zeilen}
```

### `system.heartbeat`
**Operations**
```
☀️ Systemcheck
Stand {Datum} · {n} Szenarien aktiv

{Zeilen}
```

---

## 🛑 Störungen · Topic 584

### `error.reminder_unreadable`
```
🛑 Mahnschreiben nicht verarbeitbar
Betreff: {Betreff}

Grund: {Hinweis}
Folge: kein Beleg angelegt, keine Meldung an den Vertriebler
```

### `error.reminder_unmatched`
```
🛑 Mahnschreiben nicht zuordenbar
Rechnung {Rechnungsnummer} · {Belegtyp}

Grund: kein Umsatz mit dieser Nummer in Airtable
Folge: Beleg nicht abgelegt, keine Meldung an den Vertriebler
```

### `error.lexware_orphan`
```
🛑 Lexware-ID nicht zurückgeschrieben
{Vertriebler} · {Ort}

Grund: {Fehler}
Folge: der nächste Lauf legt eine Dublette an

{Lexware ID} von Hand in »⚙ Lexware ID« eintragen.
```

### `error.sync_aborted`
```
🛑 Sync abgebrochen
{Szenario} · Abbruch bei: {Stufe}

Grund: {Fehler}
Folge: {Folge}
```

### `error.store_failed`
```
🛑 Store konnte nicht angelegt werden
{Store} · Abbruch bei: {Stufe}

Grund: {Fehler}
Folge: kein Metaobjekt, kein Lexware-Kontakt, kein Broadcast

Hinweis steht im Airtable-Datensatz.
```

### `error.store_partial`
```
🛑 Store nur teilweise angelegt
{Store} · Abbruch bei: {Stufe}

Grund: {Fehler}
Angelegt: {Angelegt}
Fehlt: {Fehlt}
```

### `error.salesperson_failed`
```
🛑 Vertriebler konnte nicht angelegt werden
{Vertriebler} · Abbruch bei: {Stufe}

Grund: {Fehler}
Angelegt: {Angelegt}
Fehlt: {Fehlt}
```

---

*Unbekannter `key` → roh nach ⁉️ Unsortiert (Topic 1), nichts verworfen. Neu ziehen: `scenarios_get(6862968)` → Modul 2.*
