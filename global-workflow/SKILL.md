---
name: "global-workflow"
description: Arbeitsprotokoll fuer Joschas Projekte - wann erst planen, wann direkt umsetzen, Repo- und Skill-Aenderungen, Fehler-Postmortem, Uebergabe an frischen Chat oder Claude Code, unbeaufsichtigte Laeufe. Laden bei Umsetzungsarbeit ueber mehrere Dateien, Architekturfragen, Skill-Updates, Handover, autonomen Laeufen (unbeaufsichtigt, bin weg) und jeder Statusuebersicht (was ist offen, Stand, Abschlussbericht). Nicht noetig bei reinen Fragen oder Lookups.
metadata:
  version: "2.9.1"
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

Vor jeder Rückfrage:
- **Nur fragen, was ich nicht selbst klären kann.** Was per MCP, Repo oder Memory nachprüfbar ist (z. B. welche Ereignisse ein Hook abonniert), selbst nachsehen.
- **Keine Fragen auf Vorrat.** Hängt eine Frage an einer noch offenen Entscheidung („nur falls …"), erst stellen, wenn die gefallen ist.
- **Folgen und Gewissheit nennen.** Pro Vorschlag ein Halbsatz: umkehrbar oder nicht, live geprüft oder Annahme.

Form der Frage (1–2 Sätze, worum es geht und warum ich frage, keine eigenen Kürzel, Entscheidung zuerst, „ok" = Vorschläge angenommen) regeln die Präferenzen.

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
5. Beim Entfernen (Task, Regel, Skill, Feld, Szenario): alle Verweise darauf suchen (Skills, Projekt-Docs, Projektanweisungen, geplante Tasks, Memory) und im selben Zug mit entfernen. Was nur Joscha entfernen kann, unter „Für Joscha" nennen.

## 4. Repo-Arbeit

- **Schreiben** über einen ausgecheckten Klon mit git: Branch → Commit → PR → Merge nach `global-git-conventions`.
- **Nie** Dateiinhalte über die GitHub-API (`push_files`, `create_or_update_file`) durch den Chat schicken — der Inhalt läge doppelt im Kontext und summiert sich mit jeder Korrekturschleife auf.
- **Lesen** über die API ist okay; bei mehr als ein paar Dateien lieber auch klonen.
- Repo in der Session nicht erreichbar, oder lange Ausführungsschleife (viele Dateien, Tests, Builds) → Übergabe an Claude Code (§7).

## 5. Skill-Updates

1. Basis = `main` von skill-library (Klon, §4), nicht die gemountete Version unter `/mnt/skills/…` — der Mount kann hinterherhinken (August 2026 hätte das bei `selectedleafs-pos-operations` fast einen Rollback ausgelöst).
2. Nur gezielte Edits — Datei nicht komplett neu tippen (Ausnahme: bewusster Neubau einer Hauptversion).
3. Kontrolle per `grep` (Version, Abschnitte), kein erneutes Komplett-Lesen.
4. `.skill` mit skill-creator `package_skill.py` bauen. Ist Joschas Chrome verbunden, selbst per Claude in Chrome mounten (Anpassungen → Skills → Skill hochladen, ersetzen); sonst ausliefern → Joscha mountet.
5. Dieselbe Änderung ins Skill-Repo committen (§4). Nach dem Mounten Abgleich per `global-setup-audit/scripts/backup_check.py` — das Mounten formatiert den Frontmatter um, verglichen werden deshalb Version, Rumpf und übrige Dateien.

## 6. Modell & Delegation

- Echte Denkarbeit (Architektur, Abwägung, verzwickte Multi-System-Bugs) → höchstes verfügbares Tier.
- Mechanisches innerhalb eines Tasks (Lookups, Massen-Lesen, Statuschecks) an einen Subagenten mit kleinerem Modell geben, statt den Hauptchat zu wechseln.
- Modellwechsel-Hinweis an Joscha nur bei echtem Mismatch im Hauptchat, sonst still.

## 7. Hygiene & Übergabe

- Ein Task, ein Chat. Kontext tragen Memory und Chat-Suche.
- **Umsetzung: Agent vor Handover.** Ist etwas entschieden und nach §10 geeignet (klar spezifiziert, umkehrbar, prüfbares Ende), startet der entscheidende Chat die Umsetzung sofort selbst als Agent. Der Auftrag an den Agenten ist das Skelett aus `references/handover.md`. Der Chat prüft das Ergebnis gegen die Definition of Done und berichtet nach §11. Kleines und Mechanisches setzt der Chat weiter direkt um (§2). Hat die Sitzung kein Agent-Werkzeug, bleibt es beim Handover.
- **Späterer Start: einmaliger geplanter Task.** Soll ein nach §10 geeigneter Lauf erst später starten, legt der Chat dafür selbst einen einmaligen geplanten Task an, statt Joscha einen Handover zu geben. Der Prompt des Tasks ist der vollständige Auftrag nach `references/handover.md`, ausgeschrieben und ohne Verweis auf diesen Chat. Für den Task gelten die Regeln unter „Geplante Tasks" in §10. Hat die Sitzung kein Werkzeug für geplante Tasks, bleibt es beim Handover.
- Ein Handover an Joscha (im Chat oder als Projekt-Doc) gibt es nur noch in drei Fällen:
  - Joschas Go fehlt noch (Geld- oder Datenkritisches, §2).
  - Die Arbeit braucht Claude Code (§4) → **🧰 Werkzeugwechsel**.
  - Das Gespräch selbst soll in einem frischen Chat weitergehen (Thread lang oder themen-gemischt) → am Antwortende:

  > **🔄 Kontextwechsel** — frischer Chat sinnvoll. Übergabe-Prompt unten.

- In diesen Fällen den fertigen Übergabe-Prompt nach `references/handover.md` mitliefern. Chat oder Werkzeug wechselt Claude nie selbst — das sind Hinweise an Joscha.

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

## 10. Unbeaufsichtigt

Gilt, wenn ein Auftrag ohne Joscha läuft: Signal „bin weg" / „läuft allein", geplanter Task, ein vom Chat gestarteter Agent (§7) oder ein Handover zur Umsetzung mit `## Bei Blocker` und maschinell prüfbarer DoD. Agent-Auftrag und Handover gelten wie „bin weg": keine Rückfragen, Lücken nach der Blocker-Regel behandeln.

**Eignung** — alle drei nötig:
- klar spezifiziert (Handover nach `references/handover.md`),
- umkehrbar: PR + CI + Auto-Merge, nur lesend oder nur vorbereitend,
- Definition of Done maschinell prüfbar.

Nicht geeignet: Live-Schreiben mit Geld- oder Datenwirkung (Make-Szenarien, Airtable-Schema, Lexware, Shopify-Bestand); Konzept, Gestaltung, Texte an Dritte; Aufgaben ohne prüfbares Ende. Bei kritischen Aufgaben läuft nur die Vorbereitung unbeaufsichtigt (z. B. Import-JSON bauen und validieren), die Ausführung macht Joscha.

**Ablauf**
1. Eignung in einer Zeile nennen.
2. Offene Fragen vorab in einem Block (§1), danach ohne Rückfragen durchlaufen.
3. Nach „bin weg" / „läuft allein" keine Fragen mehr: naheliegendste Lesart nehmen und im Bericht nennen.

**Blocker:** nicht raten, nicht anhalten — Entwurf (Draft-PR) mit Begründung, weiter mit dem Rest. Ausnahme: nicht umkehrbare Entscheidung, die in beide Richtungen gehen kann → vorbereiten, Entscheidung darlegen, dort stoppen.

**Warten**
- Innerhalb eines Laufs (CI, Merge, Release, Deploy): Hintergrund-Wächter — Shell-Befehl im Hintergrund mit Abbruchbedingung und Zeitgrenze (höchstens 2 h). Er weckt die Session, sobald die Bedingung erfüllt ist.
- Erinnerungen (send_later) nur für längere Pausen. Sie kommen erst an, wenn in der Session kein Turn läuft; der Termin ist der früheste Zeitpunkt, kein fester.
- Nach höchstens 3 Erinnerungen hintereinander ohne Fortschritt stoppen und Abschlussbericht mit dem Stand schreiben.
- Parallel nur unabhängige Stränge (§6). Hängt ein Strang am Ergebnis eines anderen, stößt der liefernde Strang den Folgeschritt am Ende selbst an (Abruf-Task); der wartende fragt nicht per Erinnerung nach.
- „Zugestellt" ist kein Erfolg. Ein Lauf ist erst mit Abschlussbericht beendet, auch bei Abbruch wegen des Limits.

**Für Joscha:** Handgriffe, die nur er kann (`.skill` mounten, Branches löschen, Repo-Einstellungen, Freigaben nach Sicherheitsregeln), nicht einzeln erfragen, sondern in dieser Liste bündeln. Vorher prüfen, was per Claude in Chrome selbst geht, wenn Joschas Chrome verbunden ist: Skill mounten und Projektanweisungen ändern sind erprobt.

**Abschlussbericht:** DoD Punkt für Punkt erfüllt / nicht erfüllt · Abweichungen und Blocker · Für Joscha · Links (PRs). Im Statusformat nach §11. Danach den umgesetzten Handover aus den Projekt-Docs löschen, sonst führt ihn ein späterer Chat erneut aus. Bleibt etwas offen, bleibt er stehen, gekürzt auf das Offene.

**Geplante Tasks**
- Das Werkzeug für geplante Tasks kann keine Konnektoren auswählen, neue Tasks erhalten alle. Bei automatischer Freigabe die nötigen Konnektoren unter „Für Joscha" nennen („in den Task-Einstellungen nur … behalten").
- Ob ein Task am Projekt hängt, zeigt nur die Aufgabenliste des Projekts im Browser (Projektseite, „Geplant"): `list_triggers` nennt kein Projekt, auch nicht mit `include_completed`. Ein aus einem Projekt-Chat angelegter Task stand dort, ohne dass ihn jemand zuordnen musste (14.11.2026). Nachsehen, wenn Joschas Chrome verbunden ist; sonst im Bericht „nicht geprüft" schreiben und keinen Handgriff daraus machen. Braucht der Task Projekt-Docs und fehlt er in der Liste: unter „Für Joscha" (Task dem Projekt zuordnen). Bis dahin setzt der Prompt die Docs nicht voraus.

**Tokens:** §6; unabhängige Stränge parallel in eigenen Worktrees.

## 11. Status zeigen

Gilt für jede Statusübersicht („was ist offen?“, „Stand?“) und für jeden Abschlussbericht.

- **Ein Punkt, eine Zeile**, mit Kennung und Namen (`B7 Webhook-Wartung`). Nie zu Gruppen zusammenfassen („B1 bis B6 zurückgestellt“).
- **Legende:** ✅ erledigt · 🔶 teilweise · ⏳ wartet auf einen Lauf oder Joschas Go · ⏸ zurückgestellt · ➖ entfällt · ❓ Joschas Entscheidung. Die Legende steht unter der Liste.
- **❓ zuerst**, je mit Vorschlag. Danach nach Herkunft gegliedert (Audit-Abschnitt, Spec, Bau-Runde).
- **Statusdatei je Thema** im Projekt (`claude/status-<thema>.md`): die vollständige Liste, zurückgestellte Punkte nach Szenario oder Komponente geordnet, damit ein Import die offenen Punkte seines Szenarios mitnimmt. Jeder Abschlussbericht und jeder Handover schreibt sie fort.
- **Im Abschlussbericht** nur, was sich geändert hat, dazu alle ❓ und ⏳ und der Verweis auf die Statusdatei. Die ganze Liste, wenn Joscha nach dem Stand fragt.
- **Jeder offene Punkt an seiner Quelle geprüft**, bevor er als ⏳ oder ❓ erscheint: Stand-Abschnitt der Spec, Live-Szenario, Laufliste. Nie aus einer älteren Liste oder einem „Offen“-Block übernehmen, der einen späteren Stand nicht kennt. Nicht prüfbar → so kennzeichnen.
