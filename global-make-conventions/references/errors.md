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

## Mit Warten gerufen: keine unvollständige Ausführung

Ein Szenario, das über `Call a scenario` mit „Wait for the scenario to
finish" gerufen wird, legt keine unvollständige Ausführung an. Make
unterbindet sie für diesen Lauf (im Lauf sichtbar als
`forceDLQCreationOff: true`), auch wenn „Store incomplete executions" am
gerufenen Szenario an ist.

Was daraus folgt:

- **Der Fehler geht an den Aufrufer zurück.** Der Lauf des gerufenen Szenarios
  endet mit Status Fehler, im gerufenen Szenario bleibt nichts zum Fortsetzen.
- **Make wiederholt dort nichts von selbst.** Das automatische Wiederholen bei
  Zeitüberschreitung, 429 und Verbindungsfehler hängt an der unvollständigen
  Ausführung. Jeder vorübergehende Fehler im gerufenen Szenario ist ein Abbruch.
- **Ein Break kann dort nicht parken.** Er endet mit „Creation of incomplete
  execution is not allowed". `Retry + park` und `Park run` gehören an Aufrufe
  ohne Warten und in das auslösende Szenario.
- **Der Fehlerweg liegt am Call-Modul des Aufrufers.** Dort wird der Fehler
  sichtbar gemacht (Hinweis am Datensatz, Meldung) und entschieden, wie es
  weitergeht.
- **Eine Kette mit Warten braucht einen wiederholbaren Neuanstoß.** Weil
  nichts fortgesetzt wird, läuft der Neulauf von vorn. Was ein Abbruch mitten
  im Schreiben stehen lässt, muss der Neulauf erkennen oder vorher entfernen.
- **Bei einem Direktstart gilt das nicht** (Run once, API, Replay): Dann hat
  das Szenario keinen Aufrufer und legt wie jedes andere eine unvollständige
  Ausführung an.

Die Gegenrichtung: Ohne Warten kann das gerufene Szenario parken und Make
wiederholt selbst, der Aufrufer sieht den Fehler aber nicht mehr und wartet
nicht auf das Ergebnis. Aufrufe laufen dann nebeneinander (A2, sync oder
async).

**Beleg (10.11.2026):** Ein sequenzieller Worker, mit Warten gerufen,
scheiterte an einer Zeitüberschreitung. Sein Lauf zeigte Status Fehler und
keine unvollständige Ausführung, der nächste Aufruf zehn Minuten später lief
normal. Eine Annahme aus dem Blueprint („der Worker behält eine
unvollständige Ausführung") hatte ein Audit vorher als Fakt geführt. Solche
Aussagen gehören an einem Lauf geprüft, nicht am Blueprint abgelesen.

## DLQ heilt nicht von selbst

Ein Eintrag in Incomplete Executions bleibt liegen, bis er aktiv per
DLQ-Replay abgearbeitet wird — er verschwindet nicht durch bloßes Warten
oder dadurch, dass der auslösende Datensatz das System auf anderem Weg
verlässt (z.B. eine View, die den Datensatz nach erfolgreicher Verarbeitung
nicht mehr zeigt). Der Eintrag und der Grund seines Entstehens sind zwei
unabhängige Zustände.
