# Lieferungen

`tblH3WUD6XchyyMYQ` · Kategorie **Ereignis** (INSERT-only)

> Feld-Block unten: **Stand 2026-08-15**, generiert aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Eine Zeile = eine **Warenübergabe (Kommission)** an einen Store, belegt durch das Lieferschein-PDF. Trägt den **Kostenanteil** des Vertrieblers — den Abzug, der bei der Lieferung entsteht.

## Beziehungen

- **→ `Store`** / **→ `Vertriebler`** (je Einzel-Link) — an wen geliefert wurde, wer liefert.
- **→ `Beleg`** (Einzel) — das Quell-PDF; `Datum` wird von dort gespiegelt und ist damit das **Leistungsdatum**.
- **→ `Konditionen`** (Einzel) — die am Leistungsdatum gültige Version; Make setzt sie (jüngste `Gültig ab ≤ Leistungsdatum`, siehe [[model]] §4).
- **→ `Lieferpositionen`** (Kinder) — die Positionszeilen; alle Mengen- und Wertsummen rollen von dort hoch → [[lieferpositionen]].
- Rückwege: `Vertriebler.Lieferungen` · `Stores.Lieferungen` · `Belege.Lieferung` · `Konditionen.Lieferungen`.

## Tragende Felder

- **`ID`** (Text) — **Dedup-Schlüssel = Belegnummer aus dem PDF.** Ein zweiter Beleg mit gleicher Nummer wird abgewiesen. Make schreibt den Wert (kein Formelfeld). **Zeitpunkt (seit 10.11.2026):** `[Process] Upload PDF (Delivery)` schreibt die Nummer schon mit dem sauberen Verdikt, vor der ersten Position, und leert sie wieder, wenn die Zeile Fehlerhaft wird. Eine Zeile In Bearbeitung trägt also ihre Nummer, eine fehlerhafte nie. Rückhol-Lieferungen (`RETURN-…`) bekommen ihre Nummer weiter erst beim Abschluss. Die Sales App zeigt die `ID` als Titel, auch bei In Bearbeitung (entschieden 10.11.2026).
- **`Kostenanteil`** (Formel, €) — **der Geldwert dieser Tabelle.** Live:
  `Kosten × Kostensatz × (1 + MwSt.)` → also **brutto**. Rollt zu `Vertriebler.Kostenanteil`. Entsteht **bei der Lieferung**.
- **`Kosten`** (Rollup, €) — Σ `Lieferpositionen.Kosten` (EK × Menge, mit **eingefrorenem** EK).
- **`Nettoverkaufswert`** (Rollup, €) — Σ `Lieferpositionen.Nettoverkaufswert` (VK-Sicht).
- **`Kostensatz`** (Lookup %) / **`MwSt.`** (Lookup %) — aus der verknüpften `Konditionen`-Version; speisen die Kostenanteil-Formel.
- **`Konditionen`** (Link) — die eff-dated gewählte Version.
- **`Status`** (Select: Abgeschlossen / In Bearbeitung / Fehlerhaft) — von Make als **String** geschrieben; Option umbenennen bricht still. **In Bearbeitung** heißt: läuft gerade oder ist Rest eines Abbruchs. Nur solche Zeilen löscht `[Process] Upload PDF (Leftovers)` vor dem Neulauf des Belegs.
- **`Datum`** (Lookup aus `Beleg.Datum`) — das **Leistungsdatum**, im **EU-Format D/M/YYYY** (Datum-Fallstrick, [[model]] §4).
- Nebenfelder: `Unterschrieben` (Checkbox) · `Menge (kg)`/`Menge (Stück)` (Rollups) · `Positionen` (Count) · `Hinweis` (Freitext, Make).

## Fallstricke

- **`Kosten` nutzt den eingefrorenen EK** aus `Lieferpositionen.EK (netto)` — **nie** `Produktvarianten.EK` (wöchentlicher Spiegel).
- **Belegnummer als `ID`** — Präfix/Format nicht anfassen (Dedup bricht sonst).
- **Kein Beleg → kein Datum → keine Konditionen-Wahl.** Das Leistungsdatum kommt aus dem verknüpften Beleg; fehlt er, greift die eff-dated Auswahl ins Leere.

## Feld-Block (Stand 2026-08-15 · `list_tables_for_base`)

| Feld | Typ | fld-ID |
|---|---|---|
| ID | singleLineText | `fldRZt5ook8jiiXaX` |
| Unterschrieben | checkbox | `fldDL1j7Xi5EXWpkJ` |
| Datum | lookup (← Beleg.Datum) | `fldKxC3S6iPZWBPbb` |
| Store | link → Stores | `fldWIfDN3u4yqZdN0` |
| Vertriebler | link → Vertriebler | `fldefhwzZt8hvQsKz` |
| Positionen | count | `fldnR6OkuOcI2AOHC` |
| Menge (kg) | rollup | `fld3IgMAQ3xYtfS7u` |
| Menge (Stück) | rollup | `fldmktz4oon39L83O` |
| Nettoverkaufswert | rollup € | `fld9tGKsmBYYRB8JD` |
| Kosten | rollup € | `fldwwJJ06eEEHgqVu` |
| Status | singleSelect | `fldCDruCnZNbtWoTp` |
| Beleg | link → Belege | `fldsXRNjRjD5uNmNo` |
| Kostenanteil | formula € | `fldRwGytS9Aykbyvx` |
| Lieferpositionen | link → Lieferpositionen | `fldKIfbnlTXtY8Eao` |
| Konditionen | link → Konditionen | `fldb9n5LNojKhKagq` |
| MwSt. | lookup % (← Konditionen) | `fld4U0at6UEhfaGjU` |
| Kostensatz | lookup % (← Konditionen) | `fldUAQIUvOVlHY0kv` |
| Hinweis | multilineText | `fldvyBYJemYnmOz5T` |

*Neu ziehen: `list_tables_for_base(appiIkOaz1ID1FjfE)` → Tabelle Lieferungen; Formeln via `get_table_schema`.*

## 🟣 Make-Zugriff (Stand 2026-08-21 · Live-Scan aller 17 Szenarien)

Make schreibt **8** Felder und liest **10**. Zwei davon matcht Make über den Klartext (Nachtrag 2026-11-10: `Status`) — sie tragen den 🟣-Marker in der Feldbeschreibung der Base und dürfen nicht umbenannt werden.

### Namens-gekoppelt — trägt den 🟣-Marker am Feld

- **`ID`** — 🟣 `make.com (KEY · Name)` · singleLineText · `fldRZt5ook8jiiXaX`  
  Belegnummer = Dedup. Szenarien: 6677862.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).
- **`Status`** — 🟣 `make.com (KEY · Options)` · singleSelect · `fldCDruCnZNbtWoTp` (gesetzt 2026-11-10, steht über 🟢 `App (KEY · Options)`)  
  8495399 vergleicht den Optionsnamen „In Bearbeitung“ im Code „Pick leftovers“. 6633991 vergleicht „Abgeschlossen“ im Code „Assign delivery note“ (seit 2026-11-11): Nur solche Lieferungen ordnet die Rechnung einem Lieferschein zu. Geschrieben wird der Status weiter über die Options-ID.  
  ⚠ Option umbenennen: Reste werden nicht mehr erkannt und nicht entfernt (still), und die Rechnung ordnet keinen Lieferschein mehr zu (sichtbar am Hinweis des Umsatzes).

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make schreibt:** `Beleg` · `Hinweis` · `Konditionen` · `Status` · `Store` · `Unterschrieben` · `Vertriebler`  
**Make löscht:** ganze Zeilen mit Status In Bearbeitung (8495399, nur am selben Beleg)  
**Make liest:** `Datum` · `Kosten` · `Kostenanteil` · `Menge (Stück)` · `Nettoverkaufswert` · `Positionen`

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**

*Ohne jeden Make-Zugriff: 4 von 18 Feldern.*
