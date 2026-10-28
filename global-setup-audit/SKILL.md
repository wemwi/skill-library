---
name: global-setup-audit
description: >-
  Regelmäßige Prüfung von Joschas Claude-Setup — Skills, Konnektoren/MCP-Server,
  Präferenzen, Memory, geplante Tasks und Projekte — auf Zeitgemäßheit, Konsistenz
  und Funktion. Liefert einen Prüfbericht mit Befunden und Vorschlägen und ändert
  selbst nichts. Laden beim monatlichen Setup-Audit (geplanter Task oder Projekt
  Setup-Audit) und immer, wenn Joscha fragt, ob ein Skill, Konnektor oder eine Regel
  noch zeitgemäß ist, eher stört, veraltet ist oder sich mit etwas überschneidet,
  oder ob das Backup-Repo skill-library vollständig und aktuell ist, oder wie viele
  Actions-Minuten und Branches die GitHub-Repos verbrauchen bzw. ansammeln.
  Nicht für die Umsetzung der Änderungen selbst — dafür global-workflow.
metadata:
  version: "1.2.0"
---

# Setup-Audit — das Claude-Setup prüfen

Gegenstand ist die Werkzeugkiste, nicht die Kundenarbeit. Der Audit **prüft und berichtet**. Was geändert wird, entscheidet Joscha; umgesetzt wird danach gezielt nach `global-workflow`.

Leitfrage: **Hilft das noch, oder stört es inzwischen?** Ein Skill kann in sich stimmig und trotzdem veraltet sein, weil sich die Umgebung um ihn herum geändert hat.

## 1. Referenzstand erheben (immer zuerst)

Ohne Referenzstand prüft Claude gegen das eigene Trainingswissen, und das ist selbst veraltet.

1. **Letzten Bericht holen** (§6). Gibt es keinen, ist es der Erstlauf.
2. **Umgebung heute erfassen:**
   - **Skills:** Name, Version, Zeilen, Länge der Beschreibung, per Skript aus `/mnt/skills/*/` — nicht jede Datei lesen.
   - **Skill-Liste der Session:** Welche Skills erscheinen dort ohne Beschreibung? Die Beschreibung in der Datei ist nicht automatisch die, die Claude sieht. Wird die Liste zu lang, fallen Beschreibungen weg, und der Trigger greift nicht mehr.
   - **Konnektoren/MCP-Server:** verfügbare Server, Zahl der Tools, Hinweise in den Server-Instructions (z. B. „deprecated").
   - **Backup-Abgleich:** `wemwi/skill-library` klonen (öffentlich, `git clone --depth 1`) und `python3 scripts/backup_check.py --mount /mnt/skills/plugins --repo <klon>` laufen lassen. Die Tabelle kommt unverändert in den Bericht (§5).
   - **Repo-Check:** alle Repos per `list_repos` holen, private per `add_repo` (Lesezugriff) anhängen, dann `python3 scripts/repo_check.py <repo> …` — Actions-Läufe und geschätzte Minuten je Repo, Abweichungen von den CI-Sparregeln, Branch-Hygiene. Die Tabelle kommt unverändert in den Bericht (§5).
   - **Geplante Tasks:** Liste mit letzter Ausführung.
   - **Produktstand:** Anthropic-Release-Notes und Claude-Hilfe seit dem letzten Lauf (WebSearch; Produktfakten über `product-self-knowledge`). Neue Fähigkeiten, Umbenennungen, Abkündigungen.
3. **Mit dem letzten Inventar vergleichen** → „Was hat sich geändert". Das bestimmt den Fokus (§2).

## 2. Prüfumfang

Nicht in jedem Lauf alle Skills komplett lesen, das ist zu teuer. Tief geprüft werden:

- alle `global-*`-Skills und `selectedleafs-pos-operations` (wirken übergreifend),
- jeder Skill, den eine Änderung aus §1.3 berührt (neues Tool, abgekündigter Server, neue Produktfunktion),
- eine **rotierende Familie**: LIFTR → Make → selectedleafs → Anthropic-Standard-Skills. Der Bericht hält fest, welche dran war; der nächste Lauf nimmt die nächste. Große Familien an Subagenten verteilen.

Alle übrigen Skills laufen nur über das Inventar (Version, Größe, Beschreibung sichtbar).

## 3. Prüfkatalog

### Skills

1. **Lade-Mechanik** — Hat er eine Beschreibung, und erreicht sie Claude in der Session-Liste? Feuert der Trigger bei den gemeinten Aufgaben — und nicht bei allen anderen?
2. **Annahmen über die Umgebung** — Stimmen Werkzeuge, Pfade, Zugriffswege, Aussagen wie „der Chat kann X nicht"? Abgleich mit dem Referenzstand.
3. **Modell- und Produktstand** — Kennt er aktuelle Modelle, Funktionen, Artifact-Typen? Hart verdrahtete Modell- oder Versionsnamen sind schon ein Befund.
4. **Standardregeln** — Bremst eine Default-Regel mehr, als sie schützt? (Beispiel: Spec-First als Default im alten `global-workflow`.)
5. **Tote Verweise** — auf Skills, Dateien, Tools oder Felder, die es nicht mehr gibt.
6. **Richtiger Ort** — Was immer gilt, gehört in die Präferenzen; Seltenes in `references/`; Volatiles nirgends in Always-on-Wissen.
7. **Konsistenz** — Widerspricht er einem anderen Skill, den Präferenzen oder dem Memory-Stand? Überschneidet er sich mit einem anderen Skill (gleicher Trigger, doppelte Regeln)?
8. **Backup** — Ergebnis von `scripts/backup_check.py` (§1.2) bewerten. Nie Dateien byte-genau vergleichen: Das Mounten formatiert den Frontmatter um, ein Byte-Vergleich meldet Scheinabweichungen. Das Skript vergleicht Version, Rumpf und übrige Dateien.

   | Status | Stufe | Bedeutung |
   |---|---|---|
   | Inhalt abweichend, gleiche Version | 🔴 | geändert ohne Versions-Bump — welcher Stand gilt, ist unklar |
   | Mount veraltet | 🔴 | im Repo liegt eine neuere Version, gemountet läuft die alte |
   | Backup veraltet | 🟡 | gemountete Version fehlt im Repo |
   | kein Backup | 🟡 | eigener Skill ohne Kopie im Repo |
   | nur im Repo | 🟡 | archivieren oder wieder mounten — Joscha entscheidet |
   | Dateien abweichend | ⚪ | z. B. Assets nur im Repo |
   | extern | — | fremder Skill mit eigenem Upstream (`metadata.author`), gehört nicht ins Backup |

### Konnektoren & MCP-Server

- **Erreichbar?** Ein billiger Lese-Aufruf pro Server (ping, whoami, list) — nie schreibend.
- **Abgekündigt oder ersetzt?** Server-Instructions und Release-Notes.
- **Noch gebraucht?** Verweist ein Skill oder ein Arbeitsbereich darauf?
- **Abgleich mit Skills:** neue Tools, die ein Skill kennen sollte; Tools, die ein Skill nennt, die aber fehlen.

### Präferenzen & Memory

- Präferenz-Zeilen: noch gültig, widerspruchsfrei zu den Skills, nicht doppelt?
- Memory: abgeschlossene Bereiche, veraltete Stände, Widersprüche zu Skills.
- Nur berichten — der Audit ändert keine Memory-Dateien.

### Geplante Tasks

- Läuft er (letzte Ausführung ok)? Wird er noch gebraucht? Gibt es Doppelte?

### Repos

Maßstab ist `global-git-conventions` (`references/ci.md`, `references/settings.md`). Bewertung des `repo_check.py`-Ergebnisses:

| Befund | Stufe |
|---|---|
| Privates Repo über dem Monatskontingent (2.000 Free / 3.000 Pro) oder ein Workflow mit hohem Windows/macOS-Anteil | 🔴 |
| Verstoß gegen eine Sparregel in einem privaten Repo (Timeout, Abbruch, Doppellauf, `workflow_run`, Polling-Cron) | 🟡 |
| „Auto-Löschen" aus oder > 20 gemergte Branches | 🟡 — Häkchen setzt Joscha; Altbestand per Workflow „Branch-Aufräumen" in `skill-library` |
| Branches ohne PR, offene Renovate-PRs, Abweichungen in öffentlichen Repos | ⚪ |

Vergleich mit dem letzten Lauf: steigen Läufe oder Minuten eines Repos deutlich, die Ursache benennen (welcher Workflow, welches Ereignis).

### Projekte (manuell)

Claude kann Anweisungen und Dateien anderer Projekte nicht lesen. Der Bericht enthält dafür eine kurze Checkliste für Joscha: Anweisungen aktuell? Wissen veraltet? Memory-Einstellung passend?

## 4. Bewerten

| Stufe | Bedeutung |
|---|---|
| 🔴 stört | lenkt Claude aktiv falsch oder blockiert (falscher Trigger, Widerspruch, toter Pflichtschritt) |
| 🟡 veraltet | stimmt nicht mehr, schadet aber nur im Einzelfall |
| ⚪ Kosmetik | Stil, Länge, Formulierung — nur nennen, wenn der Aufwand klein ist |

Ein 🔴 nicht zwischen fünf ⚪ verstecken. Findet sich nichts Ernstes, das so sagen.

Befunde unter „Entschieden" im letzten Bericht nicht erneut melden — außer der Grund für die Entscheidung ist entfallen.

## 5. Bericht

Name-first: Skills, Konnektoren, Szenarien, Tabellen beim Namen nennen, nie per ID.

```
# Setup-Audit <Monat Jahr>

## Kurzfazit
2–3 Sätze: Zustand, wichtigster Befund.

## Seit dem letzten Lauf geändert
Umgebung/Produkt: … → betroffene Skills: …

## Befunde
### 🔴 <Gegenstand> — <ein Satz>
Was · Warum es stört · Vorschlag · Aufwand (S/M/L)

## Manuell zu prüfen
Projekte: …

## Entschieden (nicht erneut melden)
<Befund> — <Joschas Entscheidung, Datum>   ← aus dem letzten Bericht übernehmen und ergänzen

## Inventar
Skills: Name · Version · Zeilen · Beschreibung sichtbar ja/nein
Backup: Tabelle aus scripts/backup_check.py
Repos: Tabelle aus scripts/repo_check.py
Konnektoren: Name · erreichbar · Hinweise
Geplante Tasks: Name · letzte Ausführung
Tief geprüft: … · Nächste Rotation: …
```

Das Inventar ist der Referenzstand für den nächsten Lauf — immer vollständig ausfüllen.

## 6. Ablage

- Bericht als Doc „Setup-Audit <Monat Jahr>" (Docs-Typ; ohne ihn als Markdown-Datei senden).
- Der nächste Lauf findet den letzten Bericht über die Artifact-Liste anhand dieses Titelmusters.
- Unbeaufsichtigter Lauf: Bericht fertigstellen, Kurzfazit per Nachricht schicken, keine Rückfragen.

## Anti-Patterns

- **Selbst umbauen.** Auch offensichtliche Fixes nur vorschlagen.
- **Gegen Trainingswissen prüfen** statt gegen den erhobenen Referenzstand.
- **Alles lesen.** Inventar + Fokus + Rotation reichen.
- **Schreibende Test-Aufrufe** an Konnektoren oder Repos (keine Workflows starten, keine Branches löschen).
- **Befund-Inflation.** Zehn Kosmetik-Punkte sind kein Audit.
