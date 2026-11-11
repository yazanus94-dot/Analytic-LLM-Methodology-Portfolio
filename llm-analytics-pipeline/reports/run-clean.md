# Pipeline Run Summary: clean

**200 records.** Accepted 175, sent to review 25, dead-lettered 0, not processed 0.

Accuracy of accepted records against ground truth: **100.0%** (175/175).

Accuracy of low-confidence outputs held for review: **48.0%** (12/25), which shows what the confidence gate keeps away from automatic acceptance.

## Routing

| Route | Records |
|---|---|
| accepted | 175 |
| review | 25 |
| dead_letter | 0 |
| not_processed | 0 |

## Reasons

| Reason | Records |
|---|---|
| low_confidence | 25 |

## Cost and load (simulated)

- Model calls: **200** (1.00 per processed record)
- Records that needed a retry: **0**
- Estimated tokens: **22,746**, estimated cost: **$0.05**
- Estimated model time: **80 s**
