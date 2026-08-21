# Bestandsprüfungen

`tblmuGjaRDYXQzHch` · Kategorie **Ereignis** (INSERT-only)

> Feld-Block: **Stand 2026-08-15**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Eine Zeile = eine **Bestandsprüfung** (Soll/Ist-Abgleich) in einem Store, belegt durch das Prüfprotokoll. Kein Geldwert zum Vertriebler — sie misst **Schwund**.

## Beziehungen

- **→ `Store`** / **→ `Vertriebler`** (Einzel) — wo geprüft, wer geprüft.
- **→ `Beleg`** (Einzel) — Prüfprotokoll; `Datum` gespiegelt = Prüfdatum.
- **→ `Bestandsprüfungspositionen`** (Kinder) — SOLL/IST je Sorte; Differenzen rollen hoch → [[bestandspruefungspositionen]].
- Rückwege: `Vertriebler.Bestandsprüfungen` · `Stores.Bestandsprüfungen` · `Belege.Bestandsprüfung`.

## Tragende Felder

- **`ID`** (Formel) — **Dedup-Schlüssel:** `"BSP-" & Store ID & "-" & DATETIME_FORMAT(Datum,'YYYY-MM-DD')`. Make baut denselben Wert als `dedupkey` und sucht per `filterByFormula`. **Präfix/Format nicht anfassen.**
- **`Differenz (Gesamt)`** (Rollup) — Σ `Bestandsprüfungspositionen.Differenz` (SOLL − IST).
- **`Nettoverkaufswert`** (Rollup, €) — Σ der **positiv** bewerteten Differenzen = **Schwundwert** (VK-Sicht).
- **`Status`** (Select) — Abgeschlossen / In Bearbeitung / Teilgebucht / Ungültig (Make-String).
- **`Unterschrieben`** / **`Inventar geprüft`** (Checkbox) — speisen die Warnzeilen der Meldung.
- `Datum` (Lookup ← Beleg, EU) · `Store ID` (Lookup ← Stores.ID) · `Positionen` (Count) · `Hinweis`.

## Fallstricke

- **Dedup über `ID`** (Store-Nr + Prüfdatum): zwei Prüfungen desselben Stores am selben Tag kollidieren bewusst.
- **`[Maintain] Overdue Inventory Checks` (→ `inventory.due`) nutzt denselben Präfix als Sortier-Schlüssel:** jüngste Prüfung je Store per `FIND("BSP-{JTL}-", {ID}) = 1` + Sort `ID` **desc**, max 1 — weil das Datum im `ID` steckt, ist `ID` desc = Datum desc innerhalb des Stores (kein separates Datumsfeld nötig).
- Nur **positive** Differenzen fließen in den `Nettoverkaufswert` (Schwund); Mehrbestand wird nicht als negativer Wert gezählt (siehe [[bestandspruefungspositionen]]).

## Feld-Block (Stand 2026-08-15 · `list_tables_for_base`)

| Feld | Typ | fld-ID |
|---|---|---|
| ID | formula | `fld24GCd9UoMFtIW6` |
| Status | singleSelect | `fldVx19XWUNiag4yJ` |
| Hinweis | multilineText | `fldPFWhLjjKt17Ra5` |
| Unterschrieben | checkbox | `fldX8yl4NxZeu2FUb` |
| Inventar geprüft | checkbox | `fldIkRcJo0tbi3St3` |
| Store | link → Stores | `fld31rwYy0IctcTWf` |
| Vertriebler | link → Vertriebler | `fldBiml9y1hrdyB5a` |
| Bestandsprüfungspositionen | link → …positionen | `fldP609B3H3G320Eo` |
| Beleg | link → Belege | `fldT3CnM4sh6xkgXK` |
| Datum | lookup (← Beleg.Datum) | `fldtcCjenPbEVtoUX` |
| Store ID | lookup (← Stores.ID) | `fldCcuJCgQZTgEmBC` |
| Differenz (Gesamt) | rollup | `fldu5g1stOUVfgf91` |
| Positionen | count | `fldkeRTSxff0AdVIj` |
| Nettoverkaufswert | rollup € | `fldIQQ71uz7zfOWN1` |

*Neu ziehen: `list_tables_for_base` → Bestandsprüfungen; Formeln via `get_table_schema`.*

## 🟣 Make-Zugriff (Stand 2026-08-21 · Live-Scan aller 17 Szenarien)

Diese Sektion ist die Langfassung. Kurzfassung steht **in der Base** als Tabellenbeschreibung:

> 🟣 make.com — Zugriffskarte (Stand 2026-08-21, Live-Scan aller 17 Szenarien).
> Make schreibt 7 Felder und liest 11.
> 2 davon matcht Make über den Klartext-Namen — sie tragen 🟣 make.com (KEY · …) in der Feldbeschreibung und dürfen nicht umbenannt werden. Alle übrigen Zugriffe laufen über die Feld-ID und sind umbenennungssicher.
> Vor dem Löschen oder Umtypisieren eines Feldes: POS-Skill → references/airtable/bestandspruefungen.md.

### Namens-gekoppelt — trägt den 🟣-Marker am Feld

- **`ID`** — 🟣 `make.com (KEY · Name)` · formula · `fld24GCd9UoMFtIW6`  
  BSP-Dedup-Schlüssel + sort. Szenarien: 6633991, 6729541, 7001118.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).
- **`Status`** — 🟣 `make.com (KEY · Options)` · singleSelect · `fldVx19XWUNiag4yJ`  
  {Status} != "Ungültig". Szenarien: 6633991.  
  ⚠ Feldname **und** Optionsnamen sind eingefroren — beides bricht den Match still.

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make schreibt:** `Beleg` · `Hinweis` · `Inventar geprüft` · `Store` · `Unterschrieben` · `Vertriebler`  
**Make liest:** `Datum` · `Differenz (Gesamt)` · `Nettoverkaufswert` · `Positionen` · `Store ID`

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**

*Ohne jeden Make-Zugriff: 1 von 14 Feldern.*
