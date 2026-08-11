# B7 — Idempotenz & Dedup

## Grundannahme: at-least-once ist der Normalfall

Webhook-Quellen und viele Trigger-Mechanismen garantieren „mindestens
einmal", nicht „genau einmal" — Retries, Timeouts, wiederholte
Statuswechsel-Events und manuelle Replays sind erwartbar, kein Edge Case.
Jedes Szenario, dessen Trigger mehrfach für dasselbe Geschäftsereignis
feuern kann, MUSS ein Idempotenz-Gate haben.

## Der Schlüssel muss stabil sein

Ein Idempotenz-/Dedup-Key entsteht aus stabilem Geschäftssinn:

- eine vom Quellsystem gelieferte Event-ID
- ein deterministischer Hash aus stabilen Payload-Feldern
- ein natürlicher, aus Geschäftsdaten abgeleiteter Schlüssel (z.B.
  `{Store}-{Datum}` als dedupkey)

**Nie geeignet:** Execution-ID, Zeitstempel der Verarbeitung — beide ändern
sich bei jedem Retry und brechen den Abgleich genau dann, wenn er gebraucht
wird.

## Lookup-before-Write statt blindem Create

Jeder Schreib-Pfad, der neue Datensätze anlegen kann, sucht zuerst mit
striktem Match (Dedup-Key, nicht Fuzzy-Matching) und erstellt nur bei
echtem Fehlschlag. Blindes Create unter Retry-Druck erzeugt Dubletten,
blindes Update unter denselben Bedingungen kann gültige Daten überschreiben
— kontrollierte Verzweigung (Suche → Treffer/kein Treffer → Update/Create)
ist in beiden Richtungen sicherer.

## Ein eigenes „bereits verarbeitet"-Verdikt

Wo ein Trigger regulär mehrfach für dasselbe Ereignis feuert (z.B. ein
Status-Event, das bei jedem Statuswechsel erneut ausgelöst wird), lohnt sich
ein dritter Verdikt neben „Treffer" und „unklar": „übersprungen" — die
Route endet still, ohne Write und ohne Meldung, sobald sie erkennt, dass die
Arbeit für dieses Ereignis bereits erledigt ist. Das verhindert, dass
wiederholtes Feuern in den Fehlerpfad läuft und dort unnötig Rauschen
erzeugt.
