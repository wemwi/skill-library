---
name: global-stress-test
description: >-
  Denk-Modus zum Härten eines bereits vorhandenen Konzepts, Entwurfs oder einer
  Architektur — Bruchstellen finden, Skalierbarkeit unter Last prüfen, Optimierungen
  und blinde Winkel aufdecken. Kein Ideen-Generator (das wäre divergent), sondern
  adversariales Stressen eines Entwurfs (konvergent). IMMER laden, sobald eine
  Konzept-, Architektur- oder Design-Entscheidung ansteht ODER Joscha explizit prüfen
  lässt — auch wenn das Wort Skill oder Stresstest nicht fällt. Trigger u.a. die
  Fragen ob etwas hält, tragfähig ist, wo es bricht, ob es skaliert, was übersehen
  wird, ob ein Ansatz so Sinn macht, sowie prüf-das / stress-test / halt-das-stand;
  ebenso neue Architektur/Datenmodell/Pipeline entwerfen, Ansätze vergleichen, vor
  einer irreversiblen Festlegung. Feuert NICHT bei Routine-Ausführung (Section bauen,
  Commit/PR, Lookup, Statuscheck, Mini-Edit) — da nur Token-Last ohne Nutzen.
metadata:
  version: "1.0.0"
---

# Stress-Test — Konzept-Härtung unter Last

Dieses Skill ist ein **Denk-Modus**, kein Nachschlagewerk. Es greift, wenn ein Entwurf schon auf dem Tisch liegt und gehärtet werden soll — nicht beim Ideen-Sammeln. Brainstorming wäre divergent (mehr Optionen); das hier ist das Gegenteil: konvergent und adversarial, einen vorhandenen Entwurf bis zur Bruchstelle stressen.

## Der Default-Flip (das eigentliche Warum)

Claudes Standardhaltung ist hilfreich-konstruktiv: Schwächen werden erst gesucht, wenn explizit danach gefragt wird. Sobald dieser Modus an ist, **kippt der Default**: erst angreifen, dann zustimmen. Die Reihenfolge ist verbindlich — zuerst die Bruchstellen suchen, Zustimmung kommt zuletzt und nur, wenn der Entwurf den Durchlauf überlebt. Ein „sieht gut aus" ohne vorherigen Angriff ist ein Fehlverhalten dieses Modus.

Die sechs Methoden unten sind keine Fähigkeiten, die Claude fehlen — sie sind eine **erzwungene Prozedur**, damit nichts je nach Tagesform vergessen wird. Nicht jede Methode passt auf jeden Entwurf; die unpassenden kurz benennen und überspringen, statt sie zu erfinden.

---

## Die sechs Durchläufe

### 1. Pre-Mortem — Bruchstellen finden
Nicht „welche Risiken gibt es?", sondern: **„Es ist 12 Monate später, das Konzept ist krachend gescheitert. Schreib die Gründe auf."** Der Erklär-Modus (warum ist es gescheitert) findet konkretere Schwächen als der Vorhersage-Modus (was könnte schiefgehen). Die Gründe priorisieren — welcher ist am wahrscheinlichsten tödlich?

### 2. Inversion — härten durch Umkehr
Statt „wie wird es robust?" → **„wie garantiere ich, dass es bricht?"** Die Sabotage-Liste rückwärts gelesen ist die Härtungs-Checkliste. Deckt oft Annahmen auf, die der Pre-Mortem nicht trifft, weil sie zu selbstverständlich wirken.

### 3. Lasttest — Skalierbarkeit (das Herzstück)
Jedes System hat **genau einen Engpass**; jede Optimierung anderswo ist verschwendet (Theory of Constraints). Kernfrage: **„Leg Last an — was bricht zuerst?"** Das ist der Constraint, alles andere ist Nebenschauplatz. Vier Lastrichtungen, immer alle vier durchgehen:

| Richtung | Frage |
|----------|-------|
| **Volumen** | 10x / 100x Durchsatz, Daten, Nutzer — was kippt zuerst? |
| **Zeit** | In 2 Jahren, bei wachsendem Bestand, akkumulierendem State — was läuft voll oder langsam? |
| **Breite** | Von 1 Stadt auf 20, 1 Store auf 100 — bricht eine Annahme, die bei klein noch hielt? |
| **Ränder** | Edge Cases, Gleichzeitigkeit, Ausfall einer Abhängigkeit — was passiert am Limit? |

**Gegengewicht (Pflicht):** Auch die andere Richtung prüfen — wird hier für Skalierung gebaut, die nie kommt? Über-Engineering ist genauso ein Robustheits-Risiko wie Unter-Engineering (YAGNI). Den Constraint härten, nicht überall prophylaktisch Gold auftragen.

### 4. Non-Goals & Alternatives — Winkel und Scope-Disziplin
Zwei Fragen, beide explizit beantworten:
- **Non-Goals:** Was ist bewusst *nicht* Ziel? Ungenannte Non-Goals sind die Einfallstür für Scope Creep.
- **Alternatives Considered:** Welche anderen Wege gäbe es, und warum ist dieser besser? Wenn keine Alternative benannt werden kann, wurde der Lösungsraum nicht abgesucht — das ist selbst ein Befund. Die stärkste Alternative in ihrer besten Form bauen (Steelman), bevor sie verworfen wird.

### 5. Second-Order — „und dann was?"
Die erste Konsequenz jeder Designentscheidung ist offensichtlich; die zweite und dritte killen Konzepte. Nach jeder tragenden Entscheidung weiterfragen: **„…und was löst das aus? …und dann?"** Bis die Kette zur Ruhe kommt oder auf ein Problem trifft.

### 6. Falsifizierbarkeit — Annahmen testbar machen
Jede tragende Annahme so formulieren, dass man sie widerlegen *könnte*: **„Woran würde ich konkret merken, dass diese Annahme falsch ist?"** Annahmen, für die es kein solches Signal gibt, sind nicht-testbare Luftschlösser — markieren, nicht durchwinken.

---

## Output-Format

Kein Fließtext-Brei. Nach den Durchläufen verdichten auf:

```
## Verdikt
[Trägt / Trägt mit Auflagen / Trägt nicht] — ein Satz Begründung.

## Bruchstellen (priorisiert)
1. [Schwerste zuerst] — was bricht, unter welcher Bedingung, wie wahrscheinlich.
2. ...

## Engpass
Was bei Last zuerst bricht (der eine Constraint) + welche Lastrichtung ihn auslöst.

## Blinde Winkel
Ungenannte Non-Goals, nicht abgesuchte Alternativen, nicht-testbare Annahmen.

## Härtung (konkret)
Was zu tun ist, damit der Entwurf hält — nach Aufwand/Wirkung sortiert.
```

Befunde kalibrieren: einen schweren Fund nicht in einer Liste mit fünf Kleinigkeiten verstecken. Wenn nichts Ernstes gefunden wird, das ehrlich sagen — aber erst, nachdem alle sechs Durchläufe wirklich liefen.

---

## Abgrenzung & Anti-Patterns

- **Verhältnis zu `global-workflow`:** Dessen Spec-Format hat eine leichte „Risiken"-Sektion als Default bei jedem Plan. Dieses Skill **ersetzt sie nicht, es vertieft sie**, wenn der Modus feuert. Die Risiken-Zeile im Spec bleibt der schnelle Default; der Stresstest ist der Tiefendurchlauf für Konzept-Entscheidungen.
- **Nicht bei Routine feuern.** Section bauen, Commit/PR, Lookup, Statuscheck, Mini-Edit brauchen keinen Stresstest — da ist er reine Token-Last und nervige Bremse.
- **Nicht zum Ja-Sager-mit-Deko verkommen.** Sechs Überschriften ausfüllen und am Ende doch „passt alles" schreiben, ohne echten Angriff, ist das Anti-Pattern, das dieses Skill verhindern soll.
- **Keine Methode erfinden, die nicht passt.** Lieber „Inversion bringt hier nichts, weil X" als eine konstruierte Pseudo-Schwäche.
- **Konzept stressen, nicht den Menschen.** Der Angriff gilt dem Entwurf, der Ton bleibt sachlich und direkt.
