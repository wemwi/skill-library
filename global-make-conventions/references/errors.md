# B8 — Fehlerbehandlung & Sichtbarkeit

## Kein stilles Schlucken

Ein grüner Szenario-Lauf muss bedeuten, dass die beabsichtigte Arbeit
tatsächlich passiert ist. Ein globaler Ignore- oder Resume-Handler ohne
Logging verletzt genau das: der Lauf zeigt Erfolg, während die eigentliche
Wirkung ausgeblieben ist.

**Dokumentierter Fall:** ein Modul mit `handleErrors: true` verlor
produktiv PDF-Anhänge still, weil die Ziel-Feld-ID zwischenzeitlich ungültig
geworden war — der Fehler wurde geschluckt, der Lauf lief grün durch, der
Datenverlust blieb tagelang unbemerkt.

## Die richtige Direktive pro Modul

Make bietet fünf Direktiven — Break, Commit, Ignore, Resume, Rollback — mit
unterschiedlicher Semantik:

| Direktive | Wirkung |
|---|---|
| Break | stoppt den Lauf, Bundle landet in Incomplete Executions zur späteren Reparatur |
| Commit | behält bereits erfolgte Änderungen, stoppt den Rest |
| Rollback | macht bereits erfolgte Änderungen rückgängig, stoppt den Rest |
| Ignore | Modul-Fehler wird übergangen, Lauf läuft weiter — nur für wirklich folgenlose Fehler |
| Resume | Lauf läuft mit einem fest definierten Fallback-Wert weiter |

Die Wahl hängt an der Kritikalität des Moduls: ein Pflicht-Write (legt den
Datensatz an, von dem alles Weitere abhängt) verträgt kein pauschales
Ignore. Ein optionaler Anreicherungs-Call (z.B. ein Enrichment-Service, der
ausfallen darf, ohne den Kern-Datensatz zu gefährden) verträgt es.

## Retry mit Cap und Backoff

Ein Retry ohne Obergrenze gegen eine dauerhaft fehlerhafte API verbrennt
unbegrenzt Operationen und blockiert den Worker. Jeder Retry-Mechanismus
braucht eine feste Obergrenze und exponentiellen Backoff, nicht nur eine
kurze feste Wartezeit.

## DLQ heilt nicht von selbst

Ein Eintrag in Incomplete Executions bleibt liegen, bis er aktiv per
DLQ-Replay abgearbeitet wird — er verschwindet nicht durch bloßes Warten
oder dadurch, dass der auslösende Datensatz das System auf anderem Weg
verlässt (z.B. eine View, die den Datensatz nach erfolgreicher Verarbeitung
nicht mehr zeigt). Der Eintrag und der Grund seines Entstehens sind zwei
unabhängige Zustände.
