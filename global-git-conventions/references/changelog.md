# changelog.md — CHANGELOG & Conventional Commits

## Der wichtigste Punkt zuerst

`CHANGELOG.md` wird **nicht von Hand gepflegt**. release-please generiert und aktualisiert die Datei automatisch aus den Conventional Commits. Eine handgepflegte `[Unreleased]`-Sektion (klassisches „Keep a Changelog") würde mit release-please kollidieren und Merge-Konflikte erzeugen.

Deshalb ist `assets/CHANGELOG.template.md` bewusst nur ein **minimaler Header** — den Rest baut release-please beim ersten Release-PR.

## Wie der Changelog entsteht

1. Du mergst Feature-/Fix-PRs nach `main` (Conventional Commits / Conventional PR-Titel).
2. release-please öffnet automatisch einen Release-PR mit Titel `chore(main): release X.Y.Z`, der `CHANGELOG.md` und die Version aktualisiert.
3. Der Release-PR bleibt offen und sammelt weitere Änderungen, bis du ihn mergst.
4. Merge des Release-PR = offizielles Release: Tag wird gesetzt, GitHub-Release erstellt, Changelog committet.

## Den Commit-Vorschlag ausliefern (web-only)

Weil du web-only von Hand committest, kommt am Ende jeder Repo-Änderung ein fertiger,
copy-paste-fähiger Block — proaktiv, nicht auf Nachfrage (Pflicht-Regel in der
`SKILL.md`). So sieht er aus:

Nur Title (Normalfall, kleine Änderung):

```text
fix(auth): GOOGLE_PRIVATE_KEY-Zeilenumbrüche korrekt escapen
```

Title + Body (wenn die Änderung Kontext braucht — der Body wird zur Changelog-Notiz):

```text
feat(global-mcp-framework): Consumer-Importe auf mcp-foundation-Fassade umstellen

Consumer importieren zod und das MCP-SDK nur noch über mcp-foundation/schema
und mcp-foundation/sdk. SDK/zod nicht mehr in den Consumer-dependencies;
overrides-Pin auf explizite Version 1.29.0.
```

Regeln für den Block:

- **Title:** `<typ>(<scope>): <beschreibung>`. Scope = berührte Komponente (Skill-Name
  bei `*-library`). Beschreibung knapp, imperativ, kein Punkt am Ende.
- **Body** nur, wenn er echten Mehrwert bringt — sonst weglassen. Eine Leerzeile zwischen
  Title und Body.
- **Typ** korrekt nach Wirkung wählen (`feat`/`fix`/`docs`/`chore` …, Tabelle oben),
  damit release-please den richtigen Bump zieht.
- **Squash-Merge:** derselbe Text taugt als PR-Titel — separat nichts nötig.
- **Skill-Bump dazu:** Bei einer `*-library`-Skill-Änderung den `metadata.version`-Bump
  im SKILL.md als Teil derselben Änderung benennen (Semantik: `versioning.md`).

## Conventional Commits — das Minimal-Set

```
<typ>[optionaler scope]: <beschreibung>
```

| Typ | Bedeutung | Changelog-Wirkung |
|-----|-----------|-------------------|
| `feat:` | neues Feature | erscheint unter „Features", minor bump |
| `fix:` | Bugfix | erscheint unter „Bug Fixes", patch bump |
| `docs:` | nur Doku | i.d.R. nicht im Changelog, kein bump |
| `chore:` | Wartung, Deps, Config | i.d.R. nicht im Changelog, kein bump |

Breaking Change: `feat!:` oder ein Footer `BREAKING CHANGE: <text>` → major bump.

**Beispiele:**

Input: Tool zum Auslesen von Zeilen-Ranges ergänzt
Output: `feat(sheets): Range-Read-Tool ergänzt`

Input: Falsche Zeilenumbrüche im Private Key behoben
Output: `fix(auth): GOOGLE_PRIVATE_KEY-Zeilenumbrüche korrekt escapen`

## Squash-Merge: PR-Titel zählt

Bei Squash-Merge (Standard bei web-only-Arbeit über GitHub) wird der **PR-Titel** zur Commit-Message auf `main` — nicht die einzelnen Commits im PR. Deshalb: der **PR-Titel** muss conventional sein. Ein PR-Titel `Update stuff` verpufft; `feat: …` wird korrekt versioniert.

## Mehrere Änderungen in einem Commit

Footer nutzen, um z.B. einen Fix und ein Feature zu trennen:

```
feat: Range-Read-Tool ergänzt

fix(utils): Money-Formatierung wirft keine Exception mehr
```
