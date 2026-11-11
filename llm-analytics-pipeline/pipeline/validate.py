"""Output validation: parse, schema, refusal and grounding checks."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Optional

from .prompts import CATEGORIES

REFUSAL_PATTERN = re.compile(r"\b(i can't|i cannot|i'm sorry|i am sorry|unable to help|can't help with)\b", re.IGNORECASE)


@dataclass
class Verdict:
    ok: bool
    reason: str = ""
    data: Optional[dict] = None


def validate_output(raw: str, source_text: str) -> Verdict:
    """Return Verdict(ok, reason, data). Reasons: refusal, invalid_json, schema_error, ungrounded_entity."""
    if REFUSAL_PATTERN.search(raw) and not raw.lstrip().startswith("{"):
        return Verdict(False, "refusal")
    try:
        data = json.loads(raw)
    except ValueError:
        return Verdict(False, "invalid_json")
    if not isinstance(data, dict):
        return Verdict(False, "schema_error")
    cat, prio, conf, ents = data.get("category"), data.get("priority"), data.get("confidence"), data.get("entities")
    if cat not in CATEGORIES:
        return Verdict(False, "schema_error")
    if isinstance(prio, bool) or not isinstance(prio, int) or not 1 <= prio <= 4:
        return Verdict(False, "schema_error")
    if isinstance(conf, bool) or not isinstance(conf, (int, float)) or not 0 <= conf <= 1:
        return Verdict(False, "schema_error")
    if not isinstance(ents, list) or not all(isinstance(e, str) for e in ents):
        return Verdict(False, "schema_error")
    if any(e not in source_text for e in ents):  # grounding: every entity must literally appear in the source
        return Verdict(False, "ungrounded_entity")
    return Verdict(True, "", data)
