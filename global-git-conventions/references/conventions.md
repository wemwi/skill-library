# conventions.md — README-Standard

Diese Datei ist die **verbindliche Prüfregel** für alle READMEs. Die Templates in `assets/readme/` sind nur die Materialisierung dieser Regel. Bei Abweichung gewinnt diese Datei.

## Pflichtsektionen (jede README, jeder Typ)

In dieser Reihenfolge:

1. **Titel + Version-Badge** — `# <repo-name>` mit shields.io-Badge, das den aktuellen Git-Tag spiegelt.
2. **Einzeiler** — ein `>`-Blockquote: Was & wofür, in einem Satz.
3. **`## Zweck`** — 2–3 Sätze. Welches Problem löst das Repo?
4. **`## Bereitstellung`** — Was bietet das Repo nach außen? Typ-spezifisch (Tools + Live-URL / Skill-Inventar / exportierte Oberfläche).
5. **`## Setup`** — Was muss ich setzen, damit es läuft? Typ-spezifisch.
6. **`## Gotchas`** — Stichpunkt-Logbuch. Alles, was beim letzten Mal Zeit gekostet hat.
7. **`## Versionierung`** — Verweis auf CHANGELOG + Hinweis, dass Versionierung über Conventional Commits / release-please läuft.

Keine Sektion ersatzlos streichen. Leere Sektion → mit `_(noch keine)_` markieren, statt löschen.

## Längenlimit

Das README passt auf **einen Bildschirm ohne Scrollen** (~50–70 Zeilen Richtwert). Was länger wird:
- typ-spezifische Tiefe → in den Fach-Skill (z.B. `global-mcp-framework`)
- repo-spezifische Tiefe → eigene Datei, aus dem README verlinkt

## Marker-Auto-Zonen

Felder, die aus einer anderen Quelle der Wahrheit stammen, werden zwischen Marker-Kommentaren gehalten, damit sie maschinell aktualisierbar sind, ohne den handgeschriebenen Text zu berühren:

```markdown
<!-- AUTO:foundation -->
Foundation: `v2.0.4`
<!-- /AUTO -->
```

Aktuell genutzt: `AUTO:foundation` in `*-mcp`-READMEs (zeigt den gepinnten Foundation-Tag). Der Generator dafür ist MCP-spezifisch und lebt in `global-mcp-framework`, nicht hier — hier wohnt nur das Zonen-Prinzip.

## Sprache

READMEs auf Deutsch. Fachbegriffe/Anglizismen (Container Query, Custom Property, Secret, Binding) sind als deutsche Fachsprache erlaubt.

## Gotchas richtig führen

Die `## Gotchas`-Sektion ist das wertvollste Feld fürs zukünftige Ich. Regeln:
- Jeder Eintrag ist ein konkreter, vergangener Schmerz — keine theoretischen Warnungen.
- Format: *Symptom → Ursache → Fix* in einem Stichpunkt.
- Beispiel: „`invalid_grant` nach Deploy → `GOOGLE_PRIVATE_KEY` mit literalen `\n` statt echten Zeilenumbrüchen → Secret neu setzen, Zeilenumbrüche als echte `\n` escapen."
