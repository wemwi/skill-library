# Bestandsprüfungen

`tblmuGjaRDYXQzHch` · Kategorie **Ereignis** (INSERT-only)

> Feld-Block: **Stand 2026-08-15**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Eine Zeile = eine **Bestandsprüfung** (Soll/Ist-Abgleich) in einem Store, belegt durch das Prüfprotokoll. Kein Geldwert zum Vertriebler — sie misst **Schwund**.

## Beziehungen

- **→ `Store`** / **→ `Vertriebler`** (Einzel) — wo geprüft, wer geprüft.
- **→ `Beleg`** (Einzel) — Prüfprotokoll; `Datum` gespiegelt = Prüfdatum.
- **→ `Bestandsprüfungspositionen`** (Kinder) — SOLL/IST je Sorte; Differenzen rollen hoch → [[bestandspruefungspositionen]].
- Rückwege: `Vertriebler.Bestandsprüfungen` · `Stores.Bestandsprüfungen` · `Belege.Bestandsprüfung`.

## Tragende Felder

- **`ID`** (Formel) — **Dedup-Schlüssel:** `"BSP-" & Store ID & "-" & DATETIME_FORMAT(Datum,'YYYY-MM-DD')`. Make baut denselben Wert als `dedupkey` und sucht per `filterByFormula`. **Präfix/Format nicht anfassen.**
- **`Differenz (Gesamt)`** (Rollup) — Σ `Bestandsprüfungspositionen.Differenz` (SOLL − IST).
- **`Nettoverkaufswert`** (Rollup, €) — Σ der **positiv** bewerteten Differenzen = **Schwundwert** (VK-Sicht).
- **`Status`** (Select) — Abgeschlossen / In Bearbeitung / Teilgebucht / Ungültig (Make-String). Eine neue Zeile ohne Status steht von selbst auf In Bearbeitung (Vorgabewert des Felds, beobachtet 11.11.2026). Die Rechnung ordnet nur Abgeschlossen und Teilgebucht zu.
- **`Unterschrieben`** / **`Inventar geprüft`** (Checkbox) — speisen die Warnzeilen der Meldung.
- **`Poster im Schaufenster`** (Checkbox) — Zeile „Poster“ im freien Bestandsprotokoll (Zahl oder Haken = ja). Nur der grid-Zweig setzt es; kein Artikel, keine Position.
- **`Bestandsprüfungskorrekturen`** (Link, Rückfeld) — offene Zählzeilen dieser Prüfung als Datensätze → [[bestandspruefungskorrekturen]]. Ersetzt seit 06.11.2026 das Textfeld `Nachtrag` (nach der Übernahme gelöscht).
- **`Offene Korrekturen`** (Anzahl mit Filter Status Offen oder Abgelehnt) · **`Unklar`** (Formel: „4 Zeilen unklar“ / „1 Zeile unklar“ / leer) — speist die Zeile „⚠️ {Unklar}“ in `inventory.checked` und `inventory.corrected`.
- **`Korrekturen buchen`** (Checkbox, bis 06.11.2026 `Nachtrag buchen`, gleiches Feld) — Joscha setzt sie, `[Process] Manual Action (Inventory Correction)` bucht und nimmt sie zurück. Erneut setzen = erneut versuchen (gebuchte Sorten werden abgelehnt, Gebucht/Verworfen nicht angefasst).
- `Datum` (Lookup ← Beleg, EU) · `Store ID` (Lookup ← Stores.ID) · `Positionen` (Count) · `Hinweis`.

## Fallstricke

- **Dedup über `ID`** (Store-Nr + Prüfdatum): zwei Prüfungen desselben Stores am selben Tag kollidieren bewusst.
- **`[Maintain] Inventory Check Reminder` (→ `inventory.due`) nutzt denselben Präfix als Sortier-Schlüssel:** jüngste Prüfung je Store per `FIND("BSP-{JTL}-", {ID}) = 1` + Sort `ID` **desc**, max 1 — weil das Datum im `ID` steckt, ist `ID` desc = Datum desc innerhalb des Stores (kein separates Datumsfeld nötig).
- Nur **positive** Differenzen fließen in den `Nettoverkaufswert` (Schwund); Mehrbestand wird nicht als negativer Wert gezählt (siehe [[bestandspruefungspositionen]]).
- **Teilgebucht / Ungültig mit `Offene Korrekturen` > 0** heißt: offene Zählzeilen warten auf die Korrektur (keine Vertriebler-Aufgabe, neu hochladen hilft nicht). Ungültig entsteht auch, wenn der SOLL-Abgleich alle Kratom-Zeilen anhält und nur Display/Vitrine gebucht sind.
- Die View **„Korrektur (make.com)“** (Filter `Korrekturen buchen` ist an) ist Trigger-Scope eines Webhooks — nicht umfiltern oder umbenennen ([[operations]]).

## Feld-Block (Stand 2026-08-15 · `list_tables_for_base`)

| Feld | Typ | fld-ID |
|---|---|---|
| ID | formula | `fld24GCd9UoMFtIW6` |
| Status | singleSelect | `fldVx19XWUNiag4yJ` |
| Hinweis | multilineText | `fldPFWhLjjKt17Ra5` |
| Unterschrieben | checkbox | `fldX8yl4NxZeu2FUb` |
| Inventar geprüft | checkbox | `fldIkRcJo0tbi3St3` |
| Store | link → Stores | `fld31rwYy0IctcTWf` |
| Vertriebler | link → Vertriebler | `fldBiml9y1hrdyB5a` |
| Bestandsprüfungspositionen | link → …positionen | `fldP609B3H3G320Eo` |
| Beleg | link → Belege | `fldT3CnM4sh6xkgXK` |
| Datum | lookup (← Beleg.Datum) | `fldtcCjenPbEVtoUX` |
| Store ID | lookup (← Stores.ID) | `fldCcuJCgQZTgEmBC` |
| Differenz (Gesamt) | rollup | `fldu5g1stOUVfgf91` |
| Positionen | count | `fldkeRTSxff0AdVIj` |
| Nettoverkaufswert | rollup € | `fldIQQ71uz7zfOWN1` |
| Poster im Schaufenster | checkbox (Nachtrag 2026-11-02) | `fldSusvZeXfKG9E3C` |
| Korrekturen buchen | checkbox (Nachtrag 2026-11-06, bis dahin „Nachtrag buchen“) | `fldztnClGsTLhYU7t` |
| Bestandsprüfungskorrekturen | link → Bestandsprüfungskorrekturen (Nachtrag 2026-11-06) | `fldVAmUqGJ6LAP0T5` |
| Offene Korrekturen | count, Filter Status Offen/Abgelehnt (Nachtrag 2026-11-06) | `fldz9mqyh2MZAaru9` |
| Unklar | formula (Nachtrag 2026-11-06) | `fldkjFKD1tV19yrUH` |

*Neu ziehen: `list_tables_for_base` → Bestandsprüfungen; Formeln via `get_table_schema`.*

## 🟣 Make-Zugriff (Stand 2026-08-21 · Live-Scan aller 17 Szenarien)

Make schreibt **9** Felder und liest **11** (Nachtrag 2026-11-02: `Poster im Schaufenster`; Stand 06.11.2026: schreibt `Korrekturen buchen` und liest `Hinweis`, `Bestandsprüfungspositionen`, `Bestandsprüfungskorrekturen` in `[Process] Manual Action (Inventory Correction)` 8413130; der Notify-Hub liest `Unklar`; `Nachtrag` entfällt). 2 davon matcht Make über den Klartext-Namen — sie tragen den 🟣-Marker in der Feldbeschreibung der Base und dürfen nicht umbenannt werden.

### Namens-gekoppelt — trägt den 🟣-Marker am Feld

- **`ID`** — 🟣 `make.com (KEY · Name)` · formula · `fld24GCd9UoMFtIW6`  
  BSP-Dedup-Schlüssel + sort. Szenarien: 6633991, 6729541, 7001118.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).
- **`Status`** — 🟣 `make.com (KEY · Options)` · singleSelect · `fldVx19XWUNiag4yJ`  
  {Status} != "Ungültig". Szenarien: 6633991; 8413130 vergleicht und schreibt die Optionsnamen (Teilgebucht · Abgeschlossen · Ungültig · In Bearbeitung) im Code „Parse corrections“ / „Close corrections“; 8495399 vergleicht „In Bearbeitung“ im Code „Pick leftovers“ und löscht nur solche Zeilen (seit 10.11.2026); 6633991 vergleicht „Abgeschlossen“ und „Teilgebucht“ im Code „Assign inventory check“ (seit 11.11.2026); 8511487 vergleicht dieselben im Code „Pick invoices to retry“ und stößt nur dann Rechnungen neu an (seit 11.11.2026).  
  ⚠ Feldname **und** Optionsnamen sind eingefroren — beides bricht den Match still.

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make schreibt:** `Beleg` · `Hinweis` · `Inventar geprüft` · `Korrekturen buchen` (8413130 und 8475632 im Fehlerweg, nur zurücksetzen) · `Poster im Schaufenster` (6729541, Modul „Write poster“) · `Store` · `Unterschrieben` · `Vertriebler`  
**Make liest:** `Bestandsprüfungskorrekturen` · `Bestandsprüfungspositionen` · `Datum` · `Differenz (Gesamt)` · `Hinweis` · `Nettoverkaufswert` · `Positionen` · `Store ID` · `Unklar` (Notify-Hub 6862968)

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**

*Ohne jeden Make-Zugriff: 1 von 17 Feldern.*
