"""Build the worked example report from the demo data."""
from __future__ import annotations

import csv
import os
from typing import Dict, List

from .calibration import expected_calibration_error, reliability_table
from .drift import interpret_psi, psi
from .estimation import decide, stratified_estimate
from .intervals import clopper_pearson, wald_interval, wilson_interval
from .planning import accept_probability, find_acceptance_plan, required_sample_size, stratified_allocation
from .simulate import coverage, variance_srs, variance_stratified


def load_strata(path: str) -> List[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return [{"name": r["stratum"], "size": int(r["population_size"]), "sample": int(r["sample_size"]),
                 "errors": int(r["errors_found"])} for r in csv.DictReader(f)]


def load_calibration(path: str):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [float(r["confidence"]) for r in rows], [r["correct"] == "1" for r in rows]


def build_report(data_dir: str, threshold: float = 0.05, simulate_trials: int = 4000) -> str:
    strata = load_strata(os.path.join(data_dir, "strata.csv"))
    sizes = {s["name"]: s["size"] for s in strata}
    total_n = sum(s["sample"] for s in strata)
    out = ["# Worked Example: Can We Trust 50,000 LLM-Labelled Records?", "",
           "An LLM labelled 50,000 records and reported a confidence for each. Reviewing all of them is too expensive, so a sample is reviewed "
           "and the result decides whether the automated output can be used.", "",
           "## 1. How many items to review", "", "| Margin of error | Sample size (unknown rate) | With a population of 50,000 |", "|---|---|---|"]
    for m in (0.05, 0.03, 0.02, 0.01):
        out.append(f"| +/-{m:.0%} | {required_sample_size(m)} | {required_sample_size(m, population=50000)} |")

    out += ["", "## 2. Where to spend the review budget", "",
            f"The records fall into three confidence tiers. With a budget of {total_n} reviews:", "",
            "| Tier | Records | Proportional | Allocation used (Neyman) |", "|---|---|---|---|"]
    prop = stratified_allocation(sizes, total_n)
    used = {s["name"]: s["sample"] for s in strata}
    for s in strata:
        out.append(f"| {s['name']} | {s['size']:,} | {prop[s['name']]} | {used[s['name']]} |")
    rates = [0.005, 0.03, 0.20]
    ss = [s["size"] for s in strata]
    v_srs = variance_srs(ss, rates, total_n)
    v_str = variance_stratified(ss, rates, [used[s["name"]] for s in strata])
    out += ["", f"Assuming error rates of 0.5%, 3% and 20% across the tiers, the stratified plan has a standard error of "
            f"**{v_str ** 0.5:.2%}** against **{v_srs ** 0.5:.2%}** for a simple random sample of the same size, so it needs about "
            f"**{v_str / v_srs:.0%}** of the variance. Review effort goes where the errors are.", "",
            "## 3. What the review found", "", "| Tier | Reviewed | Errors | Rate | 95% Wilson interval |", "|---|---|---|---|---|"]
    for s in strata:
        lo, hi = wilson_interval(s["errors"], s["sample"])
        out.append(f"| {s['name']} | {s['sample']} | {s['errors']} | {s['errors'] / s['sample']:.1%} | {lo:.1%} to {hi:.1%} |")
    est = stratified_estimate(strata)
    d = decide(est, threshold)
    out += ["", f"**Overall error rate: {est['estimate']:.2%}** (95% interval {est['lower']:.2%} to {est['upper']:.2%}).", "",
            f"**Decision against a {threshold:.0%} error budget: {d['decision']}**, because {d['reason']}."]
    if "approx_total_sample_needed" in d:
        out.append(f"Roughly {d['approx_total_sample_needed']} reviewed items would be needed to resolve it.")
    low = next(s for s in strata if s["name"].startswith("low"))
    out += ["", f"Practical reading: the {low['size']:,} low-confidence records carry most of the errors, so they should go to people, "
            "while the high-confidence tier can be accepted with periodic sampling.", "",
            "## 4. Continuous monitoring: an acceptance sampling plan", ""]
    n, c = find_acceptance_plan(0.01, 0.05)
    out += [f"To accept good batches (1% defects) with 95% probability and reject bad batches (5% defects) with 90% probability, review "
            f"**{n}** records per batch and accept the batch if **{c} or fewer** defects are found. "
            f"Check: P(accept | 1%) = {accept_probability(n, c, 0.01):.1%}, P(accept | 5%) = {accept_probability(n, c, 0.05):.1%}.", "",
            "## 5. Drift: has the label mix changed?", "", "| Label | Last month | This week |", "|---|---|---|"]
    base, now = [500, 300, 200], [350, 300, 350]
    for lab, a, b in zip(("routine", "elevated", "urgent"), base, now):
        out.append(f"| {lab} | {a} | {b} |")
    v = psi(base, now)
    out += ["", f"PSI = **{v:.3f}**, interpretation: **{interpret_psi(v)}**.", "",
            "## 6. Calibration: is the stated confidence trustworthy?", ""]
    conf, ok = load_calibration(os.path.join(data_dir, "confidence_review.csv"))
    out += ["| Confidence bin | Mean confidence | Accuracy | Gap | Items |", "|---|---|---|---|---|"]
    for mc, acc, gap, cnt in reliability_table(conf, ok, bins=5):
        out.append(f"| ~{mc:.2f} | {mc:.2f} | {acc:.2f} | {gap:+.2f} | {cnt} |")
    out += ["", f"Expected calibration error: **{expected_calibration_error(conf, ok, bins=5):.3f}**. The model is overconfident in every bin, "
            "so its confidence must be recalibrated, or replaced by review results, before it is used as a threshold.", "",
            "## 7. Why the interval method matters", "",
            f"Coverage of a nominal 95% interval for a true error rate of 1% and 50 reviewed items ({simulate_trials} simulated samples):", "",
            "| Method | Actual coverage |", "|---|---|"]
    out += [f"| Wilson | {coverage(wilson_interval, 0.01, 50, simulate_trials):.1%} |",
            f"| Clopper-Pearson (exact) | {coverage(clopper_pearson, 0.01, 50, min(simulate_trials, 1500)):.1%} |",
            f"| Wald (textbook) | {coverage(wald_interval, 0.01, 50, simulate_trials):.1%} |", "",
            "The textbook interval fails exactly where analytic work needs it: a low error rate and a modest sample. With zero errors found "
            "it reports a zero-width interval, which would wrongly suggest certainty. Wilson is far closer to the nominal level but still "
            "falls a little short at very low rates; the exact Clopper-Pearson interval is conservative and keeps its promise. "
            "For a go/no-go decision on a small sample, prefer the exact interval."]
    return "\n".join(out) + "\n"
