---
name: global-workflow
description: Meta-Skill fuer Workflow-Steuerung und Arbeitsprotokoll. MUSS als ALLERERSTER Schritt bei JEDER eingehenden Nachricht aktiv gelesen werden — es gibt KEINEN Auto-Load, Claude muss den Skill selbst oeffnen, BEVOR recherchiert, ein anderer Skill geoeffnet oder etwas umgesetzt wird. Steuert wie Claude Aufgaben analysiert, das passende Modell waehlt, nachfragt, plant und umsetzt. Gilt projektuebergreifend fuer alle Projekte. Trigger bei JEDEM Task — neue Aufgabe, Bugfix, Feature, Refactoring UND auch reine Fragen, kurze Lookups oder wenn ein anderer Skill namentlich genannt wird. "Frage" zaehlt als Task; ein namentlich genannter Skill ersetzt das Lesen von global-workflow NICHT. Kein Task ohne diesen Skill.
metadata:
  version: "1.5.0"
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

**Bei Konzept-/Architektur-/Design-Entscheidungen zusätzlich `global-stress-test` laden** — der härtet den Entwurf (Bruchstellen, Skalierbarkeit unter Last, blinde Winkel), bevor er in einen Plan gegossen wird. Die „Risiken"-Sektion im Plan-Format unten ist der leichte Default; der Stress-Test ist der Tiefendurchlauf und füttert genau diese Sektion, statt sie zu ersetzen. Nicht bei Routine-Ausführung feuern (Section bauen, Commit/PR, Lookup, Statuscheck, Mini-Edit).

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

## 3. Routing — zwei Fragen vor jedem Task

Zwei unabhängige Achsen. **Charakter** (wie schwer ist das Denken) steuert das Modell. **Aufwand/Volumen** (wie viel Arbeit) steuert das Werkzeug. Aufwand steuert NICHT das Modell — er steuert Werkzeug + Scope + Hygiene.

### Frage 1 — welcher Kopf? (Charakter → Modell-Tier)

Anker ist der Charakter, nicht das Modell — die Zuordnung nennt die aktuellen Tiers (ohne Versionsnummer, die driftet).

| Task-Charakter | Tier |
|----------------|------|
| Echte Denkarbeit — Architektur/Design, mehrdeutige Specs mit Abwägung, fiese Multi-System-Bugs, das Planen/Vorausdenken selbst | höchstes (Opus) |
| Ausführung gegen feststehende Konventionen — Skill-Inhalte, Section/CSS/JS nach LIFTR-Regeln, Commit/PR/Merge über GitHub-MCP, Routine-Refactors, Content-Entwürfe | mittleres (Sonnet) |
| Mechanisches — kurze Lookups, Statuschecks, Mini-Edits, Datei lesen | schnellstes (Haiku) |

Das Mapping Charakter→Tier ist der einzige Teil, der altern kann. Ändert sich die Tier-Landschaft, hier eine Zeile anpassen — die Logik bleibt.

**Der Self-Check läuft an jeder Phasengrenze neu, nicht nur im ersten Turn.** Der Charakter eines Tasks ist nicht fix — er kippt, wenn die Arbeit von einer Denkphase (Architektur, Recherche, Abwägung) in eine Ausführungsphase (Skill-Inhalt schreiben, Commit/PR/Merge über GitHub-MCP) übergeht. An genau dieser Naht den Charakter neu bewerten; der erste Turn bindet nicht. Beispiel: Upload-/Commit-Zyklus über GitHub-MCP = mittleres Tier (Sonnet), Marker davor — auch wenn die Architektur-Phase davor auf Opus lief.

**Self-Check** (nach jeder Charakter-Bestimmung): aktives Modell mit nötigem Tier vergleichen. NUR bei echtem Mismatch handeln, sonst still bleiben:
- Aktives Tier zu HOCH (z.B. Opus für Mechanisches) → kurzer Hinweis, dann normal weiter. Token-Sparen, kein Qualitätsrisiko.
- Aktives Tier zu NIEDRIG (z.B. Sonnet für harte Architektur) → Wechsel-Vorschlag VOR der inhaltlichen Antwort, damit Joscha wechselt und neu fragt. Achtung: diese Richtung ist unzuverlässiger — ein schwächeres Modell erkennt eigene Überforderung evtl. nicht. Im Zweifel lieber einmal mehr flaggen.

### Frage 2 — welches Werkzeug? (Aufwand/Medium-Fit → Chat ↔ Claude Code)

| Signal | Werkzeug |
|--------|----------|
| Wenige Dateien, Denken/Design/Content, plan→approve-Rhythmus | Chat (hier) |
| Arbeitsform riecht nach Ausführungsschleife — viele Dateien gleichzeitig, Code wirklich ausführen/testen, lange agentische Schleife | Claude Code |

**Harter Mechanik-Trigger (nicht verhandelbar).** Sobald die Ausführung Repo-Dateiinhalte durch den Chat-Kontext routet — GitHub-MCP `get_file_contents` → dekodieren → editieren → `push_files` über **mehr als 1-2 Dateien** — ist das Claude Code, **unabhängig davon, wie trivial der einzelne Edit ist**. Auslöser ist der Byte-Durchlauf durch den Kontext, nicht die Denk-Komplexität — dasselbe Prinzip wie `global-agent-framework` §12 („Bytes nie durch den Kontext routen"), hier als Selbst-Regel. Ein rein subtraktiver Sweep über 6 Dateien fühlt sich denk-trivial an; genau diese Trivialität darf NICHT auf die Werkzeugwahl durchschlagen (das ist der Kollaps von Frage 1 in Frage 2). **Chirurgische Ausnahme:** 1-2 Dateien, gezielter Edit, PR-Merge bleiben im Chat (§5.1) — und die Memory-Regel „GitHub-MCP verbunden → Zyklus selbst" gilt genau für diesen Fall: sie regelt die Commit-*Mechanik* (selbst mergen statt getrennter Blöcke), nicht das *Medium*. Ab dem Sweep gewinnt dieser Trigger, und der Zyklus läuft dann in Claude Code.

Der Wechsel läuft über einen **Migration-Prompt** (→ `references/handover.md`), nicht über einen rohen Kontextbruch — der Prompt IST der Kontexttransfer. Dadurch darf die Schwelle niedriger liegen als bei einem echten Bruch: nicht „lohnt der Aufwand?", sondern „passt die Arbeitsform?". Ehrlich bleibt: billiger als ein Bruch, aber nicht gratis — diese Session endet, Weiter-Iterieren im selben Thread geht nicht.

In Claude Code löst sich Frage 1 teilweise auf — Code wählt das Modell intern.

### Handover-Marker

Wenn ein Wechsel sinnvoll ist, IMMER am ENDE der Antwort als Blockquote, immer gleiche Form. Drei Typen, je eigenes Glyph:

> **🧠 Modellwechsel** — jetzt auf das mittlere Tier (Sonnet) für den Commit-Zyklus.

> **🧰 Werkzeugwechsel** — dieser Task will Claude Code: Repo-weiter Refactor mit Testlauf. Migration-Prompt unten.

> **🔄 Kontextwechsel** — dieser Thread ist lang/themen-gemischt, frischer Chat sinnvoll. Migration-Prompt unten (→ §8).

Beim 🧰- UND beim 🔄-Marker direkt den fertigen Migration-Prompt nach `references/handover.md` mitliefern, zum Rüberkopieren — nicht nur flaggen. Beim 🔄 ist es derselbe Migration-Prompt mit Ziel `frischer Chat` statt `Claude Code`.

WICHTIG: Claude kann weder Modell noch Werkzeug noch Thread selbst umschalten — alle drei Marker sind Hinweise an Joscha, der manuell wechselt (Modell per Dropdown, Werkzeug per neuer Code-Session, Thread per neuem Chat). Claude erkennt und sagt an, schaltet aber nie selbst um.

Lohnt sich nur bei längeren/gemischten Sessions. Bei kurzen Tasks: ein Setup nehmen und durchziehen — das Hin und Her hat selbst Reibungskosten.

**Drift:** Die Capability-Grenze zwischen Chat-mit-MCP und Claude Code altert (beide werden mächtiger) — genau wie die Tier-Nummern. Deshalb hier nur das Entscheidungs-PRINZIP pflegen (Ausführungsschleife/viele Dateien → Code), KEINE eingefrorene Feature-Liste von Claude Code. Die wäre in Wochen falsch.

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

### 5.1 Skill-Updates token-effizient

Der volle Datei-Inhalt läuft **genau einmal** durch den Kontext (beim Commit) — jeder andere Schritt vermeidet die Voll-Durchquerung:

1. **Basis = installierte Version:** `cp /mnt/skills/user/<name>/SKILL.md /home/claude/`. Nie base64 aus der GitHub-API abtippen, nie den Volltext per `curl` in den Kontext laden. Bei Drift-Verdacht nur Byte-Größe/SHA gegen `main` prüfen, nicht den Inhalt.
2. **Edits via `str_replace`** auf der lokalen Datei (nur die Diffs) — die Datei nie komplett neu schreiben.
3. **Struktur-Check via `grep`** (Version, Abschnittszahl, Marker) — kein erneutes `cat` der Vollversion zur reinen Kontrolle.
4. **Commit = ein `push_files`** mit vollem `content` (bei GitHub-MCP unvermeidbar — das ist die *eine* Durchquerung). Danach Byte-Verifikation: `curl` der raw-URL **nach `/tmp`** + `diff` gegen lokal → nur „IDENTISCH" landet im Kontext, nicht der Inhalt.
5. PR → Squash-Merge (→ `global-git-conventions`), dann `.skill`-Paket bauen und ausliefern.

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
- **Wenn der Chat lang wird:** Zusammenfassen was bisher passiert ist, oder neuen Chat starten mit klarem Auftrag. Der „klare Auftrag" ist dasselbe Artefakt wie der Migration-Prompt — gleiches Skelett, nur Ziel `frischer Chat` statt `Claude Code` (→ `references/handover.md`).

**Claude:** Wenn du merkst dass eine Konversation thematisch abdriftet oder sehr lang wird, weise Joscha freundlich darauf hin dass ein neuer Chat sinnvoll wäre — konkret über den `🔄 Kontextwechsel`-Marker (§3) am Antwortende, samt fertigem Migration-Prompt (Ziel `frischer Chat`).

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

### Inline (SKILL.md) vs. references/

Diese Datei wird bei JEDER Nachricht komplett gelesen — jede Zeile ist Always-on-Kost. Detaillierte Vorlagen, die nur selten gebraucht werden, gehören deshalb nach `references/` (on-demand geladen), nicht inline.

| Inhalt | Gehört |
|--------|--------|
| Häufig gebraucht ODER sehr kurz (Spec-Format §2, Postmortem §7) | inline in SKILL.md |
| Selten gebraucht UND detailliert (Migration/Handover-Template) | `references/` |

Vorhandene References:
- `references/handover.md` — Session-Handover-Template. Deckt beide Ziele ab: Chat→Claude Code (Werkzeugwechsel, §3) und Chat→frischer Chat (Hygiene, §8). Öffnen, wenn ein 🧰-Wechsel feuert oder ein neuer Chat gebrieft wird.

### Anti-Patterns

- Prozedurales Wissen ("Wie baue ich X") in Memory → gehört in Skill
- Task-spezifische API-Docs dauerhaft im Kontext → gehört in Skill
- Volatiles (Versionsnummern, häufig wechselnde Werte) in Always-on-Wissen → driftet, vermeiden
