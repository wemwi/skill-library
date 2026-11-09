# Umsatzpositionen

`tbl1fA7Ih6RseHfNk` · Kategorie **Positionen** (INSERT-only Kind von [[umsaetze]])

> Feld-Block: **Stand 2026-08-15**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Eine Zeile = **eine Sorte in einem Umsatz**. Trägt den **abgerechneten** Positionsbetrag (`Nettoumsatz`) — die Geldwahrheit, aus der `Umsätze.Nettoumsatz` rollt. Gutschriftzeilen stehen seit 09.11.2026 in [[gutschriftspositionen]].

## Beziehungen

- **→ `Umsatz`** (Einzel) — Elternzeile → [[umsaetze]].
- **→ `Produkt`** (→ Produktvarianten) / **→ `Preis`** (→ [[preise]]) / **→ `Bestand`** (→ [[bestaende]]).

## Tragende Felder

- **`ID`** (Formel) — `{Umsatz} & "#" & {Position}`.
- **`Nettoumsatz`** (€, von **Make** geschrieben) — der **abgerechnete** Positionsbetrag (mit Partnerrabatt). **Geldwahrheit**, rollt zu `Umsätze.Nettoumsatz`.
- **`Nettoumsatzerlös`** (Formel, €) — `Menge (Stück) × VK (netto)` — Wert zum **Endkunden-VK**, liegt systematisch **über** `Nettoumsatz`. Die Lücke ist die **Storemarge**, kein Fehler; fließt in **keine** Provisions-/Saldoformel. `Menge (kg)` fließt bewusst nicht ein (VK ist stückbezogen).
- **`VK (netto)`** (Lookup ← [[preise]]).
- `Menge (Stück)` / `Menge (kg)` (Zahl) · Lookups `Datum`, `Status`, `Typ`.

## Fallstricke

- **`Nettoumsatz` (Make) ≠ `Nettoumsatzerlös` (Formel).** Ersteres ist abgerechnet und saldo-relevant; letzteres ist Endkunden-VK und **nur** Anzeige/Storemarge.
- `Nettoumsatz` wird von Make als Wert geschrieben — nicht in eine Formel „reparieren".

## Feld-Block (Stand 2026-08-15 · `list_tables_for_base`)

| Feld | Typ | fld-ID |
|---|---|---|
| ID | formula | `fldBiGqojpDtj0bl9` |
| Position | number | `fldbx0pWARAoWJ0AG` |
| Produkt | link → Produktvarianten | `fldng3YPm9pXrROiU` |
| Menge (Stück) | number | `flduCHcnm4ajMRUO3` |
| Menge (kg) | number | `fldO2Pb1HqqnwNXz6` |
| Nettoumsatz | currency € (Make) | `fld5XP3ejidcHedf3` |
| Nettoumsatzerlös | formula € | `fldyiQByQKF6tbk4c` |
| Preis | link → Preise | `fld3c913AqpjDU93P` |
| VK (netto) | lookup € (← Preise) | `fldAe9Te0I5L4Dp7J` |
| Umsatz | link → Umsätze | `fldW0MfIBLe7XYsOT` |
| Bestand | link → Bestände | `fldQ78oQsJxrEssGH` |
| Datum | lookup | `fldpH9mzVV7abfwqB` |
| Status | lookup | `fldgkUqpUgDjoAQJY` |
| Typ | lookup | `fldV7NTjnV1ELyuO5` |

*Neu ziehen: `list_tables_for_base` → Umsatzpositionen; Formeln via `get_table_schema`.*

## 🟣 Make-Zugriff (Stand 2026-08-21 · Live-Scan aller 17 Szenarien)

Make **schreibt** hier 8 Felder und liest **4** (Nachtrag 2026-11-06, SOLL-Abgleich). Seither ist 1 Feld namens-gekoppelt — es trägt den 🟣-Marker in der Feldbeschreibung der Base und darf nicht umbenannt werden.

### Namens-gekoppelt — trägt den 🟣-Marker am Feld (gesetzt 2026-11-06)

- **`Bestand`** — 🟣 `make.com (KEY · Name)` · link · `fldQ78oQsJxrEssGH`  
  Steht im `filterByFormula` von „Load invoices since check day“ in `[Process] Upload PDF (Inventory)` (grid-Zweig), zusammen mit `CREATED_TIME()`. Szenarien: 6729541.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make schreibt:** `Bestand` · `Menge (Stück)` · `Menge (kg)` · `Nettoumsatz` · `Position` · `Preis` · `Produkt` · `Umsatz`  
**Make liest:** `Bestand` · `Menge (Stück)` · `Datum` · `Status` (6729541, „Load invoices since check day“; `Status` = Storniert zählt nicht)  

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**

*Ohne jeden Make-Zugriff: 6 von 14 Feldern.*
