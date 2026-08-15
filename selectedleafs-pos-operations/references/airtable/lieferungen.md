# Lieferungen

`tblH3WUD6XchyyMYQ` · Kategorie **Ereignis** (INSERT-only)

> Feld-Block unten: **Stand 2026-08-15**, generiert aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Eine Zeile = eine **Warenübergabe (Kommission)** an einen Store, belegt durch das Lieferschein-PDF. Trägt den **Kostenanteil** des Vertrieblers — den Abzug, der bei der Lieferung entsteht.

## Beziehungen

- **→ `Store`** / **→ `Vertriebler`** (je Einzel-Link) — an wen geliefert wurde, wer liefert.
- **→ `Beleg`** (Einzel) — das Quell-PDF; `Datum` wird von dort gespiegelt und ist damit das **Leistungsdatum**.
- **→ `Konditionen`** (Einzel) — die am Leistungsdatum gültige Version; Make setzt sie (jüngste `Gültig ab ≤ Leistungsdatum`, siehe [[model]] §4).
- **→ `🟣 Lieferpositionen`** (Kinder) — die Positionszeilen; alle Mengen- und Wertsummen rollen von dort hoch → [[lieferpositionen]].
- Rückwege: `Vertriebler.Lieferungen` · `Stores.Lieferungen` · `Belege.Lieferung` · `Konditionen.Lieferungen`.

## Tragende Felder

- **`ID`** (Text) — **Dedup-Schlüssel = Belegnummer aus dem PDF.** Ein zweiter Beleg mit gleicher Nummer wird abgewiesen. Make schreibt den Wert (kein Formelfeld).
- **`Kostenanteil`** (Formel, €) — **der Geldwert dieser Tabelle.** Live:
  `Kosten × ⚙ Kostenanteil × (1 + ⚙ MwSt.)` → also **brutto**. Rollt zu `Vertriebler.Kostenanteil`. Entsteht **bei der Lieferung**.
- **`Kosten`** (Rollup, €) — Σ `🟣 Lieferpositionen.Kosten` (EK × Menge, mit **eingefrorenem** EK).
- **`Nettoverkaufswert`** (Rollup, €) — Σ `🟣 Lieferpositionen.Nettoverkaufswert` (VK-Sicht).
- **`⚙ Kostenanteil`** (Lookup %) / **`⚙ MwSt.`** (Lookup %) — aus der verknüpften `Konditionen`-Version; speisen die Kostenanteil-Formel.
- **`Konditionen`** (Link) — die eff-dated gewählte Version.
- **`Status`** (Select: Abgeschlossen / In Bearbeitung / Fehlerhaft) — 🟣 von Make als **String** geschrieben; Option umbenennen bricht still.
- **`Datum`** (Lookup aus `Beleg.Datum`) — das **Leistungsdatum**, im **EU-Format D/M/YYYY** (Datum-Fallstrick, [[model]] §4).
- Nebenfelder: `Unterschrieben` (Checkbox) · `Menge (kg)`/`Menge (Stück)` (Rollups) · `Positionen` (Count) · `⚙ Hinweis` (Freitext, Make).

## Fallstricke

- **`Kosten` nutzt den eingefrorenen EK** aus `🟣 Lieferpositionen.⚙ EK (netto)` — **nie** `Produktvarianten.⚙ EK` (wöchentlicher Spiegel).
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
| Lieferpositionen | link → 🟣 Lieferpositionen | `fldKIfbnlTXtY8Eao` |
| Konditionen | link → Konditionen | `fldb9n5LNojKhKagq` |
| ⚙ MwSt. | lookup % (← Konditionen) | `fld4U0at6UEhfaGjU` |
| ⚙ Kostenanteil | lookup % (← Konditionen) | `fldUAQIUvOVlHY0kv` |
| ⚙ Hinweis | multilineText | `fldvyBYJemYnmOz5T` |

*Neu ziehen: `list_tables_for_base(appiIkOaz1ID1FjfE)` → Tabelle Lieferungen; Formeln via `get_table_schema`.*
