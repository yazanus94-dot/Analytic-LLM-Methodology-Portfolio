"""A deterministic mock LLM with injectable failure modes, so pipeline behaviour can be tested offline.

Any real model client can replace it: a model is a function  prompt (str) -> answer (str)  that may raise TimeoutError.
"""
from __future__ import annotations

import json
import random
import re
from typing import Dict

from .prompts import extract_ticket

SYSTEMS = ["payments-api", "auth-service", "billing-db", "search-index", "mobile-gateway", "report-engine"]
RULES = [
    ("security_alert", ("suspicious", "unauthorized", "phishing", "breach")),
    ("outage", (" is down", "unavailable", "outage")),
    ("billing", ("invoice", "charged", "refund")),
    ("performance", ("slow", "latency", "take minutes")),
    ("access_request", ("password reset", "permission")),
    ("feature_question", ("how do i", "is it possible")),
]
PRIORITY = {"outage": 1, "security_alert": 1, "performance": 3, "billing": 3, "access_request": 4, "feature_question": 4}
ENTITY = re.compile(r"\b(?:E-\d{3}|CUST-\d{4})\b")
REFUSAL = "I'm sorry, but I can't help with that request."


class MockLLM:
    """rates: probability per call of each failure mode (see FAILURE_MODES)."""

    FAILURE_MODES = ("timeout", "invalid_json", "wrong_schema", "hallucinated_entity", "over_refusal")

    def __init__(self, rates: Dict[str, float] | None = None, seed: int = 0):
        rates = rates or {}
        unknown = set(rates) - set(self.FAILURE_MODES)
        if unknown:
            raise ValueError(f"unknown failure modes: {sorted(unknown)}")
        self.rates, self.rnd, self.calls = rates, random.Random(seed), 0

    def _correct(self, text: str) -> dict:
        low = text.lower()
        hits = [cat for cat, words in RULES if any(w in low for w in words)]
        category = hits[0] if hits else "feature_question"
        entities = [s for s in SYSTEMS if s in text] + ENTITY.findall(text)
        return {"category": category, "priority": PRIORITY[category],
                "confidence": 0.55 if len(hits) > 1 else 0.95, "entities": entities}

    def __call__(self, prompt: str) -> str:
        self.calls += 1
        text = extract_ticket(prompt)
        draw = {m: self.rnd.random() < self.rates.get(m, 0.0) for m in self.FAILURE_MODES}
        if draw["timeout"]:
            raise TimeoutError("model did not answer in time")
        if draw["over_refusal"] and any(w in text.lower() for w in ("suspicious", "unauthorized", "phishing")):
            return REFUSAL
        out = self._correct(text)
        if draw["hallucinated_entity"]:
            out["entities"].append("CUST-9999")
        if draw["wrong_schema"]:
            out["priority"] = "high"
        raw = json.dumps(out)
        if draw["invalid_json"]:
            return "Sure! Here is the result: " + raw
        return raw
