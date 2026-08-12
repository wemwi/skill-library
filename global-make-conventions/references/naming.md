# B1 — Naming & Lesbarkeit

## Sprache

Alle Bezeichner sind **englisch** und projektweit einheitlich: Szenario-Namen,
Modul-Labels, Ordnernamen, Variablennamen (die IML-Referenz) und Doku-/
Kommentartexte. Gemischtsprachige Blueprints sind ein Audit-Befund — nicht
wegen der Sprache an sich, sondern weil Uneinheitlichkeit genau die Landkarte
zerreißt, die das Naming sein soll.

## Leitprinzip — das Label trägt nur das Delta

Ein Modul zeigt seinen Typ bereits selbst: über das App-Icon, den Default-Namen
und (beim Trigger) die Position an Stelle 1. Ein Label trägt deshalb genau das,
was der Default *nicht* schon sagt — nie den Typ wiederholen. Konkret kein
`Webhook:`, `Watch:`, `Router:`, `Var:` oder `Error:` als Präfix: redundant und
kostet Breite auf dem Canvas.

Das Grammatik-Muster ist nicht für alle Typen dasselbe, weil die Rolle nicht
dieselbe ist. **Verb + Objekt** (die Wirkung) ist der Default für jeden Knoten,
der eine Datenaktion ausführt. Drei Typen weichen begründet ab, weil ihr Job
kein Verb-Objekt ist: ein **Trigger** benennt ein Event, ein **Router-Zweig**
einen Fall, ein **Filter** eine Bedingung.

## Szenario-Naming

Namen sind handlungsbasiert: Verb + Objekt + (Ziel-App, wenn nicht
eindeutig). Ein Name soll ohne Öffnen des Szenarios sagen, was es tut.

**Gut:** `Sync New Gmail Contacts to CRM`, `Classify PDF Upload & Dispatch
Process`, `Process Payment Reminder & Dunning in Airtable`

**Schlecht:** `Google Sheet Sync` (welche Richtung? welche Daten?),
`Scenario 3`, eine nackte Szenario-ID, `Webhook Handler` (ohne zu sagen,
wofür).

Bei Teams besonders kritisch: die Namenskonvention ist die einzige Landkarte,
die neue Mitarbeitende ohne Vorwissen lesen können. Ein Name, der Zweck,
Datenfluss und Impact erkennen lässt, spart jede spätere Nachfrage.

**Check beim Audit:** Name enthält ein Verb (Sync/Process/Classify/Dispatch/
Notify …) plus ein konkretes Objekt. Reine App-Namen oder IDs sind ein
Befund.

## Modul-Naming je Typ

Das Label trägt das Delta (siehe Leitprinzip) in der für den Typ natürlichen
Grammatik. Die Spalte „Default zeigt schon" ist der Grund, warum das jeweilige
Wort *nicht* ins Label gehört.

| Modultyp | Default zeigt schon | Label trägt (Delta) | Beispiel |
|---|---|---|---|
| Instant-Trigger (Webhook) | Typ + Position 1 | das Event | `Receipt received` |
| Polling-Trigger (Watch) | Typ + Position 1 | die Entität | `New revenue row` |
| Write (Create/Update/Delete) | Write auf App X | die Wirkung | `Create receipt` · `Set revenue status` |
| Search / Read | Read auf App X | Objekt + Match-Key | `Find store (by UL number)` |
| Router | dass es ein Router ist | die Entscheidung | `Split by receipt type` |
| Route (Zweig) | dass es ein Zweig ist | der Fall | `Invoice` · `Credit note` |
| Filter (auf einer Kante) | nichts (leer) | die Bedingung | `Only if store exists` |
| Aggregator | dass aggregiert wird | was gebündelt wird | `Bundle line items` |
| Iterator | dass ein Array gesplittet wird | was iteriert wird | `Iterate receipt lines` |
| Flow-Control (Sleep/Repeat/Break) | das Steuer-Verb | der Zweck | `Sleep for rate limit` · `Repeat pages` |
| Variable (Set/Get) | dass es eine Variablen-Op ist | die Bedeutung | `Set idempotency key` |
| Transformer (Parse/Compose) | generischer Transform | Verb + Format | `Parse payload (JSON)` |
| HTTP (Escape-Hatch, B3) | dass es ein HTTP-Call ist | Wirkung + Grund | `Load revenue via REST (cellFormat)` |
| Call a scenario / Return | dass es aufruft/zurückgibt | Ziel / Output | `Notify dispatcher` · `Return receipt id` |
| Error-Handler-Route | dass es eine Fehlerroute ist | Direktive + Fall | `Retry on 429` · `Ignore (already processed)` |

Ein Default-Label wie `Airtable - Search Records` an einer flussentscheidenden
Stelle (Dedup-Gate, Route-Entscheidung) ist ein Audit-Befund — nicht weil der
Default falsch funktioniert, sondern weil er beim nächsten Debugging Zeit
kostet, die ein sprechendes Label gespart hätte.

## Klammer-Qualifier

Die Klammer hinter einem Label trägt einheitlich den *einen* Zusatz, der diesen
Knoten von einem gleichartigen unterscheidet: den Match-Key bei Reads
(`Find store (by UL number)`), den Grund bei einem HTTP-Escape
(`Load revenue via REST (cellFormat)`) oder den Fehlerfall bei einer
Fehlerroute (`Retry on 429`). Nicht mehrere Zusätze stapeln.

## Namespacing bei vielen gleichartigen Modulen

Macht ein Szenario mehrere Writes/Reads auf verschiedene Tabellen oder
Entitäten, wird die Entität als Präfix vorangestellt: `Revenues.Append note`,
`Receipts.Create`. Das zeigt auf einen Blick, welche Entität ein Modul anfasst
— sinnvoll ab dem Punkt, wo sonst mehrere Labels gleich aussähen.

## Immer labeln vs. Schwelle

Vier Knotentypen werden **immer** gelabelt, unabhängig von der Modulzahl, weil
genau sie beim Debugging Zeit kosten: **Trigger, Router-Zweige, Write-Module und
Fehlerrouten**. Ein Zwei-Modul-Szenario mit unbenanntem Router ist trotzdem
unlesbar. Alle übrigen Module sind bis ~5 Module auf Default tolerierbar; ab da
tragen auch sie sprechende Labels.

## Router-Zweige — Abwägung

Ein Router-Zweig trägt den Fall ohne Präfix: `Invoice`, `Credit note`. Auf dem
Canvas liest sich das sauber, weil der Zweig visuell als Router-Ausgang
erkennbar ist. In der flachen Execution-History ohne Canvas kann ein nacktes
`Invoice` kryptischer wirken — wer überwiegend im Log statt am Canvas debuggt,
kann hier ausnahmsweise ein `Route:`-Präfix rechtfertigen. Default ist ohne.

## Variablennamen (IML-Referenz)

Der Variablenname ist die Referenz, unter der ein Wert später als `{{...}}`
abgegriffen wird — nicht das Modul-Label. Er sagt die Bedeutung, ist englisch
und projektweit in *einer* Schreibweise gehalten (Empfehlung: lowerCamelCase).
Das Set-Modul-Label und der Name gehören zusammengedacht: Label
`Set idempotency key` → Name `idempotencyKey`; weiter z.B. `storeRecordId`,
`isDuplicate`. Kein `var1`, kein sprechendes Label bei kryptischem Namen.

## Doku & Kommentare

Modul-Notes und Szenario-Beschreibung sind englisch und tragen das *Warum*, das
im Label keinen Platz hat — nicht die Wiederholung des Labels. Gut: „HTTP statt
nativ, weil das native Modul keinen cellFormat-Parameter reicht." Schlecht:
„Sucht einen Store." (steht schon im Label).

## Ordnerstruktur

Ordner spiegeln Projekt/Teilsystem-Zugehörigkeit (`POS Operations`,
`Website Ops`), nicht Datum oder Baureihenfolge. Ein neu Hinzukommender soll
am Ordnernamen erkennen können, zu welchem Geschäftsbereich ein Szenario
gehört, ohne jedes einzeln zu öffnen.
