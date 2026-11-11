"""Simulations that check the methods against known truth."""
from __future__ import annotations

import math
import random
from typing import Callable, Dict, List, Tuple

from .intervals import wald_interval, wilson_interval


def coverage(interval: Callable, p: float, n: int, trials: int = 5000, seed: int = 0) -> float:
    """Share of simulated samples whose 95% interval contains the true rate."""
    rnd = random.Random(seed)
    hit = 0
    for _ in range(trials):
        errors = sum(rnd.random() < p for _ in range(n))
        lo, hi = interval(errors, n)
        hit += lo <= p <= hi
    return hit / trials


def variance_srs(sizes: List[int], rates: List[float], n: int) -> float:
    """Variance of the overall error-rate estimate under a simple random sample of n from the whole population."""
    total = sum(sizes)
    p = sum(s * r for s, r in zip(sizes, rates)) / total
    return p * (1 - p) / n * (1 - n / total)


def variance_stratified(sizes: List[int], rates: List[float], alloc: List[int]) -> float:
    total = sum(sizes)
    return sum((s / total) ** 2 * r * (1 - r) / a * (1 - a / s) for s, r, a in zip(sizes, rates, alloc))
