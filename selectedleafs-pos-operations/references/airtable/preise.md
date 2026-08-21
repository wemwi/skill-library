# Preise

`tblfwOn3HUmWqpIsv` · Kategorie **Version** (append-only, eff-dated)

> Feld-Block: **Stand 2026-08-15**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Versionierter **Verkaufspreis je Produktvariante**. Eine Zeile = ein ab `Gültig ab` geltender VK. Positionen ziehen daraus den `VK (netto)`.

## Beziehungen

- **→ `Produkt`** (Einzel, → Produktvarianten).
- **→ `Steuersatz`** (Einzel, → [[steuersaetze]]) — liefert die `MwSt.`.
- **→ `Umsatzpositionen`** / **→ `Lieferpositionen`** / **→ `Bestandsprüfungspositionen`** — die Positionen, die diesen Preis gewählt haben.

## Tragende Felder

- **`Gültig ab`** (Datum, EU) — **Versionswahl:** jüngste Version mit `Gültig ab ≤ Leistungsdatum` gewinnt.
- **`VK (brutto)`** (€) — der Eingabewert.
- **`VK (netto)`** (Formel, €) — `VK (brutto) / (1 + MwSt.)`. **Das ist der `VK (netto)`, den alle Positionen als Lookup ziehen.**
- **`MwSt.`** (Lookup ← Steuersatz).
- `ID` (Formel) — `Jahr(Gültig ab) & "-" & Produkt`.

## Fallstricke

- **Nie eine bestehende Preis-Version editieren** (Freeze-Invariante) — sonst verschieben sich alte Positionswerte.
- Netto wird **aus brutto gerechnet** (`/ (1+MwSt.)`), nicht umgekehrt — die Brutto-Eingabe ist die Wahrheit.

## Feld-Block (Stand 2026-08-15 · `list_tables_for_base`)

| Feld | Typ | fld-ID |
|---|---|---|
| ID | formula | `fld4MF3Mwj4YVZqB8` |
| Gültig ab | date | `fldI7FiSfUxmDxNNj` |
| Produkt | link → Produktvarianten | `fldCdNn8nWUcgPlFG` |
| Steuersatz | link → Steuersätze | `fld2CqRpUPtXmtg5t` |
| MwSt. | lookup % (← Steuersätze) | `fldlLNMrsO6dYfyoB` |
| VK (netto) | formula € | `fldsBZtlWLMMEzbPB` |
| VK (brutto) | currency | `fldrvbwTvTBGatH9M` |
| Umsatzpositionen | link → Umsatzpositionen | `fldU1uDEOoNvrj1CY` |
| Lieferpositionen | link → Lieferpositionen | `fldoFc0cajTjg8wbz` |
| Bestandsprüfungspositionen | link → …positionen | `fld83vKlDZTYdiie7` |

*Neu ziehen: `list_tables_for_base` → Preise; Formeln via `get_table_schema`.*

## 🟣 Make-Zugriff (Stand 2026-08-21 · Live-Scan aller 17 Szenarien)

Make schreibt **4** Felder und liest **6**. 2 davon matcht Make über den Klartext-Namen — sie tragen den 🟣-Marker in der Feldbeschreibung der Base und dürfen nicht umbenannt werden.

### Namens-gekoppelt — trägt den 🟣-Marker am Feld

- **`Gültig ab`** — 🟣 `make.com (KEY · Name)` · date · `fldI7FiSfUxmDxNNj`  
  eff-dated Preiswahl am Leistungsdatum. Szenarien: 6633991, 6677862, 6729541.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).
- **`Produkt`** — 🟣 `make.com (KEY · Name)` · link · `fldCdNn8nWUcgPlFG`  
  ARRAYJOIN({Produkt}) Match. Szenarien: 6633991, 6677862, 6729541.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make schreibt:** `Steuersatz` · `VK (brutto)`  
**Make liest:** `Lieferpositionen` · `Umsatzpositionen`

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**

*Ohne jeden Make-Zugriff: 4 von 10 Feldern.*
