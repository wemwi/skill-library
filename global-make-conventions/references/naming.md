# B1 — Naming & Lesbarkeit

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

## Modul-Naming

Ab ca. 5 Modulen wird ein Blueprint ohne sprechende Labels unlesbar — vor
allem an Entscheidungspunkten:

- Router-Zweige benennen, wofür sie stehen (`Route: Lieferung` /
  `Route: Bestandsprüfung`), nicht `Route 1` / `Route 2`.
- Suchmodule benennen, was sie suchen und worüber (`Bestand suchen`,
  `Store-Auflösung konsolidieren`).
- Write-Module benennen die Wirkung, nicht das Modul-Icon (`Beleg anlegen`,
  `Umsätze.⚙ Hinweis anhängen`).

Ein Default-Label wie `Airtable - Search Records` an einer Stelle, die für
den Gesamtfluss entscheidend ist (Dedup-Gate, Route-Entscheidung), ist ein
Audit-Befund — nicht weil der Default falsch funktioniert, sondern weil er
beim nächsten Debugging Zeit kostet, die ein sprechendes Label gespart hätte.

## Ordnerstruktur

Ordner spiegeln Projekt/Teilsystem-Zugehörigkeit (`POS Operations`,
`Website Ops`), nicht Datum oder Baureihenfolge. Ein neu Hinzukommender soll
am Ordnernamen erkennen können, zu welchem Geschäftsbereich ein Szenario
gehört, ohne jedes einzeln zu öffnen.
