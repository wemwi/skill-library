# Produktvarianten

`tblNQsc69xuDrMBzs` · Kategorie **Stammdaten**

> Feld-Block: **Stand 2026-08-15**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Die verkaufte Einheit (SKU-Ebene). Trägt SKU, Variant-GID und den **wöchentlichen EK-Spiegel** aus Shopify.

## Beziehungen

- **→ `Produkt`** (→ [[produkte]]) · **→ `Preise`** (→ [[preise]]) · **→ `Bestände`** (→ [[bestaende]]).
- Positionen: `Lieferpositionen` · `Umsatzpositionen` · `Bestandsprüfungspositionen`.

## Tragende Felder

- **`ID`** (Text) — **SKU / Artikelnummer.** Match-Schlüssel des Produkt-Syncs **und** Teil des Bestands-Schlüssels (`BST-<Store>-<SKU>`). **Sync schreibt sie nur beim Anlegen, nie beim Update.** Wert ändern verschiebt still den Bestandsschlüssel aller verknüpften Zeilen.
- **`⚙ EK (netto)`** (€) — **Spiegel** des aktuellen `inventoryItem.unitCost`, **wöchentlich überschrieben.** **Kein Stempel** — die Kostenwahrheit liegt eingefroren auf `🟣 Lieferpositionen.⚙ EK (netto)`. **Nie** in eine Kosten-/Saldoformel ziehen.
- **`⚙ Shopify GID`** (Text) — **volle Variant-GID** inkl. `gid://shopify/ProductVariant/…`.
- `Name` (Formel) — `⚙ Name (Produkt) & " " & Variante`. `Variante` (Text) · `⚙ Typ`/`⚙ Shopify Tags` (Lookups).

## Fallstricke

- **`⚙ EK (netto)` ist ein Wochenspiegel, keine Kostenwahrheit** — der häufigste Denkfehler in Kostenformeln.
- **`ID` (SKU) nur beim Anlegen setzen** — ändern bricht den Bestandsschlüssel still.

## Feld-Block (Stand 2026-08-15 · `list_tables_for_base`)

| Feld | Typ | fld-ID |
|---|---|---|
| ID | singleLineText (SKU) | `flduzOEUi4iJGmqmw` |
| Variante | singleLineText | `flddoYJ4b0WsDAcYh` |
| Name | formula | `fldzdSc2JoqkpRT09` |
| Preise | link → Preise | `fldcxkrQhke8lKZD3` |
| Produkt | link → Produkte | `fld0KMcyfc7pSJupr` |
| Bestände | link → Bestände | `fldBlLdkvETpwx9Rv` |
| Lieferpositionen | link → 🟣 Lieferpositionen | `fldUBk3fSQnNPUkG7` |
| Umsatzpositionen | link → 🟣 Umsatzpositionen | `fldoLUxgCSsTNOWUr` |
| Bestandsprüfungspositionen | link → 🟣 …positionen | `fldIHyJBvrfO6Y5iO` |
| ⚙ Typ | lookup | `fld6i3bS5YerX40fq` |
| ⚙ Name | lookup | `fld9VWoWA0QLHTpnP` |
| ⚙ EK (netto) | currency (Wochenspiegel) | `fldjVBRtbovK3Ky92` |
| ⚙ Shopify Tags | lookup | `fldKXKJf6jSmcboG4` |
| ⚙ Shopify GID | singleLineText (Variante) | `fldtyjDFiy2DoFRNN` |

*Neu ziehen: `list_tables_for_base` → Produktvarianten; Formeln via `get_table_schema`.*
