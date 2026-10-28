#!/usr/bin/env python3
"""Listet (und löscht mit --apply) Branches, deren PR gemergt ist.

Gelöscht wird nur, wenn ALLE Bedingungen gelten:
- nicht der Default-Branch, nicht renovate/*, nicht release-please--*
- es gibt einen gemergten PR mit diesem Branch als Kopf (aus demselben Repo)
- es gibt keinen offenen PR mit diesem Branch
- der Branch-Kopf ist exakt der Kopf des zuletzt gemergten PRs (keine Commits danach)
Der gemergte PR behält die Commits; GitHub bietet dort „Restore branch“ an.

Aufruf: OWNER=wemwi python3 scripts/branch_cleanup.py [--apply] repo1 repo2 …
Braucht die gh-CLI mit GH_TOKEN. Ausgabe: Markdown (für $GITHUB_STEP_SUMMARY).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from urllib.parse import quote

APPLY = "--apply" in sys.argv
REPOS = [a for a in sys.argv[1:] if not a.startswith("--")]
OWNER = os.environ.get("OWNER", "wemwi")


def gh(path: str, method: str = "GET"):
    r = subprocess.run(["gh", "api", "-X", method, path], capture_output=True, text=True)
    if r.returncode != 0:
        return None, (r.stderr or r.stdout).strip()
    return (json.loads(r.stdout) if r.stdout.strip() else {}), None


def pages(path: str) -> list:
    out: list = []
    for page in range(1, 100):
        res, err = gh(f"{path}&page={page}")
        if res is None:
            raise RuntimeError(err)
        out += res
        if len(res) < 100:
            return out
    return out


def plan(repo: str):
    full = f"{OWNER}/{repo}"
    info, err = gh(f"repos/{full}")
    if info is None:
        raise RuntimeError(err)
    branches = {b["name"]: b["commit"]["sha"] for b in pages(f"repos/{full}/branches?per_page=100")}
    by_head: dict[str, list] = {}
    for pr in pages(f"repos/{full}/pulls?state=all&per_page=100"):
        if pr["head"]["repo"] and pr["head"]["repo"]["full_name"] == full:
            by_head.setdefault(pr["head"]["ref"], []).append(pr)
    delete, keep = [], []
    for name, sha in sorted(branches.items()):
        if name == info["default_branch"] or name.startswith(("renovate/", "release-please--")):
            continue
        prs = by_head.get(name, [])
        if any(p["state"] == "open" for p in prs):
            keep.append((name, "PR offen"))
            continue
        merged = [p for p in prs if p.get("merged_at")]
        if not merged:
            keep.append((name, "kein gemergter PR" if prs else "ohne PR"))
            continue
        last = max(merged, key=lambda p: p["merged_at"])
        if last["head"]["sha"] != sha:
            keep.append((name, f"neue Commits nach Merge von #{last['number']}"))
            continue
        delete.append((name, last["number"]))
    return full, len(branches), delete, keep


def main() -> None:
    print(f"# Branch-Aufräumen ({'Löschen' if APPLY else 'Probelauf'})\n")
    for repo in REPOS:
        try:
            full, total, delete, keep = plan(repo)
        except RuntimeError as e:
            print(f"## {repo}\n\nFehler: `{str(e)[:200]}`\n")
            continue
        done, failed = 0, []
        if APPLY:
            for name, _ in delete:
                res, err = gh(f"repos/{full}/git/refs/heads/{quote(name, safe='/')}", "DELETE")
                if res is None:
                    failed.append((name, err))
                else:
                    done += 1
        verb = f"gelöscht: {done}" if APPLY else f"würde löschen: {len(delete)}"
        print(f"## {repo}\n\n{total} Branches · {verb} · behalten: {len(keep)}\n")
        if delete and not APPLY:
            print("<details><summary>Zu löschen</summary>\n")
            print("\n".join(f"- `{n}` (PR #{pr})" for n, pr in delete))
            print("\n</details>\n")
        if keep:
            print("Behalten:\n")
            print("\n".join(f"- `{n}` — {why}" for n, why in keep))
            print()
        for name, err in failed[:5]:
            print(f"- Fehler bei `{name}`: `{err[:150]}`")


if __name__ == "__main__":
    main()
