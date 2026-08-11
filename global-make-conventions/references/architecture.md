# Architektur — Grundprinzipien & Muster-Katalog

## A1 — Grundprinzipien vertieft

Die fünf Prinzipien in der SKILL.md sind keine Willkür — sie sind direkt aus
den Bruchmustern abgeleitet, die in produktiven Make-Portfolios am häufigsten
auftreten, sobald ein System über die erste Version hinauswächst:

- **Unklares System-of-Record.** Zwei Systeme schreiben und aktualisieren
  dieselbe Entität. Daten pingpongen zwischen ihnen, jede Seite hält sich für
  die Wahrheit, Divergenz wird erst bemerkt, wenn ein Bericht nicht mehr
  stimmt. → A1.1.
- **Fehlende kanonische Keys.** Ohne stabilen, eindeutigen Schlüssel wird über
  Datumsnähe, Textähnlichkeit oder Reihenfolge gematcht. Retries erzeugen
  Dubletten, Updates treffen den falschen Datensatz. → A1.2.
- **Trigger-Drift.** Jemand beschleunigt ein Polling-Intervall „nur ein
  bisschen", die Operations-Zahl explodiert, ein Rate-Limit greift, das
  Szenario wird stillgelegt — niemand hat das ursprünglich so geplant, es ist
  über Zeit gedriftet. → A1.4 (Kontrakt vor Bau hält die Trigger-Entscheidung
  explizit und überprüfbar, statt sie graduell zu verschieben).
- **Versteckte Router-Komplexität.** Ein Szenario wächst mit jedem neuen
  Anforderungsfall um eine weitere Route, bis niemand mehr die volle
  Verzweigungslogik überblickt und Filter auf nicht normalisierten Feldern
  fragil werden. → A1.3 (Single Responsibility: rechtzeitig splitten statt
  einen Router zum Universaldispatcher auswachsen lassen).
- **Stille Fehler.** Ein Error-Handler schluckt einen Fehler ohne Alarm, das
  Szenario zeigt grün, das Geschäftsproblem besteht Tage unbemerkt fort. →
  A1.5 (Observability by Design — Sichtbarkeit ist Teil des Entwurfs, nicht
  ein Nachrüst-Feature).

Ein sechster, aus einem dokumentierten Realfall (siehe `loops.md`)
gehärteter Zusatz: **Trigger-Wahl und Schleifenfreiheit sind Teil des
Kontrakts, nicht der Implementierung.** Welches Feld gelauscht wird und
welche Change-Types einen Lauf auslösen, gehört in die Spec-Phase (A1.4),
nicht erst ins fertige Szenario hineingebaut.

## A2 — Muster-Katalog

Jedes Muster mit Wann-Einsatz, Tradeoff und typischem Bruchmodus. Kein
Muster ist per se besser — die Aufgabe entscheidet.

### Linear (Trigger → Transform → Action)
**Wann:** Einzweck-Flow, eine Quelle, ein Ziel, keine Verzweigung nötig.
**Tradeoff:** einfachst zu bauen und zu debuggen, aber jede neue Anforderung
zwingt zum Umbau statt zur Erweiterung.
**Bruchmodus:** wächst organisch zu einem Router-Monster, wenn niemand
rechtzeitig auf ein anderes Muster wechselt.

### Router-Fan-out
**Wann:** ein Trigger, mehrere unabhängige Folgeaktionen, die parallel und
unabhängig voneinander laufen sollen (z.B. gleichzeitig ins Log schreiben
und eine Benachrichtigung senden).
**Tradeoff:** parallele Verarbeitung spart Wall-Clock-Zeit, erhöht aber die
gleichzeitige API-Last — mehrere Routen können individuell innerhalb eines
Rate-Limits liegen und in Summe trotzdem darüberschießen.
**Bruchmodus:** fragile Filter auf nicht normalisierten Feldern lassen
Bundles in die falsche oder in keine Route laufen; niemand bemerkt es, weil
jede Route für sich betrachtet unauffällig bleibt.

### Batch/Aggregate
**Wann:** viele kleine Events, die zusammen verarbeitet günstiger sind als
einzeln (API-Call-Kontingent sparen, Rate-Limits einhalten).
**Tradeoff:** senkt Operationskosten, erhöht aber Latenz — das einzelne
Event wird erst mit dem nächsten Batch-Fenster verarbeitet.
**Bruchmodus:** Aggregator-Module sind mapper-fragil (siehe B10) — eine
gemischte UI/Blueprint-Bearbeitung zerstört die Bindung leise.

### Dispatcher/Worker (asynchrone Entkopplung)
**Wann:** ein eingehendes Ereignis muss klassifiziert und an einen von
mehreren spezialisierten, unabhängig lebenden Workern übergeben werden —
jeder Worker hat einen eigenen Lebenszyklus, eigenes Fehler-/DLQ-Verhalten,
eigene Re-Trigger-Fähigkeit.
**Mechanik:** ein Dispatcher-Szenario trägt den einzigen Trigger auf die
Quelle, klassifiziert, und weckt den passenden Worker per HTTP-Call auf
dessen eigenen `gateway:CustomWebHook`.
**Tradeoff:** entkoppelt Klassifikation von Ausführung sauber — jeder Worker
lässt sich isoliert testen, re-triggern, deaktivieren, ohne den Dispatcher
anzufassen. Kostet dafür eine zusätzliche Netzwerk-Hop-Ebene und einen
eigenen Webhook pro Worker.
**Bruchmodus:** wird der Dispatcher zum heimlichen Business-Logik-Träger
statt reiner Klassifikator, verschiebt sich die Verantwortung unsauber
zurück in Richtung Router-Monster.

### Orchestrator + native Subscenarios (synchrone Wiederverwendung)
**Wann:** dieselbe Logik (Normalisierung, Validierung, ein Lookup-Baustein)
wird in mehreren Szenarien gebraucht und soll eine Single Source of Truth
haben — Änderung an einer Stelle, wirkt überall.
**Mechanik:** Subscenarios geben Daten synchron zurück in den Aufrufer,
ohne den HTTP+Webhook-Umweg, der vor ihrer Einführung nötig war.
**Tradeoff:** spart Duplikation und Wartungsaufwand massiv, ist aber
synchron — für Logik mit eigenem Lebenszyklus, eigenem Fehlerverhalten oder
eigener Re-Trigger-Notwendigkeit ist Dispatcher/Worker die bessere Wahl.
**Bruchmodus:** Subscenarios werden für Fälle genutzt, die eigentlich
asynchrone Entkopplung bräuchten — dann fehlt dem „Worker" ein eigener
Lebenszyklus, und Fehler im Subscenario blockieren den Aufrufer synchron.

### Data-Store-Queue (Producer/Consumer)
**Wann:** Erzeugung und Verarbeitung eines Events sollen zeitlich entkoppelt
sein, mit Replay-Fähigkeit und einem sichtbaren Idempotenz-Ledger.
**Tradeoff:** stärkste Entkopplung und Nachvollziehbarkeit, höchster
Bau-Aufwand — meist nur gerechtfertigt, wenn Replay oder Audit-Trail ein
echtes Anforderungsmerkmal ist, nicht nur „könnte später nützlich sein".
**Bruchmodus:** als Standardlösung für jedes Problem eingesetzt, wird sie zum
Over-Engineering — die Data-Store-Queue braucht eine echte
Entkopplungs-Anforderung, sonst ist ein einfacheres Muster richtig.

## Entscheidungsachse: synchron vs. asynchron

Die praktisch wichtigste Weichenstellung ist nicht „welches Muster klingt
moderner", sondern eine einzige Frage:

**Braucht die aufgerufene Logik einen eigenen Lebenszyklus** (eigener
Fehlerpfad, eigenes DLQ, unabhängig re-triggerbar, kann ohne den Aufrufer
laufen)?

- **Ja** → Dispatcher/Worker über eigenen Webhook. Der zusätzliche
  Netzwerk-Hop ist der Preis für echte Entkopplung.
- **Nein**, es ist reine Wiederverwendung von Logik mit synchronem
  Rückgabewert (Normalisierung, ein gemeinsamer Lookup-Baustein) → native
  Subscenarios. Die alte HTTP+Webhook-Verdrahtung für diesen Fall gilt als
  überholt: sie erzeugt Duplikations- und Wartungsaufwand, den Subscenarios
  gerade auflösen sollen.

Ein Dispatcher, der eingehende Dokumente klassifiziert und je nach Typ einen
von mehreren fachlich unabhängigen Verarbeitungspfaden weckt — jeder mit
eigenem Datenmodell, eigenem Fehlerverhalten, eigener Fähigkeit, isoliert neu
zu laufen — liegt klar auf der Ja-Seite: Dispatcher/Worker ist hier die
richtige Wahl, kein Anti-Pattern. Würde derselbe Dispatcher stattdessen nur
eine gemeinsame Validierungs- oder Formatierungsroutine mehrfach aufrufen,
die synchron ein Ergebnis zurückgibt und keinen eigenen Lebenszyklus braucht,
wäre das der Subscenario-Fall.
