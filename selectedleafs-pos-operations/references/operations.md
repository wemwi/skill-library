# Betrieb & Fehler

Wie POS-Operations verlässlich läuft: Idempotenz, Fehlerpfade, die Registry und die tragenden Views. **Generische** Muster (Error-Handler-Konvention, Blueprint-Hygiene) in **`global-make-conventions`**.

## Idempotenz-Mechanik

Kein Ereignis wird doppelt geschrieben — der Schutz sitzt in **Dedup-Schlüsseln + Match**:

- **Formel-ID als Schlüssel:** `Lieferungen.ID` = Belegnummer · `Bestandsprüfungen.ID` = `"BSP-" & Store ID & "-" & Datum` · `Belege.ID` = `"BLG-" & …` · `Bestände.ID` = `"BST-" & Store & "-" & SKU`.
- **Match vor Insert:** Make baut denselben Wert als `dedupkey` und sucht per `filterByFormula {ID} = dedupkey`. Treffer ⇒ Verdikt **„übersprungen"**, kein zweiter Datensatz.
- **Auszahlungen:** Idempotenz über **`Lexware ID`** (Voucher-UUID) — beim Erfassen entsteht der Datensatz, beim Bezahlen wird nur der Status aktualisiert.
- **City-Neuheit:** `Bestände.Erstlieferung am` ist der Dedup gegen doppelte 🌿-Posts (einmal gesetzt, nie zurück).

## Fehler-Konvention (aus dem Live-Bestand)

Drei Bausteine, situationsabhängig:

- **`builtin:Resume`** — Lesefehler **übergehen** (leeres Ergebnis weiterreichen), wenn ein fehlender Nachschlag den Lauf nicht kippen soll (Notify-Nachlesen).
- **`builtin:Break`** mit **Retry** — Zustellung wiederholen (alle Posts des Hubs, seit 11.11.2026 auch City: **3 Versuche im Abstand von 15 Minuten**), danach in die **DLQ** parken. Szenarien laufen mit `dlq:true`, `maxErrors:3`. Parken kann nur ein Szenario, das nicht mit Warten gerufen wird (`global-make-conventions` B8).
- **`builtin:Ignore`** — bewusst **fallenlassen**, wo ein Ausfall folgenlos ist („Keep original“ in `[Archive] Document PDF`: scheitert die Komprimierung, bleibt das Original am Beleg).

**Problem-Route:** harte Störungen enden als **`error.*`-Notify** im 🛑-Topic **584** (`error.sync_aborted`, `error.store_failed`, `error.lexware_orphan` …). Prinzip: **still abbrechen + melden**, nie halb schreiben und schweigen. Der **unbekannte Notify-Key** geht roh nach ⁉️ Unsortiert (nichts verwerfen).

### Upload-Belegeingang: ein Neuanstoß-Weg, der Beleg (seit 10.11.2026)

`[Dispatch] Upload PDF` ruft Kopf-Leser, `(Leftovers)` und die Worker mit Warten. Ein mit Warten gerufenes Szenario legt keine unvollständige Ausführung an, Make wiederholt dort nichts. Deshalb gibt es für diese Kette genau einen Neuanstoß:

| Fehlerort | Was passiert | Neuanstoß |
|---|---|---|
| Kopf-Leser scheitert | Hinweis am Beleg, Störung, nächster Beleg | `Belege.Hinweis` leeren (Belegtyp steht noch auf Unbekannt) |
| Aufräumen, Worker oder Start des Mahnlaufs scheitert | wie oben | `Belege.Hinweis` leeren, `Belege.Belegtyp` auf Unbekannt |
| Fehler im Mahnlauf selbst (ohne Warten gerufen) | unvollständige Ausführung in `(Reminder)` | in Make fortsetzen |
| Rechnungssuche nach der Buchung scheitert (`[Resolve] Open Invoices` oder Start des Rechnungs-Workers, seit 11.11.2026) | still übergangen, keine Meldung, kein Hinweis; der Beleg bleibt gebucht | Rechnung mit „… nicht verknüpft:“ neu anstoßen (`resource_id` = Lexware ID) |
| Fehler im Dispatcher selbst | unvollständige Ausführung im Dispatcher, der Eingang wartet, Make wiederholt | in Make fortsetzen |

- **Zurücksetzen** heißt immer dasselbe: Hinweis leeren und Belegtyp auf Unbekannt. Die View „Inbox (make.com)“ verlangt beides.
- **Nie „erneut hochladen“:** Ein zweiter Beleg desselben Dokuments bucht daneben oder endet als Duplikat.
- **Reste räumt der Neulauf weg.** Ein Abbruch mitten im Schreiben lässt Zeilen mit Status In Bearbeitung stehen, deren Positionen sofort im Bestand zählen (Rollups ohne Statusfilter). `[Process] Upload PDF (Leftovers)` entfernt sie vor dem Worker. In Bearbeitung heißt damit: läuft gerade oder ist Rest. Eine solche Zeile ohne laufenden Lauf ist ein Befund.
- **Der Hinweis am Beleg** nennt Stufe, Fehler und den Neuanstoß-Satz, derselbe Satz steht in der Zeile „Folge“ von `error.sync_aborted`.
- **Keine Direktstarts** der Worker und von `(Leftovers)` → [[scenarios]].

### Korrektur: ein Neuanstoß-Weg, der Haken (seit 11.11.2026)

`[Dispatch] Manual Action` ruft `[Process] Manual Action (Inventory Correction)` mit Warten und läuft sequenziell. Im Worker gibt es keinen Break mehr, jeder Fehler geht an den Dispatcher.

| Fehlerort | Was passiert | Neuanstoß |
|---|---|---|
| Fehler im Worker vor dem Abschluss | Zeile „KORREKTUR <Datum>: abgebrochen (…)“ in `Bestandsprüfungen.Hinweis`, Haken `Korrekturen buchen` zurück, Störung `error.sync_aborted`, nächste Prüfung | Haken neu setzen |
| Fehler im Rechnungs-Neuanstoß (Korrektur schon abgeschlossen) | Zeile „KORREKTUR <Datum>: durchgelaufen, Rechnungen nicht neu angestoßen (…)“, Störung | Rechnungen mit „Bestandsprüfung nicht verknüpft“ neu anstoßen (`resource_id` = Lexware ID), ein neuer Haken holt das nicht nach |
| Fehler im Dispatcher selbst | unvollständige Ausführung im Dispatcher, weitere Korrekturen warten | in Make fortsetzen |

- Eine halb gebuchte Korrektur setzt ohne Doppelbuchung fort (Status je Korrekturzeile, je Prüfung und Sorte höchstens eine Position) → [[scenarios]].
- **Keine Direktstarts** des Korrektur-Workers.

## Registry & Webhooks

Airtable-Webhooks **verfallen** und müssen erneuert werden. **`[Maintain] Airtable Webhooks` (6830404, tägl. 04:30)** hält die Registry frisch. Ein abgelaufener Webhook = ein Trigger, der still nicht mehr feuert.

Die Registrierungs-Liste steht im Modul „Code: Soll-Ist-Abgleich“ (nirgends sonst). Stand 06.11.2026 vier Hooks, alle auf einem View-Scope mit `changeTypes ['add']`: **Stores Inbox** · **Vertriebler Inbox** · **Belegeingang** · **Inventory amendment** (View „Korrektur (make.com)“ auf `Bestandsprüfungen`, beobachtet `Korrekturen buchen`). Beim letzten nimmt Make das gelauschte Feld selbst zurück — begründete Ausnahme zur Regel „kein gelauschtes Feld zurückschreiben“: der Record verlässt dabei die View, und `remove` ist nicht abonniert. Neuer Hook = Eintrag in der Liste, Webhook-Adresse trägt Joscha selbst ein (Zugangsschlüssel, nie durch den Chat).

## Tragende Views (Wächter)

Views sind **load-bearing**, nicht Kosmetik:

- Die **Belege-View** treibt den Gateway-Trigger von `[Dispatch] Upload PDF`.
- Die View **„Wartet auf Kundennummer“** auf `Belege` (Filter: `Hinweis` = „Wartet auf Kundennummer“, nach Alter sortiert; seit 07.11.2026) ist der **Wächter** für geparkte Sales-App-Belege eines Stores ohne `Stores.ID`. Freigabe macht die Airtable-Automation **„Belege freigeben, wenn Kundennummer da“** (Stores, Auslöser `ID` nicht leer, Skript leert den Hinweis, ältester zuerst). Ein Beleg, der hier länger als 3 Tage steht, gehört in die Make-Überwachung (Meldung ab 3 Tagen): JTL-Kunde fehlt noch oder der Store wurde abgebrochen.
- Die View **„Korrektur (make.com)“** auf `Bestandsprüfungen` (Filter: `Korrekturen buchen` ist an) treibt `[Process] Manual Action (Inventory Correction)`; dessen Modul „Load checks to correct“ liest sie zusätzlich per View-ID.
- Die **gefilterte View** ist der Circuit-Breaker der Idempotenz (nur „offene"/„neue" Datensätze werden vom Lauf gesehen).
- **Umbenennen/Umfiltern bricht den Trigger still** — Views wie Produktionscode behandeln.

## Freeze-Invarianten sind disziplin-getragen

Die drei Invarianten (append-only Versionen · INSERT-only Ereignisse · Make-/Formel-Felder unantastbar) sind **nicht strukturell erzwungen** — sie halten durch die Wächter-Views und **einen Bearbeiter**. Definierte INSERT-only-Brüche: siehe `SKILL.md`, Invariante 2. Dort steht auch die einzige Lösch-Ausnahme: `[Process] Upload PDF (Leftovers)` löscht unfertige Zeilen eines Belegs vor dessen Neulauf. Von Hand werden Ereigniszeilen weiter nicht gelöscht. Wer nur die Zeile löscht, lässt Positionen ohne Eltern zurück, die weiter zählen.

## Harte Regeln

- **Keine Testbase** — nur die Produktivbase `appiIkOaz1ID1FjfE`.
- **Altstand `appAFFDgesKLltBtd` nie anfassen** (eingefroren).
- **Ein Bearbeiter** — parallele Schreiber gefährden die Freeze-Invarianten (falsifizierbare Annahme, [[model]]/SKILL.md).
- **Make schreibt nie einen berechneten Geldwert** — nur Rohdaten + Links; gerechnet wird in Airtable-Formeln.
