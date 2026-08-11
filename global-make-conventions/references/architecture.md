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
Quelle, klassifiziert, und ruft den passenden Worker auf. Team-intern läuft
dieser Aufruf über `Scenarios > Call a scenario` im Async-Modus (Toggle „Wait
for the scenario to finish" = no) — der Worker behält seinen eigenen
Lebenszyklus, ohne öffentlichen Endpunkt und ohne Credit-Verbrauch. Ein
HTTP-Call auf einen eigenen `gateway:CustomWebHook` pro Worker ist nur nötig,
wenn der Worker eine Team-/Org-Grenze überschreitet oder von einem externen
Nicht-Make-System triggerbar sein muss.
**Tradeoff:** entkoppelt Klassifikation von Ausführung sauber — jeder Worker
lässt sich isoliert testen, re-triggern, deaktivieren, ohne den Dispatcher
anzufassen. Team-intern ist das nahezu kostenlos; nur der grenzüberschreitende
Fall kostet eine zusätzliche Netzwerk-Hop-Ebene und einen öffentlichen Webhook
pro Worker.
**Bruchmodus:** wird der Dispatcher zum heimlichen Business-Logik-Träger
statt reiner Klassifikator, verschiebt sich die Verantwortung unsauber
zurück in Richtung Router-Monster.

### Orchestrator + native Subscenarios (Scenarios-App-Verkettung)
**Wann:** dieselbe Logik (Normalisierung, Validierung, ein Lookup-Baustein)
wird in mehreren Szenarien gebraucht und soll eine Single Source of Truth
haben — Änderung an einer Stelle, wirkt überall. Ebenso jede team-interne
Szenario-zu-Szenario-Übergabe, auch entkoppelte.
**Mechanik:** der Aufrufer nutzt `Scenarios > Call a scenario`, das
Subscenario startet mit `Start scenario` und gibt über `Return output`
zurück — ohne den HTTP+Webhook-Umweg, der vor Einführung der Scenarios-App
nötig war. Sync oder async wird per „Wait for the scenario to finish"-Toggle
gewählt: sync = Aufrufer wartet auf die Outputs, async = Aufrufer läuft sofort
weiter, das Subscenario arbeitet unabhängig zu Ende. „Eigener Lebenszyklus"
zwingt also **nicht** zum Webhook — er ist der Async-Modus dieses Musters.
**Tradeoff:** spart Duplikation und Wartungsaufwand, definierte Inputs/Outputs,
kein Credit-Verbrauch, kein öffentlicher Endpunkt — die Standardwahl für alles
Team-interne, synchron wie asynchron. Grenze: nur team-intern aufrufbar; über
Team-/Org-Grenzen oder für externe öffentliche Trigger braucht es weiterhin
Webhook bzw. `Make > Run a scenario`.
**Bruchmodus:** Modus unpassend zum Datenfluss — async ohne `Return output`
gedacht, obwohl der Aufrufer ein Ergebnis braucht; oder umgekehrt der Aufrufer
wartet synchron auf ein langlaufendes Subscenario und blockiert unnötig. Den
Toggle bewusst zum Datenfluss setzen, nicht per Default.

### Data-Store-Queue (Producer/Consumer)
**Wann:** Erzeugung und Verarbeitung eines Events sollen zeitlich entkoppelt
sein, mit Replay-Fähigkeit und einem sichtbaren Idempotenz-Ledger.
**Tradeoff:** stärkste Entkopplung und Nachvollziehbarkeit, höchster
Bau-Aufwand — meist nur gerechtfertigt, wenn Replay oder Audit-Trail ein
echtes Anforderungsmerkmal ist, nicht nur „könnte später nützlich sein".
**Bruchmodus:** als Standardlösung für jedes Problem eingesetzt, wird sie zum
Over-Engineering — die Data-Store-Queue braucht eine echte
Entkopplungs-Anforderung, sonst ist ein einfacheres Muster richtig.

## Entscheidungsachse: Reichweite zuerst, Modus danach

Die praktisch wichtigste Weichenstellung ist **nicht** sync-vs-async — das ist
nur ein Toggle. Sie ist die **Reichweite** des Aufrufs:

**Bleibt der Aufruf innerhalb desselben Make-Teams?**

- **Ja** (team-intern) → **Scenarios-App** (`Call a scenario` / `Start
  scenario` / `Return output`). Der native Weg mit definierten Inputs/Outputs,
  ohne Credit-Verbrauch und ohne öffentlichen Endpunkt. Die alte
  HTTP+Webhook-Verdrahtung für team-interne Übergaben gilt als überholt: sie
  erzeugt Duplikations- und Wartungsaufwand, öffnet einen unnötigen
  öffentlichen Endpunkt und kostet Credits.
- **Nein** — der Aufruf überschreitet eine Team-/Org-Grenze, oder ein externes
  Nicht-Make-System muss per öffentlicher URL triggern → **Webhook**
  (`gateway:CustomWebHook`) bzw. `Make > Run a scenario` für cross-team. Der
  öffentliche Endpunkt und der Netzwerk-Hop sind hier der Preis für die
  Reichweite, keine Architektur-Entscheidung.

Erst *nach* dieser Weiche kommt der Modus — bei der Scenarios-App ein einziger
Toggle („Wait for the scenario to finish"):

**Braucht der Aufrufer das Ergebnis, um weiterzulaufen?**

- **Ja** → synchron (Toggle = yes): der Aufrufer pausiert, bis das Subscenario
  über `Return output` zurückgibt.
- **Nein** → asynchron (Toggle = no): der Aufrufer läuft sofort weiter, das
  Subscenario arbeitet mit eigenem Lebenszyklus unabhängig zu Ende.

Der zentrale Merksatz gegen den alten Denkfehler: **„eigener Lebenszyklus"
zwingt nicht zum Webhook.** Ein team-interner Worker mit eigenem Fehler- und
Re-Trigger-Verhalten läuft genauso über `Call a scenario` im Async-Modus —
nur ohne öffentlichen Endpunkt und ohne Credits. Der Webhook wird erst durch
die *Reichweite* nötig, nicht durch die Entkopplung.

Ein Dispatcher, der eingehende Dokumente klassifiziert und je nach Typ einen
von mehreren fachlich unabhängigen Verarbeitungspfaden mit eigenem
Datenmodell, eigenem Fehlerverhalten und eigener isolierter Re-Trigger-Fähigkeit
weckt, bleibt ein sauberes Muster — aber team-intern über `Call a scenario`
(async), nicht über einen Webhook pro Worker. Ein eigener Webhook pro Worker
ist erst dann richtig, wenn ein Worker in einem anderen Team / einer anderen
Org lebt oder von außen triggerbar sein muss.
