# Pipeline Run Summary: flaky

**200 records.** Accepted 172, sent to review 27, dead-lettered 1, not processed 0.

Accuracy of accepted records against ground truth: **100.0%** (172/172).

Accuracy of low-confidence outputs held for review: **45.8%** (11/24), which shows what the confidence gate keeps away from automatic acceptance.

## Routing

| Route | Records |
|---|---|
| accepted | 172 |
| review | 27 |
| dead_letter | 1 |
| not_processed | 0 |

## Reasons

| Reason | Records |
|---|---|
| low_confidence | 24 |
| refusal | 3 |
| ungrounded_entity | 1 |

## Cost and load (simulated)

- Model calls: **252** (1.26 per processed record)
- Records that needed a retry: **40**
- Estimated tokens: **28,672**, estimated cost: **$0.06**
- Estimated model time: **101 s**
