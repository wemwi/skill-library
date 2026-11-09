# Gutschriftspositionen

`tblTCQjXx6o8GWPMI` · Kategorie **Positionen** (INSERT-only Kind von [[gutschriften]]) · seit 09.11.2026

> Feld-Block: **Stand 2026-11-09**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Eine Zeile = **eine Sorte in einer Gutschrift**. Menge und Betrag stehen **positiv**; das Vorzeichen legt allein `[Resolve] Lexware Voucher` fest.

## Beziehungen

- **→ `Gutschrift`** (Einzel) — Elternzeile → [[gutschriften]].
- **→ `Produkt`** (→ Produktvarianten) / **→ `Preis`** (→ [[preise]]) / **→ `Bestand`** (→ [[bestaende]]).

## Tragende Felder

- **`ID`** (Formel) — `{Gutschrift} & "#" & {Position}`.
- **`Nettobetrag`** (€, von **Make** geschrieben) — Rohwert aus dem Beleg. **Geldwahrheit**, rollt zu `Gutschriften.Nettobetrag`.
- **`Menge (Stück)`** (Zahl) — rollt ohne Storniert zu `Bestände.Gutgeschrieben` und hebt dort das SOLL.
- **`Nettoverkaufswert`** (Formel, €) — `Menge (Stück) × VK (netto)`, Grundlage der `Storemarge`.
- **`Preis`** (Link) — bleibt nötig, weil die Storemarge den VK der Gutschrift braucht.
- `VK (netto)` (Lookup ← [[preise]]) · `Datum`, `Status` (Lookup ← Gutschrift, für SOLL-Abgleich und Storno-Filter).

## Fallstricke

- `Nettobetrag` wird von Make als Wert geschrieben — nicht in eine Formel „reparieren".
- Stornierte Zeilen bleiben stehen; die Filter laufen über das Lookup `Status`.

## Feld-Block (Stand 2026-11-09 · `list_tables_for_base`)

| Feld | Typ | fld-ID |
|---|---|---|
| ID | formula | `fldaTEDUfwYA9jtF2` |
| Position | number | `fldCsyIhp9wEUpCo8` |
| Produkt | link → Produktvarianten | `fldPP9VfxQF2tFyGj` |
| Menge (Stück) | number | `fldBcHURex5atXcLQ` |
| Nettobetrag | currency € (Make) | `fldHZ1zNu8DLnMNnT` |
| Gutschrift | link → Gutschriften | `fldxLt3FUFQyi9pci` |
| Preis | link → Preise | `fldpeH7fVLpJ9jjl1` |
| Bestand | link → Bestände | `fldiGIBKsjmVOg2CR` |
| VK (netto) | lookup € (← Preise) | `fldBG4fzQ4C418uOp` |
| Nettoverkaufswert | formula € | `fldU6BAA3ylJ3A9mF` |
| Datum | lookup (← Gutschrift) | `fld4C7JOEKAwSr7hf` |
| Status | lookup (← Gutschrift) | `fld9AtajTu7vSijpn` |

*Neu ziehen: `list_tables_for_base` → Gutschriftspositionen; Formeln via `get_table_schema`.*

## 🟣 Make-Zugriff (Stand 2026-11-09)

Make schreibt **7** Felder und liest **4**. Eines davon matcht Make über den Klartext-Namen — es trägt den 🟣-Marker in der Feldbeschreibung der Base und darf nicht umbenannt werden.

### Namens-gekoppelt — trägt den 🟣-Marker am Feld

- **`Bestand`** — 🟣 `make.com (KEY · Name)` · link · `fldiGIBKsjmVOg2CR`  
  Steht im `filterByFormula` von „Load credit notes since check day“ in `[Process] Upload PDF (Inventory)` (grid-Zweig), zusammen mit `CREATED_TIME()`. Szenarien: 6729541.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make schreibt:** `Gutschrift` · `Position` · `Produkt` · `Preis` · `Bestand` · `Menge (Stück)` · `Nettobetrag` (8450345 „Create credit note line“)  
**Make liest:** `Bestand` · `Menge (Stück)` · `Datum` · `Status` (6729541, „Load credit notes since check day“; `Status` = Storniert zählt nicht)

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**
