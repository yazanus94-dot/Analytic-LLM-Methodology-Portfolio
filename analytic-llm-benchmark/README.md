# Analytic LLM Benchmark

A small, extensible **evaluation benchmark for LLMs used in analytic pipelines**: a taxonomy, 20 authored analytic cases, an automatic grader, over-refusal and under-refusal measurement, and a report with confidence intervals. It covers automated triage, enrichment and analysis at scale, and the failure modes that matter in each.

> The three "models" are deterministic mocks with different behaviours (balanced, careless, over-refusing), so the benchmark runs offline and the results are reproducible. They show what the benchmark can detect; they do not describe any real model.

## What is in the benchmark
| Element | Detail |
|---|---|
| Taxonomy | 3 scenario types, 5 evaluation areas (source handling, reasoning, limitations awareness, practical utility, appropriate engagement), 13 failure modes |
| Cases | 20: 16 legitimate analytic tasks and 4 control cases that should be declined |
| Failure modes tested | Sampling bias, hallucinated source, dropped records, unit error, overconfident extrapolation, data quality, multiple comparisons, nonresponse bias, citation error, correlation as causation, drift, over-refusal |
| Grading | Automatic checks per area, a refusal detector, human verification step documented |
| Statistics | Mean score with a 95% bootstrap confidence interval, scores by area and scenario type |

## Results on the mock models
| Model | Mean score | 95% CI | Over-refusal | Under-refusal |
|---|---|---|---|---|
| Balanced | 100.0 | 100 to 100 | 0% | 0% |
| Careless (complies, shallow analysis) | 24.6 | 17.5 to 30.8 | 0% | 100% |
| Over-refuser (refuses sensitive-sounding words) | 70.0 | 50.0 to 90.0 | 38% (6 of 16) | 0% |

The over-refuser declines legitimate work such as security log triage, an outbreak summary, a ransomware headline tag, fraud-pattern summarisation and a phishing email check. It scores 70 despite strong analysis elsewhere, which shows why refusals have to be measured separately from accuracy.

## Run it
```bash
python -m benchmark data --out reports        # validates, grades the three mock models, writes the report
pytest -q
```
Output: `reports/benchmark-results.md` (overall, by area, by scenario type, most discriminating cases, over-refusal findings, taxonomy coverage grid).

## Test your own model
A model is a function `(case, responses) -> text`. Replace it with a call to your model that uses `case["prompt"]`, add it to `benchmark/models.py`, and run the benchmark.

## Project contents
| Path | Purpose |
|---|---|
| `data/taxonomy.json` | Scenario types, evaluation areas, failure modes |
| `data/cases.json` | The 20 cases with checks |
| `data/responses.json` | Strong and weak reference answers (the tests prove the strong ones pass every check and the weak ones fail) |
| `benchmark/grader.py` | Checks, refusal detector, scoring |
| `benchmark/metrics.py` | Aggregation and bootstrap confidence intervals |
| `docs/authoring-guide.md` | How to write new analytic cases |
| `docs/grading-guide.md` | Scoring rules, what each area rewards, human verification |
| `tests/` | 14 automated tests |

## Skills demonstrated
Evaluation framework and benchmark design, taxonomy mapping, authoring analytic cases from realistic deployment patterns, grading on source handling, reasoning, limitations and practical utility, over-refusal detection, statistical reporting, Python, test automation, technical documentation.

## Author
Yazan Aljabari - QA Engineer
