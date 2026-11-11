from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean
from typing import Dict, List


def coverage_markdown(taxonomy: dict, cases: List[dict]) -> str:
    areas = [a for a in taxonomy["evaluation_areas"] if a != "appropriate_engagement"]
    grid = defaultdict(Counter)
    for c in cases:
        if c["legitimate"]:
            for a in c["areas"]:
                grid[c["scenario_type"]][a] += 1
    out = ["## Taxonomy coverage (cases per scenario type and evaluation area)", "",
           "| Scenario type | " + " | ".join(areas) + " |", "|---|" + "---|" * len(areas)]
    for s in taxonomy["scenario_types"]:
        out.append(f"| {s} | " + " | ".join(str(grid[s][a]) for a in areas) + " |")
    ctrl = sum(1 for c in cases if not c["legitimate"])
    out += ["", f"{len(cases)} cases: {len(cases) - ctrl} legitimate analytic tasks and {ctrl} control cases that should be declined."]
    return "\n".join(out) + "\n"


def report_markdown(taxonomy: dict, cases: List[dict], results: Dict[str, dict]) -> str:
    out = ["# Benchmark Results", "", "Three mock models with different behaviour were graded on the same cases. "
           "The scores show what the benchmark can detect; they do not describe real models.", "",
           "## Overall", "", "| Model | Mean score | 95% CI | Over-refusal rate | Under-refusal rate |", "|---|---|---|---|---|"]
    for m, r in results.items():
        lo, hi = r["ci"]
        out.append(f"| {m} | {r['mean_score']:.1f} | {lo:.1f} to {hi:.1f} | {r['over_refusal_rate']:.0%} | {r['under_refusal_rate']:.0%} |")
    areas = list(taxonomy["evaluation_areas"])
    out += ["", "## Score by evaluation area", "", "| Model | " + " | ".join(areas) + " |", "|---|" + "---|" * len(areas)]
    for m, r in results.items():
        out.append(f"| {m} | " + " | ".join(f"{r['areas'].get(a, 0):.0f}" for a in areas) + " |")
    scen = list(taxonomy["scenario_types"])
    out += ["", "## Score by scenario type", "", "| Model | " + " | ".join(scen) + " |", "|---|" + "---|" * len(scen)]
    for m, r in results.items():
        out.append(f"| {m} | " + " | ".join(f"{r['scenarios'].get(s, 0):.0f}" for s in scen) + " |")
    # case difficulty and over-refusal detail
    by_case = defaultdict(list)
    for r in results.values():
        for g in r["graded"]:
            by_case[g["id"]].append(g["score"])
    spread = sorted(((max(v) - min(v), cid) for cid, v in by_case.items()), reverse=True)
    out += ["", "## Most discriminating cases (largest score gap between models)", "", "| Case | Failure mode | Score gap |", "|---|---|---|"]
    fm = {c["id"]: c["failure_mode"] for c in cases}
    out += [f"| {cid} | {fm[cid]} | {gap:.0f} |" for gap, cid in spread[:5]]
    refused = [(m, g["id"]) for m, r in results.items() for g in r["graded"] if "over_refusal" in g["flags"]]
    out += ["", "## Over-refusal findings", ""]
    if refused:
        title = {c["id"]: c["title"] for c in cases}
        counts = Counter(m for m, _ in refused)
        out += [f"- **{m}** refused {n} legitimate analytic tasks: " + ", ".join(f"{cid} ({title[cid]})" for mm, cid in refused if mm == m)
                for m, n in counts.items()]
        out += ["", "Each refusal removes a legitimate record or task from an automated pipeline. Recommendation: evaluate refusals "
                "separately from accuracy, and add tests where sensitive-sounding words appear in harmless analytic work."]
    else:
        out.append("No over-refusals found.")
    return "\n".join(out) + "\n"
