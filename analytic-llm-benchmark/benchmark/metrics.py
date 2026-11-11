"""Aggregate scores per model, area and scenario, with bootstrap confidence intervals."""
from __future__ import annotations

import random
from collections import defaultdict
from statistics import mean
from typing import Callable, Dict, List, Sequence, Tuple


def bootstrap_ci(values: Sequence[float], n_boot: int = 2000, alpha: float = 0.05, seed: int = 0) -> Tuple[float, float]:
    """Percentile bootstrap confidence interval for the mean (deterministic for a given seed)."""
    if not values:
        raise ValueError("no values")
    rnd = random.Random(seed)
    n = len(values)
    means = sorted(mean(rnd.choice(values) for _ in range(n)) for _ in range(n_boot))
    return means[int(n_boot * alpha / 2)], means[int(n_boot * (1 - alpha / 2)) - 1]


def evaluate_models(cases: List[dict], responses: Dict[str, dict], models: Dict[str, Callable], grade) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for name, model in models.items():
        graded = [grade(c, model(c, responses)) for c in cases]
        legit = [(c, g) for c, g in zip(cases, graded) if c["legitimate"]]
        control = [(c, g) for c, g in zip(cases, graded) if not c["legitimate"]]
        area_scores = defaultdict(list)
        for g in graded:
            for a, s in g["areas"].items():
                area_scores[a].append(s)
        scen = defaultdict(list)
        for c, g in zip(cases, graded):
            scen[c["scenario_type"]].append(g["score"])
        scores = [g["score"] for g in graded]
        out[name] = {
            "graded": graded,
            "mean_score": mean(scores),
            "ci": bootstrap_ci(scores),
            "areas": {a: mean(v) for a, v in area_scores.items()},
            "scenarios": {s: mean(v) for s, v in scen.items()},
            "over_refusal_rate": sum("over_refusal" in g["flags"] for _, g in legit) / len(legit),
            "under_refusal_rate": sum("under_refusal" in g["flags"] for _, g in control) / len(control) if control else 0.0,
        }
    return out
