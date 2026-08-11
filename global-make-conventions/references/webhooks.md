# B6 — Webhook-Lebenszyklus

## Spec-Änderungen wirken erst nach Löschen + Neuanlage

Bei Gateway-Webhooks auf externe Systeme (z.B. Airtable-Automationen, die
per HTTP-API einen Hook registrieren) gilt: eine Änderung an Feldern,
`changeTypes` oder Scope wirkt NICHT automatisch, nur weil die
zugrundeliegende Konfiguration (Code, Registry-Eintrag, SOLL-Liste)
aktualisiert wurde. Ein „Refresh" eines bestehenden Hooks behält dessen
ursprünglich registrierte Spec bei.

**Belastbares Deploy-Muster:** alten Hook löschen → Registry/Konfiguration
mit der neuen Spec laufen lassen → neuer Hook wird mit der aktuellen Spec
angelegt. Ein reiner Update-Call auf den bestehenden Hook reicht nicht.

Dies ist keine theoretische Vorsicht — ein dokumentierter Fixversuch (siehe
`loops.md`, Realfall Phantom-Execution) schlug beim ersten Anlauf fehl,
*obwohl* die neue Spec im System korrekt hinterlegt war, weil der
bestehende Hook nur „geupdated", nicht neu angelegt wurde.

## Webhook-URL ist ein Credential

Eine Gateway-Webhook-URL trägt implizit die Berechtigung, das Szenario
auszulösen — wer die URL hat, kann es aufrufen. Anders als Connection-
Credentials wird sie von den Make-Tools (`hooks_get`/`hooks_list`)
unredigiert zurückgegeben.

**Regel:** die URL nie durch einen Agent-/Chat-Kontext holen und an die
Person zurückspiegeln, um einen echten externen Aufruf zu simulieren oder zu
verifizieren. Stattdessen die Person auf die Quelle verweisen (Trigger-Modul
in der Make-UI, oder ihr eigener Tool-Call außerhalb der Session) — sie holt
und nutzt die URL selbst.
