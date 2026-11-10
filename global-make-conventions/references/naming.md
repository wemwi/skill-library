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
`Webhook:`, `Watch:`, `Router:`, `Var:`, `Call:` oder `Error:` als Präfix:
redundant und kostet Breite auf dem Canvas.

Zum Default zählt auch die **zweite Zeile**, die Make bei manchen Modulen selbst
unter das Label setzt: bei `Call a scenario` den Namen des Zielszenarios, bei
API-Calls (`Make an API Call`, HTTP) Methode und Pfad (im Editor belegt am
10.11.2026). Ein Label, das den Szenarionamen oder die HTTP-Methode trägt, zeigt
dieselbe Information doppelt — und veraltet, sobald das Ziel umbenannt wird,
während die zweite Zeile mitzieht. Das Label muss trotzdem allein lesbar
bleiben: Die zweite Zeile steht nur am Canvas (Annahme: History und
Mapping-Panel zeigen sie nicht).

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

## Rollen-Präfix (optionale Klammer-Taxonomie)

Ein Szenario-Name darf sein führendes Verb als `[Rolle]`-Präfix in eckige
Klammern ziehen (`[Sync] Inventory to Shopify` = „Sync Inventory to Shopify"),
damit die Szenarioliste im UI nach Rolle gruppiert und sortiert. Das Präfix
*ist* das Verb aus Verb+Objekt, nur vorgezogen — es tritt nie *neben* ein Verb.

Drei Bedingungen, damit die Taxonomie eine Landkarte bleibt und nicht zerfasert:

- **Eine Achse: Rolle, nicht Trigger/Kadenz.** Was das Szenario *tut*, nicht
  *wann* es läuft. `[Scheduled]`/`[Daily]` ist der klassische Fehler — die Kadenz
  steht in den Settings, und sie leckt (ein zeitgesteuerter `[Sync]` müsste dann
  zwei Präfixe tragen). Ein zeitgesteuerter Wartungsjob wird nach seiner Rolle
  benannt (z.B. `[Maintain]`), nicht nach seinem Trigger.
- **Geschlossene Menge, im Projekt-Skill definiert.** Die konkreten Labels
  (`[Sync]`, `[Create]`, `[Process]`, `[Dispatch]`, `[Notify]`, …) mit je einer
  Definitionszeile gehören in den `<projekt>-operations-*`-Skill, nicht hierher —
  sie hängen am Portfolio. Hierher gehört nur die Regel, wie die Menge geführt wird.
- **Kein Präfix ohne lebendes Mitglied.** Eine Rolle wird erst zum Präfix, wenn
  ein Szenario dieser Rolle existiert und live ist — kein Reservieren „auf Vorrat".

**Check beim Audit:** Präfix-Set einachsig (ein Trigger-/Kadenz-Präfix neben
Rollen-Präfixen ist ein Befund) · jedes Präfix im Projekt-Skill definiert · jedes
Präfix hat ≥1 lebendes Szenario · das Präfix ersetzt das Verb, dupliziert es nicht.

## Modul-Naming je Typ

Das Label trägt das Delta (siehe Leitprinzip) in der für den Typ natürlichen
Grammatik. Die Spalte „Default zeigt schon" ist der Grund, warum das jeweilige
Wort *nicht* ins Label gehört.

| Modultyp | Default zeigt schon | Label trägt (Delta) | Beispiel |
|---|---|---|---|
| Instant-Trigger (Webhook) | Typ + Position 1 | das Event | `Receipt received` |
| Polling-Trigger (Watch) | Typ + Position 1 | die Entität | `New revenue row` |
| Write (Create/Update/Delete) | Write auf App X | die Wirkung | `Create receipt` · `Set revenue status` |
| Search / Read (nativ oder per API-Call) | Read auf App X, beim API-Call Methode + Pfad | Objekt + Match-Key, keine HTTP-Methode | `Find store (by UL number)` · `Get voucher (by id)` |
| Router | dass es ein Router ist | die Entscheidung | `Split by receipt type` |
| Route (Zweig) | dass es ein Zweig ist | der Fall | `Invoice` · `Credit note` |
| Filter (auf einer Kante) | nichts (leer) | die Bedingung, kurz (siehe unten) | `Store found` |
| Aggregator | dass aggregiert wird | was gebündelt wird | `Bundle line items` |
| Iterator | dass ein Array gesplittet wird | was iteriert wird | `Iterate receipt lines` |
| Flow-Control (Sleep/Repeat/Break) | das Steuer-Verb | der Zweck | `Sleep for rate limit` · `Repeat pages` |
| Variable (Set/Get) | dass es eine Variablen-Op ist | die Bedeutung | `Set idempotency key` |
| Transformer (Parse/Compose) | generischer Transform | Verb + Format | `Parse payload (JSON)` |
| HTTP / API-Call (Escape-Hatch, B3) | dass es ein HTTP-Call ist, Methode + Pfad | die Wirkung wie bei Read/Write, der Grund steht in der Modul-Note | `Load revenue (by month)` |
| Call a scenario | dass es aufruft, und das Zielszenario (zweite Zeile) | der Zweck aus Sicht des Aufrufers, ohne das Ziel zu wiederholen; an einen Hub mit Schlüssel-Eingang nur der Schlüssel | `Set payment` · `error.sync_aborted` |
| Start scenario / Return output | Typ und Position (erstes / letztes Modul) | nichts: fest `Start` und `Return`, bei mehreren Returns der Fall in der Klammer | `Start` · `Return (no match)` |
| Error-Handler-Route | dass es eine Fehlerroute ist, die Direktive (Icon) | die Folge für den Lauf: fester Name je Muster (siehe unten), sonst der Fall | `Retry + park` · `Not a voucher` |

Ein Default-Label wie `Airtable - Search Records` an einer flussentscheidenden
Stelle (Dedup-Gate, Route-Entscheidung) ist ein Audit-Befund — nicht weil der
Default falsch funktioniert, sondern weil er beim nächsten Debugging Zeit
kostet, die ein sprechendes Label gespart hätte.

## Klammer-Qualifier

Die Klammer hinter einem Label trägt einheitlich den *einen* Zusatz, der diesen
Knoten von einem gleichartigen unterscheidet: den Match-Key bei Reads
(`Find store (by UL number)`) oder den Fall bei mehreren Returns
(`Return (no match)`). Nicht mehrere Zusätze stapeln. Der Grund für einen
HTTP-Escape gehört in die Modul-Note, nicht in die Klammer — dort konkurriert er
mit dem Match-Key um denselben Platz. Auch die Klammer wiederholt die zweite
Zeile nicht: Zwei Aufrufe mit demselben Zweck und verschiedenen Zielszenarien
tragen dasselbe Label (`Set payment`), die zweite Zeile unterscheidet sie.

## Filter- und Routennamen — kurz, Unterschied vorn

Der Canvas kürzt einen Filternamen nach rund 15 Zeichen (im Editor belegt am
10.11.2026: `Purchase invoic…`). Der Name trägt deshalb die Bedingung in
möglichst höchstens 15 Zeichen, das unterscheidende Wort vorn: `Store found`,
nicht `Only if store exists`; `Fields missing` und `Fields complete`, nicht
`Gate 1 · Required fields incomplete` und `Gate 1 · Required fields complete`.
Kein Füllwort (`Only if`), kein Zähler vorn (`Gate 1 ·`). Prüft der Filter einen
festen Wert, darf der Wert selbst der Name sein (`salesinvoice`).

**Check beim Audit:** keine zwei Filter eines Szenarios mit denselben ersten 15
Zeichen.

## Fehlerrouten — feste Namen je Muster

Das Icon zeigt die Direktive, das Label die Folge für den Lauf. Wiederkehrende
Muster tragen überall denselben Namen, damit dieselbe Folge nicht unter vier
Bezeichnungen läuft:

| Muster | Direktive | Label |
|---|---|---|
| Wiederholen, danach als unvollständige Ausführung parken | Break, Retry an | `Retry + park` |
| Ohne Wiederholung parken | Break, Retry aus | `Park run` |
| Die Meldung über einen Fehler scheitert selbst, der Lauf geht weiter | Resume | `Skip notify error` |
| Lauf nach der Meldung beenden | Commit | `Stop` |
| Dieses Bundle beenden, mit dem nächsten weiter | Ignore | `Next <Objekt>`, z. B. `Next document` |
| Erwarteter, stiller Fall | Ignore oder Resume | der Fall: `Not a voucher` · `Continue without PDF` |

**Check beim Audit:** dieselbe Direktive mit derselben Einstellung trägt im
Portfolio nicht zwei Namen.

`Retry + park` und `Park run` setzen voraus, dass das Szenario eine
unvollständige Ausführung anlegen kann. In einem mit Warten gerufenen
Szenario kann es das nicht (B8, `errors.md`).

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

Die Szenario-Beschreibung trägt zusätzlich den Trigger-Kontrakt in einer Zeile —
wer/was triggert, welche Inputs, welcher Output; bei `Call a scenario`-Zielen
(on-demand) ist sie nie leer, dort ist sie die einzige Inline-Doku.

## Ordnerstruktur

Ordner spiegeln Projekt/Teilsystem-Zugehörigkeit (`POS Operations`,
`Website Ops`), nicht Datum oder Baureihenfolge. Ein neu Hinzukommender soll
am Ordnernamen erkennen können, zu welchem Geschäftsbereich ein Szenario
gehört, ohne jedes einzeln zu öffnen.
