# Bestandsprüfungen

`tblmuGjaRDYXQzHch` · Kategorie **Ereignis** (INSERT-only)

> Feld-Block: **Stand 2026-08-15**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Eine Zeile = eine **Bestandsprüfung** (Soll/Ist-Abgleich) in einem Store, belegt durch das Prüfprotokoll. Kein Geldwert zum Vertriebler — sie misst **Schwund**.

## Beziehungen

- **→ `Store`** / **→ `Vertriebler`** (Einzel) — wo geprüft, wer geprüft.
- **→ `Beleg`** (Einzel) — Prüfprotokoll; `Datum` gespiegelt = Prüfdatum.
- **→ `🟣 Bestandsprüfungspositionen`** (Kinder) — SOLL/IST je Sorte; Differenzen rollen hoch → [[bestandspruefungspositionen]].
- Rückwege: `Vertriebler.Bestandsprüfungen` · `Stores.Bestandsprüfungen` · `Belege.Bestandsprüfung`.

## Tragende Felder

- **`ID`** (Formel) — **Dedup-Schlüssel:** `"BSP-" & ⚙ Store ID & "-" & DATETIME_FORMAT(Datum,'YYYY-MM-DD')`. Make baut denselben Wert als `dedupkey` und sucht per `filterByFormula`. **Präfix/Format nicht anfassen.**
- **`⚙ Differenz (Gesamt)`** (Rollup) — Σ `🟣 Bestandsprüfungspositionen.Differenz` (SOLL − IST).
- **`⚙ Nettoverkaufswert`** (Rollup, €) — Σ der **positiv** bewerteten Differenzen = **Schwundwert** (VK-Sicht).
- **`Status`** (Select) — Abgeschlossen / In Bearbeitung / Teilgebucht / Ungültig (Make-String).
- **`Unterschrieben`** / **`Inventar geprüft`** (Checkbox) — speisen die Warnzeilen der Meldung.
- `Datum` (Lookup ← Beleg, EU) · `⚙ Store ID` (Lookup ← Stores.ID) · `Positionen` (Count) · `⚙ Hinweis`.

## Fallstricke

- **Dedup über `ID`** (Store-Nr + Prüfdatum): zwei Prüfungen desselben Stores am selben Tag kollidieren bewusst.
- **`[Maintain] Overdue Inventory Checks` (→ `inventory.due`) nutzt denselben Präfix als Sortier-Schlüssel:** jüngste Prüfung je Store per `FIND("BSP-{JTL}-", {ID}) = 1` + Sort `ID` **desc**, max 1 — weil das Datum im `ID` steckt, ist `ID` desc = Datum desc innerhalb des Stores (kein separates Datumsfeld nötig).
- Nur **positive** Differenzen fließen in den `⚙ Nettoverkaufswert` (Schwund); Mehrbestand wird nicht als negativer Wert gezählt (siehe [[bestandspruefungspositionen]]).

## Feld-Block (Stand 2026-08-15 · `list_tables_for_base`)

| Feld | Typ | fld-ID |
|---|---|---|
| ID | formula | `fld24GCd9UoMFtIW6` |
| Status | singleSelect | `fldVx19XWUNiag4yJ` |
| ⚙ Hinweis | multilineText | `fldPFWhLjjKt17Ra5` |
| Unterschrieben | checkbox | `fldX8yl4NxZeu2FUb` |
| Inventar geprüft | checkbox | `fldIkRcJo0tbi3St3` |
| Store | link → Stores | `fld31rwYy0IctcTWf` |
| Vertriebler | link → Vertriebler | `fldBiml9y1hrdyB5a` |
| Bestandsprüfungspositionen | link → 🟣 …positionen | `fldP609B3H3G320Eo` |
| Beleg | link → Belege | `fldT3CnM4sh6xkgXK` |
| Datum | lookup (← Beleg.Datum) | `fldtcCjenPbEVtoUX` |
| ⚙ Store ID | lookup (← Stores.ID) | `fldCcuJCgQZTgEmBC` |
| ⚙ Differenz (Gesamt) | rollup | `fldu5g1stOUVfgf91` |
| Positionen | count | `fldkeRTSxff0AdVIj` |
| ⚙ Nettoverkaufswert | rollup € | `fldIQQ71uz7zfOWN1` |

*Neu ziehen: `list_tables_for_base` → Bestandsprüfungen; Formeln via `get_table_schema`.*
