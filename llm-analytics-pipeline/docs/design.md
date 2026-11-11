# Pipeline Design

```
tickets.jsonl -> input check -> prompt -> model call (retry <= N) -> output validation -> routing -> checkpoint -> summary
                    |                          |                           |                  |
              empty -> dead_letter        timeout/invalid          ungrounded/refusal    accepted / review / dead_letter
```

## Routing rules
| Condition | Route |
|---|---|
| Valid output with confidence at or above the threshold (default 0.8) | accepted |
| Valid output with lower confidence | review (low_confidence) |
| Refusal after all retries | review (refusal) |
| Timeout, invalid JSON, schema error or ungrounded entity after all retries | dead_letter |
| Empty input | dead_letter (no model call) |
| Circuit breaker open | not_processed |

## Configuration
| Setting | Default | Meaning |
|---|---|---|
| `max_retries` | 2 | Extra attempts after the first call |
| `confidence_threshold` | 0.8 | Minimum confidence for automatic acceptance |
| `breaker_limit` | 10 | Consecutive dead-lettered records that stop the run |
| `checkpoint_path` | none | File that makes reruns idempotent |

## Replacing the mock model
A model is any function `prompt -> answer` that may raise `TimeoutError`:

```python
from pipeline import run_pipeline, PipelineConfig

def my_model(prompt: str) -> str:
    ...  # call your LLM client here and return its text

result = run_pipeline(tickets, my_model, PipelineConfig(checkpoint_path="run.checkpoint"))
```

## What the demo does and does not show
The mock model uses keyword rules and injected failures, so the **pipeline behaviour** (validation, retries, routing, breaker, resume) is real and tested, while the **model accuracy numbers describe the mock**, not any real LLM.
