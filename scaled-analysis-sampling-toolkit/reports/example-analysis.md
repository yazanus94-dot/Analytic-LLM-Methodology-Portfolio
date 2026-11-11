# Worked Example: Can We Trust 50,000 LLM-Labelled Records?

An LLM labelled 50,000 records and reported a confidence for each. Reviewing all of them is too expensive, so a sample is reviewed and the result decides whether the automated output can be used.

## 1. How many items to review

| Margin of error | Sample size (unknown rate) | With a population of 50,000 |
|---|---|---|
| +/-5% | 385 | 382 |
| +/-3% | 1068 | 1045 |
| +/-2% | 2401 | 2291 |
| +/-1% | 9604 | 8057 |

## 2. Where to spend the review budget

The records fall into three confidence tiers. With a budget of 600 reviews:

| Tier | Records | Proportional | Allocation used (Neyman) |
|---|---|---|---|
| high_confidence | 30,000 | 360 | 190 |
| medium_confidence | 15,000 | 180 | 230 |
| low_confidence | 5,000 | 60 | 180 |

Assuming error rates of 0.5%, 3% and 20% across the tiers, the stratified plan has a standard error of **0.54%** against **0.71%** for a simple random sample of the same size, so it needs about **57%** of the variance. Review effort goes where the errors are.

## 3. What the review found

| Tier | Reviewed | Errors | Rate | 95% Wilson interval |
|---|---|---|---|---|
| high_confidence | 190 | 1 | 0.5% | 0.1% to 2.9% |
| medium_confidence | 230 | 8 | 3.5% | 1.8% to 6.7% |
| low_confidence | 180 | 36 | 20.0% | 14.8% to 26.4% |

**Overall error rate: 3.36%** (95% interval 2.26% to 4.46%).

**Decision against a 5% error budget: ACCEPT**, because the upper bound 4.46% is below the 5.00% threshold.

Practical reading: the 5,000 low-confidence records carry most of the errors, so they should go to people, while the high-confidence tier can be accepted with periodic sampling.

## 4. Continuous monitoring: an acceptance sampling plan

To accept good batches (1% defects) with 95% probability and reject bad batches (5% defects) with 90% probability, review **132** records per batch and accept the batch if **3 or fewer** defects are found. Check: P(accept | 1%) = 95.6%, P(accept | 5%) = 9.9%.

## 5. Drift: has the label mix changed?

| Label | Last month | This week |
|---|---|---|
| routine | 500 | 350 |
| elevated | 300 | 300 |
| urgent | 200 | 350 |

PSI = **0.137**, interpretation: **moderate shift: investigate**.

## 6. Calibration: is the stated confidence trustworthy?

| Confidence bin | Mean confidence | Accuracy | Gap | Items |
|---|---|---|---|---|
| ~0.55 | 0.55 | 0.42 | +0.13 | 153 |
| ~0.70 | 0.70 | 0.53 | +0.17 | 325 |
| ~0.90 | 0.90 | 0.77 | +0.13 | 322 |

Expected calibration error: **0.144**. The model is overconfident in every bin, so its confidence must be recalibrated, or replaced by review results, before it is used as a threshold.

## 7. Why the interval method matters

Coverage of a nominal 95% interval for a true error rate of 1% and 50 reviewed items (4000 simulated samples):

| Method | Actual coverage |
|---|---|
| Wilson | 90.5% |
| Clopper-Pearson (exact) | 98.5% |
| Wald (textbook) | 39.6% |

The textbook interval fails exactly where analytic work needs it: a low error rate and a modest sample. With zero errors found it reports a zero-width interval, which would wrongly suggest certainty. Wilson is far closer to the nominal level but still falls a little short at very low rates; the exact Clopper-Pearson interval is conservative and keeps its promise. For a go/no-go decision on a small sample, prefer the exact interval.
