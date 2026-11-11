"""How many items to review, how to split the review across strata, and acceptance sampling plans."""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

from .intervals import z_value


def required_sample_size(margin: float, p: float = 0.5, confidence: float = 0.95, population: Optional[int] = None) -> int:
    """Sample size to estimate a proportion within +/- margin. p = 0.5 is the worst case when the rate is unknown."""
    if not 0 < margin < 1 or not 0 < p < 1:
        raise ValueError("margin and p must be between 0 and 1")
    z = z_value(confidence)
    n0 = z * z * p * (1 - p) / (margin * margin)
    if population is not None:
        if population <= 0:
            raise ValueError("population must be positive")
        n0 = n0 / (1 + (n0 - 1) / population)  # finite population correction
    return math.ceil(n0)


def stratified_allocation(sizes: Dict[str, int], total: int, std: Optional[Dict[str, float]] = None) -> Dict[str, int]:
    """Split a review budget across strata. Proportional by default; Neyman (size x std) when standard deviations are given.
    Uses largest remainders so the allocation always sums to the budget."""
    if total <= 0 or not sizes:
        raise ValueError("need a positive budget and at least one stratum")
    weights = {k: v * (std[k] if std else 1.0) for k, v in sizes.items()}
    wsum = sum(weights.values())
    raw = {k: total * w / wsum for k, w in weights.items()}
    alloc = {k: int(v) for k, v in raw.items()}
    for k in sorted(raw, key=lambda k: raw[k] - alloc[k], reverse=True)[: total - sum(alloc.values())]:
        alloc[k] += 1
    return alloc


def accept_probability(n: int, c: int, p: float) -> float:
    """Probability that a lot with defect rate p passes: at most c defects found in a sample of n (binomial)."""
    if n < 0 or c < 0 or not 0 <= p <= 1:
        raise ValueError("invalid arguments")
    return sum(math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(0, min(c, n) + 1))


def find_acceptance_plan(aql: float, ltpd: float, alpha: float = 0.05, beta: float = 0.10, max_n: int = 3000) -> Tuple[int, int]:
    """Smallest sample size n (with its accept number c) such that
    - a good lot (defect rate = aql) is accepted with probability >= 1 - alpha, and
    - a bad lot (defect rate = ltpd) is accepted with probability <= beta."""
    if not 0 < aql < ltpd < 1:
        raise ValueError("need 0 < aql < ltpd < 1")
    for n in range(1, max_n + 1):
        best_c = None
        for c in range(0, n + 1):
            if accept_probability(n, c, ltpd) <= beta:
                best_c = c            # acceptance of bad lots only grows with c, so keep the largest c that still rejects them
            else:
                break
        if best_c is not None and accept_probability(n, best_c, aql) >= 1 - alpha:
            return n, best_c
    raise ValueError("no plan found within max_n")
