---
name: "global-workflow"
description: Arbeitsprotokoll fuer Joschas Projekte - wann erst planen, wann direkt umsetzen, Repo- und Skill-Aenderungen, Fehler-Postmortem, Session-Uebergabe an frischen Chat oder Claude Code. Laden bei Umsetzungsarbeit ueber mehrere Dateien, Architekturfragen, Skill-Updates und Handover. Nicht noetig bei reinen Fragen oder Lookups.
metadata:
  version: "2.0.0"
---

# Workflow — Arbeitsprotokoll

Gilt projektübergreifend. Die Grundregeln für *jede* Nachricht stehen in Joschas Präferenzen (immer im Kontext). Dieser Skill ergänzt nur, was bei echter Umsetzungsarbeit gebraucht wird.

## 1. Auftrag prüfen

| Dimension | Wenn unklar |
|---|---|
| **WAS** — Neubau, Änderung, Bugfix, Refactor? | nachfragen, nicht anfangen |
| **WO** — Datei, Modul, Szenario, Tabelle? | erst selbst suchen (Repo, MCP, Memory), dann fragen |
| **REGELN** — Pattern, Vorgabe, Skill? | Annahme explizit benennen |
| **OUTPUT** — Plan, Code, Diff, Import-JSON? | Default nach §2 |

Höchstens 3–4 gezielte Fragen auf einmal.

## 2. Plan oder direkt?

**Direkt umsetzen** — klarer Scope und billig zu korrigieren: Bugfix, Textänderung, isolierte Anpassung, mechanische Änderung (auch über mehrere Dateien). Ebenso, wenn Joscha „mach einfach" / „direkt" sagt.

**Erst Plan, auf OK warten** — Architektur-/Konzeptentscheidung, neue Komponente, Struktur-Refactor, mehrdeutige Spec, alles schwer Umkehrbare oder Geld-/Daten-kritische (Live-Szenarien, Airtable-Schema, Lexware).

Bei Architektur-/Konzeptentscheidungen zusätzlich `global-stress-test` laden — nicht bei Routine.

Plan-Format, knapp: **Analyse · Geltende Skills · Plan (nummeriert) · Risiken** → Warte auf OK.

## 3. Vor jeder Änderung

1. Relevante Skills öffnen — nicht aus Erinnerung arbeiten.
2. Dateien, Szenarien, Schema selbst holen (Repo-Checkout, MCP). Nur ohne Zugriff anfordern. Nie raten.
3. Minimal-Prinzip: nur das Gefragte, keine ungefragten „Verbesserungen".
4. Seiteneffekte prüfen: Wer nutzt das noch?

## 4. Repo-Arbeit

- **Schreiben** über einen ausgecheckten Klon mit git: Branch → Commit → PR → Merge nach `global-git-conventions`.
- **Nie** Dateiinhalte über die GitHub-API (`push_files`, `create_or_update_file`) durch den Chat schicken — der Inhalt läge doppelt im Kontext und summiert sich mit jeder Korrekturschleife auf.
- **Lesen** über die API ist okay; bei mehr als ein paar Dateien lieber auch klonen.
- Repo in der Session nicht erreichbar, oder lange Ausführungsschleife (viele Dateien, Tests, Builds) → Übergabe an Claude Code (§7).

## 5. Skill-Updates

1. Basis = installierte Version (`/mnt/skills/…/<name>/`) in den Arbeitsordner kopieren. Bei Drift-Verdacht nur SHA/Größe gegen `main` vergleichen, nicht den Inhalt laden.
2. Nur gezielte Edits — Datei nicht komplett neu tippen (Ausnahme: bewusster Neubau einer Hauptversion).
3. Kontrolle per `grep` (Version, Abschnitte), kein erneutes Komplett-Lesen.
4. `.skill` mit skill-creator `package_skill.py` bauen und ausliefern → Joscha mountet.
5. Exakt dieselben Bytes ins Skill-Repo committen (§4) und per `diff` verifizieren. Eine Edit-Quelle — gemountete Version und `main` bleiben byte-identisch.

## 6. Modell & Delegation

- Echte Denkarbeit (Architektur, Abwägung, verzwickte Multi-System-Bugs) → höchstes verfügbares Tier.
- Mechanisches innerhalb eines Tasks (Lookups, Massen-Lesen, Statuschecks) an einen Subagenten mit kleinerem Modell geben, statt den Hauptchat zu wechseln.
- Modellwechsel-Hinweis an Joscha nur bei echtem Mismatch im Hauptchat, sonst still.

## 7. Hygiene & Übergabe

- Ein Task, ein Chat. Kontext tragen Memory und Chat-Suche.
- Thread lang oder themen-gemischt → am Antwortende:

  > **🔄 Kontextwechsel** — frischer Chat sinnvoll. Übergabe-Prompt unten.

- Übergabe an Claude Code analog mit **🧰 Werkzeugwechsel**.
- Beide Male den fertigen Übergabe-Prompt nach `references/handover.md` mitliefern. Claude schaltet nie selbst um — das sind Hinweise an Joscha.

## 8. Fehler

Dokumentieren: **Was** · **Warum** (Root Cause) · **Vermeidung** — bei wiederkehrenden Fehlern Skill-Update vorschlagen.

## 9. Wissen ablegen

| Wissen | Ort |
|---|---|
| Regeln, die bei jeder Nachricht gelten | Präferenzen |
| Stabile Fakten, Identität, Projektstand | Memory |
| Prozeduren, „Wie baue ich X", API-Docs | Skill (on demand) |
| Projektweite Referenz | Project-Knowledge |

Volatiles (Versionsnummern, Modellnamen, Feature-Listen von Tools) nicht in Always-on-Wissen — driftet.
