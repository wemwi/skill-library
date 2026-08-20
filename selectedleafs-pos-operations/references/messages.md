# Nachrichten-Übersicht

> Zeigt pro Anlass, **was in welchen Channel gepostet wird** — mit **ausgefüllten Beispielwerten** statt Token. Alle Familien auf **Runde 26 (Stand 2026-08-18)**. Infozeilen sind in den Live-Templates durchgängig kursiv (Q1); hier plain gerendert.
>
> Die **Wortlaut-Templates** (mit Token) sind die Text-SSoT in [[catalog]]; die **Mechanik** (Renderer, Token-Regeln, Channels) steht in [[notify]]. Hier steht keine Wahrheit, sondern die *Ansicht*. **Achtung:** Katalog Runde 25 ist dem Hub-Modul 2 voraus — die Angleichung läuft als Import-JSON.

**Beispieldaten:** Vertriebler `Max Berger` · Store `Kiosk Nordstern` (JTL-Kundennummer `10132`) · Stadtteil `Linden` · `30449 Hannover` · `Limmerstraße 12` · Lieferung `UL-10042-1` · Rechnung `RG-10128-1` (12.08.2026, fällig 26.08.2026) · Nettoverkaufswert `248,50 €` · Gesamtkosten `96,00 €` · Kostenanteil `28,80 €` · `60 Einheiten` · Bestandsdifferenz `12 Einheiten` / `41,00 €` · Nettoumsatz `312,40 €` · Provision `46,86 €` · Ertrag `78,10 €` · offener Saldo `134,20 €` · Auszahlung `150,00 €`.

**Register:** **Operations** (Team-Forum, Topic) · **Vertriebler** (persönlicher Sales-Channel) · **City** (öffentlicher Stadt-Channel).

**Status:** `live` = Emitter postet · `gebaut · … ausstehend` = Emitter/Klingel gebaut, Reimport in Make (bzw. Import des neuen Szenarios) noch offen · `geplant` = hängt an einem noch zu bauenden Trigger · `offen` = Meldung definiert, Emitter/Trigger fehlt · `gestrichen` = nicht aktiv.

---

## 📥 Vorgänge — ein Anlass, alle Register

### 🎉 `store.created` — Neuer Store · `live`
**Operations** — 📥 Vorgänge · 586
```
🎉 Neuer Store
Kiosk Nordstern · Linden

Akquiriert von Max Berger
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
**Begleitend** → 🛑 `error.salesperson_failed` · 🛑 `error.lexware_orphan`

### 👋 `salesperson.onboarded` — Onboarding · `gebaut · Reimport 6821121 ausstehend`
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
• mindestens eine Bestandsprüfung alle 30 Tage

Dein Store-Formular
• neuen Partnerstore anlegen → https://…
• nur über diesen Link — er trägt deinen Namen

Schön, dass du dabei bist.
```

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
**Begleitend** → 👉 `task.jtl_stock`

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

Gesamtdifferenz: 12 Einheiten
Nettoverkaufswert: 41,00 €

⚠️ Inventar nicht geprüft.
⚠️ Protokoll ohne Unterschrift.

Geprüft am 12.08.2026
```
**Vertriebler**
```
📋 Bestandsprüfung erfasst
Kiosk Nordstern · Linden

Gesamtdifferenz: 12 Einheiten
Nettoverkaufswert: 41,00 €

⚠️ Inventar nicht geprüft.
⚠️ Protokoll ohne Unterschrift.

Geprüft am 12.08.2026
```
**City** — —
**Begleitend** → 👉 `task.jtl_inventory_date`

### ⏳ `inventory.due` — Prüfung fällig · `gebaut · Import ausstehend`
*Auslöser ist das eigene Szenario `[Maintain] Overdue Inventory Checks` (Schedule tgl. ~07:00, gebaut 18.08.2026 — Import + Schedule-Aktivierung noch offen). Vertrag siehe [[scenarios]].*
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

👉 Zeit für einen Besuch — Route öffnen → https://maps.google.com/…

Letzte Prüfung: 12.08.2026
```
**City** — —

### 🧾 `invoice.created` — Rechnung erstellt · `live`
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
🧾 Neuer Umsatz
Kiosk Nordstern · RG-10128-1

Nettoumsatz: 312,40 €
Deine Provision: 46,86 €

👉 Bitte leite die Rechnung an deinen Ansprechpartner vor Ort weiter.

Fällig am 26.08.2026
```
**Begleitend** → 👉 `task.terms_missing`

### ✅ `invoice.paid` — Rechnung bezahlt · `live`
**Operations** — 📥 Vorgänge · 586
```
✅ Zahlungseingang
Kiosk Nordstern · RG-10128-1

Saldo Max (offen): 134,20 €

⚠️ Zahlung nach Mahnung.
```
**Vertriebler**
```
✅ Zahlungseingang
Kiosk Nordstern · RG-10128-1

Deine Provision: +46,86 €
Dein Saldo (offen): 134,20 €
```
*Ops-⚠️ nur konditional (`{gesetzt Gemahnt}`): fällt weg, wenn pünktlich gezahlt.*
**Begleitend** → 👉 `task.jtl_payment`

### ⏰ `invoice.reminder_filed` — Zahlungserinnerung · `live`
**Operations** — 📥 Vorgänge · 586
```
⏰ Zahlungserinnerung erstellt
Kiosk Nordstern · RG-10128-1

Fällig seit 26.08.2026
```
**Vertriebler**
```
⏰ Zahlungserinnerung versendet
Kiosk Nordstern · RG-10128-1

Fällig seit 26.08.2026
```
*`{Mahnstufe}` aus ctx (Zahlungserinnerung / Mahnung).*
**Begleitend** → 🛑 `error.reminder_unmatched`

### 📮 `invoice.dunning_filed` — Mahnung · `live`
**Operations** — 📥 Vorgänge · 586
```
📮 Mahnung erstellt
Kiosk Nordstern · RG-10128-1

Fällig seit 26.08.2026
```
**Vertriebler**
```
📮 Mahnung versendet
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
*Runde 26: Identifikator in der Infozeile. `task.telegram_missing` bleibt gestrichen (18.08.). `task.digest` dormant/raus.*

### 👉 `task.jtl_missing` · `gebaut · Reimport 6820980 ausstehend`
```
👉 JTL Datensatz anlegen
Kunde & Lager für Kiosk Nordstern

• Kunden anlegen, Erstkontakt: Max Berger
• Lager anlegen, Namen und Adresse wie Kunde
• Kundennummer in Airtable unter »ID« eintragen
```

### 👉 `task.jtl_stock` · `live`
```
👉 Lager buchen (JTL)
Kiosk Nordstern · UL-10042-1

• Lager Modul öffnen
• Wareneingang buchen

Geliefert am 12.08.2026
```

### 👉 `task.jtl_inventory_date` · `live`
```
👉 Prüfdatum setzen (JTL)
Kiosk Nordstern · 10132

• Kunde öffnen
• Letzte Bestandsprüfung setzen

Geprüft am 12.08.2026
```

### 👉 `task.jtl_payment` · `gebaut · Reimport 6633991 ausstehend` · NEU
```
👉 Zahlung setzen (JTL)
Kiosk Nordstern · RG-10128-1

• Kunde in JTL öffnen
• Zahlung als bezahlt buchen

Bezahlt am 12.08.2026
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

*Runde 26: `task.digest` (07:00-Digest) ist aus dem Hub entfernt (dormant) — `task.invoice_unlinked` / `task.beleg_no_pdf` haben damit aktuell keinen Ausgabeort.*

---

## ⚙️ System · 583
*Runde 26: Titel „X aktualisiert", Infozeile = Richtung, kein Datum. Templates final — der **Hub-Reimport 6862968 steht aus**, bis dahin postet der Live-Hub noch die R25-Form.*

### ⚙️ `sync.products` — Produkt-Sync · `live` (R26-Layout mit Hub-Reimport)
*Postet nur bei materieller Änderung; No-Op-Lauf bleibt still.*
```
⚙️ Produkte aktualisiert
Shopify → Airtable

+2 Produkte · +5 Varianten · 3 Preise
```
**Begleitend** → 🛑 `error.sync_aborted`

### ⚙️ `sync.stores` — Store-Sync · `gebaut · Hub-Reimport ausstehend`
*Runde 26: R24-Streichung zurückgenommen. Erfolgs-Klingel an 6655783 bleibt; ctx `{Stores}` / `{Öffnungszeiten}`.*
```
⚙️ Stores aktualisiert
Google Places → Airtable

3 Stores · 1 Öffnungszeiten geändert
```

### ⚙️ `sync.inventory` — Bestand-Sync · `gebaut · Hub-Reimport ausstehend`
*Runde 26: 10.08.-Streichung zurückgenommen. **Shape-Konflikt:** Template (R26-final) ist aggregat `{Stores}`, der 18.08. gebaute Emitter 6805674 klingelt aber **pro Store** mit `{Store}` — vor dem Reimport klären.*
```
⚙️ Bestand aktualisiert
Airtable → Shopify

2 Stores · 4 Varianten
```

*`system.heartbeat` bleibt gestrichen. Abbrüche → `error.sync_aborted`.*

---

## 🛑 Störungen · 584
*Alle im Topic 🛑 Störungen · 584. Werte als ctx aus dem abbrechenden Lauf. Runde 26: 2–3-Wort-Betreff, kursive Infozeile (2 label-freie Fakten), 👉-Aktionszeile als eigener Absatz. **7 Keys** — `error.reminder_unreadable` gestrichen, `error.payment_unmatched` neu. Templates final, Hub-Reimport steht aus.*

### 🛑 `error.reminder_unmatched` · `live`
```
🛑 Mahnschreiben ohne Treffer
RG-10128-1 · Zahlungserinnerung

Grund: keine Rechnung mit dieser Nummer in Airtable

👉 Nummer prüfen — Tippfehler im Betreff oder Umsatz fehlt
```

### 🛑 `error.lexware_orphan` · `live`
```
🛑 Lexware-ID nicht gespeichert
Max Berger · Hannover

Grund: Lexware-Antwort ohne ID-Feld
Folge: der nächste Lauf legt eine Dublette an

👉 a257b406-… von Hand in »Lexware ID« eintragen
```

### 🛑 `error.sync_aborted` · `live`
```
🛑 Sync abgebrochen
[Sync] Inventory to Shopify · Belegdatum

Grund: Belegdatum fehlt im Beleg
Folge: kein Bestands-Push, keine City-Posts

👉 [Sync] Inventory to Shopify prüfen, wenn der Fehler bleibt
```

### 🛑 `error.store_failed` · `live`
```
🛑 Store nicht angelegt
Kiosk Nordstern · Kontakt anlegen

Grund: Steuernummer fehlt am Store
Folge: kein Metaobjekt, kein Lexware-Kontakt, kein Broadcast

👉 Hinweis im Datensatz prüfen: airtable.com/…
```

### 🛑 `error.store_partial` · `live`
```
🛑 Store unvollständig
Kiosk Nordstern · Kontakt anlegen

Grund: Steuernummer fehlt am Store

👉 Datensatz öffnen, Onboarding erneut auslösen: airtable.com/…
```

### 🛑 `error.salesperson_failed` · `live`
```
🛑 Vertriebler-Anlage gestoppt
Max Berger · Eingangsprüfung

Grund: Steuernummer fehlt am Vertriebler

👉 Grund prüfen und Anlage erneut anstoßen
```

### 🛑 `error.payment_unmatched` · `gebaut · Hub-Reimport ausstehend` · NEU
*No-Match-Zweig von `[Sync] Lexware Payments` (6955541) klingelt den Key; deckt Sales + Store (ein Key, `{Rechnungsnummer}` als Kennung).*
```
🛑 Zahlung ohne Treffer
RG-10128-1

Grund: keine Rechnung mit dieser Nummer in Airtable
Folge: Zahlungsstatus nicht gesetzt — der Umsatz bleibt offen

👉 Prüfen, ob RG-10128-1 als Umsatz existiert
```

---

*City-Channel hängt an genau zwei Anlässen: `delivery.booked` (→ `city.restock` / `city.strain_new`) und `store.created`.*
