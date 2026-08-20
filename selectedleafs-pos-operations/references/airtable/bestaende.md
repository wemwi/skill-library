# Bestände

`tblFboBzXrCop4nYt` · Kategorie **Silo** (abgeleitet, make-getrieben)

> Feld-Block: **Stand 2026-08-15**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

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

## Feld-Block (Stand 2026-08-15 · `list_tables_for_base`)

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
| Store | lookup | `fldPuoageKdiyfZvd` |
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

## 🟣 Make-Zugriff (Marker in der Base-Feldbeschreibung)

Trägt einen 🟣-Zugriffsmarker in der Base-Feldbeschreibung (SSoT: [[model]] §2).

- **`Store`** — 🟣 WRITE. Make setzt die Verknüpfung beim Upsert (die Formel-ID liest daraus die Store-Nummer).
- **`Letzte Lieferung`** — 🟣 READ. Rollup; der Owner-Sync vergleicht dieses Datum mit dem Belegdatum. ⚠ Rollup-Konfig (Link-Feld, Zielfeld, Aggregation MAX) nicht ändern — sonst fallen City-Posts still aus.
- **`Erstlieferung am`** — 🟣 READ+WRITE. Post-Datum je Sorte/Store; einmal gesetzt, nie zurückgesetzt — Löschen löst einen erneuten Neuheits-Post aus.

- **`ID`** — 🟣 READ. Bestands-Schlüssel "BST-" & Store-Nr & "-" & SKU (Upsert-Match). Präfix/Trennzeichen nicht ändern.
