# skill-library

Versionierte Heimat meiner Agent Skills für Claude (claude.ai, Claude Code, API).
Dieses Repo ist die **einzige Quelle der Wahrheit** — installierte `.skill`-Pakete sind
nur Build-Artefakte daraus.

## Aufbau

Ein Ordner pro Skill, Ordnername == `name` im Frontmatter:

```
<skill-name>/
├── SKILL.md        # Frontmatter (name, description, metadata.version) + Anleitung
├── references/     # vertiefende Docs, on-demand geladen
└── assets/         # Vorlagen, Skelette, Icons
```

## Namens-Familien

- `global-*` — projektübergreifend (z.B. `global-mcp-framework`, `global-prompt-quality`).
- `liftr-*` — das LIFTR Shopify-Theme-System (Komponenten, CSS, Sections, Blocks).
- `selectedleafs-*` — markenspezifisch (Brand-Kit, Telegram, City-Content).
- `figma-*` — Print-/Figma-Workflows.

## Versionierung

Der Agent-Skills-Standard hat kein eingebautes Versionsfeld — Git ist der Mechanismus.

- Versionsnummer in `SKILL.md` unter `metadata.version` (z.B. `"1.0.0"`).
- Diese Nummer wird **synchron zum Git-Tag** gehalten (`<skill>-vX.Y.Z` oder Repo-Tag).
- Das installierte `.skill` ist ein Artefakt eines Tags; bei einem Bump neu installieren.
- Claude Code liest Skills aus diesem Repo, idealerweise **an einem Tag gepinnt**
  (reproduzierbar, statt `main`).

## Packen & Installieren

Packen über das `skill-creator`-Skill (Ordner als ZIP-Root, `.skill`-Endung):

```bash
python -m scripts.package_skill <skill-ordner> <output-verzeichnis>
```

- **claude.ai:** das `.skill` in den Einstellungen installieren. Gleicher Name
  überschreibt die installierte Version.
- **Claude Code:** dieses Repo in den Kontext geben und den Skill-Ordner direkt lesen.

## Konvention beim Update

Bei einer Skill-Änderung: `metadata.version` erhöhen → committen → Tag setzen → neu packen →
in claude.ai neu installieren. So bleibt die Version an allen Stellen konsistent.
