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

## Bytes nie mehrfach durch den Kontext

Ein Blueprint-Inhalt sollte innerhalb eines Chat-/Agent-Kontexts nicht
wiederholt gelesen und vollständig zurückgeschrieben werden — jeder
Lese-Schreib-Zyklus verdoppelt die Bytes im Kontext und akkumuliert über
mehrere Korrekturschleifen. Die konkrete Mechanik (Basis = installierte/
exportierte Version, Edits als Diff statt Volltext, ein einziger
vollständiger Durchlauf beim finalen Paketieren) ist projektübergreifend in
`global-workflow §5` beschrieben und wird hier nur als Prinzip referenziert,
nicht dupliziert.
