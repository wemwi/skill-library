# Nachrichtenkatalog

> **Runde 26** · **Stand 2026-08-18** · alle Familien auf R26-Wortlaut. ⚙️ System + 🛑 Störungen aus `POS-Meldungen_System-Stoerungen_R26-final.md`, 📥 Vorgänge + 👉 Aufgaben aus `POS-Meldungen_Liste_Format-A.md`. **Q1: Infozeile (Zeile 2) durchgängig kursiv `<i>…</i>`.** Noch offen im Wortlaut: `invoice.reminder_filed` (Richtung).
> **Achtung — dem Hub VORAUS:** dieser Satz wurde im Wortlaut-Durchgang festgelegt und ist die neue Text-SSoT. Der Hub (`[Report/Notify] Telegram Notifications` 6862968, Modul 2 „Ereignis-Landkarte") ist **noch nicht angeglichen** — die Angleichung läuft als Import-JSON. Bis dahin gilt: **diese Datei ist die Wahrheit, der Hub zieht nach**, nicht umgekehrt.
> Mechanik (Renderer, Token, Channels, Empfänger-Logik) steht in [[notify]] — hier nur die Wortlaute.

**Register je Meldung:** `text` → Operations · `vtext` → Vertriebler · `ctext` → City. Fehlt ein Register, gibt es dorthin keine Meldung. Token-Regeln (`{abs}`, `{Vorname}`, `{Maps-URL}`, `{Saldoabruf}`, `{leer …}`/`{gesetzt …}`) siehe [[notify]].
**Runde-26-Änderungen:** Q1 (Infozeile durchgängig kursiv) · Mahnleiter-Verben `{Mahnstufe}` erstellt/versendet (reminder_filed + dunning_filed) · store.created „Akquiriert **von**" · inventory.checked „**Gesamtdifferenz**" · invoice.created-vtext „🧾 Neuer Umsatz / … **Ansprechpartner vor Ort**" · invoice.paid ohne `({Zahlungsverlauf})` + Ops-⚠️ „Zahlung nach Mahnung" (`{gesetzt Gemahnt}`) · JTL-Tasks tragen den Identifikator in der Infozeile · neuer Key `task.jtl_payment` · System kompakt (Richtung als Infozeile), `sync.stores`+`sync.inventory` reaktiviert · Störungen neu geschnitten, `error.reminder_unreadable` raus, `error.payment_unmatched` neu · `task.digest`/`task.telegram_missing` raus.

**Grammatik dieser Runde (fest):** Betreff = reines Ereignis (Emoji + Ereignis) — **kein Store-Name, keine Beleg-ID, kein Zustandswort**; Referenzen (Store, RG-Nr.) in die Infozeile. **Ops- und Sales-Label getrennt** (Ops = Ereignis-Substantiv, Sales = „… erfasst"). **RG-Nr. in die Infozeile**, Datum in die Belegzeile. **⚠️ auf jeder Vorbehaltszeile**, in Ops und Sales gleich, konditional. Reine Floskeln raus (Ausnahme: warmer Halbsatz an Meilensteinen — Onboarding, Auszahlung). Sales-Body trägt **einen** fetten Anker-Wert, Ops bleibt mager.

---

## 📥 Vorgänge · Topic 586

### `store.created`
**Operations**
```
🎉 Neuer Store
<i>{Store} · {Stadtteil}</i>

Akquiriert von {Vertriebler}
```
**Vertriebler**
```
🎉 Neuer Store erfasst
<i>{Store} · {Postleitzahl} {Stadt}</i>
```
**City** (mit Foto)
```
🎉 Neuer Partner
<i>{Store} · {Straße / Nr.}</i>

🕒 <b>Öffnungszeiten</b>
{Öffnungszeiten}

<a href="{Maps-URL}">Google Maps öffnen</a>
```

### `salesperson.created`
**Operations**
```
🤝 Neuer Vertriebler
<i>{Vertriebler} · {Ort}</i>
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
<i>{Vertriebler} bei {Store}</i>

Nettoverkaufswert: {Nettoverkaufswert}
Gesamtkosten: {Kosten}

{leer Unterschrieben}⚠️ Protokoll ohne Unterschrift.

<i>Geliefert am {Datum}</i>
```
**Vertriebler**
```
📦 Lieferung erfasst
<i>{Store} · {Menge (Stück)} Einheiten</i>

Nettoverkaufswert: {Nettoverkaufswert}
Dein Kostenanteil: <b>{Kostenanteil}</b>

<i>Geliefert am {Datum}</i>
```

### `delivery.returned`
**Operations**
```
📥 Kommissionsware abgeholt
<i>{Vertriebler} bei {Store}</i>

Nettoverkaufswert: {abs Nettoverkaufswert}
Gesamtkosten: {abs Kosten}

{leer Unterschrieben}⚠️ Protokoll ohne Unterschrift.

<i>Zurückgeholt am {Datum}</i>
```
**Vertriebler**
```
📥 Rückholung erfasst
<i>{Store} · {Menge (Stück)} Einheiten</i>

Nettoverkaufswert: {abs Nettoverkaufswert}
Dein Kostenanteil: <b>{abs Kostenanteil}</b>

Die Kosten wurden deinem Saldo gutgeschrieben.

<i>Zurückgeholt am {Datum}</i>
```

### `inventory.checked`
**Operations**
```
📋 Bestand geprüft
<i>{Vertriebler} bei {Store}</i>

Gesamtdifferenz: {⚙ Differenz (Gesamt)} Einheiten
Nettoverkaufswert: {⚙ Nettoverkaufswert}

{leer Inventar geprüft}⚠️ Inventar nicht geprüft.
{leer Unterschrieben}⚠️ Protokoll ohne Unterschrift.

<i>Geprüft am {Datum}</i>
```
**Vertriebler**
```
📋 Bestandsprüfung erfasst
<i>{Store} · {Stadtteil}</i>

Gesamtdifferenz: {⚙ Differenz (Gesamt)} Einheiten
Nettoverkaufswert: <b>{⚙ Nettoverkaufswert}</b>

{leer Inventar geprüft}⚠️ Inventar nicht geprüft.
{leer Unterschrieben}⚠️ Protokoll ohne Unterschrift.

<i>Geprüft am {Datum}</i>
```

### `inventory.due`
**Operations**
```
⏳ Bestandsprüfung fällig
<i>{Vertriebler} bei {Store}</i>

Zuletzt geprüft am {Datum}
```
**Vertriebler**
```
⏳ Bestandsprüfung fällig
<i>{Store} · {Stadtteil}</i>

👉 Zeit für einen Besuch
<a href="{Maps-URL}">Routenplanung öffnen</a>

<i>Letzte Prüfung: {Datum}</i>
```

### `invoice.created`
**Operations**
```
🧾 Rechnung erstellt
<i>{Store} · {ID}</i>

Nettoumsatz: {Nettoumsatz}
Ertrag nach Provision: {Nettoertrag}

{gesetzt Hinweis}⚠️ Umsatz ohne Bestandsprüfung.

<i>Fällig am {⚙ Fällig am}</i>
```
**Vertriebler**
```
🧾 Neuer Umsatz
<i>{Store} · {ID}</i>

Nettoumsatz: {Nettoumsatz}
Deine Provision: <b>{Provision}</b>

👉 Bitte leite die Rechnung an deinen Ansprechpartner vor Ort weiter.

<i>Fällig am {⚙ Fällig am}</i>
```

### `invoice.paid`
**Operations**
```
✅ Zahlungseingang
<i>{Store} · {ID}</i>

Saldo {Vorname} (offen): {Offen}

{gesetzt Gemahnt}⚠️ Zahlung nach Mahnung.
```
**Vertriebler**
```
✅ Zahlungseingang
<i>{Store} · {ID}</i>

Deine Provision: +{Provision}
Dein Saldo (offen): <b>{Offen}</b>
```

### `invoice.reminder_filed`
**Operations**
```
⏰ {Mahnstufe} erstellt
<i>{Store} · {ID}</i>

Fällig seit {⚙ Fällig am}
```
**Vertriebler**
```
⏰ {Mahnstufe} versendet
<i>{Store} · {ID}</i>

Fällig seit {⚙ Fällig am}
```

### `invoice.dunning_filed`
**Operations**
```
📮 {Mahnstufe} erstellt
<i>{Store} · {ID}</i>

Fällig seit {⚙ Fällig am}
```
**Vertriebler**
```
📮 {Mahnstufe} versendet
<i>{Store} · {ID}</i>

Fällig seit {⚙ Fällig am}
```

### `invoice.voided`
**Operations**
```
↩️ Rechnung storniert
<i>{Store} · {ID}</i>

Nettoumsatz: {Nettoumsatz}
Entgangener Ertrag: −{Nettoertrag}

<i>Erstellt am {Datum}</i>
```
**Vertriebler**
```
↩️ Rechnung storniert
<i>{Store} · {ID}</i>

Nettoumsatz: {Nettoumsatz}
Entfallene Provision: <b>−{Provision}</b>

<i>Erstellt am {Datum}</i>
```

### `invoice.written_off`
**Operations**
```
❌ Rechnung ausgebucht
<i>{Store} · {ID}</i>

Nettoumsatz: {Nettoumsatz}
Entgangener Ertrag: −{Nettoertrag}

<i>Fällig seit {⚙ Fällig am}</i>
```
**Vertriebler**
```
❌ Rechnung ausgebucht
<i>{Store} · {ID}</i>

Entfallene Provision: <b>−{Provision}</b>

Der Betrag konnte leider nicht eingetrieben werden.

<i>Fällig seit {⚙ Fällig am}</i>
```

### `payout.created` · `saldo: created`
**Operations**
```
💶 Auszahlung beantragt
<i>{Vertriebler} · {Rechnungsnummer}</i>

Betrag: {Betrag}

<i>Erstellt am {Datum}</i>
```
**Vertriebler**
```
🧾 Rechnung erfasst
<i>{Rechnungsnummer} · {Saldoabruf}</i>

Betrag: <b>{Betrag}</b>

Auszahlung erfolgt in Kürze.
```

### `payout.settled` · `saldo: settled`
**Operations**
```
💶 Auszahlung abgeschlossen
<i>{Vertriebler} · {Rechnungsnummer}</i>

Betrag: {Betrag}
Neuer Saldo: {Offen}

<i>Rechnung vom {Datum}</i>
```
**Vertriebler**
```
💶 Auszahlung unterwegs
<i>{Rechnungsnummer} vom {Datum}</i>

Betrag: {Betrag}
Neuer Saldo: <b>{Offen}</b>

Danke für deine Arbeit! :)
```

### `city.restock` · City
```
📦 Frisch aufgefüllt
<i>{Store} · {Stadtteil}</i>

{Sorten}

<a href="{Maps-URL}">Google Maps öffnen</a>
```

### `city.strain_new` · City (ein Post je neuer Sorte)
```
🌿 Neue Sorte verfügbar
<i>{Store} · {Stadtteil}</i>

{Sorte} ({Vein}) ab sofort vor Ort erhältlich

<a href="{Maps-URL}">Google Maps öffnen</a>
```

---

## 👉 Aufgaben · Topic 585
*Runde 26: Identifikator wandert in die (kursive) Infozeile. `task.telegram_missing` bleibt **gestrichen** (18.08.: ⚙ Telegram ID kommt aus dem Formular) — in Format-A noch gelistet, hier bewusst nicht.*

### `task.jtl_missing`
**Operations**
```
👉 JTL Datensatz anlegen
<i>Kunde & Lager für {Store}</i>

• Kunden anlegen, Erstkontakt: {Vertriebler}
• Lager anlegen, Namen und Adresse wie Kunde
• Kundennummer in Airtable unter »ID« eintragen
```

### `task.jtl_stock`
**Operations**
```
👉 Lager buchen (JTL)
<i>{Store} · {ID}</i>

• Lager Modul öffnen
• Wareneingang buchen

<i>Geliefert am {Datum}</i>
```

### `task.jtl_inventory_date`
**Operations**
```
👉 Prüfdatum setzen (JTL)
<i>{Store} · {⚙ Store ID}</i>

• Kunde öffnen
• Letzte Bestandsprüfung setzen

<i>Geprüft am {Datum}</i>
```

### `task.jtl_payment`
**Operations**
```
👉 Zahlung setzen (JTL)
<i>{Store} · {ID}</i>

• Kunde in JTL öffnen
• Zahlung als bezahlt buchen

<i>Bezahlt am {Datum}</i>
```

### `task.terms_missing`
**Operations**
```
👉 Konditionen prüfen
<i>{Store} · {ID}</i>

• Leistungsdatum {Leistungsdatum} an der Rechnung prüfen
• Konditionen-Version mit »Gültig ab« ≤ Leistungsdatum anlegen

<i>Rechnung vom {Rechnungsdatum}</i>
```

### `task.doctype_unclear`
**Operations**
```
👉 Belegtyp korrigieren
<i>{ID} · Unbekannt</i>

• Grund prüfen: Belegtyp nicht eindeutig erkannt
• Belegtyp in Airtable setzen — danach läuft der Prozess weiter

<i>Beleg vom {Datum}</i>
```

## ⚙️ System · Topic 583
*Titel „X aktualisiert" · kursive Infozeile = Richtung (ein Fakt) · **kein Datum** (Telegram stempelt die Sendezeit). Zähler-Token ctx.*

### `sync.products` · feuert nur bei materieller Änderung
**Operations**
```
⚙️ Produkte aktualisiert
<i>Shopify → Airtable</i>

+{a} Produkte · +{c} Varianten · {e} Preise
```

### `sync.stores` · Runde 26: R24-Streichung zurückgenommen
**Operations**
```
⚙️ Stores aktualisiert
<i>Google Places → Airtable</i>

{Stores} Stores · {Öffnungszeiten} Öffnungszeiten geändert
```

### `sync.inventory` · Runde 26: 10.08.-Streichung zurückgenommen
*Template = R26-final (aggregat). ACHTUNG: der 18.08. gebaute Emitter 6805674 klingelt **pro Store** mit `{Store}` (nicht `{Stores}`) — Shape-Konflikt vor dem Hub-Reimport klären.*
**Operations**
```
⚙️ Bestand aktualisiert
<i>Airtable → Shopify</i>

{Stores} Stores · {Varianten} Varianten
```

*`system.heartbeat` bleibt gestrichen. Abbrüche laufen über `error.sync_aborted`.*

---

## 🛑 Störungen · Topic 584
*Skelett: 2–3-Wort-Betreff (der Fehler-Zustand IST das Ereignis) · kursive Infozeile mit 2 label-freien Fakten (Fachbezug · `{Stufe}`/Unterscheider) · Body `Grund:` (Wert), `Folge:` nur wo nicht impliziert · **👉-Aktionszeile als eigener Absatz**. Familie = 7 Keys (`error.reminder_unreadable` gestrichen). `{Fehler}` trägt den menschlichen Grund (Feld/Stufe), nie den rohen HTTP-Status.*

### `error.reminder_unmatched`
```
🛑 Mahnschreiben ohne Treffer
<i>{Rechnungsnummer} · {Belegtyp}</i>

Grund: keine Rechnung mit dieser Nummer in Airtable

👉 Nummer prüfen — Tippfehler im Betreff oder Umsatz fehlt
```

### `error.lexware_orphan`
```
🛑 Lexware-ID nicht gespeichert
<i>{Vertriebler} · {Ort}</i>

Grund: {Fehler}
Folge: der nächste Lauf legt eine Dublette an

👉 {Lexware ID} von Hand in »⚙ Lexware ID« eintragen
```

### `error.sync_aborted`
```
🛑 Sync abgebrochen
<i>{Szenario} · {Stufe}</i>

Grund: {Fehler}
Folge: {Folge}

👉 {Szenario} prüfen, wenn der Fehler bleibt
```

### `error.store_failed`
```
🛑 Store nicht angelegt
<i>{Store} · {Stufe}</i>

Grund: {Fehler}
Folge: kein Metaobjekt, kein Lexware-Kontakt, kein Broadcast

👉 Hinweis im Datensatz prüfen: {Record-Link}
```

### `error.store_partial`
```
🛑 Store unvollständig
<i>{Store} · {Stufe}</i>

Grund: {Fehler}

👉 Datensatz öffnen, Onboarding erneut auslösen: {Record-Link}
```

### `error.salesperson_failed` · ein Key, neutraler Titel
```
🛑 Vertriebler-Anlage gestoppt
<i>{Vertriebler} · Eingangsprüfung</i>

Grund: {Fehler}

👉 Grund prüfen und Anlage erneut anstoßen
```

### `error.payment_unmatched` · NEU (Key wurde geklingelt, Template fehlte)
```
🛑 Zahlung ohne Treffer
<i>{Rechnungsnummer}</i>

Grund: keine Rechnung mit dieser Nummer in Airtable
Folge: Zahlungsstatus nicht gesetzt — der Umsatz bleibt offen

👉 Prüfen, ob {Rechnungsnummer} als Umsatz existiert
```

---

*Unbekannter `key` → roh nach ⁉️ Unsortiert (Topic 1), nichts verworfen. Nach der Hub-Angleichung neu ziehen: `scenarios_get(6862968)` → Modul 2.*
