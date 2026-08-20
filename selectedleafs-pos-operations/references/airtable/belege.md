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

## 🟣 Make-Zugriff (Marker in der Base-Feldbeschreibung)

Trägt einen 🟣-Zugriffsmarker in der Base-Feldbeschreibung (SSoT: [[model]] §2).

- **`Auszahlung`** — 🟣 WRITE. Vierter Fach-Link; `Process Salesperson Invoice` setzt ihn beim Anlegen des Belegs.

- **`Belegtyp`** — 🟣 READ. Make matcht als String; Option umbenennen bricht still.
- **`Datum`** — 🟣 READ+WRITE. Leistungsdatum-Quelle, wird nach Umsatz/Lieferung/Bestandsprüfung gespiegelt.
- **`Umsatz`** — 🟣 WRITE. Fach-Link, per Name/Ziel aufgelöst.
