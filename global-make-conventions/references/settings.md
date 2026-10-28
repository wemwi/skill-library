# B2 — Szenario-Settings

## Scheduling-Typ bei Webhook-Triggern

Ein Szenario, dessen erstes Modul ein Webhook ist (`gateway:CustomWebHook`
oder ein instant App-Trigger), MUSS mit Scheduling-Typ `immediately` laufen.

**Der Fehler ist stumm, nicht laut.** Ein Intervall-Scheduling auf einem
Webhook-Szenario wird von Make akzeptiert: das Szenario bleibt aktiv, die
Liste zeigt es grün, und es sammelt sogar Executions. Was fehlt, ist die
Zustellung — eingehende Calls landen in der Trigger-Queue und werden nur noch
im Takt abgeholt. Jeder solche Zyklus endet mit

    Trigger cannot be handled when processing an incomplete execution

als Warnung: ein Lauf, 1 Operation, kein Durchlauf, keine Fehler-Mail (nur die
Warnungs-Digest von Make). Der Nutzdaten-Call ist damit verloren. Nicht darauf
verlassen, dass ein falsches Scheduling beim Aktivieren auffällt — es fällt
nicht auf, und der Betrieb sieht wochenlang gesund aus, während die Execution-
und Operations-Zähler still hochlaufen (96 Leerläufe/Tag bei 15-Min-Takt).

**Häufigste Ursache: ein Blueprint-Import.** Der Import zieht das Scheduling
aus dem Blueprint und überschreibt dabei den bis dahin richtigen Wert. Deshalb
gehört die Nachkontrolle in die Import-Checkliste (B10), nicht in die
Bau-Checkliste — beim Bauen stimmt es meist, es kippt später.

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
