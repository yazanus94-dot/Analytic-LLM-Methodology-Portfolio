# LLM Analytics Pipeline

A Python pipeline that sends batches of records through an LLM for **automated triage and enrichment at scale**, with the safeguards a production analytic pipeline needs: output validation, grounding checks, bounded retries, human-review routing, a circuit breaker and idempotent resume. It is built to show how LLMs are integrated into data pipelines and how automation fails.

> The model here is a deterministic **mock** with injectable failures, so everything runs offline and reproducibly. The tickets are synthetic. Swap in a real model with a one-line function (see `docs/design.md`).

## What it does
- Triage: category, priority and confidence for each IT incident ticket
- Enrichment: extracts system names, error codes and customer ids
- Validates every answer: strict JSON, schema, refusal detection, and a **grounding check** (every extracted entity must appear in the source text)
- Retries, then routes each record to `accepted`, `review` or `dead_letter`, so **no record is ever silently dropped**
- Stops runaway failures with a **circuit breaker** and resumes safely from a checkpoint
- Reports routing, reasons, retries, simulated cost and accuracy

## Results from the three demo scenarios
| Scenario | Accepted | Review | Dead-letter | Not processed | Note |
|---|---|---|---|---|---|
| clean | 175 | 25 | 0 | 0 | The confidence gate holds back ambiguous tickets (their outputs are right only 48% of the time) |
| flaky | 172 | 27 | 1 | 0 | Retries recover most failures; accepted records stay 100% correct; 3 refusals are routed to review |
| degraded | 14 | 4 | 41 | 141 | The circuit breaker halts the run instead of retrying a failing model for every record |

## Run it
```bash
python scripts/generate_tickets.py              # regenerate the 200 synthetic tickets
python -m pipeline --scenario flaky             # clean | flaky | degraded
pytest -q
```
Reports are written to `reports/run-<scenario>.md`.

## Project contents
| Path | Purpose |
|---|---|
| `pipeline/runner.py` | Retry loop, routing, circuit breaker, checkpoint, summary |
| `pipeline/validate.py` | JSON, schema, refusal and grounding checks |
| `pipeline/models.py` | Mock LLM with five failure modes |
| `pipeline/scenarios.py` | clean, flaky and degraded failure profiles |
| `docs/failure-modes.md` | Catalogue of ten failure modes with detection and mitigation |
| `docs/design.md` | Flow, routing rules, configuration, how to plug in a real model |
| `tests/` | 14 automated tests |

## Skills demonstrated
LLM pipeline integration, automation failure modes, validation and grounding, over-refusal handling, scaled-analysis judgment, Python, test automation, technical documentation.

## Author
Yazan Aljabari - QA Engineer
