# B10 — Blueprint- & Deploy-Hygiene

## Blueprint immer als JSON-Datei

Ein Blueprint wird nie als Prosa-Beschreibung, Chat-Text oder Teil-Snippet
übergeben — immer als vollständige, valide JSON-Datei. Das ist die einzige
Form, die verlustfrei importierbar ist und sich eindeutig gegen einen
vorherigen Stand diffen lässt.

## Query-String-Konvention für API-Calls

Wo ein Modul (nativ oder HTTP) Query-Parameter setzt, gehören sie in die
dafür vorgesehenen Parameter-/Query-String-Felder des Moduls — nicht als
Teil der URL zusammengebaut (String-Konkatenation). Beim aktuellen
generischen HTTP-Modul `http:MakeRequest` (v4) ist das die
`queryParameters`-Liste (`{name, value}`-Paare im Mapper), nicht die
`url`. Grund: das Modul übernimmt dann Encodierung (Sonderzeichen,
Leerzeichen) korrekt, und die Parameter bleiben im Blueprint als
strukturierte Werte statt als Teil eines unstrukturierten URL-Strings
sichtbar — leichter zu lesen, leichter zu ändern, ohne die URL-Struktur
selbst anzufassen.

## UI-Export statt programmatischem Full-Fetch

Für ein bereits bestehendes Szenario wird der Export über die Make-UI
(⋯ → Export Blueprint) angefordert, nicht ein programmatischer Full-Fetch
über die API. Der UI-Export liefert einen kleineren, saubereren Blueprint
ohne Laufzeit-Metadaten (z.B. ohne den `scheduling`-Key, ohne
Designer-Sample-Daten), die ein API-Fetch mitliefert und die beim
Zurückschreiben unnötige Diffs erzeugen.

## Aggregatoren: ganz oder gar nicht

Aggregator-Module (`util:TextAggregator`, `builtin:BasicAggregator` etc.)
sind mapper-fragil: ihre Bindung an das Feeder-Modul hängt an internen
Referenzen, die eine UI-Bearbeitung anders aktualisiert als ein
Blueprint-Edit. Ein Aggregator wird deshalb entweder komplett per Blueprint
bearbeitet oder komplett im UI — eine gemischte Bearbeitung (erst UI, dann
Blueprint-Patch oder umgekehrt) zerstört die Bindung leise, ohne sichtbaren
Fehler beim Speichern.

## Connection-Bindings nach jedem Update verifizieren

Ein programmatisches Update eines vollständigen Blueprints setzt
Connection-Bindings mal zurück, mal nicht — das Verhalten ist über
verschiedene Szenarien/Update-Wege hinweg nicht verlässlich vorhersagbar.
Die sichere Invariante ist deshalb: nach jedem Blueprint-Update die
Bindings aktiv prüfen (z.B. über die Modul-Konfiguration in der UI oder
einen Testlauf), statt sich auf ein einmal beobachtetes Verhalten zu
verlassen und anzunehmen, es gelte für jedes künftige Update gleich.

## StartSubscenario-Interface nach jedem Import verifizieren

Das Interface eines `Start scenario`-Triggers — die typisierten Inputs/Outputs,
über die ein Call-a-scenario-Ziel angesprochen wird — ist eine **eigene
Szenario-Einstellung**, kein Teil des Flows. Im UI-Export lebt es als
top-level `io`-Block (`input_spec`/`output_spec`), getrennt vom `flow`. Ein
Blueprint-Import, der diesen Block nicht mitträgt, **wischt das Interface leer**,
ohne einen Fehler zu werfen: das Szenario importiert grün, aber die deklarierten
Felder sind weg. Betroffen sind nur Call-a-scenario-Ziele (StartSubscenario-
Trigger) — `CustomWebHook`-Szenarien haben kein Interface und sind gegen diesen
Fehlermodus immun.

**Bau-Regel.** Jedes StartSub-Blueprint, das zum Import geht, behält seinen
top-level `io`-Block (`input_spec`/`output_spec`) — nie auf `name`/`flow`/
`metadata` reduzieren. Die Felder gehören zusätzlich in
`trigger.metadata.interface`, damit der Trigger-Knoten selbst sie kennt.

**Pflicht-Verifikation nach jedem StartSub-Import.** Direkt nach dem Import das
Interface aktiv prüfen (`scenarios_interface(id)`). Ist es leer, wird es
restauriert: `validate_scenario_interface` (Kontrakt bilden) →
`scenarios_set-interface` (setzen). Nicht annehmen, das Interface sei
durchgekommen — der Import meldet keinen Fehler, wenn es fehlt.

**MCP-Falle bei der Restauration.** `scenarios_set-interface` lehnt ein
`help: ""` ab — das Feld braucht ≥1 Zeichen oder muss ganz weggelassen werden.
Ein Feld-Objekt vom Typ `text` hat die Form
`{name, type, label, required, multiline}` — `multiline` ist bei `text`
**Pflicht**, sonst schlägt das Setzen fehl.

**Symptom, wenn es durchrutscht** (Realfall 14.08.): ein Notification-Hub-
Szenario wurde mit leerem Interface importiert. Alle Referenzen auf die
Trigger-Bundle-Felder (`{{1.key}}`, `{{1.id}}`, `{{1.ctx}}`) liefen damit ins
Leere — jede ausgelöste Notification meldete „Unbekannter Schlüssel" und stürzte
auf den Default-Thread ab, was in `[400] message thread not found` endete. Ein
leeres Interface ist also kein kosmetischer Defekt, sondern bricht jeden
nachgelagerten Consumer, der auf die Trigger-Felder mappt.

## Bytes nie mehrfach durch den Kontext

Ein Blueprint-Inhalt sollte innerhalb eines Chat-/Agent-Kontexts nicht
wiederholt gelesen und vollständig zurückgeschrieben werden — jeder
Lese-Schreib-Zyklus verdoppelt die Bytes im Kontext und akkumuliert über
mehrere Korrekturschleifen. Die konkrete Mechanik (Basis = installierte/
exportierte Version, Edits als Diff statt Volltext, ein einziger
vollständiger Durchlauf beim finalen Paketieren) ist projektübergreifend in
`global-workflow §5` beschrieben und wird hier nur als Prinzip referenziert,
nicht dupliziert.
