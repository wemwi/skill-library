#!/usr/bin/env python3
"""Prüft, dass die README-Inventartabelle den tatsächlichen Skills im Repo entspricht.

Drift-Quelle: Die Tabelle unter `## Bereitstellung` dupliziert `name` und
`metadata.version` aus jedem `<skill>/SKILL.md` von Hand. Dieser Check vergleicht
beide Seiten und schlägt fehl (Exit 1), sobald sie auseinanderlaufen:

- Skill-Ordner ohne Tabellenzeile (neuer Skill nicht eingetragen)
- Tabellenzeile ohne Skill-Ordner (Skill entfernt/umbenannt)
- Versions-Zelle != metadata.version (Version gebumpt, README nicht nachgezogen)

Die `Zweck`-Spalte bleibt redaktionell und wird NICHT geprüft.

Stdlib-only, kein PyYAML — läuft ohne Setup in CI.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
README = REPO / "README.md"
NO_VERSION = "–"  # En-Dash, wie in der Tabelle für Skills ohne metadata.version


def frontmatter(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    return m.group(1) if m else ""


def skill_name(fm: str, fallback: str) -> str:
    m = re.search(r"^name:\s*(\S+)", fm, re.MULTILINE)
    return m.group(1).strip().strip("\"'") if m else fallback


def skill_version(fm: str) -> str:
    # metadata.version: eingerückte version-Zeile innerhalb des metadata-Blocks
    m = re.search(r"^\s+version:\s*[\"']?([0-9][0-9.]*)", fm, re.MULTILINE)
    return m.group(1) if m else NO_VERSION


def actual_skills() -> dict[str, str]:
    skills: dict[str, str] = {}
    for skill_md in sorted(REPO.glob("*/SKILL.md")):
        fm = frontmatter(skill_md)
        name = skill_name(fm, skill_md.parent.name)
        skills[name] = skill_version(fm)
    return skills


def readme_rows() -> dict[str, str]:
    text = README.read_text(encoding="utf-8")
    # Inventartabelle: ab "## Bereitstellung" bis zur nächsten "## "-Sektion
    section = re.search(r"## Bereitstellung\n(.*?)(?=\n## )", text, re.DOTALL)
    body = section.group(1) if section else ""
    rows: dict[str, str] = {}
    for line in body.splitlines():
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) < 2:
            continue
        name = cells[0].strip("`").strip()
        version = cells[1].strip("`").strip()
        if not name or name == "Skill" or set(name) <= {"-"}:  # Header / Trennzeile
            continue
        rows[name] = version
    return rows


def main() -> int:
    skills = actual_skills()
    rows = readme_rows()
    errors: list[str] = []

    for name, version in skills.items():
        if name not in rows:
            errors.append(f"  fehlt in README: `{name}` (Version `{version}`)")
        elif rows[name] != version:
            errors.append(
                f"  Version weicht ab: `{name}` — SKILL.md `{version}` vs README `{rows[name]}`"
            )
    for name in rows:
        if name not in skills:
            errors.append(f"  README listet nicht-existenten Skill: `{name}`")

    if errors:
        print("README-Inventar driftet von den Skills im Repo ab:\n")
        print("\n".join(sorted(errors)))
        print("\nFix: Tabelle unter '## Bereitstellung' in README.md angleichen.")
        return 1

    print(f"README-Inventar ist synchron ({len(skills)} Skills).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
