# Pipeline Run Summary: degraded

**200 records.** Accepted 14, sent to review 4, dead-lettered 41, not processed 141. **The circuit breaker halted the run.**

Accuracy of accepted records against ground truth: **100.0%** (14/14).

Accuracy of low-confidence outputs held for review: **50.0%** (2/4), which shows what the confidence gate keeps away from automatic acceptance.

## Routing

| Route | Records |
|---|---|
| accepted | 14 |
| review | 4 |
| dead_letter | 41 |
| not_processed | 141 |

## Reasons

| Reason | Records |
|---|---|
| circuit_open | 141 |
| timeout | 40 |
| low_confidence | 4 |
| invalid_json | 1 |

## Cost and load (simulated)

- Model calls: **159** (2.69 per processed record)
- Records that needed a retry: **54**
- Estimated tokens: **16,521**, estimated cost: **$0.03**
- Estimated model time: **64 s**
