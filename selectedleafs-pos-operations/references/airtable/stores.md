# Stores

`tblfB5nsTSOXrUK1q` · Kategorie **Stammdaten**

> Feld-Block: **Stand 2026-08-18**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Der Partner-Kiosk (POS). Trägt Identität, Standort, Steuer-/Shopify-Anker und die **Akquise-Zuordnung** zum Vertriebler.

## Beziehungen

- **→ `Stadt`** / **→ `Stadtteil`** (→ [[staedte]] / [[stadtteile]]) — Standort; `Telegram ID` (City-Channel) kommt per Lookup aus der **Stadt**.
- **→ `Akquise durch`** (Einzel, → [[vertriebler]]) — wer den Store akquiriert hat.
- **→ `Umsätze` / `Gutschriften` / `Lieferungen` / `Bestände` / `Bestandsprüfungen`**.

## Tragende Felder

- **`ID`** (Text) — **JTL-Kundennummer**; trägt den Bestands-Schlüssel (`Bestände.ID = "BST-" & ID & "-" & SKU`). Inhalt nicht umwidmen. Über die Sales App angelegte Stores haben sie zunächst nicht (App: „Kundennummer folgt“, Beleg wird geparkt, → [[belege]]). **Wird `ID` gesetzt (nicht leer), feuert die Airtable-Automation „Belege freigeben, wenn Kundennummer da“** (Auslöser „Datensatz erfüllt Bedingung“, seit 07.11.2026): Sie leert `Hinweis` = „Wartet auf Kundennummer“ an den verknüpften Belegen (Rückfeld `Belege`). Erst die richtige Nummer eintragen — schon ein vorläufiger Wert gibt die Belege frei.
- **`Name`** (Text) — **Restock-Match läuft zeichengenau** hierüber. Umbenennen bricht still.
- **`Akquise durch`** (Link) — wird **ausschließlich** über den personalisierten Formularlink gesetzt (`prefill` + `hide`, Wert = Record-ID des Vertrieblers). `[Create] Store` prüft es als Pflichtfeld; `[Notify] Telegram Channels` navigiert darüber. **Feld-ID nicht ändern, „Neue Datensätze erlauben" nicht einschalten** (sonst still ein zweiter Vertriebler).
- **`Shopify GID`** (Metaobjekt-GID, voll inkl. Präfix) · **`Google Place ID`** (baut den Maps-Link der City-Posts; leer ⇒ Namenssuche).
- `Storemarge (Jahr/Gesamt)` (Formel, €) — `Nettoumsatzerlös − Nettoumsatz − Gutschriften Storemarge` (Handelsmarge des Stores; Basis Umsätze, nicht Lieferungen, sonst zählte unverkaufter Regalbestand als Verdienst mit).
- `Gutschriften Storemarge (Jahr/Gesamt)` (Rollup ← `Gutschriften.Storemarge`, ohne Storniert, seit 09.11.2026; das Jahr über `Datum`). `Nettoumsatz (Jahr/Gesamt)` zählt nur Rechnungen. `Nettoumsatz (Jahr/Gesamt)` und `Nettoumsatzerlös (Jahr/Gesamt)` ohne Storniert (seit 19.11.2026, live geprüft); die Jahres-Rollups filtern zusätzlich auf das Kalenderjahr über `Umsätze.Datum`. Ausgebucht zählt mit (Ware verkauft).
- **`Modell`** (Select: Kommission / Eigenbestand) — Abrechnungsmodell, siehe [[model]] §3. **Make schreibt es seit 05.11.2026:** der erste Lieferschein eines Kommission-Stores setzt `Eigenbestand` (`[Process] Upload Voucher (Delivery)`, nur diese Richtung, meldet `store.model_changed`). Zurück auf Kommission nur von Hand. Bei Eigenbestand: keine Bestandsprüfungen und Erinnerungen, Rechnungen ohne Prüfzuordnung, der Shop behält die gelieferten Sorten, eine Rückholung ohne Rest setzt den Store nicht inaktiv.
- **`Stufe`** (Keine Stufe · Bronze … Diamant; bis 18.11.2026 hieß die erste Option „Nicht registriert“, gleiche ID) — laufende Partnerstufe, Spiegel des JTL-Kunden-Labels. **Make schreibt sie seit 17.11.2026** (`[Maintain] Partner Tier Check`): die höhere von Vorjahres- und laufender Stufe aus [[jahresboni]]; bei einer Änderung `store.tier_reached` bzw. `store.tier_adjusted` mit `task.partner_tier`, das Label in JTL setzt Joscha. Gehaltene Stufe: Sie fällt nur am 01.01. oder nach einem Storno. Die Sales App schreibt bei der Store-Anlage „Keine Stufe“ über die Options-ID (seit 0.1.28). Der Bonus kommt nie aus diesem Feld, nur aus `Jahresboni`.
- **`Bonusguthaben`** (Rollup Σ `Jahresboni.Guthaben`, brutto, seit 17.11.2026) — liest `[Process] JTL Voucher (Delivery)` für `task.bonus_redeem`. `Jahresboni` (Link) ist das Rückfeld von `Jahresboni.Store`.
- **`Status`** (Aktiv / Inaktiv / Probezeit) — Probezeit gilt bis zur 2. bezahlten Rechnung. **Make schreibt Aktiv seit 19.11.2026** (`[Maintain] Store Probation Check`, nur Probezeit → Aktiv, ab `Bezahlte Rechnungen` ≥ 2, meldet `store.probation_passed`); bei weniger als 2 bezahlten Rechnungen und 90 Tagen seit der ersten Warenlieferung wöchentlich `task.probation_review`, der Status bleibt. Inaktiv setzt `[Process] Upload Voucher (Return)` bei einer Rückholung ohne Rest. Den Startwert setzt nicht `[Create] Store`.
- `Bezahlte Rechnungen` (Anzahl ← `Umsätze` mit `Status` = Bezahlt) und `Erste Warenlieferung` (Rollup MIN ← `Lieferungen.Datum`, nur Lieferungen mit `Status` = Abgeschlossen und `Menge (kg)` > 0: keine reine Ausstattung, keine Rückholung, keine Korrektur), beide seit 19.11.2026. Liest `[Maintain] Store Probation Check` und der Hub über die fld-ID.
- `Telegram ID` (Lookup ← Stadt) · `Lexware ID` · `Sortiment`/`Paketdienste` (Mehrfachauswahl) · Adress-/Social-Felder.
- **`Fällig gemeldet am`** (Datum) — **B2-Idempotenz-Marker** von `[Maintain] Inventory Check Reminder` (→ `inventory.due`): der Emitter setzt ihn `= heute`, wenn er den Store als überfällig meldet, und meldet erst wieder, wenn der Marker älter als das wöchentliche Re-Nag-Fenster ist. Nur diese Klingel schreibt hier.

## Fallstricke

- **`Name` und `ID` sind Match-Schlüssel** (Restock bzw. Bestand) — nicht anfassen.
- **GIDs immer voll** (`gid://shopify/…`), keine führenden Leerzeichen.
- Store↔City-Zuordnung ist **redaktionell** (über Stadtteil/Stadt), nicht aus der Adresse abgeleitet.

## Feld-Block (Stand 2026-08-18 · `list_tables_for_base`)

| Feld | Typ | fld-ID |
|---|---|---|
| ID | singleLineText (JTL-Nr) | `fldL1YaDEswIZNnNP` |
| Name | singleLineText | `fld7fbRS1BHvrqJrj` |
| Bild | attachments | `fldhtzwUV5qXTs8BY` |
| Status | singleSelect | `fld8fYS00U23noJST` |
| Modell | singleSelect | `fld8C3tgNKcDqBgdP` |
| Stufe | singleSelect (Keine Stufe `selRRb3q13BdkHh8z` · Bronze `selon7hvwWI63Paok` · Silber `selPpZ5pxipye20u7` · Gold `selJ76DYbUEF5eoq5` · Platin `selHc4mmOoJkShbsE` · Diamant `selXUYZqaQMzC8fcO`; Nachtrag 2026-11-17) | `fldogYE4AvaPvYEcb` |
| Stadt | link → Städte | `fldTYy4JUNZuGVOlE` |
| Stadtteil | link → Stadtteile | `fldjVrpQh4LqaxqOk` |
| Sortiment | multipleSelects | `fldA81gIXLtI9ZT3C` |
| Paketdienste | multipleSelects | `fldTTMLi9aaL9kVa0` |
| Telegram ID | lookup (← Stadt) | `fld09mGXJrafZXyjN` |
| Storemarge (Jahr) | formula € | `flduK3o9ZPrYliqHx` |
| Nettoumsatz (Jahr) | rollup € | `fld7tasG7ULKOFgwc` |
| Nettoumsatzerlös (Jahr) | rollup € | `fld6vzXFGzquyfqDN` |
| Umsätze | link → Umsätze | `fldGTcMH3nl5rYF1q` |
| Lieferungen | link → Lieferungen | `fldPEygqmLN2bMIlB` |
| Bestände | link → Bestände | `fldaFRXpAm0IAJNWk` |
| Bestandsprüfungen | link → Bestandsprüfungen | `fldIah3g3pJWAfHUE` |
| Storemarge (Gesamt) | formula € | `fldqHkKwzRcONh9oB` |
| Nettoumsatz (Gesamt) | rollup € | `fld1HB9Kb1SH9htCU` |
| Nettoumsatzerlös (Gesamt) | rollup € | `fldwqQt0rWUaDLEbw` |
| Hinweis | multilineText | `fldTSV4EiyIkKOUAI` |
| Lexware ID | singleLineText | `fldk5PuObAVdGbWP4` |
| Shopify GID | singleLineText (Metaobjekt) | `fldE7ux5MwwvJGJZl` |
| Google Place ID | singleLineText | `fldQ6BHP9c9FlVZE1` |
| Postleitzahl | number | `fldJzdkest3PwK2y6` |
| Straße / Nr. | singleLineText | `fld3qcSSGz8Y6M3zx` |
| Telefon | phoneNumber | `fld6abb6WVqH9i5Qi` |
| WhatsApp | phoneNumber | `fld1CzHQpAmfTPUIz` |
| Instagram / Facebook / TikTok / Webseite | url | `fldsVzi4cb6TQkMx3` … |
| Zuletzt geprüft | rollup date | `fld36tZGPVPcuqOJU` |
| Akquise durch | link → Vertriebler | `fldMF3vhN0mNklbkb` |
| Fällig gemeldet am | date | `fldzaj0Ai31RqgqnU` |
| Belege | link → Belege (Rückfeld von `Belege.Upload zu`; Nachtrag 2026-11-07) | `fldmG4IXjoLtmpNxL` |
| Gutschriften | link → Gutschriften (Nachtrag 2026-11-09) | `fldMmuahibd8mDfj4` |
| Gutschriften Storemarge (Jahr) | rollup € (Nachtrag 2026-11-09) | `fldKB4y4WjCNEsqnC` |
| Gutschriften Storemarge (Gesamt) | rollup € (Nachtrag 2026-11-09) | `fldHUUgOZvTDrJXtk` |
| Jahresboni | link → Jahresboni (Nachtrag 2026-11-17) | `fld4JPOdHuu08XDJg` |
| Bonusguthaben | rollup Σ Jahresboni.Guthaben (Nachtrag 2026-11-17) | `fldqVMheQjFwPhPTr` |
| Bezahlte Rechnungen | count ← Umsätze (Status Bezahlt; Nachtrag 2026-11-19) | `fldGU3FMnAfnVaIOn` |
| Erste Warenlieferung | rollup MIN ← Lieferungen.Datum (Abgeschlossen, Menge (kg) > 0; Nachtrag 2026-11-19) | `fld4hjSPX9PBPAKFb` |

*Neu ziehen: `list_tables_for_base` → Stores; Formeln via `get_table_schema`.*

## 🟣 Make-Zugriff (Stand 2026-08-21 · Live-Scan aller 17 Szenarien)

Make schreibt **8** Felder (seit 05.11.2026 auch `Modell`) und liest **25** (seit 2026-11-06 `Umsätze`). 7 davon matcht Make über den Klartext-Namen — sie tragen den 🟣-Marker in der Feldbeschreibung der Base und dürfen nicht umbenannt werden.

### Namens-gekoppelt — trägt den 🟣-Marker am Feld

- **`Fällig gemeldet am`** — 🟣 `make.com (KEY · Name)` · date · `fldzaj0Ai31RqgqnU`  
  Re-Nag-Fenster. Szenarien: 7001118.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).
- **`ID`** — 🟣 `make.com (KEY · Name)` · singleLineText · `fldL1YaDEswIZNnNP`  
  JTL-Kundennummer Match. Szenarien: 7049889 (`[Resolve] Store`; 6729541 liest `Stores` seit 12.11.2026 nicht mehr selbst, geprüft 15.11.2026).  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).
- **`Lexware ID`** — 🟣 `make.com (KEY · Name)` · singleLineText · `fldk5PuObAVdGbWP4`  
  Kontakt → Store. Szenarien: 6633991, 6872775.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).
- **`Modell`** — 🟣 `make.com (KEY · Options)` · singleSelect · `fld8C3tgNKcDqBgdP`  
  Kommission als String. Szenarien: 7001118. Seit 05.11.2026 zusätzlich: **schreibt** 6677862 („Eigenbestand" als Optionsname, `typecast: false`); liest 6633991, 6677862, 6805674, 7062902.  
  ⚠ Feldname **und** Optionsnamen sind eingefroren — beides bricht den Match still.
- **`Name`** — 🟣 `make.com (KEY · Name)` · singleLineText · `fld7fbRS1BHvrqJrj`  
  LOWER({Name}) Kommissionär-Match. Szenarien: 7049889 (`[Resolve] Store`; 6729541 liest `Stores` seit 12.11.2026 nicht mehr selbst, geprüft 15.11.2026).  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).
- **`Status`** — 🟣 `make.com (KEY · Options)` · singleSelect · `fld8fYS00U23noJST`  
  Aktiv/Probezeit als String. Szenarien: 7001118. Seit 19.11.2026 zusätzlich `[Maintain] Store Probation Check` (Suche `{Status}="Probezeit"`, schreibt Aktiv als Options-ID).  
  ⚠ Feldname **und** Optionsnamen sind eingefroren — beides bricht den Match still.
- **`Zuletzt geprüft`** — 🟣 `make.com (KEY · Name)` · rollup · `fld36tZGPVPcuqOJU`  
  DATETIME_DIFF-Vergleich. Szenarien: 7001118.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make schreibt:** `Google Place ID` · `Hinweis` · `Shopify GID` · `Stadt` · `Stadtteil`  
**Make liest:** `Bezahlte Rechnungen` · `Erste Warenlieferung` (seit 19.11.2026) · `Akquise durch` · `Bild` · `Umsätze` (8413130 „Load store“, seit 2026-11-06) · `Facebook` · `Instagram` · `Paketdienste` · `Postleitzahl` · `Sortiment` · `Straße / Nr.` · `Telefon` · `Telegram ID` · `TikTok` · `Webseite` · `WhatsApp`

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**

### Webhook-Scope (`[Maintain] Airtable Webhooks`, 6830404)

Der Airtable-Webhook lauscht per `watchDataInFieldIds` auf: `Name` · `Postleitzahl` · `Straße / Nr.` · `Bild` · `Sortiment` · `Paketdienste` · `Telefon` · `WhatsApp` · `Instagram` · `Facebook` · `TikTok` · `Webseite`.

Feld-IDs, kein Namensbezug — Umbenennen unkritisch. Wird eines gelöscht, fällt der Trigger für dieses Feld still aus.

*Ohne jeden Make-Zugriff: 11 von 36 Feldern.*
