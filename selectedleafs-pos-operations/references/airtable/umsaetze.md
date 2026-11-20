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
- **`Offen`** (Formel, €) — bei `Status` Bezahlt 0, sonst `Nettoumsatz − Bezahlt` (seit 19.11.2026, sonst bliebe ein Skonto als Rest offen). `Bezahlt` ist seit 09.11.2026 eine Formel: `IF({Bruttobetrag}>0, IF({Gezahlt brutto}>={Bruttobetrag}, {Nettoumsatz}, ROUND({Nettoumsatz}*{Gezahlt brutto}/{Bruttobetrag},2)), 0)`. Die Rohwerte schreibt Make: `Bruttobetrag` der Rechnungs-Worker, `Gezahlt brutto` nur `[Process] Lexware Payment (Invoice · Store)`.
- **`Realprovision`** (Formel, €) — `(Bezahlt × Provisionssatz) × (1 + MwSt.)` — Provision auf den **tatsächlich gezahlten** Betrag (bei Teilzahlung oder Skonto < Provision). Rollt zu `Vertriebler.Realprovision`. Die Meldung `invoice.paid` zeigt sie dem Vertriebler (seit 20.11.2026).
- **Skonto (seit 19.11.2026):** 5 % bei Zahlung innerhalb von 7 Tagen, Zahlungsbedingung in JTL. Lexware führt den Abzug als Zahlungsposten `cashDiscount`; `[Process] Lexware Payment (Invoice · Store)` zählt ihn nicht als Zahlung. Bei Skonto bleibt `Gezahlt brutto` unter `Bruttobetrag`, `Bezahlt` und `Realprovision` sinken anteilig, `Offen` ist 0. Mahngebühren (`dunningCosts`) zählen weiter als Zahlung. Abgenommen an RG-10149-1: Gezahlt brutto 517,78 von 545,03, Bezahlt 435,11, Realprovision 217,56 statt 229,01. Die Partnerstufe zählt `Bezahlt` ([[jahresboni]]).
- **`Deckungsbeitrag`** (Formel, €) — `Nettoumsatz − Provision`.
- **`Zahlungsverlauf`** (Rollup ← `Belege.Belegtyp`) — »pünktlich« / »nach Zahlungserinnerung« / »nach Mahnung«; speist `{Zahlungsverlauf}` in der invoice.paid-Meldung.
- **`Status`** (Select) — Offen / Bezahlt / **Teilgezahlt** / Überfällig / Angemahnt / Storniert / Ausgebucht. Teilzahlung ist ein definierter Zustand (Lexware-Payments-Sync).
- **`Lexware ID`** (Text, seit 2026-11-06) — Voucher-ID der Rechnung in Lexware = `resource_id` für den Neuanstoß von `[Process] Lexware Voucher (Invoice · Store)`. Nachgepflegt am 06.11.2026 für alle 41 Umsätze (Abgleich über die Rechnungsnummer).
- **Nur Rechnungen** (seit 09.11.2026): Gutschriften (`RK-…`) stehen in [[gutschriften]]. Ausgewählt wird über die Nummer, nie über das Vorzeichen: RG-10146-1 trägt eine negative Zeile und gehört hierher.
- **`Provisionssatz`** / **`MwSt.`** (Lookup %, ← Konditionen) · **`Fällig am`** (Datum) · `Datum` (Lookup ← Beleg, EU; nur Belegtyp Ausgangsrechnung, Mahnstufen zählen nicht) · `Nettoumsatzerlös` (Rollup) · `Hinweis`.

## Fallstricke

- **`Nettoumsatz` ist die Geldwahrheit, nicht `Nettoumsatzerlös`** (Endkunden-VK, liegt höher = Storemarge). Nur `Nettoumsatz` speist Provision/Saldo.
- **Status wird von Make als String geschrieben** — Optionen nicht umbenennen (still).
- **Storno gibt Belege frei (seit 19.11.2026):** Beim Wechsel auf Storniert schreibt `[Process] Lexware Voucher (Invoice · Store)` `Belege` neu, ohne Bestandsprotokoll, Rückholprotokoll und Lieferschein; Rechnungs- und Mahnbelege bleiben (`Zahlungsverlauf`). Die alte Zuordnung steht weiter im `Hinweis`. `Belege` nie von Hand ändern.
- **Bezahlt / Storniert / Ausgebucht setzt nur `[Process] Lexware Voucher (Invoice · Store)`** (`[Process] Lexware Payment (Invoice · Store)` schreibt nur Teilgezahlt/Offen). Darauf beruht das Gate der Abschlussmeldung (vorher ≠ nachher). Ein zweiter Schreiber dieser Werte würde die Meldung verschlucken.
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
| Bezahlt | formula | `fldzRKStpN9Ol5waf` |
| Gezahlt brutto | currency | `fldtFkDczxFZGRalc` |
| Bruttobetrag | currency | `fldRfprL0RWaSinb9` |
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
| Lexware ID | singleLineText (Voucher-ID, Nachtrag 2026-11-06) | `fldmTPQs0S1RTilAi` |

*Neu ziehen: `list_tables_for_base` → Umsätze; Formeln via `get_table_schema`.*

## 🟣 Make-Zugriff (Stand 2026-08-21 · Live-Scan aller 17 Szenarien)

Make schreibt **9** Felder und liest **14** (seit 2026-11-06 mit `Lexware ID`). Zwei davon matcht Make über den Klartext (Nachtrag 2026-11-11: `Status`) — sie tragen den 🟣-Marker in der Feldbeschreibung der Base und dürfen nicht umbenannt werden.

### Namens-gekoppelt — trägt den 🟣-Marker am Feld

- **`ID`** — 🟣 `make.com (KEY · Name)` · singleLineText · `flda4tTUPnyeuQbDP`  
  Rechnungsnummer = Dedup. Szenarien: `[Process] Lexware Voucher (Invoice · Store)`, `[Process] Lexware Payment (Invoice · Store)` („Find invoice row (by ID)“), `[Process] Invoice (Store) · REMINDER` (Altlast, abgeschaltet).  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).
- **`Status`** — 🟣 `make.com (KEY · Options)` · singleSelect · `fldBavq4sjk2A1swZ` (gesetzt 2026-11-11)  
  `[Process] Lexware Payment (Invoice · Store)` vergleicht Offen, Überfällig, Angemahnt und Teilgezahlt im Code „Decide (store)“, `[Process] Lexware Voucher (Invoice · Store)` Teilgezahlt, Angemahnt und Überfällig in „Update status“ und den Filter „Not terminal“, „Load store sales“ in `[Process] Manual Action (Inventory Correction)` und `[Resolve] Open Invoices` Storniert und Ausgebucht, „Plan tiers“ in `[Maintain] Partner Tier Check` Storniert und Ausgebucht (seit 19.11.2026), „Build text“ in `[Notify] Telegram Channels` Bezahlt (`{Skonto}`, seit 20.11.2026). Geschrieben wird der Status über die Options-ID.  
  ⚠ Option umbenennen: Diese Vergleiche greifen nicht mehr (still).

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make schreibt:** `Bruttobetrag` · `Gezahlt brutto` · `Fällig am` · `Hinweis` · `Konditionen` · `Lexware ID` (6633991 „Umsatz anlegen“; „Status updaten“ füllt sie, wenn leer; gelesen von 8413130 „Load store sales“ zusammen mit `ID`, `Status`, `Hinweis`, ebenso von 8511487 „Load store sales“, dazu `Datum`; beide vergleichen im Code die Optionsnamen Storniert und Ausgebucht und die Marke am Anfang einer Hinweiszeile) · `Status` · `Store` · `Vertriebler`  
**Make liest:** `Belege` · `Datum` · `Deckungsbeitrag` · `Nettoumsatz` · `Provision` · `Umsatzpositionen` · `Zahlungsverlauf` · `Bezahlt` (8651392 „Find invoices“ mit `Datum`, `Store`, `ID`, `Status`, seit 19.11.2026) · `Realprovision`, `Bruttobetrag`, `Gezahlt brutto`, `Status` (6862968 „Map event“, Meldung `invoice.paid`, über die Feld-ID, seit 20.11.2026)

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**

*Ohne jeden Make-Zugriff: 7 von 22 Feldern.*
