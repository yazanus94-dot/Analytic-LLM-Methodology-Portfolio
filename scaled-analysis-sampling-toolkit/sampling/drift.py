"""Population Stability Index: has the distribution of model outputs shifted?"""
from __future__ import annotations

import math
from typing import Sequence


def psi(expected: Sequence[float], actual: Sequence[float], eps: float = 1e-4) -> float:
    """PSI between two category distributions (counts or shares). 0 means identical."""
    if len(expected) != len(actual) or not expected:
        raise ValueError("distributions must be non-empty and the same length")
    se, sa = float(sum(expected)), float(sum(actual))
    if se <= 0 or sa <= 0:
        raise ValueError("distributions must have a positive total")
    total = 0.0
    for e, a in zip(expected, actual):
        pe, pa = max(e / se, eps), max(a / sa, eps)
        total += (pa - pe) * math.log(pa / pe)
    return total


def interpret_psi(value: float) -> str:
    """Common rule of thumb: below 0.1 stable, 0.1 to 0.25 moderate shift, 0.25 or more major shift."""
    if value < 0.1:
        return "stable"
    if value < 0.25:
        return "moderate shift: investigate"
    return "major shift: stop and investigate"
