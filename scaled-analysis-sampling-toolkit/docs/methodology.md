# Methodology: Judging Automated Analysis at Scale

## The problem
An LLM pipeline labels, enriches or summarises tens of thousands of records. Nobody can review them all, the model's stated confidence may be misleading, and a wrong answer repeated at scale is expensive. The question is: **how many records must a person review, which ones, and what do the results allow us to conclude?**

## Method in six steps
| Step | Tool | Rule of thumb |
|---|---|---|
| 1. Decide the error budget | A business decision | "No more than 5% of records may be wrong" |
| 2. Choose the sample size | `required_sample_size` | About 385 reviews gives +/-5% and about 1,068 gives +/-3%, whatever the population size |
| 3. Stratify | `stratified_allocation` | Split records by model confidence or risk and review more where errors are likely |
| 4. Estimate with an honest interval | `stratified_estimate`, Wilson and Clopper-Pearson | Report the interval, not only the point estimate |
| 5. Decide | `decide` | ACCEPT only if the whole interval is below the budget; REJECT if it is wholly above; otherwise review more |
| 6. Monitor | `find_acceptance_plan`, `psi`, calibration | Sample every batch and watch for drift and miscalibration |

## Why each choice matters
- **Stratifying** puts the review effort where the errors are. In the worked example it needs about 57% of the variance of a simple random sample of the same size.
- **Confidence is not correctness.** A model can be overconfident in every bin (expected calibration error 0.144 in the example). Use reviewed samples, not self-reported confidence, to decide.
- **Review only flagged items and recall is invisible.** An estimate of precision from flagged records says nothing about what was missed. Sample the unflagged records too.
- **Intervals must be right at low error rates.** The textbook (Wald) interval collapses to zero width when no error is found, and in the example its real coverage is 39.6% against a nominal 95%. Wilson reaches 90.5% and the exact Clopper-Pearson interval 98.5% in the same simulation.
- **Acceptance sampling** turns monitoring into a rule: review n records per batch and accept it if at most c defects are found, with the false-accept and false-reject risks stated up front.
- **Drift** (PSI) catches a change in the label mix before accuracy checks do. A PSI under 0.1 is stable, 0.1 to 0.25 needs investigation, and 0.25 or more means stop.

## Decision rule
| Interval versus the error budget | Decision |
|---|---|
| Entirely below | ACCEPT |
| Entirely above | REJECT |
| Straddles the budget | INCONCLUSIVE: review more (an estimate of the total sample needed is given) |

## Assumptions and limits
- Reviewers are correct. If reviewers disagree, measure their agreement first (see the Data Annotation Quality Toolkit) and add reviewer error to the interval.
- Records are independent. Clustered data (many records from one customer) needs a larger sample than these formulas give.
- Strata must be fixed before sampling. Choosing strata after seeing the results biases the estimate.
- The normal interval used for the stratified total is an approximation; with very few errors in a stratum, report that stratum's exact interval too.
- Sample sizes assume simple random sampling inside each stratum.
