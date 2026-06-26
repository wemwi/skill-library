#!/usr/bin/env python3
"""Prüft, dass die README-Inventartabelle dieselben Skills listet wie das Repo.

Die Tabelle unter `## Bereitstellung` listet jeden `<skill>/SKILL.md` mit `name`
und `Zweck`. Versionen stehen bewusst NICHT mehr in der README — SSoT ist das
SKILL.md-Frontmatter (`metadata.version`), die Historie die CHANGELOG, die
veröffentlichte Version der Release-Badge. Dadurch kann die Versionsspalte nicht
mehr driften. Dieser Check vergleicht nur noch die *Präsenz* und schlägt fehl
(Exit 1), sobald Skills und Tabelle auseinanderlaufen:

- Skill-Ordner ohne Tabellenzeile (neuer Skill nicht eingetragen)
- Tabellenzeile ohne Skill-Ordner (Skill entfernt/umbenannt)

Die `Zweck`-Spalte bleibt redaktionell und wird NICHT geprüft.

Stdlib-only, kein PyYAML — läuft ohne Setup in CI.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
README = REPO / "README.md"


def frontmatter(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    return m.group(1) if m else ""


def skill_name(fm: str, fallback: str) -> str:
    m = re.search(r"^name:\s*(\S+)", fm, re.MULTILINE)
    return m.group(1).strip().strip("\"'") if m else fallback


def actual_skills() -> set[str]:
    names: set[str] = set()
    for skill_md in sorted(REPO.glob("*/SKILL.md")):
        fm = frontmatter(skill_md)
        names.add(skill_name(fm, skill_md.parent.name))
    return names


def readme_rows() -> set[str]:
    text = README.read_text(encoding="utf-8")
    # Inventartabelle: ab "## Bereitstellung" bis zur nächsten "## "-Sektion
    section = re.search(r"## Bereitstellung\n(.*?)(?=\n## )", text, re.DOTALL)
    body = section.group(1) if section else ""
    names: set[str] = set()
    for line in body.splitlines():
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) < 2:
            continue
        name = cells[0].strip("`").strip()
        if not name or name == "Skill" or set(name) <= {"-"}:  # Header / Trennzeile
            continue
        names.add(name)
    return names


def main() -> int:
    skills = actual_skills()
    rows = readme_rows()
    errors: list[str] = []

    for name in sorted(skills - rows):
        errors.append(f"  fehlt in README: `{name}`")
    for name in sorted(rows - skills):
        errors.append(f"  README listet nicht-existenten Skill: `{name}`")

    if errors:
        print("README-Inventar driftet von den Skills im Repo ab:\n")
        print("\n".join(errors))
        print("\nFix: Tabelle unter '## Bereitstellung' in README.md angleichen.")
        return 1

    print(f"README-Inventar ist synchron ({len(skills)} Skills).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
