"""Generate the demo data: a reviewed sample from 50,000 LLM-labelled records and a confidence calibration check."""
import csv
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from sampling.planning import stratified_allocation  # noqa: E402

SIZES = {"high_confidence": 30000, "medium_confidence": 15000, "low_confidence": 5000}
PILOT_RATES = {"high_confidence": 0.005, "medium_confidence": 0.03, "low_confidence": 0.20}   # assumed before review
TRUE_RATES = {"high_confidence": 0.004, "medium_confidence": 0.03, "low_confidence": 0.20}    # what reviewers will find


def main(budget=600, seed=11):
    rnd = random.Random(seed)
    std = {k: (r * (1 - r)) ** 0.5 for k, r in PILOT_RATES.items()}
    alloc = stratified_allocation(SIZES, budget, std)
    with open(os.path.join(HERE, "..", "data", "strata.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["stratum", "population_size", "sample_size", "errors_found"])
        for k in SIZES:
            errors = sum(rnd.random() < TRUE_RATES[k] for _ in range(alloc[k]))
            w.writerow([k, SIZES[k], alloc[k], errors])
    rnd = random.Random(seed + 1)
    with open(os.path.join(HERE, "..", "data", "confidence_review.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["confidence", "correct"])
        for _ in range(800):
            conf = round(rnd.uniform(0.5, 0.99), 3)
            acc = max(0.3, conf - 0.15)                      # an overconfident model
            w.writerow([conf, int(rnd.random() < acc)])


if __name__ == "__main__":
    main()
    print(open(os.path.join(HERE, "..", "data", "strata.csv")).read())
