# Handover — Session-Übergabe

Vorlage für die Übergabe an eine **frische Session**, die diesen Chat nie gesehen hat. Zwei Ziele, gleiches Skelett:
- **Claude Code** — ausgelöst durch einen 🧰-Werkzeugwechsel (global-workflow §3)
- **frischer Chat** — ausgelöst durch Konversations-Hygiene (global-workflow §8, „ein Task, ein Chat")

## Leitgedanke

Ein Handover ist das **Gegenteil einer Zusammenfassung.** Eine Zusammenfassung komprimiert, was passiert ist. Ein Handover projiziert nach vorn: er trägt nur den *entschiedenen Zustand*, nicht die Herleitung. Das Denken ist HIER passiert — die neue Session darf settled questions nicht neu aufrollen.

## Prinzipien (in Reihenfolge der Wichtigkeit)

1. **Entschieden-Zustand, nicht Deliberation.** Outcomes nennen, nicht den Abwägungsweg. „Architektur steht: X. Nicht neu abwägen, umsetzen."
2. **Selbst-tragend, keine Chat-Referenzen.** Kein „wie oben besprochen", kein „die Datei die wir geändert haben". Die neue Session sieht kein „oben". Alles als konkreter Anker: Repo, Branch, exakte Pfade.
3. **Definition of Done / Stop-Grenze.** Besonders bei Ziel `Claude Code` (agentische Schleife): „Fertig wenn Tests grün + PR offen. Nicht weiter optimieren." Sonst wandert die Session.
4. **Negative Scope.** „Y ist bereits erledigt, nicht anfassen." Verhindert redundante oder zerstörerische Re-Arbeit.

**Nicht** mit reinpacken: Transcript-Dump (kuratierte Entscheidungen schlagen Verlauf) und Duplikate aus anderen Skills. Bei REGELN nur *nennen*, welche Skills drüben gelten — die lädt die neue Session selbst. DRY.

## Skelett

Die Felder WAS/WO/REGELN/OUTPUT sind die Prompt-Vollständigkeit aus global-workflow §1. **Entschieden** und **Bereits erledigt** sind die zwei handover-spezifischen Felder, die den eigentlichen Wert ausmachen.

```
# Handover → [Claude Code | frischer Chat]

## Auftrag (WAS)
[Ein Satz: was gebaut/geändert wird]

## Repo & Dateien (WO)
Repo: …   Branch: …
Betroffen: [exakte Pfade — keine „die Datei von vorhin"]

## Entschieden (nicht neu abwägen)
[Outcomes aus diesem Chat: Architektur, Patterns, Namen, Versionsentscheidung]

## Bereits erledigt / nicht anfassen
[Negative Scope: was steht schon, was darf nicht verändert werden]

## Geltende Skills (REGELN)
[Nur nennen, nicht zitieren — z.B. global-git-conventions + taskspezifischer Skill]

## Definition of Done (OUTPUT)
[Stop-Kriterium + Verifikation — z.B. „Tests grün, PR gegen main offen,
 Read-back per Blob-SHA". Bei Ziel Claude Code zwingend, sonst wandert die Session.]
```

## Ausfüll-Checks

- Ist jeder Pfad ein echter Anker (Repo + Branch + Datei), oder steckt noch ein „oben/vorhin" drin? → auflösen.
- Steht unter **Entschieden** ein Outcome oder eine Abwägung? → auf das Outcome reduzieren.
- Gibt es eine harte Stop-Grenze? Ohne sie schleift eine Code-Session weiter als gewollt.
- Wird ein Skill-Inhalt zitiert statt nur genannt? → auf den Namen kürzen.
