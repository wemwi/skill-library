# Preise

`tblfwOn3HUmWqpIsv` · Kategorie **Version** (append-only, eff-dated)

> Feld-Block: **Stand 2026-08-15**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Versionierter **Verkaufspreis je Produktvariante**. Eine Zeile = ein ab `Gültig ab` geltender VK. Positionen ziehen daraus den `⚙ VK (netto)`.

## Beziehungen

- **→ `Produkt`** (Einzel, → Produktvarianten).
- **→ `Steuersatz`** (Einzel, → [[steuersaetze]]) — liefert die `MwSt.`.
- **→ `Umsatzpositionen`** / **→ `🟣 Lieferpositionen`** / **→ `🟣 Bestandsprüfungspositionen`** — die Positionen, die diesen Preis gewählt haben.

## Tragende Felder

- **`Gültig ab`** (Datum, EU) — **Versionswahl:** jüngste Version mit `Gültig ab ≤ Leistungsdatum` gewinnt.
- **`VK (brutto)`** (€) — der Eingabewert.
- **`VK (netto)`** (Formel, €) — `VK (brutto) / (1 + MwSt.)`. **Das ist der `⚙ VK (netto)`, den alle Positionen als Lookup ziehen.**
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
| Umsatzpositionen | link → 🟣 Umsatzpositionen | `fldU1uDEOoNvrj1CY` |
| Lieferpositionen | link → 🟣 Lieferpositionen | `fldoFc0cajTjg8wbz` |
| 🟣 Bestandsprüfungspositionen | link → 🟣 …positionen | `fld83vKlDZTYdiie7` |

*Neu ziehen: `list_tables_for_base` → Preise; Formeln via `get_table_schema`.*
