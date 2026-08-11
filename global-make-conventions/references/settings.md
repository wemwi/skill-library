# B2 — Szenario-Settings

## Scheduling-Typ bei Webhook-Triggern

Ein Szenario, dessen erstes Modul ein Webhook ist (`gateway:CustomWebHook`
oder ein instant App-Trigger), MUSS mit Scheduling-Typ `immediately` laufen.
`indefinitely` lässt die Aktivierung mit „Invalid interval" fehlschlagen —
kein Grauzonen-Fall, sondern ein harter Fehler.

## Incomplete Executions

„Store incomplete executions" ist standardmäßig AUS. Für jedes Szenario mit
Write-Seiteneffekten (legt Datensätze an, ändert Zustand, verschickt
Nachrichten) MUSS es AN sein — sonst verschwindet ein gescheiterter Lauf
spurlos, ohne Queue, ohne Replay-Möglichkeit. Ein DLQ-Eintrag heilt dabei
nicht von selbst (siehe `errors.md`) — die Einstellung allein reicht nicht,
der Eintrag muss auch abgearbeitet werden.

## Sequenziell vs. parallel

Standardmäßig läuft Make sequenziell pro Szenario. Parallele Ausführung
erhöht den Durchsatz, gefährdet aber Datenintegrität, sobald mehrere Läufe
gleichzeitig auf denselben geteilten State zugreifen (z.B. ein Dedup-Gate,
das erst nach dem Write greift). Die Entscheidung gehört in die
Kontrakt-Phase (A1.4): „kann dieses Szenario parallel laufen, ohne dass zwei
Läufe sich gegenseitig überschreiben?" — nicht als nachträgliche
Performance-Optimierung, wenn ein Race-Condition-Bug schon aufgetreten ist.

## Auto-Deaktivierung nach Folgefehlern

Wo ein durchlaufender Fehler unbemerkt Schaden anhäuft (z.B. jeder Lauf
verliert ein Datenfeld still), ist eine Grenze für aufeinanderfolgende
Fehler samt automatischer Deaktivierung sinnvoll — der Fehler stoppt sich
selbst, statt tagelang weiterzulaufen, bevor ihn jemand bemerkt.
