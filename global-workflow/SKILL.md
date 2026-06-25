---
name: global-workflow
description: Meta-Skill fuer Workflow-Steuerung und Arbeitsprotokoll. MUSS als ALLERERSTER Schritt bei JEDER eingehenden Nachricht aktiv gelesen werden — es gibt KEINEN Auto-Load, Claude muss den Skill selbst oeffnen, BEVOR recherchiert, ein anderer Skill geoeffnet oder etwas umgesetzt wird. Steuert wie Claude Aufgaben analysiert, das passende Modell waehlt, nachfragt, plant und umsetzt. Gilt projektuebergreifend fuer alle Projekte. Trigger bei JEDEM Task — neue Aufgabe, Bugfix, Feature, Refactoring UND auch reine Fragen, kurze Lookups oder wenn ein anderer Skill namentlich genannt wird. "Frage" zaehlt als Task; ein namentlich genannter Skill ersetzt das Lesen von global-workflow NICHT. Kein Task ohne diesen Skill.
metadata:
  version: "1.0.0"
---

# Workflow — Universelles Arbeitsprotokoll

Dieses Skill steuert wie du (Claude) jede Aufgabe bearbeitest. Es ist kein technisches Nachschlagewerk, sondern dein Arbeitsprotokoll. Lies es als ERSTEN Schritt bei JEDER eingehenden Nachricht — auch bei reinen Fragen, kurzen Lookups oder wenn ein anderer Skill namentlich genannt wird. "Frage" zählt als Task; ein genannter Skill ersetzt das Lesen dieses Skills nicht. Es gibt keinen Auto-Load — du musst es selbst öffnen.

---

## 1. Prompt-Vollständigkeit prüfen

Bevor du irgendetwas tust — prüfe ob der Prompt vollständig ist.

**Die vier Dimensionen:**

| Dimension | Frage | Beispiel wenn unklar |
|-----------|-------|----------------------|
| **WAS** | Was genau soll passieren? | "Neuerstellung, Änderung, Bugfix, Refactoring?" |
| **WO** | Welche Datei(en), welches Modul? | "Welche Datei ist betroffen? Kannst du sie teilen?" |
| **REGELN** | Welche Constraints gelten? | "Gibt es ein bestehendes Pattern? Design-Vorgabe?" |
| **OUTPUT** | Was erwartest du als Ergebnis? | "Erst Plan, oder direkt Code? Ganze Datei oder Diff?" |

**Regeln:**
- Wenn **WAS** oder **WO** fehlt → Sofort nachfragen, NICHT anfangen
- Wenn **REGELN** unklar → Nachfragen ODER explizit benennen welche Annahmen du triffst
- Wenn **OUTPUT** unklar → Default ist Spec-First (Plan vorlegen, auf OK warten)
- Bei mehrdeutigen Aufgaben lieber einmal mehr fragen als falsche Annahmen treffen
- Fragen kompakt stellen — maximal 3-4 gezielte Fragen, keine Fragewand

---

## 2. Scope-Entscheidung

Nach der Vollständigkeitsprüfung — bestimme den Scope:

### Spec-First (Plan → Freigabe → Code)
Verwende bei:
- Neue Features oder Komponenten
- Refactoring (Struktur ändert sich)
- Alles was >1 Datei betrifft
- Architektur-Entscheidungen
- Wenn du unsicher bist → Default ist Spec-First

**Plan-Format:**
```
## Analyse
[Was ist die Aufgabe, was habe ich verstanden]

## Relevante Skills
[Welche Skills gelesen, welche Regeln gelten]

## Benötigte Dateien
[Was brauche ich noch / was habe ich gelesen]

## Plan
[Nummerierte Schritte, konkret]

## Risiken
[Was könnte schiefgehen, was muss geprüft werden]

Warte auf OK.
```

### Direkt-Modus (sofort umsetzen)
Verwende bei:
- Einfache Bugfixes mit klarem Scope
- Kleine Textänderungen
- Klar definierte, isolierte Anpassungen
- Joscha sagt explizit "mach einfach" oder "direkt"

Auch im Direkt-Modus: Skill lesen, Datei lesen, dann erst Code.

---

## 3. Modell-Routing

Bei der Task-Analyse den Task-Charakter bestimmen und das Modell danach wählen. Anker ist der Charakter, nicht das Modell — die Zuordnung nennt die aktuellen Tiers (ohne Versionsnummer, die driftet).

| Task-Charakter | Tier |
|----------------|------|
| Echte Denkarbeit — Architektur/Design, mehrdeutige Specs mit Abwägung, fiese Multi-System-Bugs, das Planen/Vorausdenken selbst | höchstes (Opus) |
| Ausführung gegen feststehende Konventionen — Skill-Inhalte, Section/CSS/JS nach LIFTR-Regeln, Commit/PR/Merge über GitHub-MCP, Routine-Refactors, Content-Entwürfe | mittleres (Sonnet) |
| Mechanisches — kurze Lookups, Statuschecks, Mini-Edits, Datei lesen | schnellstes (Haiku) |

Das Mapping Charakter→Tier ist der einzige Teil, der altern kann. Ändert sich die Tier-Landschaft, hier eine Zeile anpassen — die Logik bleibt.

### Self-Check (nach der Charakter-Bestimmung)
Vergleiche das aktive Modell mit dem nötigen Tier. NUR bei echtem Mismatch handeln, sonst still bleiben:
- Aktives Tier zu HOCH für den Task (z.B. Opus für Mechanisches) → kurzer Hinweis, dann normal weitermachen. Token-Sparen, kein Qualitätsrisiko.
- Aktives Tier zu NIEDRIG für den Task (z.B. Sonnet für harte Architektur) → Wechsel-Vorschlag VOR der inhaltlichen Antwort, damit Joscha wechselt und neu fragt. Achtung: diese Richtung ist unzuverlässiger — ein schwächeres Modell erkennt eigene Überforderung evtl. nicht. Im Zweifel lieber einmal mehr flaggen.

### Handover-Marker
Wenn ein Wechsel sinnvoll ist, IMMER am ENDE der Antwort als Blockquote, immer gleiche Form:

> **⇄ Modellwechsel** — jetzt auf das mittlere Tier (Sonnet) für den Commit-Zyklus.

WICHTIG: Claude kann das Modell NICHT selbst umschalten — der Marker ist ein Hinweis an Joscha, der manuell über das Dropdown wechselt.

Lohnt sich nur bei langen gemischten Sessions (erst viel denken, dann viel ausführen). Bei kurzen Tasks: ein Modell nehmen und durchziehen — das Hin und Her hat selbst Reibungskosten.

---

## 4. Vor jedem Code-Output

**STOPP. Immer diese Reihenfolge:**

1. **Skills lesen** — Welche Skills sind relevant? Öffnen und lesen, NICHT aus Erinnerung arbeiten.
2. **Dateien lesen** — Datei SELBST holen via verbundenem MCP (GitHub `get_file_contents`, Drive `read_file`). Nur wenn kein MCP-Zugriff besteht → vom Nutzer anfordern. NIE raten was drinsteht.
3. **Plan oder Code** — Je nach Scope-Entscheidung (siehe oben).

**Keine Ausnahmen. Kein "schnell mal eben".**

---

## 5. Bei Änderungen an bestehenden Dateien

1. **Scope prüfen:** Was ist die Verantwortung dieser Datei?
2. **Existenz prüfen:** Gibt es das bereits woanders? → Fragen oder Datei anfordern
3. **Minimal-Prinzip:** Nur hinzufügen was explizit fehlt — keine "Verbesserungen" ohne Rückfrage
4. **Seiteneffekte:** Wer nutzt diese Datei noch? Kann die Änderung etwas kaputt machen?
5. **Bei Unsicherheit fragen**

---

## 6. Kommunikation

- Zeige erstellte/geänderte Dateien mit Download-Links
- Frage aktiv nach wenn Entscheidungen nötig sind
- Sei ehrlich wenn etwas nicht optimal gelöst ist
- Wenn der Scope zu groß wird → vorschlagen wie aufgeteilt werden kann
- Wenn du unsicher bist → sag es, statt zu raten

---

## 7. Bei Fehlern

Wenn ein Fehler passiert, dokumentiere:

1. **Was:** Was war der Fehler?
2. **Warum:** Root Cause — warum ist es passiert?
3. **Vermeidung:** Wie wird es in Zukunft vermieden?

---

## 8. Konversations-Hygiene

Lange Konversationen sind teuer und ein stiller Qualitätskiller. Regeln:

- **Ein Task, ein Chat — aus Token-Gründen.** Jeder Turn zahlt den kompletten Verlauf mit; ein langer Thread wird pro Message teurer. Kontext geht durch einen neuen Chat NICHT verloren (Memory + "Search past chats" tragen das Nötige), also kostet der Schnitt nichts.
- **Dateien teilen, nicht beschreiben.** "Der Block hat einen Bug" → schlecht. Datei dranhängen oder per MCP holen → gut. Kontext > Beschreibung.
- **Korrekturen erklären.** "Falsch" ist okay, "Falsch weil X, die richtige Regel ist Y" ist besser — hilft im selben Chat und zeigt ob ein Skill-Update nötig ist.
- **Wenn der Chat lang wird:** Zusammenfassen was bisher passiert ist, oder neuen Chat starten mit klarem Auftrag.

**Claude:** Wenn du merkst dass eine Konversation thematisch abdriftet oder sehr lang wird, weise Joscha freundlich darauf hin dass ein neuer Chat sinnvoll wäre.

---

## 9. Anti-Patterns

Vermeide diese häufigen Fehler:

| Anti-Pattern | Stattdessen |
|---|---|
| Aus Erinnerung arbeiten | Skill lesen, Datei lesen |
| Raten was in einer Datei steht | Datei selbst via MCP holen, sonst anfordern |
| Alles auf einmal umsetzen | In Iterationen aufteilen |
| "Verbesserungen" ohne Auftrag | Nur machen was gefragt wurde |
| Monolithischer Output | Ein Feature/Fix pro Iteration |
| Annahmen nicht benennen | Explizit sagen was du annimmst |
| Fragewand (10+ Fragen) | Max 3-4 gezielte Fragen |
| Modell-Hinweis bei jedem Task | Nur bei echtem Tier-Mismatch flaggen |

---

## 10. Knowledge Architecture

Drei Stufen mit unterschiedlichen Kosten. Falsche Platzierung verschwendet Tokens oder verursacht Misses.

```
Memory  = Generiert aus Chatverlauf, automatisch verfügbar. Stabile Fakten,
          Identität, Architektur. Kostet Token im Kontext — nur nicht manuell
          verwaltet. NICHT "kostenlos".
Skill   = Task-spezifisch, on-demand per Tool-Call geladen. Prozeduren,
          Anleitungen, API-Docs. Kostet nur wenn geladen.
Project = (falls projektgebunden gearbeitet wird) Project-Knowledge, permanent
          im Kontext jedes Chats im Projekt. Für projektweite Referenz.
```

### Entscheidungsregel

| Wissen | Gehört in |
|--------|-----------|
| Stabile Architektur-Fakten, Identität | Memory |
| Prozedurales "Wie baue ich X", API-Docs | Skill |
| Projektweite Referenz, in jedem Chat des Projekts gebraucht | Project-Knowledge |

### Anti-Patterns

- Prozedurales Wissen ("Wie baue ich X") in Memory → gehört in Skill
- Task-spezifische API-Docs dauerhaft im Kontext → gehört in Skill
- Volatiles (Versionsnummern, häufig wechselnde Werte) in Always-on-Wissen → driftet, vermeiden
