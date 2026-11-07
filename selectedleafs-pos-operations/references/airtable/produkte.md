# Produkte

`tblzCvZoJSrpbuJ5N` · Kategorie **Stammdaten**

> Feld-Block: **Stand 2026-08-15**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Das Produkt (Produkt-Ebene, über den Varianten). Trägt die Shopify-Produkt-Anker.

## Beziehungen

- **→ `Varianten`** (→ [[produktvarianten]]) — die SKUs unter dem Produkt.

## Tragende Felder

- **`ID`** (Text) — **Produktnummer = SKU-Präfix** (Teil vor dem letzten Bindestrich, `10001-003 → 10001`). Match-Schlüssel des Produkt-Syncs (Upsert).
- **`Typ`** (Select: Kratom / Inventar (POS)) — „Inventar (POS)“ = Theken-Displays und Vitrinen (`A10000-…`, `A10001-…`), nie berechnet. Die Vein-Info steht in `Shopify Tags`.
- **`Shopify Tags`** (Text, kommasepariert) — trägt `vein:white|red|green`, auf das der Restock-Filter umstellt. Format/Trennzeichen ändern bricht den Filter still.
- **`Shopify GID`** (Text) — **volle Product-GID** inkl. `gid://shopify/Product/…`. Ebenenwechsel beachten: die Variant-GID sitzt auf [[produktvarianten]].
- `Name` (Text).

## Fallstricke

- **`ID` = SKU-Präfix** ist der Sync-Match — nicht umwidmen.
- **GID voll und produkt-eben** — nicht mit der Variant-GID mischen.

## Feld-Block (Stand 2026-08-15 · `list_tables_for_base`)

| Feld | Typ | fld-ID |
|---|---|---|
| ID | singleLineText (SKU-Präfix) | `fldglRrcSpfvq4ySR` |
| Name | singleLineText | `fldZa1wmLlTenikuC` |
| Varianten | link → Produktvarianten | `fldrtyqubXiTGE2xm` |
| Typ | singleSelect | `fldKkreKUYX5WuLoW` |
| Shopify Tags | singleLineText | `fldWyNQ07Mh6Xcpgg` |
| Shopify GID | singleLineText (Produkt) | `fld2a7MGVts13AEeW` |

*Neu ziehen: `list_tables_for_base` → Produkte; Formeln via `get_table_schema`.*

## 🟣 Make-Zugriff (Stand 2026-08-21 · Live-Scan aller 17 Szenarien)

Make schreibt **5** Felder und liest **5**. Ein Feld trägt den 🟣-Marker in der Feldbeschreibung der Base (seit 2026-11-06).

### Namens-gekoppelt — trägt den 🟣-Marker am Feld

- **`Typ`** — 🟣 `make.com (KEY · Options)` · singleSelect · `fldKkreKUYX5WuLoW`  
  Optionsname „Inventar (POS)“ wird in 6633991 „Bestandsprüfung zuordnen“ verglichen (gelesen über das Lookup [[bestandspruefungspositionen]].Typ). Die 🟢-Zeile der App bleibt darunter.  
  ⚠ Option umbenennen bricht den Vergleich still: Displays zählen dann wieder als „fehlt auf der Rechnung“.

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make schreibt:** `ID` · `Name` · `Shopify GID` · `Shopify Tags` · `Typ`  

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**

*Ohne jeden Make-Zugriff: 1 von 6 Feldern.*
