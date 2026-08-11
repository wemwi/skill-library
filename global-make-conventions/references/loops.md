# B5 — Schleifenfreiheit (Flaggschiff-Regel)

Dies ist die teuerste Fehlerklasse in Webhook-getriebenen Make-Szenarien:
ein Szenario, das seinen eigenen Trigger erneut auslöst. Der Effekt ist
selten ein offensichtlicher Crash — meist ein leiser Doppellauf, der Tage
unbemerkt bleibt, weil der zweite Lauf ins Leere greift und harmlos wirkt.

## Die Grundregel

**Ein gelauschtes Watch-Feld darf nie ein Feld sein, das derselbe
Trigger-Pfad (der Trigger selbst oder ein von ihm geweckter Folgeprozess)
zurückschreibt.** Jeder Schreibzugriff auf ein gelauschtes Feld ist ein
potenzielles zweites Trigger-Signal.

**Check:** Diff aus (a) der Liste der Watch-Felder eines Triggers und (b)
der Liste aller Felder, die das Szenario oder ein von ihm angestoßener
Folgeprozess schreibt. Der Diff muss leer sein.

## `changeTypes` bewusst setzen

Wo die Trigger-Konfiguration zwischen Change-Types unterscheidet (add /
update / remove), ist die Auswahl kein Default, sondern eine bewusste
Entscheidung: welcher Change-Type soll wirklich einen neuen Lauf
rechtfertigen? „Reagiert nur auf Neuanlage" heißt fast immer `add` allein —
jedes `update` (auch ein harmlos wirkendes wie ein In-Place-Dateiaustausch)
holt sonst denselben Datensatz erneut in den Trigger.

## Realfall: Phantom-Execution im Dispatch-Upload

Ein produktives Dispatcher-Szenario klassifizierte hochgeladene PDFs und
schrieb dabei den Belegtyp auf denselben Datensatz zurück, den sein eigener
Trigger beobachtete.

**Symptom:** jeder Upload erzeugte zwei Executions statt einer — eine echte
(klassifiziert, verarbeitet) und eine zweite, leere (WARNING, kein
Datenschaden, weil eine gefilterte View als Zufalls-Circuit-Breaker
wirkte und der bereits klassifizierte Datensatz beim zweiten Lauf nicht
mehr in der Trefferliste war).

**Erster Fixversuch (unvollständig):** das Watch-Feld für den Typ aus der
Spec entfernt, `changeTypes` auf `add` + `update` belassen. Ergebnis: das
Phantom blieb — weil nicht nur der Typ-Writeback ein zweites Signal
erzeugte, sondern auch das Ersetzen des Anhangs in place (derselbe Trigger
lauschte weiterhin auf das Anhang-Feld, und das Fachszenario ersetzt den
Anhang bei der Verarbeitung).

**Korrekter Fix:** `changeTypes` auf ausschließlich `add`. Damit feuert der
Trigger nur bei echter Neuanlage — jedes spätere `update` (Typ-Writeback
UND Anhang-Ersetzung) löst keinen zweiten Lauf mehr aus. Verifiziert: nach
der Korrektur genau eine Execution pro Upload, kein Nachläufer.

**Lehre für die Regel:** eine unvollständige Diagnose („nur das eine
zurückgeschriebene Feld ist das Problem") kann den Fix scheitern lassen,
obwohl er formal korrekt aussieht — die Prüfung muss ALLE Schreibzugriffe
im Trigger-Pfad einschließen, nicht nur den offensichtlichsten.

**Zweite Lehre — Deploy-Mechanik:** eine geänderte Watch-Spec (Feld oder
changeTypes) wirkt bei Airtable-Gateway-Webhooks erst nach Löschen und
Neuanlage des Hooks. Ein reines „Refresh" eines bestehenden Hooks behält die
alte Spec, auch wenn die neue Konfiguration im Code/System bereits korrekt
hinterlegt ist — deshalb ist dies zusätzlich als eigene Regel unter B6
(Webhook-Lebenszyklus) verankert.

## Architektur-Hinweis

Kein Szenario in einem gesunden Portfolio nutzt einen Airtable-„Watch
Records"-Trigger als Grundmuster (siehe `triggers.md`) — damit entfällt der
klassischste Auslöser dieser Fehlerklasse von vornherein. Wo dennoch ein
Trigger auf Datenänderungen lauscht (Gateway-Webhook auf eine Automation,
Mailhook, App-Event), gilt dieselbe Diff-Prüfung unverändert.
