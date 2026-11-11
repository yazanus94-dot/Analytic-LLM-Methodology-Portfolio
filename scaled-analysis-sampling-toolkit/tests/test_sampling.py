import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from sampling import (accept_probability, clopper_pearson, decide, expected_calibration_error, find_acceptance_plan,  # noqa: E402
                      interpret_psi, psi, required_sample_size, stratified_allocation, stratified_estimate, wald_interval,
                      wilson_interval)
from sampling.__main__ import main  # noqa: E402
from sampling.calibration import reliability_table  # noqa: E402
from sampling.report import build_report, load_strata  # noqa: E402
from sampling.simulate import coverage, variance_srs, variance_stratified  # noqa: E402


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


def close(a, b, tol=1e-4):
    return abs(a - b) <= tol


def test_required_sample_size_known_values():
    assert [required_sample_size(m) for m in (0.05, 0.03, 0.02, 0.01)] == [385, 1068, 2401, 9604]
    assert required_sample_size(0.05, population=1000) == 278            # finite population correction
    assert required_sample_size(0.05, p=0.02) < required_sample_size(0.05)   # a known low rate needs fewer items
    assert required_sample_size(0.05, confidence=0.99) > 385
    assert raises(required_sample_size, 0) and raises(required_sample_size, 0.05, p=1.5) and raises(required_sample_size, 0.05, population=0)


def test_wilson_interval_known_values_and_properties():
    lo, hi = wilson_interval(0, 10)
    assert lo == 0.0 and close(hi, 0.2775)
    lo, hi = wilson_interval(5, 10)
    assert close(lo + hi, 1.0)
    assert wilson_interval(10, 10)[1] == 1.0
    assert wilson_interval(5, 100)[1] - wilson_interval(5, 100)[0] > wilson_interval(50, 1000)[1] - wilson_interval(50, 1000)[0]
    assert raises(wilson_interval, 5, 0) and raises(wilson_interval, 11, 10) and raises(wilson_interval, 1, 10, 1.5)


def test_wald_interval_collapses_with_zero_errors():
    assert wald_interval(0, 10) == (0.0, 0.0)
    assert wald_interval(5, 10)[0] < 0.5 < wald_interval(5, 10)[1]


def test_clopper_pearson_known_values():
    lo, hi = clopper_pearson(0, 10)
    assert lo == 0.0 and close(hi, 1 - 0.025 ** 0.1, 1e-6)       # = 0.3085
    lo, hi = clopper_pearson(10, 10)
    assert hi == 1.0 and close(lo, 0.025 ** 0.1, 1e-6)
    lo, hi = clopper_pearson(3, 50)
    assert lo < 0.06 < hi and hi - lo > wilson_interval(3, 50)[1] - wilson_interval(3, 50)[0]   # the exact interval is wider
    assert raises(clopper_pearson, 5, 0)


def test_accept_probability():
    assert close(accept_probability(50, 0, 0.01), 0.99 ** 50, 1e-12)
    assert close(accept_probability(10, 10, 0.3), 1.0, 1e-9) and accept_probability(10, 0, 0.0) == 1.0
    assert accept_probability(50, 2, 0.05) < accept_probability(50, 2, 0.01)   # worse lots are accepted less often
    assert raises(accept_probability, 10, 1, 1.5)


def test_acceptance_plan_meets_both_risks_and_is_the_smallest():
    n, c = find_acceptance_plan(0.01, 0.05)
    assert (n, c) == (132, 3)
    assert accept_probability(n, c, 0.01) >= 0.95 and accept_probability(n, c, 0.05) <= 0.10
    for smaller in range(1, n):   # no smaller sample size has any workable accept number
        for cc in range(0, smaller + 1):
            assert not (accept_probability(smaller, cc, 0.05) <= 0.10 and accept_probability(smaller, cc, 0.01) >= 0.95)
    assert raises(find_acceptance_plan, 0.05, 0.01)


def test_stratified_allocation():
    sizes = {"a": 30000, "b": 15000, "c": 5000}
    prop = stratified_allocation(sizes, 600)
    assert prop == {"a": 360, "b": 180, "c": 60}
    ney = stratified_allocation(sizes, 600, {"a": 0.07, "b": 0.17, "c": 0.4})
    assert sum(ney.values()) == 600 and ney["c"] > prop["c"] and ney["a"] < prop["a"]
    odd = stratified_allocation({"a": 1, "b": 1, "c": 1}, 10)
    assert sum(odd.values()) == 10 and set(odd.values()) == {3, 4}
    assert raises(stratified_allocation, sizes, 0) and raises(stratified_allocation, {}, 5)


def test_stratified_estimate_matches_hand_calculation():
    strata = [{"name": "x", "size": 1000, "sample": 100, "errors": 2}, {"name": "y", "size": 1000, "sample": 100, "errors": 10}]
    e = stratified_estimate(strata)
    assert close(e["estimate"], 0.06, 1e-12)
    expected_var = 0.25 * (0.02 * 0.98 / 100 + 0.1 * 0.9 / 100) * 0.9
    assert close(e["se"], math.sqrt(expected_var), 1e-9)
    assert e["lower"] < 0.06 < e["upper"]


def test_reviewing_a_whole_stratum_leaves_no_sampling_error():
    e = stratified_estimate([{"name": "all", "size": 100, "sample": 100, "errors": 5}])
    assert e["estimate"] == 0.05 and e["se"] == 0 and e["lower"] == e["upper"] == 0.05


def test_stratified_estimate_validates_input():
    assert raises(stratified_estimate, [])
    assert raises(stratified_estimate, [{"name": "x", "size": 10, "sample": 20, "errors": 1}])
    assert raises(stratified_estimate, [{"name": "x", "size": 10, "sample": 5, "errors": 6}])


def test_decision_rule():
    assert decide({"estimate": 0.03, "lower": 0.02, "upper": 0.04}, 0.05)["decision"] == "ACCEPT"
    assert decide({"estimate": 0.09, "lower": 0.07, "upper": 0.11}, 0.05)["decision"] == "REJECT"
    d = decide({"estimate": 0.045, "lower": 0.03, "upper": 0.06}, 0.05)
    assert d["decision"] == "INCONCLUSIVE" and d["approx_total_sample_needed"] > 1000   # the estimate is close to the threshold
    assert decide({"estimate": 0.05, "lower": 0.04, "upper": 0.06}, 0.05)["decision"] == "INCONCLUSIVE"


def test_psi_known_values_and_properties():
    assert psi([50, 50], [50, 50]) == 0
    assert close(psi([0.5, 0.5], [0.4, 0.6]), 0.040546, 1e-6)
    assert close(psi([500, 300, 200], [350, 300, 350]), psi([350, 300, 350], [500, 300, 200]))   # symmetric
    assert math.isfinite(psi([10, 0], [5, 5]))                                              # empty bins do not break it
    assert [interpret_psi(x)[:6] for x in (0.05, 0.137, 0.3)] == ["stable", "modera", "major "]
    assert raises(psi, [1, 2], [1]) and raises(psi, [], []) and raises(psi, [0, 0], [1, 1])


def test_expected_calibration_error():
    well = [0.9] * 10
    assert close(expected_calibration_error(well, [True] * 9 + [False]), 0.0, 1e-12)
    over = [0.95] * 10
    assert close(expected_calibration_error(over, [True] * 7 + [False] * 3), 0.25, 1e-12)
    rows = reliability_table([0.2, 0.25, 0.9], [False, True, True], bins=5)
    assert sum(r[3] for r in rows) == 3
    assert raises(expected_calibration_error, [1.2], [True]) and raises(expected_calibration_error, [0.5], [True, False])


def test_interval_coverage_simulation():
    cw = coverage(wilson_interval, 0.05, 100, trials=3000)
    assert 0.92 <= cw <= 0.98                                                  # close to the nominal 95%
    assert coverage(wald_interval, 0.01, 50, trials=3000) < 0.5                # the textbook interval fails at low rates
    assert coverage(clopper_pearson, 0.01, 50, trials=1500) >= 0.94           # the exact interval keeps its promise


def test_stratification_reduces_variance_when_error_rates_differ():
    sizes, rates = [30000, 15000, 5000], [0.005, 0.03, 0.20]
    std = {i: (r * (1 - r)) ** 0.5 for i, r in enumerate(rates)}
    alloc = stratified_allocation(dict(enumerate(sizes)), 600, std)
    v_str = variance_stratified(sizes, rates, [alloc[i] for i in range(3)])
    assert v_str < variance_srs(sizes, rates, 600)
    same = [0.05, 0.05, 0.05]   # no gain when every stratum has the same rate
    prop = stratified_allocation(dict(enumerate(sizes)), 600)
    assert close(variance_stratified(sizes, same, [prop[i] for i in range(3)]), variance_srs(sizes, same, 600), 1e-6)


def test_demo_data_and_report():
    strata = load_strata(os.path.join(ROOT, "data", "strata.csv"))
    assert sum(s["sample"] for s in strata) == 600 and sum(s["size"] for s in strata) == 50000
    text = build_report(os.path.join(ROOT, "data"), simulate_trials=800)
    for h in ("How many items to review", "Where to spend the review budget", "What the review found", "acceptance sampling plan",
              "Drift", "Calibration", "Why the interval method matters", "Decision against a 5% error budget: ACCEPT"):
        assert h in text


def test_cli_commands():
    assert main(["plan", "--margin", "0.03"]) == 0
    assert main(["estimate", os.path.join(ROOT, "data", "strata.csv"), "--threshold", "0.05"]) == 0
    assert main(["drift", "--expected", "500,300,200", "--actual", "350,300,350"]) == 0
    assert main(["acceptance", "--aql", "0.01", "--ltpd", "0.05"]) == 0
