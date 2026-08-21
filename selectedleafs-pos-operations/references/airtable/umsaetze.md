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

## 🟣 Make-Zugriff (Stand 2026-08-21 · Live-Scan aller 17 Szenarien)

Diese Sektion ist die Langfassung. Kurzfassung steht **in der Base** als Tabellenbeschreibung:

> 🟣 make.com — Zugriffskarte (Stand 2026-08-21, Live-Scan aller 17 Szenarien).
> Make schreibt 8 Felder und liest 13.
> Eines davon matcht Make über den Klartext-Namen — es trägt 🟣 make.com (KEY · …) in der Feldbeschreibung und darf nicht umbenannt werden. Alle übrigen Zugriffe laufen über die Feld-ID und sind umbenennungssicher.
> Vor dem Löschen oder Umtypisieren eines Feldes: POS-Skill → references/airtable/umsaetze.md.

### Namens-gekoppelt — trägt den 🟣-Marker am Feld

- **`ID`** — 🟣 `make.com (KEY · Name)` · singleLineText · `flda4tTUPnyeuQbDP`  
  Rechnungsnummer = Dedup. Szenarien: 6633991, 6955541, 6844567.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make schreibt:** `Bezahlt` · `Fällig am` · `Hinweis` · `Konditionen` · `Status` · `Store` · `Vertriebler`  
**Make liest:** `Belege` · `Datum` · `Deckungsbeitrag` · `Nettoumsatz` · `Provision` · `Umsatzpositionen` · `Zahlungsverlauf`

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**

*Ohne jeden Make-Zugriff: 7 von 22 Feldern.*
