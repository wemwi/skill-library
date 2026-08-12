# B11 — Variablen & State

Make bietet vier Variablen-Tools (`Set variable`, `Set multiple variables`,
`Get variable`, `Get multiple variables`) plus zwei benachbarte State-Ebenen
(Custom Variables, Data Store). Die MUST/SHOULD-Zeilen in `SKILL.md` decken
die Konvention ab; hier steht das Warum, die Mechanik und die
Entscheidungsachse.

## Scenario-Variablen sind laufflüchtig

Make positioniert Scenario-Variablen ausdrücklich als **temporären Speicher
für genau einen Lauf** — Zwischenwerte, Weitergabe zwischen Modulen im selben
Szenario, einfache Zähler/Flags. Nichts davon überlebt das Szenario-Ende. Wer
einen Wert über das Laufende hinaus „merken" will, benutzt das falsche
Werkzeug (→ State-Ebenen unten).

## Set/Get Multiple statt Einzel-Ketten

Die Var-Tools sind Module wie jedes andere: **jeder Modul-Lauf pro Bundle ist
eine Operation.** Der verbreitete Mythos „Set Variable ist gratis" stimmt
nicht. Der reale Effizienzhebel ist das *Multiple*-Modul — Make nennt als
Hauptvorteil, dass ein `Get multiple variables` eine ganze Serie einzelner
`Get variable` ersetzt und dabei nur eine Operation verbraucht. Also: vier
Werte an einem Punkt → **ein** `Set multiple variables`, nicht vier
`Set variable`.

Der teure Fehler in freier Wildbahn ist das Gegenteil: ein `Get variable`
hinter einem Aggregator/Iterator feuert pro Bundle erneut und frisst
überraschend viele Operationen.

## Vor den Router setzen, in den Zweigen direkt referenzieren

Make dokumentiert, dass man für den Zugriff auf eine Variable **in einer
anderen Route als der, in der sie gesetzt wurde**, die Get-Tools braucht.
Make's eigenes Lehrbuch-Beispiel setzt deshalb in Route 1 und holt in Route 2
per `Get multiple variables` zurück — was pro Zweig zusätzliche
Get-Operationen kostet.

**Die sauberere Topologie:** das `Set multiple variables` **vor** den Router
ziehen. Dann sind alle Zweige nachgelagert, und jeder Zweig referenziert den
Output direkt als `{{<setId>.name}}` — ganz ohne `Get variable`. Das spart die
Get-Operationen komplett und hält die Referenz sichtbar-verdrahtet statt über
den unsichtbaren Variablen-Namensraum.

`Get variable` ist damit nur legitim, wenn die Set-Quelle **nicht**
nachgelagert liegt — echte Parallel-/Geschwisterzweige, wo Direktreferenz
topologisch unmöglich ist. Ein Get auf eine Quelle, die auf dem aktuellen
Pfad/Cycle nie lief, liefert still leer — das ist ein Korrektheitsfehler, kein
bloßer Stil.

## Scope: One cycle vs. Whole execution

Zwei Lebensdauern, und die Wahl ist folgenreich:

- **One cycle** (`roundtrip`) — die Variable wird bei jedem neuen Cycle
  zurückgesetzt. Der Default für laufflüchtige Pro-Bundle-Werte: jeder
  Datensatz, der durch die Kette läuft, bekommt seinen eigenen Wert.
- **Whole execution** (`execution`) — hält über alle Cycles derselben
  Ausführung. Nur für Werte, die man **absichtlich** über Bundles hinweg
  trägt oder akkumuliert (z.B. ein Zähler über alle Datensätze eines Laufs).

**Bruchmodus:** `Whole execution` auf einem Pro-Datensatz-Wert leckt — sobald
der Trigger mehr als ein Bundle liefert, sieht Bundle 2 noch den Wert von
Bundle 1, bis das Set-Modul überschreibt. Bei Webhooks mit `maxResults: 1`
fällt das nie auf und schlägt später bei Batch-Läufen zu. Default deshalb
`One cycle`, `Whole execution` nur mit dokumentiertem Grund.

## Der benannte Kontrakt (die Picker-Symptomatik)

Der stärkste Grund für ein `Set multiple variables` ist oft gar nicht
Wiederverwendung, sondern **Kapselung fragiler Referenzen**. Typische
Kandidaten:

- Ergebnisobjekte aus Code- oder AI-Modulen (`{{5.result.datum}}` etc.) —
  strukturell da, aber im Mapping-Picker nachgelagerter Module oft nicht
  sauber aufklappbar/klickbar, weil der Output als generische Collection
  typisiert ist.
- Array-Index-Zugriffe wie ein Attachment-URL
  (`{{2.fldXX[1].url}}`) — von Hand
  fehleranfällig zu tippen und in jeden Consumer zu kopieren.
- Rohe Feld-ID-Referenzen, die bei einer Airtable-Feldumbenennung an *jeder*
  Stelle brechen würden (Kopplung zu B9).

Ein `Set multiple variables` lupft solche Werte einmal in **benannte,
top-level, pickbare Tokens** und wird damit zum deklarierten Kontrakt zwischen
dem opaken/fragilen Upstream und allem Nachgelagerten — eine Mini-Anti-
Corruption-Layer. Wird die Feld-ID oder der Array-Pfad einmal falsch, ist es
ein Edit statt N.

**Caveat zur Picker-Formulierung:** dass ein bestimmter Wert im Picker nicht
klickbar ist, ist konkretes Make-UI-Verhalten und kann sich mit Releases
ändern — es ist das *Symptom*, nicht die Regel. Die Regel ist das
Kontrakt-Prinzip (fragile/opake Referenz an eine Stelle), das jede
Picker-Verbesserung überlebt. Nicht am UI-Detail festmachen, am Prinzip.

**Check beim Audit:** derselbe tiefe Array-Index oder dieselbe rohe Feld-ID
mehrfach über nachgelagerte Module dupliziert, wo ein benannter Kontrakt sie
bündeln würde → SHOULD-Befund. Ein `Set multiple variables`, das als Kontrakt
gedacht ist, aber nur *einen Teil* der Upstream-Werte kapselt (Rest fließt
weiter roh durch), ist inkonsistent — entweder ganz oder gar nicht.

## State-Ebenen — wann man Variablen verlässt

Die eigentliche Skalierungsfrage ist zu wissen, wann eine Scenario-Variable
nicht mehr das richtige Werkzeug ist. Make hat drei Ebenen:

| Ebene | Lebensdauer / Reichweite | Wofür |
|-------|--------------------------|--------|
| **Scenario-Variable** (Set/Get) | ein Lauf, ein Szenario | laufflüchtige Zwischenwerte, Kontrakte, Zähler/Flags |
| **Custom Variable** | persistent, Team-/Org-weit, über Szenarien | Konfiguration & Business-Logik (`testmode`, Telefonnummer, Schwellwerte); ab Pro/Teams/Enterprise. Keine Datenbank — nicht für viel oder häufig wechselnde Daten |
| **Data Store** | persistent, über Läufe hinweg | State/Memory: Deduplizierung, „schon verarbeitet"-Keys, Caching, laufübergreifende Akkumulation |

**Entscheidungsregel:** braucht ein Wert nur diesen Lauf → Scenario-Variable.
Ist es Konfiguration/Business-Logik über Szenarien → Custom Variable. Braucht
es State über Läufe (Dedup, Cache, Memory) → Data Store. Das Idempotenz-Gate
aus B7 ist deshalb ein Data-Store-Fall, keine Variable — eine Scenario-
Variable kann per Definition nicht wissen, was ein früherer Lauf verarbeitet
hat.
