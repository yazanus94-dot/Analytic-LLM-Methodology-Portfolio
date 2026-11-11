# Analytic LLM Methodology Portfolio

[![Tests](https://github.com/yazanus94-dot/Analytic-LLM-Methodology-Portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/yazanus94-dot/Analytic-LLM-Methodology-Portfolio/actions/workflows/ci.yml)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Three projects answering one question from three angles: **how do you put an
LLM into an analytic pipeline and stay honest about it?** One measures the
model (a benchmark with a failure-mode taxonomy), one bounds it (a production
pipeline with validation, grounding checks and a circuit breaker), one
statistically audits it (sampling theory for reviewing 50,000 outputs with a
600-review budget). All three run offline and reproducibly with deterministic
mocks — the methodology is the product, not any particular model.

| # | Project | Role | Validation |
|---|---------|------|------------|
| 1 | [analytic-llm-benchmark](analytic-llm-benchmark/) | **Measure** — a benchmark for LLMs used in analytic work: 20 authored cases (16 legitimate tasks + 4 should-decline controls), 3 scenario types, 5 evaluation areas, 13 failure modes (sampling bias, hallucinated source, dropped records, unit error, overconfident extrapolation, over-refusal…) | 14 tests; grader + report with confidence intervals; detects balanced vs careless vs over-refusing model behaviour |
| 2 | [llm-analytics-pipeline](llm-analytics-pipeline/) | **Bound** — batch triage/enrichment of IT tickets with strict JSON + schema validation, refusal detection, **grounding checks** (every extracted entity must appear in the source), bounded retries, human-review routing, circuit breaker, idempotent resume | 14 tests incl. injectable-failure scenarios (`run-clean`, `run-flaky`, `run-degraded`); **no record is ever silently dropped** |
| 3 | [scaled-analysis-sampling-toolkit](scaled-analysis-sampling-toolkit/) | **Audit** — sample-size planning (n = 1,068 for ±3%), stratified review allocation across confidence tiers, Wilson/Agresti-Coull intervals, a go/no-go decision rule, acceptance sampling, drift detection and calibration | 17 tests against known values and simulations; worked example regenerates `reports/example-analysis.md` |

## The methodology, not the model

- **Mock-first, reproducible.** Deterministic model mocks with injectable
  behaviours mean every result regenerates identically — and a real model
  swaps in behind one function.
- **Failure modes are first-class.** The benchmark names 13 ways an LLM fails
  an analytic task; the pipeline defends against the operational ones; the
  toolkit quantifies the residual risk statistically.
- **Refusal is measured, not assumed.** Over-refusal and under-refusal are
  scored as first-class failure modes, with should-decline control cases.
- **Numbers with intervals.** Every reported proportion ships with an honest
  confidence interval, and review effort is allocated where errors concentrate.

## Quick start

```bash
# 1. Benchmark: grade 20 analytic cases across three mock models
cd analytic-llm-benchmark
python -m pytest -q
python -m benchmark            # writes reports/benchmark-results.md

# 2. Pipeline: triage + enrich 200 synthetic tickets, three failure scenarios
cd ../llm-analytics-pipeline
python -m pytest -q
python -m pipeline             # writes reports/run-*.md

# 3. Sampling toolkit: plan, allocate, audit a 50,000-record run
cd ../scaled-analysis-sampling-toolkit
python -m pytest -q
python -m sampling report      # writes reports/example-analysis.md
```

CI runs all three suites and CLIs on Python 3.11 / 3.12 / 3.13.

## Scope

Portfolio projects by Yazan Aljabari. All data is synthetic and seeded; the
"models" are deterministic mocks chosen to demonstrate what the measurement
tools can detect, and do not describe any real LLM.

## License

MIT, see [LICENSE](LICENSE).
