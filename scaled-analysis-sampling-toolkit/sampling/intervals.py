"""Confidence intervals for an error rate measured on a reviewed sample."""
from __future__ import annotations

import math
from statistics import NormalDist
from typing import Tuple


def z_value(confidence: float) -> float:
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    return NormalDist().inv_cdf(0.5 + confidence / 2)


def wilson_interval(errors: int, n: int, confidence: float = 0.95) -> Tuple[float, float]:
    """Wilson score interval. Reliable for small samples and rates near 0, unlike the simple (Wald) interval."""
    if n <= 0 or not 0 <= errors <= n:
        raise ValueError("need n > 0 and 0 <= errors <= n")
    z = z_value(confidence)
    p = errors / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    lo = 0.0 if errors == 0 else max(0.0, centre - half)       # exactly 0 / 1 at the extremes, without floating-point noise
    hi = 1.0 if errors == n else min(1.0, centre + half)
    return lo, hi


def wald_interval(errors: int, n: int, confidence: float = 0.95) -> Tuple[float, float]:
    """The textbook interval p +/- z*sqrt(p(1-p)/n). Shown for comparison: it collapses to zero width when errors = 0."""
    if n <= 0 or not 0 <= errors <= n:
        raise ValueError("need n > 0 and 0 <= errors <= n")
    z, p = z_value(confidence), errors / n
    half = z * math.sqrt(p * (1 - p) / n)
    return max(0.0, p - half), min(1.0, p + half)


def _binom_cdf(k: int, n: int, p: float) -> float:
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))


def clopper_pearson(errors: int, n: int, confidence: float = 0.95) -> Tuple[float, float]:
    """Exact (conservative) interval: coverage is at least the stated confidence for every true rate."""
    if n <= 0 or not 0 <= errors <= n:
        raise ValueError("need n > 0 and 0 <= errors <= n")
    alpha = 1 - confidence

    def solve(target, f, increasing):
        lo, hi = 0.0, 1.0
        for _ in range(80):
            mid = (lo + hi) / 2
            if (f(mid) < target) == increasing:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    # lower: p such that P(X >= errors | p) = alpha/2 ; upper: p such that P(X <= errors | p) = alpha/2
    lower = 0.0 if errors == 0 else solve(alpha / 2, lambda q: 1 - _binom_cdf(errors - 1, n, q), True)
    upper = 1.0 if errors == n else solve(alpha / 2, lambda q: _binom_cdf(errors, n, q), False)
    return lower, upper
