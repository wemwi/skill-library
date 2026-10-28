#!/usr/bin/env python3
"""Repo-Check für den Setup-Audit: Actions-Verbrauch, CI-Regelverstöße, Branch-Hygiene.

Nur lesend. Maßstab: global-git-conventions (references/ci.md, references/settings.md).

Aufruf: python3 repo_check.py [--owner wemwi] repo1 repo2 …
Braucht die gh-CLI mit Lesezugriff auf die Repos (in einer Claude-Sitzung vorher
add_repo je privatem Repo). Ausgabe: Markdown für den Bericht. Exit-Code immer 0.

Hinweise:
- Die Runs-API liefert höchstens 1.000 Läufe; bei mehr wird über den abgedeckten
  Zeitraum auf 30 Tage hochgerechnet (markiert mit „~").
- Abgerechnete Minuten werden aus einer Stichprobe von Jobs des teuersten Workflows
  geschätzt (je Job aufgerundet, Linux/Windows/macOS getrennt).
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None

RATE = {"linux": 0.006, "windows": 0.010, "macos": 0.062}  # $/min, 2-Core (Stand Okt. 2026)
args = sys.argv[1:]
OWNER = "wemwi"
if "--owner" in args:
    i = args.index("--owner")
    OWNER = args[i + 1]
    del args[i : i + 2]
REPOS = args
NOW = datetime.now(timezone.utc)


def gh(path: str):
    for _ in range(2):
        r = subprocess.run(["gh", "api", path], capture_output=True, text=True)
        if r.returncode == 0:
            return json.loads(r.stdout) if r.stdout.strip() else {}
    return None


def pages(path: str, key: str | None = None, limit: int = 20) -> list:
    out: list = []
    for page in range(1, limit + 1):  # manuell: --paginate folgt Link-URLs mit numerischer ID
        res = gh(f"{path}&page={page}")
        if res is None:
            break
        items = res.get(key, []) if key else res
        out += items
        if len(items) < 100:
            break
    return out


def ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def os_of(labels) -> str:
    s = " ".join(labels if isinstance(labels, list) else [str(labels)]).lower()
    return "windows" if "windows" in s else "macos" if "macos" in s else "linux"


def workflow_findings(repo_full: str) -> list[str]:
    found: list[str] = []
    files = gh(f"repos/{repo_full}/contents/.github/workflows")
    if not isinstance(files, list) or yaml is None:
        return found
    for f in files:
        if not f["name"].endswith((".yml", ".yaml")):
            continue
        c = gh(f"repos/{repo_full}/contents/{f['path']}")
        if not c:
            continue
        import base64

        try:
            wf = yaml.safe_load(base64.b64decode(c["content"]))
        except Exception:
            found.append(f"`{f['name']}`: YAML nicht lesbar")
            continue
        if not isinstance(wf, dict):
            continue
        on = wf.get("on", wf.get(True)) or {}
        if isinstance(on, str):
            on = {on: None}
        elif isinstance(on, list):
            on = {k: None for k in on}
        jobs = wf.get("jobs") or {}
        name = f["name"]
        no_timeout = [j for j, d in jobs.items() if isinstance(d, dict) and "timeout-minutes" not in d]
        if no_timeout:
            found.append(f"`{name}`: kein `timeout-minutes` ({', '.join(no_timeout)})")
        has_conc = "concurrency" in wf or any(isinstance(d, dict) and "concurrency" in d for d in jobs.values())
        if "pull_request" in on and not has_conc:
            found.append(f"`{name}`: keine `concurrency` mit Abbruch")
        if "pull_request" in on and "push" in on and not any(k in name.lower() for k in ("deploy", "release")):
            found.append(f"`{name}`: läuft auf PR **und** nach dem Merge auf `main` (Doppellauf)")
        if "workflow_run" in on:
            found.append(f"`{name}`: startet nach anderen Workflows (`workflow_run`)")
        for cron in [s.get("cron", "") for s in (on.get("schedule") or []) if isinstance(s, dict)]:
            hour = cron.split()[1] if len(cron.split()) > 1 else ""
            if hour in ("*",) or hour.startswith("*/"):
                found.append(f"`{name}`: Polling-Cron `{cron}`")
        for j, d in jobs.items():
            if isinstance(d, dict) and os_of(d.get("runs-on", "")) != "linux":
                found.append(f"`{name}`: Job `{j}` auf {os_of(d.get('runs-on'))} — nur wo nötig?")
    return found


def actions_usage(repo_full: str):
    since = (NOW - timedelta(days=30)).strftime("%Y-%m-%d")
    runs = pages(f"repos/{repo_full}/actions/runs?created=>={since}&per_page=100", key="workflow_runs", limit=10)
    if not runs:
        return None
    span = max(1.0, (NOW - ts(runs[-1]["created_at"])).total_seconds() / 86400)
    factor = 30 / span if len(runs) >= 1000 else 1.0
    by = Counter(f"{r['name']} [{r['event']}]" for r in runs)
    wall = defaultdict(float)
    for r in runs:
        if r.get("status") == "completed" and r.get("run_started_at"):
            wall[r["name"]] += max(0.0, (ts(r["updated_at"]) - ts(r["run_started_at"])).total_seconds() / 60)
    top = max(wall, key=wall.get) if wall else None
    billed = None
    if top:
        sample = [r for r in runs if r["name"] == top and r.get("status") == "completed"][:5]
        per_os = defaultdict(float)
        for r in sample:
            jobs = gh(f"repos/{repo_full}/actions/runs/{r['id']}/jobs?per_page=100") or {}
            for j in jobs.get("jobs", []):
                if j.get("started_at") and j.get("completed_at"):
                    per_os[os_of(j.get("labels", []))] += math.ceil(
                        max(0.0, (ts(j["completed_at"]) - ts(j["started_at"])).total_seconds()) / 60)
        if sample:
            n_top = sum(1 for r in runs if r["name"] == top) * factor
            billed = {o: m / len(sample) * n_top for o, m in per_os.items()}
    return {
        "runs": len(runs) * factor, "capped": len(runs) >= 1000,
        "top": by.most_common(4), "factor": factor, "top_wf": top, "billed": billed,
    }


def branch_hygiene(repo_full: str, info: dict):
    branches = {b["name"]: b["commit"]["sha"] for b in pages(f"repos/{repo_full}/branches?per_page=100")}
    by_head: dict[str, list] = {}
    for pr in pages(f"repos/{repo_full}/pulls?state=all&per_page=100"):
        if pr["head"]["repo"] and pr["head"]["repo"]["full_name"] == repo_full:
            by_head.setdefault(pr["head"]["ref"], []).append(pr)
    c = Counter()
    no_pr: list[str] = []
    for name, sha in branches.items():
        if name == info.get("default_branch") or name.startswith(("renovate/", "release-please--")):
            continue
        prs = by_head.get(name, [])
        merged = [p for p in prs if p.get("merged_at")]
        if any(p["state"] == "open" for p in prs):
            c["offen"] += 1
        elif merged and max(merged, key=lambda p: p["merged_at"])["head"]["sha"] == sha:
            c["gemergt"] += 1
        elif not prs:
            c["ohne PR"] += 1
            no_pr.append(name)
        else:
            c["sonstige"] += 1
    renovate_open = sum(1 for ps in by_head.values() for p in ps if p["state"] == "open" and p["head"]["ref"].startswith("renovate/"))
    return len(branches), c, no_pr, renovate_open


def main() -> None:
    rows, details = [], []
    for repo in REPOS:
        full = f"{OWNER}/{repo}"
        info = gh(f"repos/{full}")
        if not info:
            rows.append(f"| {repo} | ? | kein Zugriff | | | | |")
            continue
        private = info.get("private", True)
        usage = actions_usage(full)
        total, bc, no_pr, ren = branch_hygiene(full, info)
        findings = workflow_findings(full)
        cost = "–"
        runs = "0"
        if usage:
            runs = f"{'~' if usage['capped'] else ''}{usage['runs']:.0f}"
            if usage["billed"] and private:
                b = usage["billed"]
                cost = " + ".join(f"{m:.0f} {o}" for o, m in sorted(b.items())) + f" (≈{sum(RATE[o] * m for o, m in b.items()):.0f} $)"
        auto_del = "an" if info.get("delete_branch_on_merge") else "**aus**"
        rows.append(f"| {repo} | {'privat' if private else 'öffentlich'} | {runs} | {cost} | {total} ({bc['gemergt']} gemergt, {bc['ohne PR']} ohne PR) | {auto_del} | {len(findings)} |")
        d = []
        if usage:
            d.append("Läufe: " + ", ".join(f"{k} {v * usage['factor']:.0f}" for k, v in usage["top"]))
        if findings and private:
            d += findings
        elif findings:
            d.append(f"{len(findings)} Abweichungen von den Sparregeln (öffentlich, kostenfrei — nur SHOULD)")
        if no_pr:
            d.append("Branches ohne PR: " + ", ".join(f"`{n}`" for n in no_pr[:6]) + (" …" if len(no_pr) > 6 else ""))
        if ren:
            d.append(f"{ren} offene Renovate-PRs")
        if d:
            details.append(f"**{repo}**\n" + "\n".join(f"- {x}" for x in d))
    print("| Repo | Sichtbarkeit | Läufe 30 T. | teuerster Workflow, Min./Monat | Branches | Auto-Löschen | Regel-Abweichungen |")
    print("|---|---|---|---|---|---|---|")
    print("\n".join(rows))
    print()
    print("\n\n".join(details))


if __name__ == "__main__":
    main()
