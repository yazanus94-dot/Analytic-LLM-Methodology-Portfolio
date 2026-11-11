"""Estimate the overall error rate from a stratified review sample and decide what to do."""
from __future__ import annotations

import math
from typing import Dict, List

from .intervals import z_value


def stratified_estimate(strata: List[dict], confidence: float = 0.95) -> Dict[str, float]:
    """strata: [{'name', 'size', 'sample', 'errors'}]. Returns the weighted error rate, its standard error and a normal interval.
    The finite population correction is applied within each stratum."""
    total = sum(s["size"] for s in strata)
    if total <= 0:
        raise ValueError("empty population")
    est, var = 0.0, 0.0
    for s in strata:
        if not 0 < s["sample"] <= s["size"] or not 0 <= s["errors"] <= s["sample"]:
            raise ValueError(f"invalid stratum {s.get('name')}")
        w, p, n = s["size"] / total, s["errors"] / s["sample"], s["sample"]
        est += w * p
        var += w * w * p * (1 - p) / n * (1 - n / s["size"])
    se = math.sqrt(var)
    z = z_value(confidence)
    return {"estimate": est, "se": se, "lower": max(0.0, est - z * se), "upper": min(1.0, est + z * se)}


def decide(estimate: Dict[str, float], threshold: float) -> Dict[str, object]:
    """Decision rule for 'is the automated output good enough?'

    ACCEPT        the whole interval is below the threshold
    REJECT        the whole interval is above the threshold
    INCONCLUSIVE  the interval straddles the threshold: more review is needed (an estimate of how much is returned)
    """
    lo, hi, est = estimate["lower"], estimate["upper"], estimate["estimate"]
    if hi < threshold:
        return {"decision": "ACCEPT", "reason": f"the upper bound {hi:.2%} is below the {threshold:.2%} threshold"}
    if lo > threshold:
        return {"decision": "REJECT", "reason": f"the lower bound {lo:.2%} is above the {threshold:.2%} threshold"}
    gap = max(abs(est - threshold), 1e-6)
    z = z_value(0.95)
    # additional-sample estimate: how many reviewed items would shrink the margin to the distance from the threshold
    needed = math.ceil(z * z * max(est * (1 - est), 1e-6) / (gap * gap))
    return {"decision": "INCONCLUSIVE", "reason": f"the interval {lo:.2%} to {hi:.2%} straddles the {threshold:.2%} threshold",
            "approx_total_sample_needed": needed}
