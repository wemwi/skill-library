# Stores

`tblfB5nsTSOXrUK1q` · Kategorie **Stammdaten**

> Feld-Block: **Stand 2026-08-18**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Der Partner-Kiosk (POS). Trägt Identität, Standort, Steuer-/Shopify-Anker und die **Akquise-Zuordnung** zum Vertriebler.

## Beziehungen

- **→ `Stadt`** / **→ `Stadtteil`** (→ [[staedte]] / [[stadtteile]]) — Standort; `Telegram ID` (City-Channel) kommt per Lookup aus der **Stadt**.
- **→ `Akquise durch`** (Einzel, → [[vertriebler]]) — wer den Store akquiriert hat.
- **→ `Umsätze` / `Lieferungen` / `Bestände` / `Bestandsprüfungen`**.

## Tragende Felder

- **`ID`** (Text) — **JTL-Kundennummer**; trägt den Bestands-Schlüssel (`Bestände.ID = "BST-" & ID & "-" & SKU`). Inhalt nicht umwidmen.
- **`Name`** (Text) — **Restock-Match läuft zeichengenau** hierüber. Umbenennen bricht still.
- **`Akquise durch`** (Link) — wird **ausschließlich** über den personalisierten Formularlink gesetzt (`prefill` + `hide`, Wert = Record-ID des Vertrieblers). `[Create] New Store Partner` prüft es als Pflichtfeld; `[Dispatch] Telegram Notifications` navigiert darüber. **Feld-ID nicht ändern, „Neue Datensätze erlauben" nicht einschalten** (sonst still ein zweiter Vertriebler).
- **`Shopify GID`** (Metaobjekt-GID, voll inkl. Präfix) · **`Google Place ID`** (baut den Maps-Link der City-Posts; leer ⇒ Namenssuche).
- `Storemarge (Jahr/Gesamt)` (Formel, €) — `Nettoumsatzerlös − Nettoumsatz` (Handelsmarge des Stores; Basis Umsätze, nicht Lieferungen).
- `Status` (Aktiv/Inaktiv/Probezeit) · `Modell` (Kommission/Eigenbestand) · `Stufe` (Bronze … Diamant) · `Telegram ID` (Lookup ← Stadt) · `Lexware ID` · `Sortiment`/`Paketdienste` (Mehrfachauswahl) · Adress-/Social-Felder.
- **`Fällig gemeldet am`** (Datum) — **B2-Idempotenz-Marker** von `[Maintain] Overdue Inventory Checks` (→ `inventory.due`): der Emitter setzt ihn `= heute`, wenn er den Store als überfällig meldet, und meldet erst wieder, wenn der Marker älter als das wöchentliche Re-Nag-Fenster ist. Nur diese Klingel schreibt hier.

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
| Stufe | singleSelect | `fldogYE4AvaPvYEcb` |
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

*Neu ziehen: `list_tables_for_base` → Stores; Formeln via `get_table_schema`.*

## 🟣 Make-Zugriff (Stand 2026-08-21 · Live-Scan aller 17 Szenarien)

Diese Sektion ist die Langfassung. Kurzfassung steht **in der Base** als Tabellenbeschreibung:

> 🟣 make.com — Zugriffskarte (Stand 2026-08-21, Live-Scan aller 17 Szenarien).
> Make schreibt 7 Felder und liest 24.
> 7 davon matcht Make über den Klartext-Namen — sie tragen 🟣 make.com (KEY · …) in der Feldbeschreibung und dürfen nicht umbenannt werden. Alle übrigen Zugriffe laufen über die Feld-ID und sind umbenennungssicher.
> Zusätzlich lauscht ein Airtable-Webhook auf 12 Felder dieser Tabelle; deren Löschen legt die zugehörige Inbox still.
> Vor dem Löschen oder Umtypisieren eines Feldes: POS-Skill → references/airtable/stores.md.

### Namens-gekoppelt — trägt den 🟣-Marker am Feld

- **`Fällig gemeldet am`** — 🟣 `make.com (KEY · Name)` · date · `fldzaj0Ai31RqgqnU`  
  Re-Nag-Fenster. Szenarien: 7001118.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).
- **`ID`** — 🟣 `make.com (KEY · Name)` · singleLineText · `fldL1YaDEswIZNnNP`  
  JTL-Kundennummer Match. Szenarien: 6729541.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).
- **`Lexware ID`** — 🟣 `make.com (KEY · Name)` · singleLineText · `fldk5PuObAVdGbWP4`  
  Kontakt → Store. Szenarien: 6633991, 6872775.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).
- **`Modell`** — 🟣 `make.com (KEY · Options)` · singleSelect · `fld8C3tgNKcDqBgdP`  
  Kommission als String. Szenarien: 7001118.  
  ⚠ Feldname **und** Optionsnamen sind eingefroren — beides bricht den Match still.
- **`Name`** — 🟣 `make.com (KEY · Name)` · singleLineText · `fld7fbRS1BHvrqJrj`  
  LOWER({Name}) Kommissionär-Match. Szenarien: 6729541.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).
- **`Status`** — 🟣 `make.com (KEY · Options)` · singleSelect · `fld8fYS00U23noJST`  
  Aktiv/Probezeit als String. Szenarien: 7001118.  
  ⚠ Feldname **und** Optionsnamen sind eingefroren — beides bricht den Match still.
- **`Zuletzt geprüft`** — 🟣 `make.com (KEY · Name)` · rollup · `fld36tZGPVPcuqOJU`  
  DATETIME_DIFF-Vergleich. Szenarien: 7001118.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make schreibt:** `Google Place ID` · `Hinweis` · `Shopify GID` · `Stadt` · `Stadtteil`  
**Make liest:** `Akquise durch` · `Bild` · `Facebook` · `Instagram` · `Paketdienste` · `Postleitzahl` · `Sortiment` · `Straße / Nr.` · `Telefon` · `Telegram ID` · `TikTok` · `Webseite` · `WhatsApp`

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**

### Webhook-Scope (`[Maintain] Airtable Webhooks`, 6830404)

Der Airtable-Webhook lauscht per `watchDataInFieldIds` auf: `Name` · `Postleitzahl` · `Straße / Nr.` · `Bild` · `Sortiment` · `Paketdienste` · `Telefon` · `WhatsApp` · `Instagram` · `Facebook` · `TikTok` · `Webseite`.

Feld-IDs, kein Namensbezug — Umbenennen unkritisch. Wird eines gelöscht, fällt der Trigger für dieses Feld still aus.

*Ohne jeden Make-Zugriff: 11 von 36 Feldern.*
