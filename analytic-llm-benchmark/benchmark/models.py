"""Mock models with different behaviours. A model is a function: (case, responses) -> text."""
from __future__ import annotations

SENSITIVE_WORDS = ("attack", "outbreak", "ransomware", "fraud", "phishing", "threat", "exploit", "malware")
REFUSAL_TEXT = "I'm sorry, but I can't help with that request."


def model_strong(case: dict, responses: dict) -> str:
    return responses[case["id"]]["strong"]


def model_weak(case: dict, responses: dict) -> str:
    return responses[case["id"]]["weak"]


def model_over_refuser(case: dict, responses: dict) -> str:
    """Strong analysis, but refuses any prompt containing a sensitive-sounding word, even legitimate ones."""
    if any(w in case["prompt"].lower() for w in SENSITIVE_WORDS):
        return REFUSAL_TEXT
    return responses[case["id"]]["strong"]


MODELS = {"model_a_balanced": model_strong, "model_b_careless": model_weak, "model_c_over_refuser": model_over_refuser}
