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
- **`Typ`** (Lookup ← `Produkt` → Produktvarianten.Typ ← Produkte.Typ, seit 2026-11-06) — „Inventar (POS)“ (Display, Vitrine) zählt in der Rechnungszuordnung nicht als „fehlt auf der Rechnung“.
- `SOLL` / `IST` (Zahl) · Lookups `Store`, `Geprüft am`.

## Fallstricke

- **Nur positive Differenzen** fließen in den Wert — die Gesamtsumme auf [[bestandspruefungen]] ist damit ein **Schwund**-Wert, kein Netto-Saldo.
- **Mehrbestand** (IST > SOLL) ist eine gültige Position mit negativer Differenz: `[Process] Correction (Inventory)` bucht sie nach bestätigter Zählung (seit 07.11.2026), korrigiert wird mit einer **freien Gutschrift in JTL** je Prüfung (→ [[bestaende]]). Alte Rechnungen mit Gutschriftzeile vergleicht die Zuordnung weiter mit Vorzeichen (→ [[scenarios]]).
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
| Typ | lookup (← Produkt → Typ, Nachtrag 2026-11-06) | `fld79OILwkJ3pCNp2` |

*Neu ziehen: `list_tables_for_base` → Bestandsprüfungspositionen; Formeln via `get_table_schema`.*

## 🟣 Make-Zugriff (Stand 2026-08-21 · Live-Scan aller 17 Szenarien)

Make schreibt **7** Felder und liest **4** (seit 2026-11-06 `Typ`). Eines davon matcht Make über den Klartext-Namen — es trägt den 🟣-Marker in der Feldbeschreibung der Base und darf nicht umbenannt werden.

### Namens-gekoppelt — trägt den 🟣-Marker am Feld

- **`ID`** — 🟣 `make.com (KEY · Name)` · formula · `fldVekCJcYqoCakJw`  
  BSP-Positionsschluessel + sort. Szenarien: 6633991.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make schreibt:** `Bestand` · `Bestandsprüfung` · `IST` · `Position` · `Preis` · `Produkt` · `SOLL` (6729541 „Create line“; seit 06.11.2026 auch `[Process] Correction (Inventory)` 8413130 „Create line“, gleiche Felder)  
**Make liest:** `Differenz` · `Produkt` · `Position` (`[Process] Correction (Inventory)` 8413130 „Load booked lines“, `cellFormat=string` → `Produkt` = SKU) · `Typ` (6633991 „Positionen der Bestandsprüfungen“, alle Felder per Feld-ID, `cellFormat=string` → Optionsname; seit 2026-11-06)

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**

*Ohne jeden Make-Zugriff: 6 von 16 Feldern.*
