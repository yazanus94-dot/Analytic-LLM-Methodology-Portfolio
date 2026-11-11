"""Named failure scenarios for the mock model."""
SCENARIOS = {
    "clean": {},
    "flaky": {"invalid_json": 0.08, "timeout": 0.05, "hallucinated_entity": 0.05, "over_refusal": 0.30, "wrong_schema": 0.03},
    "degraded": {"timeout": 0.85, "invalid_json": 0.20},
}
