# Failure Modes of LLM Analytic Pipelines

| Failure mode | What happens | Detection in this project | Mitigation |
|---|---|---|---|
| Timeout | The model does not answer | `TimeoutError` caught per call | Retry up to a limit, then dead-letter |
| Invalid JSON | Extra text around the data, or truncated output | Strict `json.loads` of the full answer | Retry; never repair silently |
| Schema drift | Right JSON, wrong types or values (priority "high") | Field-by-field schema check | Retry; dead-letter after the limit |
| Hallucinated entity | The model adds a customer id or system not in the source | **Grounding check**: every entity must literally appear in the source text | Reject and retry; never accept ungrounded output |
| Over-refusal | The model refuses a legitimate task (for example a security ticket) | Refusal pattern on non-JSON answers | Route to human review, count it, do not drop the record |
| Low confidence | The model is unsure, often on ambiguous inputs | Confidence below the threshold | Route to review instead of automatic acceptance |
| Silent record loss | Failed records disappear from the results | Invariant: accepted + review + dead-letter + not processed equals input | Tests assert it in every scenario |
| Runaway cost | A failing model is retried across the whole batch | Circuit breaker on consecutive failures | Halt, mark the rest `not_processed`, resume later |
| Reprocessing | A restart repeats finished work | Checkpoint file of finished record ids | Idempotent resume |
| False confidence | High confidence is mistaken for correctness | Reported accuracy of accepted and low-confidence outputs | Sample accepted records for review (see the Scaled Analysis Sampling Toolkit) |

## Design principles
1. **Never trust model output unchecked.** Parse, validate the schema, and verify grounding against the source.
2. **Every record ends in a known state.** Nothing is silently dropped.
3. **Fail loudly and cheaply.** Retries are bounded and a circuit breaker stops runaway spend.
4. **Refusals are data.** A legitimate request that is refused is routed to a person and measured.
5. **Resume safely.** A checkpoint makes reruns idempotent.
