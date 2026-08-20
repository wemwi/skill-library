# Bestandsprüfungspositionen

`tbllbej3aFEnxRobH` · Kategorie **Positionen** (INSERT-only Kind von [[bestandspruefungen]])

> Feld-Block: **Stand 2026-08-15**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Eine Zeile = **eine Sorte in einer Bestandsprüfung** (SOLL vs. IST). Bewertet **Schwund** — nur positive Differenzen.

## Beziehungen

- **→ `Bestandsprüfung`** (Einzel) — Elternzeile → [[bestandspruefungen]].
- **→ `Produkt`** (→ Produktvarianten) / **→ `Preis`** (→ [[preise]]) / **→ `Bestand`** (→ [[bestaende]]).

## Tragende Felder

- **`ID`** (Formel) — `{Bestandsprüfung} & " #" & {Position}`.
- **`Differenz`** (Formel) — `SOLL − IST`.
- **`Nettoverkaufswert`** (Formel, €) — `IF(Differenz > 0, Differenz × VK (netto), 0)` — **nur positiver Schwund** wird bewertet; Mehrbestand zählt 0.
- **`Prüfstempel`** (Formel) — `IF(IST leer, BLANK(), VALUE(Geprüft am als YYYYMMDD) × 100000 + IST)` — kodiert Prüfdatum + IST in einer Zahl (Sortier-/Match-Stempel).
- **`VK (netto)`** (Lookup ← [[preise]]).
- `SOLL` / `IST` (Zahl) · Lookups `Store`, `Geprüft am`.

## Fallstricke

- **Nur positive Differenzen** fließen in den Wert — die Gesamtsumme auf [[bestandspruefungen]] ist damit ein **Schwund**-Wert, kein Netto-Saldo.
- `Prüfstempel` ist ein zusammengesetzter Schlüssel — Datumsformat/Faktor nicht ändern.

## Feld-Block (Stand 2026-08-15 · `list_tables_for_base`)

| Feld | Typ | fld-ID |
|---|---|---|
| ID | formula | `fldVekCJcYqoCakJw` |
| Position | number | `fldvtEBhtqnjfT9Y3` |
| Produkt | link → Produktvarianten | `fldHcHaafIcSK1XGh` |
| SOLL | number | `fldmstYhkrSpA0nf9` |
| IST | number | `fldOyloIfDXe513cq` |
| Differenz | formula | `fldFxKTS4YK7pI2Xr` |
| Nettoverkaufswert | formula € | `fldleCIbmBisJ3Bjn` |
| Preis | link → Preise | `fldIVtjZLN0NgPVlW` |
| VK (netto) | lookup € (← Preise) | `fldNXWuRYkEQAOkP6` |
| Bestandsprüfung | link → Bestandsprüfungen | `fldgWqr3uk12g8Bcg` |
| Bestand | link → Bestände | `flda3MAblikmXCB44` |
| Store | lookup | `fld0IRQ14sjWPrh8k` |
| Geprüft am | lookup | `fldBQjuphN88Xx0Oe` |
| Prüfstempel | formula | `fldvsrzTPvaRNvmPo` |

*Neu ziehen: `list_tables_for_base` → Bestandsprüfungspositionen; Formeln via `get_table_schema`.*

## 🟣 Make-Zugriff (Marker in der Base-Feldbeschreibung)

Trägt einen 🟣-Zugriffsmarker in der Base-Feldbeschreibung (SSoT: [[model]] §2).

- **`ID`** — 🟣 READ. Positions-Schlüssel, per Name referenziert.
