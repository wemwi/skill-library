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

### 🏅 `store.tier_reached` — Partnerstufe erreicht · `live 18.11.2026` · NEU
**Operations** — 📥 Vorgänge · 586
```
🏅 Partnerstufe erreicht
Kiosk Nordstern · Silber

Jahresbonus: 400,00 €
```
**Vertriebler** (Stores.Betreut von)
```
🏅 Partnerstufe erreicht
Kiosk Nordstern · Silber

Jahresbonus: **400,00 €**
```
**Begleitend** → 👉 `task.partner_tier` (zweite Meldung)
*Emitter: `[Maintain] Partner Tier Check`.*

### 🏅 `store.tier_adjusted` — Partnerstufe angepasst · `live 18.11.2026` · NEU
**Operations** — 📥 Vorgänge · 586
```
🏅 Partnerstufe angepasst
Kiosk Nordstern · Bronze

Vorher: Gold
Jahresbonus: 150,00 €
```
**Vertriebler** (Stores.Betreut von): wie Operations, Jahresbonus fett. Bei „Keine Stufe“ ohne Bonuszeile.
**Begleitend** → 👉 `task.partner_tier` (zweite Meldung)
*Emitter: `[Maintain] Partner Tier Check`, am 01.01. oder nach einem Storno.*

### ✅ `store.probation_passed` — Probezeit bestanden · `live 19.11.2026` · NEU
**Operations** — 📥 Vorgänge · 586
```
✅ Probezeit bestanden
Kiosk Nordstern · Linden-Nord

Warenlieferungen: 2

Erste Lieferung am 17.09.2026
```
**Vertriebler** (Stores.Betreut von)
```
✅ Probezeit bestanden
Kiosk Nordstern · Linden-Nord

Der Store ist jetzt **aktiver Partner**.
```
*Emitter: `[Maintain] Store Probation Check`.*

### 🔁 `store.model_changed` — Modell umgestellt · `live` · NEU
**Operations** — 📥 Vorgänge · 586
```
🔁 Modell umgestellt
Kiosk Nordstern · Eigenbestand

Vorher: Kommission
Auslöser: Lieferschein AF-10163-1-001

ℹ️ Keine Bestandsprüfungen mehr für diesen Store.
```
**Vertriebler** — — · **City** — —
**Begleitend** → 👉 `task.jtl_lock_stock` (zweite Meldung, seit 18.11.2026)
*Emitter: `[Process] JTL Voucher (Delivery)`, nur beim ersten Lieferschein eines Kommission-Stores; kommt zusammen mit `delivery.note_booked`.*

### 🤝 `salesperson.created` — Neuer Vertriebler · `live`
**Operations** — 📥 Vorgänge · 586
```
🤝 Neuer Vertriebler
Max Berger · Hannover
```
**Vertriebler** — kein Kanal (existiert bei Anlage noch nicht) · **City** — —
**Begleitend** → 🛑 `error.salesperson_failed` · 🛑 `error.lexware_orphan`

### 👋 `salesperson.onboarded` — Onboarding · `gebaut · eingesetzt · Produktivlauf ausstehend`
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

### 📦 `delivery.note_booked` — Lieferung per Lieferschein · `live` · NEU
**Operations** — 📥 Vorgänge · 586
```
📦 Ware geliefert
Max Berger bei Kiosk Nordstern

Nettoverkaufswert: 248,50 €
Gesamtkosten: 96,00 €

Geliefert am 12.08.2026
```
**Vertriebler** — wie `delivery.booked` („📦 Lieferung erfasst")
**City** — wie `delivery.booked` (über `[Sync] Airtable to Shopify`, restock)
**Begleitend** → beim ersten Lieferschein 🔁 `store.model_changed` · **kein** 👉 `task.jtl_stock` (JTL liefert aus dem eigenen Lager)

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
**Begleitend** → 👉 `task.jtl_return` · 👉 `task.jtl_inventory_date` (die Rückholung bucht auch eine Bestandsprüfung) · bei Gate-Blockade 🛑 `error.return_failed`
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
⚠️ 1 Zeile unklar

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
⚠️ 1 Zeile unklar

Geprüft am 12.08.2026
```
**City** — —
**Begleitend** → 👉 `task.jtl_inventory_date`

### 📋 `inventory.corrected` — Bestand nachgetragen · `gebaut · Import ausstehend`
*Auslöser `[Process] Manual Action (Inventory Correction)` nach Buchung oder Statuswechsel (06.11.2026).*
**Operations** — 📥 Vorgänge · 586
```
📋 Bestand nachgetragen
Max Berger bei Kiosk Nordstern

Gesamtdifferenz: 14 Einheiten
Nettoverkaufswert: 48,50 €

⚠️ 1 Zeile unklar

Geprüft am 12.08.2026
```
**Vertriebler**
```
📋 Bestandsprüfung nachgetragen
Kiosk Nordstern · Linden

Gesamtdifferenz: 14 Einheiten
Nettoverkaufswert: 48,50 €

⚠️ 1 Zeile unklar

Geprüft am 12.08.2026
```
**City** — —

### ⏳ `inventory.due` — Prüfung fällig · `gebaut · Import ausstehend`
*Auslöser ist das eigene Szenario `[Maintain] Inventory Check Reminder` (Schedule tgl. ~07:00, gebaut 18.08.2026 — Import + Schedule-Aktivierung noch offen). Vertrag siehe [[scenarios]].*
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

👉 Zeit für einen Besuch
Routenplanung öffnen → https://maps.google.com/…

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

### ↩️ `refund.created` — Gutschrift erstellt · `live` · NEU
**Operations** — 📥 Vorgänge · 586
```
↩️ Gutschrift erstellt
Kiosk Nordstern · RK-10003-1

Gutschrift netto: 12,40 €
Provision: −1,48 €

👉 Mit der nächsten Rechnung verrechnen
```
**Vertriebler**: „↩️ Gutschrift erfasst“, Gutschrift netto, Provision bei Verrechnung fett.
**Begleitend** → 👉 `task.jtl_inventory_count` (zweite Meldung, nur bei Kommission, seit 18.11.2026)
*Emitter: `[Process] Lexware Voucher (Refund · Store)`.*

### ✅ `refund.settled` — Gutschrift verrechnet · `live` · NEU
**Operations** — 📥 Vorgänge · 586
```
✅ Gutschrift verrechnet
Kiosk Nordstern · RK-10003-1

Gutschrift netto: 12,40 €
Saldo Max (offen): 134,20 €
```
**Vertriebler**: Deine Provision −…, Dein Saldo (offen) fett.
**Begleitend** → 👉 `task.jtl_refund` (zweite Meldung)
*Emitter: `[Process] Lexware Voucher (Refund · Store)`.*

*`invoice.overdue` gestrichen (16.08.2026) — der Überfällig-Hinweis läuft über `reminder_filed`.*

---

## 👉 Aufgaben · 585
*Runde 26: Identifikator in der Infozeile. `task.telegram_missing` bleibt gestrichen (18.08.). `task.digest` **gestrichen** (nicht dormant — der 07:00-Lauf kommt nicht).*

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
*Emitter: `[Process] Upload Voucher (Inventory)` und `[Process] Upload Voucher (Return)`.*

### 👉 `task.jtl_return` · `live` · NEU
```
👉 Rückholung buchen (JTL)
Kiosk Nordstern · RETURN-10132-2026-08-12

• Lager Modul öffnen
• Warenausgang buchen

Zurückgeholt am 12.08.2026
```

### 👉 `task.jtl_payment` · `gebaut · Reimport 6633991 ausstehend` · NEU
```
👉 Zahlung setzen (JTL)
Kiosk Nordstern · RG-10128-1

• Kunde in JTL öffnen
• Zahlung als bezahlt buchen

Bezahlt am 12.08.2026
```

### 👉 `task.jtl_refund` · `live`
```
👉 Gutschrift verrechnen (JTL)
Kiosk Nordstern · RK-10003-1

• Zahlung „Verrechnung Gutschrift“ an der Rechnung eintragen (Anmerkung RK-10003-1)
• In der Gutschrift Status „verrechnet mit RG-…“ setzen
```
*Zweite Meldung zu `refund.settled`.*

### 👉 `task.jtl_lock_stock` · `live 18.11.2026` · NEU
```
👉 Lager sperren (JTL)
Kiosk Nordstern · Eigenbestand

• Lager des Stores öffnen
• Für die Auslieferung sperren
```
*Zweite Meldung zu `store.model_changed` (Wechsel auf Eigenbestand).*

### 👉 `task.jtl_inventory_count` · `live 18.11.2026` · NEU
```
👉 Bestand korrigieren (JTL)
Kiosk Nordstern · RK-10003-1

• Inventur im Lager des Stores buchen
• Mengen laut Gutschrift RK-10003-1 nachbuchen
```
*Zweite Meldung zu `refund.created`, nur bei `Stores.Modell` = Kommission.*

### 👉 `task.partner_tier` · `live 18.11.2026` · NEU
```
👉 Partnerstufe setzen (JTL)
Kiosk Nordstern · Silber

• Kunde öffnen
• Label setzen
```

### 👉 `task.probation_review` · `live 19.11.2026` · NEU
```
👉 Probezeit entscheiden
Kiosk die Ecke · seit 188 Tagen

• Noch keine zweite Lieferung
• Status auf Aktiv setzen oder Rückholung planen

Erste Lieferung am 20.05.2026
```
*Vertriebler: „👉 Probezeit läuft ab“, gleiche Infozeile, Hinweis zur Abstimmung mit Joscha. Wöchentlich bis zur Entscheidung; Emitter: `[Maintain] Store Probation Check`.*

### 👉 `task.bonus_redeem` · `live 18.11.2026` · NEU
```
👉 Jahresbonus einlösen (JTL)
Alero Kiosk · AF-10180-1-001

• Restguthaben 250,00 € brutto als Bonuszeile auf die Rechnung
• Nur wenn alle Vorjahresrechnungen bezahlt sind
• Höchstens das Restguthaben und weniger als der Warenwert

Geliefert am 03.02.2027
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

*Runde 26 / Stand 2026-08-22: **es gibt keinen Digest und es wird keinen geben.** `task.digest` ist aus dem Hub entfernt, der 07:00-Lauf ist gestrichen (→ [[scenarios]], am Live-Hub gemessen). `task.invoice_unlinked` und `task.beleg_no_pdf` waren reine Digest-Zeilen und sind damit **tot** — kein Sender, kein Text, keine Zeile in der Landkarte, und das bleibt so (Entscheidung Joscha). Kommentare, die sie „bis der Digest steht" reservieren, sind Reste eines verworfenen Plans.*

---

## ⚙️ System · 583
*Runde 26: Titel „X aktualisiert", Infozeile = Richtung, kein Datum. Templates final — der **Hub-Reimport 6862968 steht aus**, bis dahin postet der Live-Hub noch die R25-Form.*

### ⚙️ `sync.products` — Produkt-Sync · `live` (R26-Layout mit Hub-Reimport)
*Postet nur bei materieller Änderung; No-Op-Lauf bleibt still. 15.11.2026: an die Vorlage im Hub angeglichen, Anlegen und Ändern getrennt.*
```
⚙️ Produkte aktualisiert
Shopify → Airtable

Neu: Produkte +2 · Varianten +5 · Preise +5
Geändert: Produkte 1 · Varianten 0 · Preise 3
```
**Begleitend** → 🛑 `error.sync_aborted`

### ⚙️ `sync.stores` — Store-Sync · `gebaut · Hub-Reimport ausstehend`
*Runde 26: R24-Streichung zurückgenommen. Erfolgs-Klingel an 6655783 bleibt; ctx `{Stores}` / `{Öffnungszeiten}`.*
```
⚙️ Stores aktualisiert
Google Places → Shopify

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
[Sync] Airtable to Shopify · Belegdatum

Grund: Belegdatum fehlt im Beleg
Folge: kein Bestands-Push, keine City-Posts

👉 [Sync] Airtable to Shopify prüfen, wenn der Fehler bleibt
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
*Zweig „No match“ von `[Process] Lexware Payment (Invoice · Store)` und `(Invoice · Salesperson)` klingelt den Key, nur wenn das Lesen gelang und keine Zeile passt; deckt Sales + Store (ein Key, `{Rechnungsnummer}` als Kennung).*
```
🛑 Zahlung ohne Treffer
RG-10128-1

Grund: keine Rechnung mit dieser Nummer in Airtable
Folge: Zahlungsstatus nicht gesetzt — der Umsatz bleibt offen

👉 Prüfen, ob RG-10128-1 als Umsatz existiert
```

### 🛑 `error.return_failed` · `live` · NEU
*Gate-Blockade in `[Process] Upload Voucher (Return)` (nicht alle Positionen auflösbar, Resolver-Fehler oder negatives Verdikt) — keine Buchung, Hinweis steht im Beleg.*
```
🛑 Rückholung nicht gebucht
BLG-00077 · Buchungsprüfung

Grund: Positionen nicht aufloesbar: 3, 7
Positionen: 9 erwartet / 7 aufgeloest
Folge: keine Buchung, kein Offboarding

👉 Hinweis im Beleg prüfen
```

---

*City-Channel hängt an genau zwei Anlässen: Lieferung (`delivery.booked` / `delivery.note_booked` → `city.restock` / `city.strain_new`) und `store.created`.*
