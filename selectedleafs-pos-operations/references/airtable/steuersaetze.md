# Steuersätze

`tblFF5JzqngWUaKSw` · Kategorie **Version** (append-only, eff-dated)

> Feld-Block: **Stand 2026-08-15**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Versionierte **MwSt.-Sätze**. Eine Zeile = ein ab `Gültig ab` geltender Satz. Speist `MwSt.` in [[konditionen]] und [[preise]].

## Beziehungen

- **→ `Konditionen`** / **→ `Preise`** — die Versionen, die diesen Satz ziehen.

## Tragende Felder

- **`Gültig ab`** (Datum, EU) — Versionswahl.
- **`Steuersatz`** (%) — der Satz selbst (z. B. 19 % / 7 % / 0 %).
- `Name` / `Kürzel` (Text) — für die ID.
- `ID` (Formel) — `Jahr(Gültig ab) & "-" & Kürzel & "-" & ROUND(Steuersatz×100,0)` (z. B. `2026-USt-19`).

## Fallstricke

- **Append-only** — ein Satzwechsel ist eine neue Zeile mit neuem `Gültig ab`, keine Bearbeitung.

## Feld-Block (Stand 2026-08-15 · `list_tables_for_base`)

| Feld | Typ | fld-ID |
|---|---|---|
| ID | formula | `fldiAKmk98CoI52Vn` |
| Name | singleLineText | `fldX7idN4PIA0Cp5L` |
| Kürzel | singleLineText | `fldAK2IIHURkJ6p88` |
| Gültig ab | date | `flda8dLWKeYOfHk9x` |
| Steuersatz | percent | `fldetjU6evewvPK0b` |
| Konditionen | link → Konditionen | `fldfLsi6mN1sUi5q7` |
| Preise | link → Preise | `fldlPdLO38WeBxgEC` |

*Neu ziehen: `list_tables_for_base` → Steuersätze; Formeln via `get_table_schema`.*
