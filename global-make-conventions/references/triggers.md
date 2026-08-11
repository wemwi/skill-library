# B4 — Trigger-Architektur

## Event vor Polling

Instant-/Webhook-Trigger sind schneller und operations-günstiger als
Polling. Der Tradeoff: sie sind nach dem Deployment schwerer end-to-end zu
verifizieren, weil ein simulierter Testlauf den echten Trigger-Pfad nicht
originalgetreu durchläuft. Trotzdem gilt die Grundregel — Event-Trigger vor
Polling, wo die Quelle es anbietet —, und die Verifikation läuft über einen
echten externen Request, nicht über einen Ersatz-Testlauf.

## Kein Airtable-„Watch Records"-Trigger

Airtables nativer Watch-Records-Trigger arbeitet auf Polling-Basis mit
eigenen Zuverlässigkeitsproblemen bei schnell aufeinanderfolgenden
Änderungen. Die belastbare Alternative: ein Gateway-Webhook, den eine
Airtable-Automation beim relevanten Ereignis aktiv aufruft — Airtable meldet
sich, statt dass Make pollt.

## Kein berechnetes Feld als Trigger-Cursor

Formel- oder Rollup-Felder (`Zuletzt bearbeitet`, ein berechnetes
„Erstellt am") sind als Cursor für einen Trigger ungeeignet: sie können bei
der eigentlich relevanten Änderung ausbleiben (das Feld bewegt sich nicht
bei jedem Schreibzugriff) oder bei der Anlage eines Datensatzes gar nicht
zuverlässig feuern. Das Resultat ist ein lautloser Totalausfall — der
Trigger bleibt technisch aktiv, meldet aber nie wieder etwas.

**Belastbare Alternative:** ein editierbares Feld, das genau bei dem einen
gewünschten Ereignis gesetzt wird und von keinem nachgelagerten Prozess
zurückgeschrieben wird (siehe `loops.md` für die Verzahnung mit
Schleifenfreiheit — dieselbe Feldwahl entscheidet über beide Fragen).
