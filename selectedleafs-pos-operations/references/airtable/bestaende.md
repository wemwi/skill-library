# Bestände

`tblFboBzXrCop4nYt` · Kategorie **Silo** (abgeleitet, make-getrieben)

> Feld-Block: **Stand 2026-08-21**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Ein **abgeleiteter Silo** je **Store × Produktvariante**: rekonstruiert den laufenden Bestand aus Lieferungen, Verkäufen und der letzten Prüfung — und trägt die Trigger für die City-Posts.

## Beziehungen

- **→ `Store`** (→ [[stores]]) / **→ `Produkt`** (→ [[produktvarianten]]) — die beiden Achsen des Silos.
- **→ `Lieferpositionen` / `Umsatzpositionen` / `Bestandsprüfungspositionen`** — die Bewegungen, die hier zusammenlaufen.

## Tragende Felder

- **`ID`** (Formel) — `"BST-" & Store & "-" & Produkt` = `BST-<JTL-Nr>-<SKU>`. Der Bestands-Schlüssel; Positionen upserten dagegen.
- **`IST`** (Formel) — laufender Bestand: `Prüfstand` **+** `Geliefert seit Prüfung`.
- **`SOLL`** (Formel) — `Geliefert − Verkauft`.
- **`Differenz`** (Formel) — `MAX(SOLL − IST, 0)`.
- **`Letzte Lieferung`** (Rollup **MAX** ← `Lieferpositionen.Geliefert am`) — **der Owner-Sync postet nur die Sorten, deren letzte Lieferung exakt aufs Belegdatum fällt.** Rollup-Konfiguration (Link, Zielfeld, MAX) **nicht ändern** — sonst fallen City-Posts still aus.
- **`Erstlieferung am`** (Datum) — Datum des 🌿-Neuheits-Posts. **Einmal gesetzt, nie zurückgesetzt** (auch nicht bei Rückholung). Löschen ⇒ erneuter Neuheits-Post.
- **`Ø EK (netto)`** (Formel) — `Warenkosten / Geliefert` (Durchschnitts-EK).
- Rollups: `Geliefert` · `Verkauft` · `Prüfstand` · `Geliefert seit Prüfung` · `Warenkosten` · `Letzte Prüfung`.

## Fallstricke

- **`Letzte Lieferung` (MAX) steuert die City-Posts** — Rollup nicht anfassen.
- **`Erstlieferung am` nie zurücksetzen** — es ist der Dedup gegen doppelte 🌿-Posts.
- `IST`/`SOLL`/`Differenz` liefern bei fehlender Prüfung `"-"` (String) — nicht als Zahl weiterrechnen ohne Guard.

## Feld-Block (Stand 2026-08-21 · `list_tables_for_base`)

| Feld | Typ | fld-ID |
|---|---|---|
| ID | formula | `fld6KO67C2lmpjZ0V` |
| Produkt | link → Produktvarianten | `fldTJVVXGcFC4JMTg` |
| IST | formula | `fld0lKVZKGZRytGao` |
| SOLL | formula | `fld8OepBzfJSL0xyt` |
| Differenz | formula | `fldm1RQEokRy9E3z5` |
| Letzte Prüfung | rollup date | `fldZhiZtRPUuaQR6i` |
| Lieferpositionen | link → Lieferpositionen | `fldsvFGwel4mmJYvK` |
| Umsatzpositionen | link → Umsatzpositionen | `fldjydjHapLsTlnit` |
| Bestandsprüfungspositionen | link → …positionen | `fldDuRv23YyncvwGQ` |
| Store | link → Stores | `fldhvkGD2RkmYOMKz` |
| Geliefert | rollup | `fldmOWd6beQiTnZF5` |
| Verkauft | rollup | `fldXBX7L99gnBo9Tl` |
| Prüfstand | rollup (← Prüfstempel) | `fldfho1EkQTGY6kVG` |
| Geliefert seit Prüfung | rollup | `fldYgA2UNNdGkYHEb` |
| Warenkosten | rollup € | `flduhECzrxvABE7vH` |
| Ø EK (netto) | formula € | `fldyfjs6US0Xd8kON` |
| Letzte Lieferung | rollup date (MAX) | `fldkKyVPdEVdqRrXT` |
| Erstlieferung am | date | `flddmYNCwH7P0YKmu` |

*Neu ziehen: `list_tables_for_base` → Bestände; Formeln via `get_table_schema`.*

## 🟣 Make-Zugriff (Stand 2026-08-21 · Live-Scan aller 17 Szenarien)

Make schreibt **3** Felder und liest **9**. Eines davon matcht Make über den Klartext-Namen — es trägt den 🟣-Marker in der Feldbeschreibung der Base und darf nicht umbenannt werden.

### Namens-gekoppelt — trägt den 🟣-Marker am Feld

- **`ID`** — 🟣 `make.com (KEY · Name)` · formula · `fld6KO67C2lmpjZ0V`  
  Bestands-Schlüssel BST-<JTL>-<SKU>; Upsert-Match. Szenarien: 6633991, 6677862, 6729541, 6805674.  
  ⚠ Umbenennen bricht den Match still (kein Fehler, kein Log).

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make schreibt:** `Erstlieferung am` · `Produkt` · `Store`  
**Make liest:** `IST` · `Letzte Lieferung` · `Letzte Prüfung` · `SOLL` · `Verkauft` · `Ø EK (netto)`

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**

*Ohne jeden Make-Zugriff: 8 von 18 Feldern.*
