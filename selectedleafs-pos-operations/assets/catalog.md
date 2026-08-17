# Nachrichtenkatalog

> **Runde 24** · finalisierter Wortlaut, **Stand 2026-08-16**.
> **Achtung — dem Hub VORAUS:** dieser Satz wurde im Wortlaut-Durchgang festgelegt und ist die neue Text-SSoT. Der Hub (`[Report/Notify] Telegram Notifications` 6862968, Modul 2 „Ereignis-Landkarte") ist **noch nicht angeglichen** — die Angleichung läuft als Import-JSON. Bis dahin gilt: **diese Datei ist die Wahrheit, der Hub zieht nach**, nicht umgekehrt.
> Mechanik (Renderer, Token, Channels, Empfänger-Logik) steht in [[notify]] — hier nur die Wortlaute.

**Register je Meldung:** `text` → Operations · `vtext` → Vertriebler · `ctext` → City. Fehlt ein Register, gibt es dorthin keine Meldung. Token-Regeln (`{abs}`, `{Vorname}`, `{Maps-URL}`, `{Saldoabruf}`, `{leer …}`/`{gesetzt …}`) siehe [[notify]].

**Grammatik dieser Runde (fest):** Betreff = reines Ereignis (Emoji + Ereignis) — **kein Store-Name, keine Beleg-ID, kein Zustandswort**; Referenzen (Store, RG-Nr.) in die Infozeile. **Ops- und Sales-Label getrennt** (Ops = Ereignis-Substantiv, Sales = „… erfasst"). **RG-Nr. in die Infozeile**, Datum in die Belegzeile. **⚠️ auf jeder Vorbehaltszeile**, in Ops und Sales gleich, konditional. Reine Floskeln raus (Ausnahme: warmer Halbsatz an Meilensteinen — Onboarding, Auszahlung). Sales-Body trägt **einen** fetten Anker-Wert, Ops bleibt mager.

---

## 📥 Vorgänge · Topic 586

### `store.created`
**Operations**
```
🎉 Neuer Store
{Store} · {Stadtteil}

Akquiriert durch {Vertriebler}
```
**Vertriebler**
```
🎉 Neuer Store erfasst
{Store} · {Postleitzahl} {Stadt}
```
**City** (mit Foto)
```
🎉 Neuer Partner
{Store} · {Straße / Nr.}

🕒 <b>Öffnungszeiten</b>
{Öffnungszeiten}

<a href="{Maps-URL}">Google Maps öffnen</a>
```

### `salesperson.created`
**Operations**
```
🤝 Neuer Vertriebler
{Vertriebler} · {Ort}
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
{Vertriebler} bei {Store}

Nettoverkaufswert: {Nettoverkaufswert}
Gesamtkosten: {Kosten}

{leer Unterschrieben}⚠️ Protokoll ohne Unterschrift.

<i>Geliefert am {Datum}</i>
```
**Vertriebler**
```
📦 Lieferung erfasst
{Store} · {Menge (Stück)} Einheiten

Nettoverkaufswert: {Nettoverkaufswert}
Dein Kostenanteil: <b>{Kostenanteil}</b>

<i>Geliefert am {Datum}</i>
```

### `delivery.returned`
**Operations**
```
📥 Kommissionsware abgeholt
{Vertriebler} bei {Store}

Nettoverkaufswert: {abs Nettoverkaufswert}
Gesamtkosten: {abs Kosten}

{leer Unterschrieben}⚠️ Protokoll ohne Unterschrift.

<i>Zurückgeholt am {Datum}</i>
```
**Vertriebler**
```
📥 Rückholung erfasst
{Store} · {Menge (Stück)} Einheiten

Nettoverkaufswert: {abs Nettoverkaufswert}
Dein Kostenanteil: <b>{abs Kostenanteil}</b>

Die Kosten wurden deinem Saldo gutgeschrieben.

<i>Zurückgeholt am {Datum}</i>
```

### `inventory.checked`
**Operations**
```
📋 Bestand geprüft
{Vertriebler} bei {Store}

Differenz: {⚙ Differenz (Gesamt)} Einheiten
Nettoverkaufswert: {⚙ Nettoverkaufswert}

{leer Inventar geprüft}⚠️ Inventar nicht geprüft.
{leer Unterschrieben}⚠️ Protokoll ohne Unterschrift.

<i>Geprüft am {Datum}</i>
```
**Vertriebler**
```
📋 Bestandsprüfung erfasst
{Store} · {Stadtteil}

Differenz: {⚙ Differenz (Gesamt)} Einheiten
Nettoverkaufswert: <b>{⚙ Nettoverkaufswert}</b>

{leer Inventar geprüft}⚠️ Inventar nicht geprüft.
{leer Unterschrieben}⚠️ Protokoll ohne Unterschrift.

<i>Geprüft am {Datum}</i>
```

### `inventory.due`
**Operations**
```
⏳ Bestandsprüfung fällig
{Vertriebler} bei {Store}

Zuletzt geprüft am {Datum}
```
**Vertriebler**
```
⏳ Bestandsprüfung fällig
{Store} · {Stadtteil}

Zeit für einen Besuch — <a href="{Maps-URL}">Route öffnen</a>

Letzte Prüfung: {Datum}
```

### `invoice.created`
*Beträge gültig, sobald die Klingel hinter die Positionsschreibung wandert (Szenario-Änderung 1b, Import-JSON offen). Vorher rendert der Nettoumsatz-Rollup 0.*
**Operations**
```
🧾 Rechnung erstellt
{Store} · {ID}

Nettoumsatz: {Nettoumsatz}
Ertrag nach Provision: {Nettoertrag}

{gesetzt Hinweis}⚠️ Umsatz ohne Bestandsprüfung.

<i>Fällig am {⚙ Fällig am}</i>
```
**Vertriebler**
```
🧾 Neue Rechnung
{Store} · {ID}

Nettoumsatz: {Nettoumsatz}
Deine Provision: <b>{Provision}</b>

Bitte leite die Rechnung an den Store weiter.

<i>Fällig am {⚙ Fällig am}</i>
```

### `invoice.paid`
**Operations**
```
✅ Zahlungseingang ({Zahlungsverlauf})
{Store} · {ID}

Saldo {Vorname} (offen): {Offen}
```
**Vertriebler**
```
✅ Zahlungseingang ({Zahlungsverlauf})
{Store} · {ID}

Deine Provision: +{Provision}
Dein Saldo (offen): <b>{Offen}</b>
```

### `invoice.reminder_filed`
**Operations**
```
⏰ Rechnung überfällig
{Store} · {ID}

Fällig seit {⚙ Fällig am}
```
**Vertriebler**
```
⏰ Rechnung überfällig
{Store} · {ID}

Fällig seit {⚙ Fällig am}
```

### `invoice.dunning_filed`
**Operations**
```
📮 Mahnung erfasst
{Store} · {ID}

Fällig seit {⚙ Fällig am}
```
**Vertriebler**
```
📮 Rechnung im Mahnlauf
{Store} · {ID}

Fällig seit {⚙ Fällig am}
```

### `invoice.voided`
**Operations**
```
↩️ Rechnung storniert
{Store} · {ID}

Nettoumsatz: {Nettoumsatz}
Entgangener Ertrag: −{Nettoertrag}

<i>Erstellt am {Datum}</i>
```
**Vertriebler**
```
↩️ Rechnung storniert
{Store} · {ID}

Nettoumsatz: {Nettoumsatz}
Entfallene Provision: <b>−{Provision}</b>

<i>Erstellt am {Datum}</i>
```

### `invoice.written_off`
**Operations**
```
❌ Rechnung ausgebucht
{Store} · {ID}

Nettoumsatz: {Nettoumsatz}
Entgangener Ertrag: −{Nettoertrag}

<i>Fällig seit {⚙ Fällig am}</i>
```
**Vertriebler**
```
❌ Rechnung ausgebucht
{Store} · {ID}

Entfallene Provision: <b>−{Provision}</b>

Der Betrag konnte leider nicht eingetrieben werden.

<i>Fällig seit {⚙ Fällig am}</i>
```

### `payout.created` · `saldo: created`
**Operations**
```
💶 Auszahlung beantragt
{Vertriebler} · {Rechnungsnummer}

Betrag: {Betrag}

<i>Erstellt am {Datum}</i>
```
**Vertriebler**
```
🧾 Rechnung erfasst
{Rechnungsnummer} · {Saldoabruf}

Betrag: <b>{Betrag}</b>

Auszahlung erfolgt in Kürze.
```

### `payout.settled` · `saldo: settled`
**Operations**
```
💶 Auszahlung abgeschlossen
{Vertriebler} · {Rechnungsnummer}

Betrag: {Betrag}
Neuer Saldo: {Offen}

<i>Rechnung vom {Datum}</i>
```
**Vertriebler**
```
💶 Auszahlung unterwegs
{Rechnungsnummer} vom {Datum}

Betrag: {Betrag}
Neuer Saldo: <b>{Offen}</b>

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
🌿 Neue Sorte verfügbar
{Store} · {Stadtteil}

{Sorte} ({Vein}) ab sofort vor Ort erhältlich

<a href="{Maps-URL}">Google Maps öffnen</a>
```

---

## 👉 Aufgaben · Topic 585

### `task.jtl_missing`
**Operations**
```
👉 JTL Datensatz anlegen
Kunde & Lager für {Store}

• Kunden anlegen, Erstkontakt: {Vertriebler}
• Lager anlegen, Namen und Adresse wie Kunde
• Kundennummer in Airtable unter »ID« eintragen
```

### `task.telegram_missing`
**Operations**
```
👉 Telegram-Channel anlegen
für {Vertriebler} in Region {Ort}

• Channel anlegen: „selectedleafs.com · Region {Ort}"
• {Vorname} und „selectedleafs_sales_bot" einladen
• Chat-ID in »⚙ Telegram ID« eintragen
```

### `task.terms_missing`
**Operations**
```
👉 Konditionen prüfen
{Store} · {ID}

• Leistungsdatum {Leistungsdatum} an der Rechnung prüfen
• Konditionen-Version mit »Gültig ab« ≤ Leistungsdatum anlegen

<i>Rechnung vom {Rechnungsdatum}</i>
```

### `task.doctype_unclear`
**Operations**
```
👉 Belegtyp korrigieren
{ID} · Unbekannt

• Grund prüfen: Belegtyp nicht eindeutig erkannt
• Belegtyp in Airtable setzen — danach läuft der Prozess weiter

<i>Beleg vom {Datum}</i>
```

### `task.digest` · 07:00-Lauf
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
*Postet nur bei materieller Änderung — Preis korrigiert oder Sorte neu; ein No-Op-Lauf bleibt still.*
**Operations**
```
⚙️ Produkte aktualisiert
{n} Produkte · {m} Varianten

Produkte: {a} angelegt · {b} geändert
Varianten: {c} angelegt · {d} geändert
Preise: {e} korrigiert
```

*`sync.stores` (Erfolg) und `system.heartbeat` sind gestrichen (16.08.2026) — nur noch Störungen im System-/Sync-Bereich. `sync.inventory` bleibt gestrichen. Abbrüche laufen über `error.sync_aborted`.*

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

*Unbekannter `key` → roh nach ⁉️ Unsortiert (Topic 1), nichts verworfen. Nach der Hub-Angleichung neu ziehen: `scenarios_get(6862968)` → Modul 2.*
