# Stadtteile

`tblVSeQnhhVHLML3l` · Kategorie **Stammdaten**

> Feld-Block: **Stand 2026-08-15**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Der Stadtteil — feinere Geo-Ebene unter der Stadt, für City-Posts (`{Stadtteil}`) und Store-Karten.

## Beziehungen

- **→ `Stadt`** (→ [[staedte]]) · **→ `Stores`** (→ [[stores]]).

## Tragende Felder

- `Name` (Text) — erscheint als `{Stadtteil}` in City-Meldungen.

## Fallstricke

- Die Store↔Stadtteil↔Stadt-Zuordnung ist **redaktionell** gesetzt, nicht aus der Adresse abgeleitet — ein Store in einer Nachbargemeinde kann bewusst einer größeren Stadt zugeordnet sein.

## Feld-Block (Stand 2026-08-15 · `list_tables_for_base`)

| Feld | Typ | fld-ID |
|---|---|---|
| Name | singleLineText | `fldNJ60R7UN2vNtJ5` |
| Stores | link → Stores | `flddlbfbXbZlKKWr8` |
| Stadt | link → Städte | `fld3aeuw7c8wxXnMg` |

*Neu ziehen: `list_tables_for_base` → Stadtteile.*

## 🟣 Make-Zugriff (Stand 2026-08-21 · Live-Scan aller 17 Szenarien)

Diese Sektion ist die Langfassung. Kurzfassung steht **in der Base** als Tabellenbeschreibung:

> 🟣 make.com — Zugriffskarte (Stand 2026-08-21, Live-Scan aller 17 Szenarien).
> Make schreibt 2 Felder und liest 2.
> Eines davon matcht Make über den Klartext-Namen — es trägt 🟣 make.com (KEY · …) in der Feldbeschreibung und darf nicht umbenannt werden. Alle übrigen Zugriffe laufen über die Feld-ID und sind umbenennungssicher.
> Vor dem Löschen oder Umtypisieren eines Feldes: POS-Skill → references/airtable/stadtteile.md.

### Namens-gekoppelt — trägt den 🟣-Marker am Feld

- **`Name`** — 🟣 `make.com (KEY · Name)` · singleLineText · `fldNJ60R7UN2vNtJ5`  
  formulaDistricts + find-or-create. Szenarien: 6820980.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make schreibt:** `Stadt`  

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**

*Ohne jeden Make-Zugriff: 1 von 3 Feldern.*
