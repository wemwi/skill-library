# Belege

`tbld7UQwDBbq9A8Xk` · Kategorie **Stammdaten** (Dokument-Drehscheibe)

> Feld-Block: **Stand 2026-08-15**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Die **Drehscheibe für jedes eingehende PDF.** Jeder Beleg trägt seinen Typ, das PDF und je **einen** Fach-Link in die passende Ereignis-Tabelle. Das `Datum` eines Belegs ist das **Leistungsdatum** des daraus entstehenden Ereignisses.

## Beziehungen (vier Fach-Links)

- **→ `Umsatz`** (→ [[umsaetze]]) · **→ `Lieferung`** (→ [[lieferungen]]) · **→ `Bestandsprüfung`** (→ [[bestandspruefungen]]) · **→ `Auszahlung`** (→ [[auszahlungen]]).

## Klassifikator-Vertrag: `Belegtyp` → Zieltabelle

| Belegtyp | Ziel |
|---|---|
| Übergabeprotokoll | Lieferung (`delivery.booked`) |
| Rückholprotokoll | Lieferung (Rückholung, `delivery.returned`) |
| Bestandsprotokoll | Bestandsprüfung |
| Ausgangsrechnung | Umsatz |
| Eingangsrechnung | Auszahlung (Provisionsrechnung des Vertrieblers) |
| Zahlungserinnerung | Umsatz (Beleg-Link, Mahnstufe) |
| Mahnung | Umsatz (Beleg-Link, Mahnstufe) |
| **Unbekannt** | — → 👉 `task.doctype_unclear` (Belegtyp von Hand setzen) |

## Tragende Felder

- **`ID`** (Formel) — `"BLG-" & RIGHT("00000" & Belegnummer, 5)` (z. B. `BLG-00044`).
- **`Belegtyp`** (Select) — die acht Typen oben; **`Unbekannt`** löst die Korrektur-Aufgabe aus (Make-String, nicht umbenennen).
- **`Datum`** (EU) — **Quelle des Leistungsdatums**; die Ereignis-Tabellen spiegeln es per Lookup.
- **`Anhang`** (Attachments) — das PDF.
- `Hinweis` (Freitext) · `Belegnummer` (autoNumber).

## Fallstricke

- **`Datum` ist das Leistungsdatum** — ein falsches Belegdatum wählt die falsche Konditionen-/Preis-Version.
- Genau **ein** Fach-Link je Beleg — der Belegtyp bestimmt welcher.

## Feld-Block (Stand 2026-08-15 · `list_tables_for_base`)

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
| Belegnummer | autoNumber | `fldUprNttE4qhl3ph` |

*Neu ziehen: `list_tables_for_base` → Belege; Formeln via `get_table_schema`.*

## 🟣 Make-Zugriff (Stand 2026-08-21 · Live-Scan aller 17 Szenarien)

Make schreibt **6** Felder und liest **7**. 3 davon matcht Make über den Klartext-Namen — sie tragen den 🟣-Marker in der Feldbeschreibung der Base und dürfen nicht umbenannt werden.

### Namens-gekoppelt — trägt den 🟣-Marker am Feld

- **`Belegtyp`** — 🟣 `make.com (KEY · Options)` · singleSelect · `fldKSqryQHeRzUCMd`  
  Option als String. Szenarien: 6633991, 6844567.  
  ⚠ Feldname **und** Optionsnamen sind eingefroren — beides bricht den Match still.
- **`Datum`** — 🟣 `make.com (KEY · Name)` · date · `fldPoeEx87w0wF8w9`  
  Dubletten-Match + Vergabeliste-sort. Szenarien: 6633991, 6844567.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).
- **`Umsatz`** — 🟣 `make.com (KEY · Name)` · link · `fldI5lU4NQ7ymG4d0`  
  Dubletten-Match. Szenarien: 6844567.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make schreibt:** `Anhang` · `Auszahlung` · `Hinweis`  
**Make liest:** `Bestandsprüfung` · `ID`

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**

### Webhook-Scope (`[Maintain] Airtable Webhooks`, 6830404)

Der Airtable-Webhook lauscht per `watchDataInFieldIds` auf: `Anhang`.

Feld-IDs, kein Namensbezug — Umbenennen unkritisch. Wird eines gelöscht, fällt der Trigger für dieses Feld still aus.

*Ohne jeden Make-Zugriff: 2 von 10 Feldern.*
