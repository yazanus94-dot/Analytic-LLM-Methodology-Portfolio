# Scaled Analysis Sampling Toolkit

A statistical toolkit for the question that decides whether an LLM pipeline can run at scale: **can we trust the output of 50,000 automated analyses, and how many should a person review?** It covers sample-size planning, stratified review allocation, honest confidence intervals, a decision rule, acceptance sampling, drift detection and calibration, all in pure Python with tests against known values and simulations.

> The records and review results are **synthetic** (seeded), created to demonstrate the method. Run `python -m sampling report` to regenerate the worked example.

## Worked example (from `reports/example-analysis.md`)
An LLM labelled 50,000 records in three confidence tiers. With a review budget of 600:

| Step | Result |
|---|---|
| Sample size for +/-3% (unknown rate) | 1,068 reviews (1,045 for a population of 50,000) |
| Allocation | Proportional: 360 / 180 / 60. Neyman: 190 / 230 / 180, with about 57% of the variance of simple random sampling |
| Review result | 0.5% errors in the high tier, 3.5% in the medium tier, 20.0% in the low tier |
| Overall error rate | 3.36% (95% interval 2.26% to 4.46%) |
| Decision against a 5% error budget | **ACCEPT**: the upper bound is below the budget |
| Batch monitoring plan | Review 132 records per batch, accept if 3 or fewer defects (P(accept at 1% defects) = 95.6%, P(accept at 5%) = 9.9%) |
| Drift check | PSI 0.137: moderate shift, investigate |
| Calibration | Expected calibration error 0.144: the model is overconfident in every bin |
| Interval coverage at a 1% error rate and 50 items | Wilson 90.5%, Clopper-Pearson 98.5%, textbook Wald 39.6% (nominal 95%) |

## What is inside
| Module | Purpose |
|---|---|
| `sampling/planning.py` | Sample size with finite population correction, stratified (Neyman) allocation, acceptance sampling plans |
| `sampling/intervals.py` | Wilson, exact Clopper-Pearson and textbook Wald intervals |
| `sampling/estimation.py` | Stratified estimate with standard error, and the ACCEPT / REJECT / INCONCLUSIVE rule |
| `sampling/drift.py` | Population Stability Index and its interpretation |
| `sampling/calibration.py` | Reliability table and expected calibration error |
| `sampling/simulate.py` | Coverage and variance simulations that check the methods against known truth |
| `docs/methodology.md` | The six-step method, why each choice matters, assumptions and limits |
| `tests/` | 17 automated tests (known values, hand calculations, brute-force minimality, simulations) |

## Command line
```bash
python -m sampling plan --margin 0.03 --population 50000
python -m sampling estimate data/strata.csv --threshold 0.05
python -m sampling acceptance --aql 0.01 --ltpd 0.05
python -m sampling drift --expected 500,300,200 --actual 350,300,350
python -m sampling calibration data/confidence_review.csv
python -m sampling report            # writes reports/example-analysis.md
pytest -q
```

## Why this matters for LLM pipelines
Automation failure modes (silent record loss, drift, overconfident outputs, sampling only flagged items) are statistical problems as much as engineering ones. This toolkit gives the evidence needed to say, with a stated level of confidence, whether automated analysis at scale is good enough, and what to do when it is not.

## Skills demonstrated
Statistical methodology, scaled-analysis judgment, sampling design, confidence intervals, acceptance sampling, drift and calibration monitoring, simulation-based verification, Python, test automation, technical documentation.

## Author
Yazan Aljabari - QA Engineer
