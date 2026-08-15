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
