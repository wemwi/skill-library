# Lieferpositionen

`tblx50DHx4MmgNDz0` · Kategorie **Positionen** (INSERT-only Kind von [[lieferungen]])

> Feld-Block: **Stand 2026-08-15**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Eine Zeile = **eine Sorte in einer Lieferung**. Hier entstehen **Kosten** und **Nettoverkaufswert** einer Position — und hier wird der **Einkaufspreis eingefroren**.

## Beziehungen

- **→ `Lieferung`** (Einzel) — Elternzeile → [[lieferungen]].
- **→ `Produkt`** (→ Produktvarianten) / **→ `Preis (VK)`** (→ [[preise]], eff-dated) / **→ `Bestand`** (→ [[bestaende]]).

## Tragende Felder

- **`ID`** (Formel) — `{Lieferung} & "#" & {Position}`.
- **`EK (netto)`** (€) — **eingefrorene Kostenwahrheit:** Make stempelt den EK zum Lieferzeitpunkt. **Nie** `Produktvarianten.EK` (Wochenspiegel) verwenden.
- **`Kosten`** (Formel, €) — `Menge (Stück) × EK (netto)`. `Menge (kg)` fließt bewusst **nicht** ein (stückbezogen). Rollt zu `Lieferungen.Kosten`.
- **`Nettoverkaufswert`** (Formel, €) — `Menge (Stück) × VK (netto)`.
- **`VK (netto)`** (Lookup ← [[preise]]) — der VK der am Leistungsdatum gültigen Preis-Version.
- **`Menge nach Prüfung`** (Formel) — `IF(Geprüft am UND Geliefert am ≥ Geprüft am, Menge (Stück), 0)`; zählt nur Lieferungen nach der letzten Prüfung.
- `Menge (Stück)` / `Menge (kg)` (Zahl) · Lookups `Store`, `Typ`, `Geliefert am`, `Geprüft am`.

## Fallstricke

- **`EK (netto)` ist der Anker der ganzen Kostenrechnung** — einmal gestempelt, nie nachziehen.
- Kosten/Nettoverkaufswert sind **stückbezogen**; kg-Ware trägt separat.

## Feld-Block (Stand 2026-08-15 · `list_tables_for_base`)

| Feld | Typ | fld-ID |
|---|---|---|
| ID | formula | `fld786Wnznynl6z7P` |
| Position | number | `fldHnqVVQPviYPomm` |
| Produkt | link → Produktvarianten | `fldT6tuOC7kRtXc4A` |
| Preis (VK) | link → Preise | `fldz8UF0axxIEXrkS` |
| Menge (Stück) | number | `fld0s7ImC25dOXiAJ` |
| Menge (kg) | number | `fldkSfH0XolhyTllM` |
| Kosten | formula € | `fldWKTdp2YcEIkYj2` |
| Nettoverkaufswert | formula € | `fldMegtghD0qglzZd` |
| Lieferung | link → Lieferungen | `fldsQcLHRJ91Z4QAz` |
| Bestand | link → Bestände | `fldKDWcARIDbNzWaY` |
| Store | lookup | `fldmDlpdNvGpwyIT0` |
| Typ | lookup | `flds0OYRLeoqGNTZj` |
| EK (netto) | currency (Stempel) | `fldXjhHYoQHScHO3x` |
| VK (netto) | lookup € (← Preise) | `fld6EC8C4Kbj6U9zr` |
| Menge nach Prüfung | formula | `fldZkXmoj818dSR88` |
| Geliefert am | lookup | `fldXhSj8qLpfzmTlF` |
| Geprüft am | lookup | `fld7MUJBmICExHpBV` |

*Neu ziehen: `list_tables_for_base` → Lieferpositionen; Formeln via `get_table_schema`.*

## 🟣 Make-Zugriff (Stand 2026-08-21 · Live-Scan aller 17 Szenarien)

Diese Sektion ist die Langfassung. Kurzfassung steht **in der Base** als Tabellenbeschreibung:

> 🟣 make.com — Zugriffskarte (Stand 2026-08-21, Live-Scan aller 17 Szenarien).
> Make SCHREIBT hier 8 Felder und liest keines.
> Alle Zugriffe laufen über die Feld-ID — Umbenennen ist hier folgenlos.
> Vor dem Löschen oder Umtypisieren eines Feldes: POS-Skill → references/airtable/lieferpositionen.md.

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make schreibt:** `Bestand` · `EK (netto)` · `Lieferung` · `Menge (Stück)` · `Menge (kg)` · `Position` · `Preis (VK)` · `Produkt`  

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**

*Ohne jeden Make-Zugriff: 9 von 17 Feldern.*
