# Auszahlungen

`tblUrdeNTiSlerMr3` · Kategorie **Ereignis** (INSERT-only)

> Feld-Block: **Stand 2026-08-15**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Eine Zeile = eine **Auszahlung an den Vertriebler** gegen seinen offenen Saldo, gespiegelt aus der **Provisionsrechnung** (Eingangsrechnung des Vertrieblers in Lexware). Kein Positions-Kind.

## Beziehungen

- **→ `Vertriebler`** (Einzel) — an wen. `Ausgezahlt` auf [[vertriebler]] rollt aus **abgeschlossenen** Auszahlungen.
- **→ `Beleg`** (Einzel) — die gespiegelte Eingangsrechnung (Belegtyp Eingangsrechnung, PDF aus Lexware); Gegenfeld `Belege.Auszahlung`.
- Rückwege: `Vertriebler.Auszahlungen`.

## Tragende Felder

- **`ID`** (Formel) — `"ASZ-" & RIGHT("00000" & Auszahlungsnummer, 5)` (z. B. `ASZ-00005`).
- **`Betrag`** (€) / **`Bezahlt`** (€) — beantragt vs. tatsächlich überwiesen.
- **`Offen`** (Formel, €) — `Betrag − Bezahlt`.
- **`Status`** (Select) — In Bearbeitung / Teilzahlung / Abgeschlossen / Storniert. `Vertriebler.Ausgezahlt` rollt **`Bezahlt`** (nicht statusgefiltert; `Bezahlt` ist bis zur Zahlung 0, Teilzahlung zählt anteilig).
- **`Lexware ID`** (Text) — **Voucher-UUID der Lexware-Eingangsrechnung; Idempotenz-Klammer.** `[Process] Invoice (Sales)` sucht darüber, ob zu diesem Beleg schon eine Auszahlung existiert: beim **Erfassen** entsteht der Datensatz, beim **Bezahlen** wird nur der Status aktualisiert. Nicht manuell ändern.
- `Rechnungsnummer` (Text) · `Auszahlungsnummer` (autoNumber) · `Datum` (EU).

## Fallstricke

- **`Lexware ID` ist die Idempotenz** — ohne sie legt der nächste Lauf eine Dublette an.
- `Vertriebler.Offen` sinkt um `Bezahlt` (real überwiesen), nicht um `Betrag` (beantragt) — Teilzahlung wirkt anteilig.

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

Diese Sektion ist die Langfassung. Kurzfassung steht **in der Base** als Tabellenbeschreibung:

> 🟣 make.com — Zugriffskarte (Stand 2026-08-21, Live-Scan aller 17 Szenarien).
> Make schreibt 6 Felder und liest 6.
> Eines davon matcht Make über den Klartext-Namen — es trägt 🟣 make.com (KEY · …) in der Feldbeschreibung und darf nicht umbenannt werden. Alle übrigen Zugriffe laufen über die Feld-ID und sind umbenennungssicher.
> Vor dem Löschen oder Umtypisieren eines Feldes: POS-Skill → references/airtable/auszahlungen.md.

### Namens-gekoppelt — trägt den 🟣-Marker am Feld

- **`Lexware ID`** — 🟣 `make.com (KEY · Name)` · lookup · `fldgfj7Wr3OxjY2Zz`  
  Beleg → Auszahlung. Szenarien: 6955541, 6872651.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make schreibt:** `Betrag` · `Bezahlt` · `Datum` · `Rechnungsnummer` · `Status` · `Vertriebler`  

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**

*Ohne jeden Make-Zugriff: 4 von 11 Feldern.*
