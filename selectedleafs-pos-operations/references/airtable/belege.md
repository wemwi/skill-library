# Belege

`tbld7UQwDBbq9A8Xk` · Kategorie **Stammdaten** (Dokument-Drehscheibe)

> Feld-Block: **Stand 2026-11-05**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Die **Drehscheibe für jedes eingehende PDF.** Jeder Beleg trägt seinen Typ, das PDF und je **einen** Fach-Link in die passende Ereignis-Tabelle. Das `Datum` eines Belegs ist das **Leistungsdatum** des daraus entstehenden Ereignisses.

## Beziehungen (vier Fach-Links)

- **→ `Umsatz`** (→ [[umsaetze]]) · **→ `Lieferung`** (→ [[lieferungen]]) · **→ `Bestandsprüfung`** (→ [[bestandspruefungen]]) · **→ `Auszahlung`** (→ [[auszahlungen]]).

## Klassifikator-Vertrag: `Belegtyp` → Zieltabelle

| Belegtyp | Ziel |
|---|---|
| Übergabeprotokoll | Lieferung (`delivery.booked`) |
| Lieferschein | Lieferung (Eigenbestand, `delivery.note_booked`; erster Lieferschein eines Kommission-Stores stellt `Stores.Modell` um) · seit 05.11.2026 |
| Gutschrift | Umsatz mit negativen Positionen (`refund.created`), Nummernkreis `RK-` · seit 08.11.2026; legt `[Process] Refund (Store)` bei neuem Umsatz an, läuft nicht durch die Inbox |
| Rückholprotokoll | Lieferung (Rückholung, `delivery.returned`) **und** Bestandsprüfung (Rückhol-Prüfung) |
| Bestandsprotokoll | Bestandsprüfung |
| Ausgangsrechnung | Umsatz |
| Eingangsrechnung | Auszahlung (Provisionsrechnung des Vertrieblers) |
| Zahlungserinnerung | Umsatz (Beleg-Link, Mahnstufe) |
| Mahnung | Umsatz (Beleg-Link, Mahnstufe) |
| **Unbekannt** | — → 👉 `task.doctype_unclear` (Belegtyp von Hand setzen) |

## Tragende Felder

- **`ID`** (Formel) — `"BLG-" & RIGHT("00000" & Belegnummer, 5)` (z. B. `BLG-00044`).
- **`Belegtyp`** (Select) — die zehn Typen oben; **`Unbekannt`** löst die Korrektur-Aufgabe aus (Make-String, nicht umbenennen).
- **`Datum`** (EU) — **Quelle des Leistungsdatums**; die Ereignis-Tabellen spiegeln es per Lookup.
- **`Anhang`** (Attachments) — das PDF.
- `Hinweis` (Freitext) · `Belegnummer` (autoNumber) · `Upload durch` (→ Vertriebler) / `Upload zu` (→ Stores) — Herkunft eines Uploads aus der Sales App, keine Fach-Links.
- **`Hinweis` = „Wartet auf Kundennummer“** (seit 07.11.2026, Spec `claude/spec-beleg-ohne-kundennummer.md`): fester Wert, den die **Sales App** beim Anlegen setzt, wenn der gewählte Store (`Upload zu`) keine `Stores.ID` hat. Der Beleg ist damit **geparkt** — außerhalb der View „Inbox (make.com)“ (Filter u. a. `Hinweis` leer). Sobald `Stores.ID` gesetzt ist, leert die Airtable-Automation **„Belege freigeben, wenn Kundennummer da“** (Tabelle Stores) diesen Hinweis an den verknüpften Belegen, ältester zuerst; der Beleg rutscht per Feldänderung in die Inbox und läuft wie gewohnt durch `[Dispatch] Upload PDF`. Hängen gebliebene zeigt die View **„Wartet auf Kundennummer“** (Wächter, → [[operations]]). In der App gilt dieser Hinweis nicht als Problem („In Bearbeitung“, löschbar).

## Fallstricke

- **`Datum` ist das Leistungsdatum** — ein falsches Belegdatum wählt die falsche Konditionen-/Preis-Version.
- **„Wartet auf Kundennummer“ ist zeichengenau gekoppelt:** Sales App (Konstante `BELEG_HINWEIS.wartetAufKundennummer`), Skript der Automation „Belege freigeben, wenn Kundennummer da“ und Filter der View „Wartet auf Kundennummer“. Wortlaut nur an allen drei Stellen zugleich ändern. Einen geparkten Beleg nicht von Hand freigeben, solange `Stores.ID` leer ist — Make findet sonst keinen Store.
- Der Belegtyp bestimmt den Fach-Link beim Anlegen — einer je Beleg, nur das **Rückholprotokoll** trägt zwei (Lieferung + Bestandsprüfung).
- **Protokoll-Belege bekommen später den `Umsatz`.** Bestands- und Rückholprotokoll sind die **Vergabeliste** der Rechnungszuordnung: `[Process] Invoice (Store)` hängt die Rechnung an den Protokoll-Beleg der passenden Prüfung; ein Beleg mit `Umsatz` gilt als vergeben (→ [[scenarios]], „Bestandsprüfung zuordnen"). Ein Rückholprotokoll ohne Differenz bleibt ohne Umsatz — es gibt nichts abzurechnen.

## Feld-Block (Stand 2026-11-05 · `list_tables_for_base`)

| Feld | Typ | fld-ID |
|---|---|---|
| ID | formula | `fld7DgKiRjGPJitvf` |
| Datum | date (EU) | `fldPoeEx87w0wF8w9` |
| Belegtyp | singleSelect | `fldKSqryQHeRzUCMd` |
| Anhang | attachments | `fldd3wi6dceGmnppx` |
| Umsatz | link → Umsätze | `fldI5lU4NQ7ymG4d0` |
| Lieferung | link → Lieferungen | `fld3Ca5ejPbG2DVYb` |
| Bestandsprüfung | link → Bestandsprüfungen | `fldbzOIOSaNcwdNAL` |
| Hinweis | multilineText | `fldW8Gk8tDwDoJoJ8` |
| Auszahlung | link → Auszahlungen | `fld0o0yQ9AS4iFYKN` |
| Belegnummer | autoNumber | `fldn5KrXi5x4werVB` |
| Upload durch | link → Vertriebler | `fldS5BmsfqPi5TOdv` |
| Upload zu | link → Stores | `fldPuVFi2iKbf9aeh` |

*Neu ziehen: `list_tables_for_base` → Belege; Formeln via `get_table_schema`.*

## 🟣 Make-Zugriff (Stand 2026-08-21 · Live-Scan aller 17 Szenarien)

Make schreibt **6** Felder und liest **7**. 4 davon matcht Make über den Klartext-Namen (Nachtrag 2026-11-06: `Bestandsprüfung`) — sie tragen den 🟣-Marker in der Feldbeschreibung der Base und dürfen nicht umbenannt werden.

### Namens-gekoppelt — trägt den 🟣-Marker am Feld

- **`Belegtyp`** — 🟣 `make.com (KEY · Options)` · singleSelect · `fldKSqryQHeRzUCMd`  
  Option als String. Szenarien: 6633991, 6844567, 8392806 (schreibt „Unbekannt", seit 05.11.2026).  
  ⚠ Feldname **und** Optionsnamen sind eingefroren — beides bricht den Match still.
- **`Datum`** — 🟣 `make.com (KEY · Name)` · date · `fldPoeEx87w0wF8w9`  
  Dubletten-Match + Vergabeliste-sort. Szenarien: 6633991, 6844567.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).
- **`Umsatz`** — 🟣 `make.com (KEY · Name)` · link · `fldI5lU4NQ7ymG4d0`  
  Dubletten-Match. Szenarien: 6844567.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).
- **`Bestandsprüfung`** — 🟣 `make.com (KEY · Name)` · link · `fldbzOIOSaNcwdNAL` (gesetzt 2026-11-06)  
  Vergabeliste je Store: `FIND("BSP-<Kundennr>-", {Bestandsprüfung}) = 1`, zusammen mit `Belegtyp` (Bestands- oder Rückholprotokoll). Szenarien: 6633991.  
  ⚠ Umbenennen bricht den Match still — die Vergabeliste käme leer zurück, jede Rechnung bliebe unverknüpft.

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make schreibt:** `Anhang` (auch `[Sync] JTL Delivery Note to Airtable`, Upload-Endpunkt) · `Auszahlung` · `Hinweis`  
**Make liest:** `ID`

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**

### Webhook-Scope (`[Maintain] Airtable Webhooks`, 6830404)

Der Airtable-Webhook lauscht per `watchDataInFieldIds` auf: `Anhang`.

Feld-IDs, kein Namensbezug — Umbenennen unkritisch. Wird eines gelöscht, fällt der Trigger für dieses Feld still aus.

*Ohne jeden Make-Zugriff: 2 von 10 Feldern (Scan 21.08.; `Upload durch` / `Upload zu` sind jünger und nicht gescannt).*
