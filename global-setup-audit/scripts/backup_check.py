#!/usr/bin/env python3
"""Gleicht die gemounteten Skills mit dem Backup-Repo (wemwi/skill-library) ab.

Das Mounten formatiert den Frontmatter um (Quotes, gefaltete Beschreibung). Ein
Byte-Vergleich meldet deshalb Abweichungen, die keine sind. Verglichen werden:
Version (metadata.version), Rumpf (SKILL.md ohne Frontmatter) und alle übrigen
Dateien per Hash.

Geprüft werden nur Skills, die Joscha selbst hochgeladen hat (manifest.json:
source == "plugin"). Skills mit metadata.author (z. B. Make, Airtable) gelten
als extern: Sie haben ein eigenes Upstream und gehören nicht ins Backup.

Aufruf:
  python3 backup_check.py --mount /mnt/skills/plugins --repo <klon von skill-library>

Stdlib-only. Ausgabe: Markdown-Tabelle, Exit-Code immer 0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def split(skill_md: Path) -> tuple[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.DOTALL)
    return (m.group(1), m.group(2)) if m else ("", text)


def field(fm: str, key: str) -> str:
    m = re.search(rf"^\s+{key}:\s*(.+)$", fm, re.MULTILINE)
    if not m:
        return ""
    return re.sub(r"#.*$", "", m.group(1)).strip().strip("\"'")


def vtuple(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in re.findall(r"\d+", v)) or (0,)


def files(d: Path) -> dict[str, str]:
    out = {}
    for p in sorted(d.rglob("*")):
        if p.is_file() and p.name != "SKILL.md" and not p.name.startswith("."):
            out[str(p.relative_to(d))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def skills(root: Path) -> dict[str, Path]:
    return {p.parent.name: p.parent for p in root.glob("*/SKILL.md")}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mount", default="/mnt/skills/plugins")
    ap.add_argument("--repo", required=True)
    a = ap.parse_args()
    mount, repo = Path(a.mount), Path(a.repo)

    own = None
    manifest = mount / "manifest.json"
    if manifest.exists():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        own = {s["name"] for s in data.get("skills", []) if s.get("source") == "plugin"}

    ms, rs = skills(mount), skills(repo)
    rows = []
    for name in sorted(set(ms) | set(rs)):
        if name in ms and own is not None and name not in own:
            continue  # Anthropic-Skill, nicht Joschas
        m, r = ms.get(name), rs.get(name)
        mfm, mbody = split(m / "SKILL.md") if m else ("", "")
        rfm, rbody = split(r / "SKILL.md") if r else ("", "")
        mv, rv = field(mfm, "version"), field(rfm, "version")
        author = field(mfm or rfm, "author")

        if author and not r:
            status, note = "extern", f"Upstream: {author}"
        elif m and not r:
            status, note = "kein Backup", ""
        elif r and not m:
            status, note = "nur im Repo", "archivieren oder mounten?"
        elif mv != rv:
            newer = "Mount" if vtuple(mv) > vtuple(rv) else "Repo"
            status = "Backup veraltet" if newer == "Mount" else "Mount veraltet"
            note = ""
        else:
            fm_, fr_ = files(m), files(r)
            diffs = []
            if mbody.strip() != rbody.strip():
                diffs.append("SKILL.md-Rumpf")
            only_m = sorted(set(fm_) - set(fr_))
            only_r = sorted(set(fr_) - set(fm_))
            changed = sorted(k for k in set(fm_) & set(fr_) if fm_[k] != fr_[k])
            if only_m:
                diffs.append(f"nur gemountet: {len(only_m)} Datei(en)")
            if only_r:
                diffs.append(f"nur im Repo: {len(only_r)} Datei(en)")
            if changed:
                diffs.append(f"geändert: {', '.join(changed[:3])}")
            if not diffs:
                status, note = "identisch", ""
            elif diffs == [f"nur im Repo: {len(only_r)} Datei(en)"]:
                status, note = "Dateien abweichend", diffs[0] + " (" + ", ".join(only_r[:3]) + ")"
            else:
                status, note = "Inhalt abweichend, gleiche Version", "; ".join(diffs)
        rows.append((name, mv or "-", rv or "-", status, note))

    print("| Skill | Mount | Repo | Status | Hinweis |")
    print("|---|---|---|---|---|")
    for row in rows:
        print("| " + " | ".join(row) + " |")


if __name__ == "__main__":
    main()
