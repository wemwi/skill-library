# Städte

`tbleuI57pG71mP6xg` · Kategorie **Stammdaten**

> Feld-Block: **Stand 2026-08-15**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Die Stadt — **Träger des öffentlichen City-Telegram-Channels.** Die City-Auflösung läuft `Store.Stadt → Städte.Telegram ID`.

## Beziehungen

- **→ `Stadtteile`** (→ [[stadtteile]]) · **→ `Stores`** (→ [[stores]]).

## Tragende Felder

- **`Telegram ID`** (Text) — **die Chat-ID des öffentlichen City-Channels.** Muss gesetzt sein, **bevor** ein Restock-/Store-Post dorthin gehen kann (neue Stadt = manueller, fail-closed Schritt, siehe [[notify]]).
- `Name` (Text).

## Fallstricke

- **Kein `Telegram ID` ⇒ kein City-Post** (fail-closed). Eine neue Stadt wird nicht automatisch angelegt.

## Feld-Block (Stand 2026-08-15 · `list_tables_for_base`)

| Feld | Typ | fld-ID |
|---|---|---|
| Name | singleLineText | `fldD5NSzJjupX7waM` |
| Stadtteile | link → Stadtteile | `fldMW44bgSYNm95uR` |
| Telegram ID | singleLineText (City-Channel) | `fldl5GAsDGTHl8iHL` |
| Stores | link → Stores | `fldeTZ5tmD9bSc1hb` |

*Neu ziehen: `list_tables_for_base` → Städte.*

## 🟣 Make-Zugriff (Stand 2026-08-21 · Live-Scan aller 17 Szenarien)

Make **liest** hier 2 Felder und schreibt nie in diese Tabelle. Eines davon matcht Make über den Klartext-Namen — es trägt den 🟣-Marker in der Feldbeschreibung der Base und darf nicht umbenannt werden.

### Namens-gekoppelt — trägt den 🟣-Marker am Feld

- **`Name`** — 🟣 `make.com (KEY · Name)` · singleLineText · `fldD5NSzJjupX7waM`  
  formulaCity aus M10. Szenarien: 6820980.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make liest:** `Telegram ID`

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**

*Ohne jeden Make-Zugriff: 2 von 4 Feldern.*
