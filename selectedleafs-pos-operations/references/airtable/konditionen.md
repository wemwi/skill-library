# Konditionen

`tblFDfn7qyO8criBa` · Kategorie **Version** (append-only, eff-dated)

> Feld-Block: **Stand 2026-08-15**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Versionierte **Provision** und **Kostenanteil** (in %), **nach Steuerstatus getrennt**. Eine Zeile = eine ab `Gültig ab` geltende Kondition für Kleinunternehmer *oder* Regelbesteuerung.

## Beziehungen

- **→ `Steuersatz`** (Einzel, → [[steuersaetze]]) — liefert die `MwSt.` dieser Kondition.
- **→ `Umsätze`** / **→ `Lieferungen`** — die Ereignisse, die diese Version gewählt haben.

## Tragende Felder

- **`Gültig ab`** (Datum, EU) — **Versionswahl:** die jüngste Version mit `Gültig ab ≤ Leistungsdatum` gewinnt.
- **`Gültig für`** (Select: **Kleinunternehmer** / **Regelbesteuerung**) — **Scope:** die Auswahl wird zusätzlich über den Steuerstatus des Vertrieblers (`Vertriebler.Besteuerung`) gefiltert. Ein Vertriebler zieht nur die Version seines Status.
- **`Provision`** (%) / **`Kostenanteil`** (%) — die versionierten Sätze; speisen `Umsätze.Provision` bzw. `Lieferungen.Kostenanteil`.
- **`MwSt.`** (Lookup ← Steuersatz) — 0 % bei Kleinunternehmer.

## Fallstricke

- **Nie eine bestehende Version editieren** (Freeze-Invariante) — verschiebt Geld rückwirkend. Immer neu mit neuem `Gültig ab`.
- Die Auswahl braucht **beide** Achsen: `Gültig ab ≤ Leistungsdatum` **und** `Gültig für = Besteuerung`. Fehlt die passende Kombination, greift die Konditionen-Wahl ins Leere (→ 👉 task.terms_missing).

## Feld-Block (Stand 2026-08-15 · `list_tables_for_base`)

| Feld | Typ | fld-ID |
|---|---|---|
| ID | singleLineText | `fldSuQBQxDERrPx38` |
| Gültig ab | date | `fldLCQhky7QB1uZ20` |
| Gültig für | singleSelect | `fldJmJuFo4eDbNvP3` |
| Steuersatz | link → Steuersätze | `fldlyBJ6B3RsrXaoV` |
| Provision | percent | `fldKLBP5uLb0iYrUI` |
| Kostenanteil | percent | `fldQ6t2tYWT2jCZZs` |
| MwSt. | lookup % (← Steuersätze) | `flddkHRd0uT4PLRAX` |
| Umsätze | link → Umsätze | `fldxStBzEHMBXhgpD` |
| Lieferungen | link → Lieferungen | `fldaG7zFSh44if4T6` |

*Neu ziehen: `list_tables_for_base` → Konditionen; Formeln via `get_table_schema`.*

## 🟣 Make-Zugriff (Stand 2026-08-21 · Live-Scan aller 17 Szenarien)

Diese Sektion ist die Langfassung. Kurzfassung steht **in der Base** als Tabellenbeschreibung:

> 🟣 make.com — Zugriffskarte (Stand 2026-08-21, Live-Scan aller 17 Szenarien).
> Make LIEST hier 5 Felder und schreibt nie in diese Tabelle.
> 2 davon matcht Make über den Klartext-Namen — sie tragen 🟣 make.com (KEY · …) in der Feldbeschreibung und dürfen nicht umbenannt werden. Alle übrigen Zugriffe laufen über die Feld-ID und sind umbenennungssicher.
> Vor dem Löschen oder Umtypisieren eines Feldes: POS-Skill → references/airtable/konditionen.md.

### Namens-gekoppelt — trägt den 🟣-Marker am Feld

- **`Gültig ab`** — 🟣 `make.com (KEY · Name)` · date · `fldLCQhky7QB1uZ20`  
  eff-dated Konditionswahl. Szenarien: 6633991, 6821121.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).
- **`Gültig für`** — 🟣 `make.com (KEY · Options)` · singleSelect · `fldJmJuFo4eDbNvP3`  
  Besteuerung als String. Szenarien: 6633991, 6821121.  
  ⚠ Feldname **und** Optionsnamen sind eingefroren — beides bricht den Match still.

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make liest:** `ID` · `Kostenanteil` · `Provision`

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**

*Ohne jeden Make-Zugriff: 4 von 9 Feldern.*
