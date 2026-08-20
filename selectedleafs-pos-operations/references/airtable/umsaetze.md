# Umsätze

`tbl0Xqw2eK7KPVVWY` · Kategorie **Ereignis** (INSERT-only)

> Feld-Block: **Stand 2026-08-15**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Eine Zeile = ein **abgerechneter Store-Umsatz** (Rechnung an den Store). Trägt die **Provision** des Vertrieblers — den Betrag, der bei **Zahlung** gutgeschrieben wird.

## Beziehungen

- **→ `Vertriebler`** / **→ `Store`** (Einzel) — wessen Provision, welcher Store.
- **→ `Belege`** (mehrere) — Rechnung + Mahnstufen; `Datum` und `Zahlungsverlauf` leiten sich daraus ab.
- **→ `Konditionen`** (Einzel) — die eff-dated Version (Provision %/MwSt.).
- **→ `Umsatzpositionen`** (Kinder) — Positionszeilen; `Nettoumsatz` rollt von dort → [[umsatzpositionen]].
- Rückwege: `Vertriebler.Umsätze` · `Stores.Umsätze` · `Konditionen.Umsätze` · `Belege.Umsatz`.

## Tragende Felder

- **`Provision`** (Formel, €) — **der Geldwert dieser Tabelle:** `(Nettoumsatz × Provisionssatz) × (1 + MwSt.)`, brutto. Rollt zu `Vertriebler.Provision`. Wirksam **bei Zahlung**.
- **`Nettoumsatz`** (Rollup, €) — Σ `Umsatzpositionen.Nettoumsatz`. **Die Geldwahrheit.**
- **`Offen`** (Formel, €) — `Nettoumsatz − Bezahlt`. `Bezahlt` (€) setzt der Zahlungs-Sync.
- **`Realprovision`** (Formel, €) — `(Bezahlt × Provisionssatz) × (1 + MwSt.)` — Provision auf den **tatsächlich gezahlten** Betrag (bei Teilzahlung < Provision). Rollt zu `Vertriebler.Realprovision`.
- **`Deckungsbeitrag`** (Formel, €) — `Nettoumsatz − Provision`.
- **`Zahlungsverlauf`** (Rollup ← `Belege.Belegtyp`) — »pünktlich« / »nach Zahlungserinnerung« / »nach Mahnung«; speist `{Zahlungsverlauf}` in der invoice.paid-Meldung.
- **`Status`** (Select) — Offen / Bezahlt / **Teilgezahlt** / Überfällig / Angemahnt / Storniert / Ausgebucht. Teilzahlung ist ein definierter Zustand (Lexware-Payments-Sync).
- **`Provisionssatz`** / **`MwSt.`** (Lookup %, ← Konditionen) · **`Fällig am`** (Datum) · `Datum` (Lookup ← Beleg, EU) · `Nettoumsatzerlös` (Rollup) · `Hinweis`.

## Fallstricke

- **`Nettoumsatz` ist die Geldwahrheit, nicht `Nettoumsatzerlös`** (Endkunden-VK, liegt höher = Storemarge). Nur `Nettoumsatz` speist Provision/Saldo.
- **Status wird von Make als String geschrieben** — Optionen nicht umbenennen (still).
- Provision ist nominal auf `Nettoumsatz`; die *ausgezahlt-relevante* Größe bei Teilzahlung ist `Realprovision`.

## Feld-Block (Stand 2026-08-15 · `list_tables_for_base`)

| Feld | Typ | fld-ID |
|---|---|---|
| ID | singleLineText | `flda4tTUPnyeuQbDP` |
| Datum | lookup (← Beleg.Datum) | `fld0Im1qb7MkoHdpU` |
| Status | singleSelect | `fldBavq4sjk2A1swZ` |
| Vertriebler | link → Vertriebler | `fldTobkViXGCZIQeF` |
| Store | link → Stores | `fldUQQ1FP5N7pRoX9` |
| Nettoumsatz | rollup € (← Umsatzpos.) | `fld0GMbvW8P8t25Nq` |
| Bezahlt | currency | `fldzRKStpN9Ol5waf` |
| Offen | formula € | `fldR5minFlFXlIQD8` |
| Menge (Stück) | rollup | `fldEEcde4x6hLzUtY` |
| Menge (kg) | rollup | `fldisY72MEBPUnsRc` |
| Provision | formula € | `fldFyNHkSGWdNgSKr` |
| Deckungsbeitrag | formula € | `fldbQPXY2teAQy3Mb` |
| Belege | link → Belege | `fldNzKOlcz5XPnN4R` |
| Konditionen | link → Konditionen | `fldmJIe1HsS2AbhEq` |
| Umsatzpositionen | link → Umsatzpositionen | `fldL8VZayamrjaTtO` |
| Nettoumsatzerlös | rollup € | `fldAMjqcnsoThk6Mh` |
| Provisionssatz | lookup % (← Konditionen) | `fld7cBwzN5gapHOsi` |
| MwSt. | lookup % (← Konditionen) | `fldb9cPCsjUz2jAHe` |
| Hinweis | multilineText | `fldFD4fPdpvi9pVQZ` |
| Fällig am | date | `fldj7QHDMWnFxSTZn` |
| Realprovision | formula € | `fldXTWtER7WgOIqd6` |
| Zahlungsverlauf | rollup (← Belege.Belegtyp) | `fldVQODqhEZrbBNDm` |

*Neu ziehen: `list_tables_for_base` → Umsätze; Formeln via `get_table_schema`.*

## 🟣 Make-Zugriff (Marker in der Base-Feldbeschreibung)

Trägt einen 🟣-Zugriffsmarker in der Base-Feldbeschreibung (SSoT: [[model]] §2).

- **`Hinweis`** — 🟣 WRITE. Freitext des pos-invoice-Szenarios (Extraktions-Hinweise / Fehlertexte).
- **`Zahlungsverlauf`** — 🟣 READ. Rollup; speist {Zahlungsverlauf} in der invoice.paid-Meldung.

- **`ID`** — 🟣 READ+WRITE. Make-geschriebener Dedup-Schlüssel.
- **`Status`** — 🟣 WRITE (Offen / Bezahlt / Teilgezahlt / Überfällig / Angemahnt / Storniert / Ausgebucht). Make schreibt als String.
