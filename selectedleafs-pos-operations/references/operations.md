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
- **`builtin:Break`** mit **Retry** — Zustellung wiederholen (Ops/Vertriebler-Posts: **3× / 15 s**), danach in die **DLQ** parken. Szenarien laufen mit `dlq:true`, `maxErrors:3`.
- **`builtin:Ignore`** — bewusst **fallenlassen**, wo ein Ausfall folgenlos ist (öffentlicher **City-Broadcast**).

**Problem-Route:** harte Störungen enden als **`error.*`-Notify** im 🛑-Topic **584** (`error.sync_aborted`, `error.store_failed`, `error.lexware_orphan` …). Prinzip: **still abbrechen + melden**, nie halb schreiben und schweigen. Der **unbekannte Notify-Key** geht roh nach ⁉️ Unsortiert (nichts verwerfen).

## Registry & Webhooks

Airtable-Webhooks **verfallen** und müssen erneuert werden. **`[Maintain] Airtable Webhooks` (6830404, tägl. 04:30)** hält die Registry frisch. Ein abgelaufener Webhook = ein Trigger, der still nicht mehr feuert.

Die Registrierungs-Liste steht im Modul „Code: Soll-Ist-Abgleich“ (nirgends sonst). Stand 06.11.2026 vier Hooks, alle auf einem View-Scope mit `changeTypes ['add']`: **Stores Inbox** · **Vertriebler Inbox** · **Belegeingang** · **Inventory amendment** (View „Korrektur (make.com)“ auf `Bestandsprüfungen`, beobachtet `Korrekturen buchen`). Beim letzten nimmt Make das gelauschte Feld selbst zurück — begründete Ausnahme zur Regel „kein gelauschtes Feld zurückschreiben“: der Record verlässt dabei die View, und `remove` ist nicht abonniert. Neuer Hook = Eintrag in der Liste, Webhook-Adresse trägt Joscha selbst ein (Zugangsschlüssel, nie durch den Chat).

## Tragende Views (Wächter)

Views sind **load-bearing**, nicht Kosmetik:

- Die **Belege-View** treibt den Gateway-Trigger von `[Dispatch] Upload PDF`.
- Die View **„Korrektur (make.com)“** auf `Bestandsprüfungen` (Filter: `Korrekturen buchen` ist an) treibt `[Process] Correction (Inventory)`; dessen Modul „Load checks to correct“ liest sie zusätzlich per View-ID.
- Die **gefilterte View** ist der Circuit-Breaker der Idempotenz (nur „offene"/„neue" Datensätze werden vom Lauf gesehen).
- **Umbenennen/Umfiltern bricht den Trigger still** — Views wie Produktionscode behandeln.

## Freeze-Invarianten sind disziplin-getragen

Die drei Invarianten (append-only Versionen · INSERT-only Ereignisse · Make-/Formel-Felder unantastbar) sind **nicht strukturell erzwungen** — sie halten durch die Wächter-Views und **einen Bearbeiter**. Definierte INSERT-only-Brüche gibt es **zwei**: den Zahlungs-Status über `[Sync] Lexware Payments` und die Korrektur über `[Process] Correction (Inventory)` (legt Positionen einer bestehenden Bestandsprüfung nach, setzt `Status`, `Hinweis`, `Korrekturen buchen`; seit 06.11.2026). In `Bestandsprüfungskorrekturen` schreiben Make und Hand: Make legt an und setzt Offen/Gebucht/Abgelehnt, die Hand ergänzt die Zahlen und setzt Verworfen.

## Harte Regeln

- **Keine Testbase** — nur die Produktivbase `appiIkOaz1ID1FjfE`.
- **Altstand `appAFFDgesKLltBtd` nie anfassen** (eingefroren).
- **Ein Bearbeiter** — parallele Schreiber gefährden die Freeze-Invarianten (falsifizierbare Annahme, [[model]]/SKILL.md).
- **Make schreibt nie einen berechneten Geldwert** — nur Rohdaten + Links; gerechnet wird in Airtable-Formeln.
