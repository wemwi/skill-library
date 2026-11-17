# Jahresboni

`tblmfGeURrwQyeqDc` · Kategorie **Stammdaten je Jahr** (eine Zeile je Store und Bemessungsjahr) · seit 17.11.2026

> Feld-Block: **Stand 2026-11-17**, aus `list_tables_for_base` und `get_table_schema`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Der Jahresbonus eines Eigenbestand-Stores (Spec Jahresbonus Stufe A v3.1, Projekt „selectedleafs.com · Technik“). Make hält je Store und Jahr die erreichte **Stufe** fest; Airtable rechnet daraus Bonus, Einlösung und Guthaben. Make schreibt hier **keinen Geldwert**.

## Beziehungen

- **→ `Store`** (→ [[stores]]) — Rückfeld `Stores.Jahresboni`, darüber das Rollup `Stores.Bonusguthaben`.
- **← `Bonuszeilen`** (Rückfeld von `Umsatzpositionen.Jahresbonus`, → [[umsatzpositionen]]) — die Bonuszeilen der Rechnungen, die diesen Bonus einlösen.

## Tragende Felder

- **`ID`** (Text, Primärfeld) — `<Kundennummer>-<Jahr>`, z. B. „10026-2026“. Dedup-Schlüssel: `[Maintain] Partner Tier Check` schreibt per Upsert über dieses Feld, `[Resolve] Lexware Voucher` sucht die Vorjahreszeile mit `{ID} = "…"`.
- `Jahr` (Zahl) — Bemessungsjahr · `Store` (Link).
- **`Stufe`** (Auswahl Bronze · Silber · Gold · Platin · Diamant) — von Make gesetzt, leer = keine Stufe (Storno unter Bronze). Bis 31.01. rechnet Make das Vorjahr nach, danach bleibt die Vorjahreszeile, wie sie ist.
- `Eingelöst` (Rollup Σ `Umsatzpositionen.Bonus brutto`, ohne Storniert, negativ) — Storno und Neulauf rechnen sich selbst.
- **`Guthaben`** (Formel) — `IF({Jahr}+1=YEAR(TODAY()), ROUND(SWITCH({Stufe},"Bronze",150,"Silber",400,"Gold",800,"Platin",1500,"Diamant",2500,0)+{Eingelöst},2), 0)`: brutto, einlösbar nur im Folgejahr, verfällt am 31.12. von selbst.

## Fallstricke

- **Staffel an drei Stellen:** Schwellen im Code „Plan tiers“ von `[Maintain] Partner Tier Check`, Bonusbeträge in der Formel `Guthaben`, dazu die Eigenen Felder der Firma in JTL. Ändern nur alle drei zugleich, die Formel mit Jahresweiche (`IF({Jahr}>=…)`), alte Jahre bleiben.
- Optionsnamen von `Stufe` stehen als Text in der Formel `Guthaben` und im Code „Plan tiers“ (dort mit Options-ID): umbenennen bricht beides.
- Rückwechsel zu Kommission oder Vertragsende: Guthaben bleibt stehen, ist aber nicht einlösbar (`[Resolve] Lexware Voucher` lehnt eine Bonuszeile außerhalb Eigenbestand ab).

## Feld-Block (Stand 2026-11-17 · `list_tables_for_base`)

| Feld | Typ | fld-ID |
|---|---|---|
| ID | singleLineText (Primärfeld) | `fldvwd4Lslt71Lbmh` |
| Jahr | number (0 Stellen) | `fldTh3d4kPXToX95a` |
| Stufe | singleSelect (Bronze `selQQ5W7PCdzkuqia` · Silber `selUJT2xrYSVoCwWC` · Gold `selmSU4soSApSLJD2` · Platin `seltKC0gwQsVF3Iml` · Diamant `sel3Tkvp9zcNXbSGE`) | `fldvRIzDidCCDNBln` |
| Store | link → Stores | `fldx9YoYyk5ROzZCX` |
| Bonuszeilen | link → Umsatzpositionen (Rückfeld von `Jahresbonus`) | `fldbp0XciMkPB7MrV` |
| Eingelöst | rollup | `fldg97OWQbxclPucd` |
| Guthaben | formula | `fldFzDlKbSb27rq9u` |

*Neu ziehen: `list_tables_for_base` → Jahresboni; Formel via `get_table_schema`.*

## 🟣 Make-Zugriff (Stand 2026-11-17 · gebaute Import-JSON)

### Namens-gekoppelt — trägt den 🟣-Marker am Feld

- **`ID`** — 🟣 `make.com (KEY · Name)` · `fldvwd4Lslt71Lbmh` — `filterByFormula` in „Find annual bonus (by ID)“ (`[Resolve] Lexware Voucher`).
- **`Stufe`** — 🟣 `make.com (KEY · Options)` · `fldvRIzDidCCDNBln` — „Plan tiers“ vergleicht die gelesenen Optionsnamen.
- `Jahr` steht in der Suchformel von „Find annual bonuses“ (`{Jahr}>=YEAR(TODAY())-2`).

### fld-ID-fest

**Make schreibt** (`[Maintain] Partner Tier Check`, „Upsert annual bonus“): `ID` · `Store` · `Jahr` · `Stufe` (Options-ID).
**Make liest:** `ID` · `Jahr` · `Stufe` · `Store` („Find annual bonuses“), Record-ID für `Umsatzpositionen.Jahresbonus` („Find annual bonus (by ID)“).
