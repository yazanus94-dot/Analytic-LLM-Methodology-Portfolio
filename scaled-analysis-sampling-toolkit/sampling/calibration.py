"""Is the model's stated confidence a reliable guide to correctness?"""
from __future__ import annotations

from typing import List, Sequence, Tuple


def reliability_table(confidences: Sequence[float], correct: Sequence[bool], bins: int = 10) -> List[Tuple[float, float, float, int]]:
    """Rows of (mean confidence, accuracy, gap, count) for each non-empty confidence bin."""
    if len(confidences) != len(correct) or not confidences:
        raise ValueError("need non-empty sequences of the same length")
    if any(not 0 <= c <= 1 for c in confidences):
        raise ValueError("confidences must be between 0 and 1")
    buckets: List[List[Tuple[float, bool]]] = [[] for _ in range(bins)]
    for c, ok in zip(confidences, correct):
        buckets[min(int(c * bins), bins - 1)].append((c, bool(ok)))
    rows = []
    for b in buckets:
        if b:
            conf = sum(c for c, _ in b) / len(b)
            acc = sum(ok for _, ok in b) / len(b)
            rows.append((conf, acc, conf - acc, len(b)))
    return rows


def expected_calibration_error(confidences: Sequence[float], correct: Sequence[bool], bins: int = 10) -> float:
    """Weighted average gap between confidence and accuracy. 0 is perfectly calibrated."""
    rows = reliability_table(confidences, correct, bins)
    n = len(confidences)
    return sum(abs(gap) * count for _, _, gap, count in rows) / n
