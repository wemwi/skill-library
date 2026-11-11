# Auszahlungen

`tblUrdeNTiSlerMr3` · Kategorie **Ereignis** (INSERT-only)

> Feld-Block: **Stand 2026-08-15**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Eine Zeile = eine **Auszahlung an den Vertriebler** gegen seinen offenen Saldo, gespiegelt aus der **Provisionsrechnung** (Eingangsrechnung des Vertrieblers in Lexware). Kein Positions-Kind.

## Beziehungen

- **→ `Vertriebler`** (Einzel) — an wen. `Ausgezahlt` auf [[vertriebler]] summiert `Bezahlt` aller Auszahlungen außer Storniert.
- **→ `Beleg`** (Einzel) — die gespiegelte Eingangsrechnung (Belegtyp Eingangsrechnung, PDF aus Lexware); Gegenfeld `Belege.Auszahlung`.
- Rückwege: `Vertriebler.Auszahlungen`.

## Tragende Felder

- **`ID`** (Formel) — `"ASZ-" & RIGHT("00000" & Auszahlungsnummer, 5)` (z. B. `ASZ-00005`).
- **`Betrag`** (€) / **`Bezahlt`** (€) — beantragt vs. tatsächlich überwiesen.
- **`Offen`** (Formel, €) — `Betrag − Bezahlt`.
- **`Status`** (Select) — In Bearbeitung / Teilzahlung / Abgeschlossen / Storniert. `Vertriebler.Ausgezahlt` rollt **`Bezahlt`** ohne stornierte Zeilen (live 11.11.2026; `Bezahlt` ist bis zur Zahlung 0, Teilzahlung zählt anteilig). Wer welchen Status setzt: [[scenarios]], `[Process] Lexware Voucher (Invoice · Salesperson)` und `[Process] Lexware Payment (Invoice · Salesperson)`.
- **`Lexware ID`** (Text) — **Voucher-UUID der Lexware-Eingangsrechnung; Idempotenz-Klammer.** `[Process] Lexware Voucher (Invoice · Salesperson)` sucht darüber, ob zu diesem Beleg schon eine Auszahlung existiert: beim **Erfassen** entsteht der Datensatz, beim **Bezahlen** wird nur der Status aktualisiert. Nicht manuell ändern.
- `Rechnungsnummer` (Text) · `Auszahlungsnummer` (autoNumber) · `Datum` (EU).

## Fallstricke

- **`Lexware ID` ist die Idempotenz** — ohne sie legt der nächste Lauf eine Dublette an.
- `Vertriebler.Offen` sinkt um `Bezahlt` (real überwiesen), nicht um `Betrag` (beantragt) — Teilzahlung wirkt anteilig.
- **Optionsnamen gekoppelt:** Beide Worker vergleichen `Status` über die Optionsnamen „Teilzahlung“ und „In Bearbeitung“. Umbenennen bricht das still; das Feld trägt deshalb den Marker 🟣 `make.com (KEY · Options)`.

## Feld-Block (Stand 2026-08-15 · `list_tables_for_base`)

| Feld | Typ | fld-ID |
|---|---|---|
| ID | formula | `fldLMw1VpcEyitnVF` |
| Datum | date | `fldB9IXQtOoZb0M9K` |
| Vertriebler | link → Vertriebler | `fld7eIRfIEd1aml1D` |
| Status | singleSelect | `fldd9jOWUYEpcwA4c` |
| Betrag | currency | `fld9icyZRghWzi7cp` |
| Bezahlt | currency | `fld6irHe7OmHkKcep` |
| Offen | formula € | `fldMWYrk1KmVo1lPo` |
| Rechnungsnummer | singleLineText | `fldYiJxowFyiCiLDu` |
| Beleg | link → Belege | `fld6re9aNdk0lM1x3` |
| Lexware ID | singleLineText | `fldgfj7Wr3OxjY2Zz` |
| Auszahlungsnummer | autoNumber | `fldMK9TjMDXrYPogU` |

*Neu ziehen: `list_tables_for_base` → Auszahlungen; Formeln via `get_table_schema`.*

## 🟣 Make-Zugriff (Stand 2026-08-21 · Live-Scan aller 17 Szenarien)

Make schreibt **6** Felder und liest **6**. Zwei davon matcht Make über den Klartext (Nachtrag 2026-11-11: `Status`) — sie tragen den 🟣-Marker in der Feldbeschreibung der Base und dürfen nicht umbenannt werden.

### Namens-gekoppelt — trägt den 🟣-Marker am Feld

- **`Lexware ID`** — 🟣 `make.com (KEY · Name)` · singleLineText · `fldgfj7Wr3OxjY2Zz`  
  Beleg → Auszahlung. Szenarien: `[Process] Lexware Voucher (Invoice · Salesperson)` und `[Process] Lexware Payment (Invoice · Salesperson)`, je „Find payout (by Lexware ID)“.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).
- **`Status`** — 🟣 `make.com (KEY · Options)` · singleSelect · `fldd9jOWUYEpcwA4c` (gesetzt 2026-11-11)  
  `[Process] Lexware Payment (Invoice · Salesperson)` vergleicht „In Bearbeitung“ und „Teilzahlung“ im Code „Decide (salesperson)“, `[Process] Lexware Voucher (Invoice · Salesperson)` vergleicht „Teilzahlung“ in „Update status“. Geschrieben wird der Status über die Options-ID.  
  ⚠ Option umbenennen: Teilzahlung wird nicht mehr gesetzt und nicht mehr erhalten (still).

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make schreibt:** `Betrag` · `Bezahlt` · `Datum` · `Rechnungsnummer` · `Status` · `Vertriebler`  

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**

*Ohne jeden Make-Zugriff: 4 von 11 Feldern.*
