# Gutschriften

`tbl898JRp3HFDymhJ` · Kategorie **Ereignis** (INSERT-only, Sonderfall `Status`) · seit 09.11.2026

> Feld-Block: **Stand 2026-11-09**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Eine Zeile = eine **Gutschrift an den Store** (JTL-Nummernkreis `RK-`). Beträge und Mengen stehen **positiv**, abgezogen wird nur in den Summen mit zwei Quellen (→ [[model]] §3). Was eine Gutschrift ist, entscheidet die Tabelle, nie das Vorzeichen: Eine negative Warenzeile auf einer Rechnung (RG-10146-1) bleibt in [[umsaetze]].

## Beziehungen

- **→ `Vertriebler`** / **→ `Store`** (Einzel) — wessen Provision sinkt, welcher Store.
- **→ `Konditionen`** (Einzel) — die Version zum Datum der Gutschrift.
- **→ `Belege`** — Rückfeld von `Belege.Gutschrift`; `Datum` leitet sich daraus ab.
- **→ `Gutschriftspositionen`** (Kinder) — `Nettobetrag`, `Menge (Stück)` und `Nettoverkaufswert` rollen von dort → [[gutschriftspositionen]].
- Rückwege: `Vertriebler.Gutschriften` · `Stores.Gutschriften` · `Konditionen.Gutschriften` · `Belege.Gutschrift`.

## Tragende Felder

- **`Nettobetrag`** (Rollup, €, positiv) — Σ `Gutschriftspositionen.Nettobetrag`. **Die Geldwahrheit.**
- **`Status`** (Select) — Offen / Verrechnet / Storniert. Setzt nur `[Process] Lexware Voucher (Refund · Store)`; ein Storniert bleibt Storniert. Make schreibt an einer Gutschrift **keinen Betrag**: Der Status entscheidet, die Formel rechnet.
- **`Provision`** (Formel, €) — `(Nettobetrag × Provisionssatz) × (1 + MwSt.)`, wie an `Umsätze`.
- **`Realprovision`** (Formel, €) — `Status = Verrechnet`: `Provision`, sonst 0. Rollt ohne Storniert zu `Vertriebler.Gutschriften Realprovision` und mindert dort den Saldo. Ganz oder gar nicht, es gibt keine Teilverrechnung.
- **`Nettoverkaufswert`** (Rollup, €) — zum Endkunden-VK.
- **`Storemarge`** (Formel, €) — `Nettoverkaufswert − Nettobetrag`. Rollt ohne Storniert zu `Stores.Gutschriften Storemarge (Jahr/Gesamt)`, das Jahr über `Datum`.
- `Menge (Stück)` (Rollup, Kennzahlen der Sales App) · `Datum` (Lookup ← `Belege.Datum`) · `Provisionssatz` / `MwSt.` (Lookup ← Konditionen) · `Hinweis` (aus `[Resolve] Lexware Voucher`) · **`Lexware ID`** (Voucher-ID, `resource_id` für einen Neuanstoß).

Anders als an `Umsätze` gibt es kein `Bezahlt`, `Offen`, `Fällig am`, `Menge (kg)`, `Deckungsbeitrag`, `Zahlungsverlauf`, `Modell`: Eine Gutschrift hat keine Fälligkeit.

## Fallstricke

- **Nicht von selbst verrechnet.** Die Hand trägt die Verrechnung ein (`task.jtl_refund`). Eine Gutschrift, die länger als 30 Tage Offen steht, ist ein Signal.
- **Das Lexware-Ereignis zur Verrechnung ist noch unbelegt** (Stand 09.11.2026): Bei Rechnungen funktioniert es, bei einer Gutschrift wurde es nie beobachtet. Bleibt es aus, bleibt der Status Offen, `Realprovision` 0 und der Saldo still zu hoch.
- **`Status` wird vom App-Code über den Optionsnamen verglichen** (🟢) — Optionen nicht umbenennen.
- **Eine neue Summe über `Umsätze` vergisst die Gutschriften still** → [[model]] §3.

## Feld-Block (Stand 2026-11-09 · `list_tables_for_base`)

| Feld | Typ | fld-ID |
|---|---|---|
| ID | singleLineText | `fld2tlGJe15RAO5Ze` |
| Status | singleSelect | `fld8A4cFX8lAYWnuc` |
| Vertriebler | link → Vertriebler | `fldpNUciKGaUi9mLX` |
| Store | link → Stores | `fldJtxbitmBc6X98R` |
| Konditionen | link → Konditionen | `fldXraJ91MpYEMvaD` |
| Belege | link → Belege | `fldbq9UUI1JlNYYVk` |
| Gutschriftspositionen | link → Gutschriftspositionen | `fldpuR150rV84SXAV` |
| Datum | lookup (← Belege.Datum) | `fld7BGAwB3NMTJIaB` |
| Nettobetrag | rollup € | `fld0gfAtT80Gd32H3` |
| Menge (Stück) | rollup | `fldBjWHFrOcsJVUZK` |
| Provisionssatz | lookup % (← Konditionen) | `fldv3HtofF7v7XD1S` |
| MwSt. | lookup % (← Konditionen) | `fldzLL7i2Mp2Yv8CW` |
| Nettoverkaufswert | rollup € | `fldz09A0Okw5vwPsX` |
| Provision | formula € | `fldXvaAj0FdZSzWXz` |
| Hinweis | multilineText | `fldYhDAqE3sxw3BRb` |
| Lexware ID | singleLineText | `fldsTEENILz0mkHx0` |
| Realprovision | formula € | `fldIAySMYDsuX5sCS` |
| Storemarge | formula € | `fldLiob1fyDDfxfgj` |

*Neu ziehen: `list_tables_for_base` → Gutschriften; Formeln via `get_table_schema`.*

## 🟣 Make-Zugriff (Stand 2026-11-09)

Make schreibt **7** Felder und liest **8**, alle in `[Process] Lexware Voucher (Refund · Store)` (8450345) und `[Notify] Telegram Channels` (6862968). Eines davon matcht Make über den Klartext-Namen — es trägt den 🟣-Marker in der Feldbeschreibung der Base und darf nicht umbenannt werden.

### Namens-gekoppelt — trägt den 🟣-Marker am Feld

- **`ID`** — 🟣 `make.com (KEY · Name)` · singleLineText · `fld2tlGJe15RAO5Ze`  
  RK-Nummer = Dedup: `filterByFormula` von „Find credit note“. Szenarien: 8450345.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make schreibt:** `Status` · `Hinweis` · `Vertriebler` · `Store` · `Konditionen` · `Lexware ID`  
**Make liest:** `Status` · `Gutschriftspositionen` (8450345 „Verdict“) · `Belege` (8450345 „Reload credit note (by number)“, für „Document exists?“ und „Read document (by ID)“, Nachtrag 2026-11-12) · `Vertriebler` · `Store` · `Nettobetrag` · `Provision` (6862968 „Map event“)

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**

## 🟢 App-Zugriff

**`Status`** — 🟢 `App (KEY · Options)`: Die Sales App vergleicht Offen, Verrechnet und Storniert über den Optionsnamen. Feldliste: `src/config/airtable.ts` (Repo `selectedleafs-app`).
