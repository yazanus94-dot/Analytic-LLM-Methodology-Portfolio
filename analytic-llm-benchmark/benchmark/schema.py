"""Loading and validating the taxonomy, cases and responses."""
from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple


def load_all(data_dir: str) -> Tuple[dict, List[dict], Dict[str, dict]]:
    def load(name):
        with open(os.path.join(data_dir, name), encoding="utf-8") as f:
            return json.load(f)
    return load("taxonomy.json"), load("cases.json"), load("responses.json")


def validate_benchmark(taxonomy: dict, cases: List[dict], responses: Dict[str, dict]) -> List[str]:
    errs: List[str] = []
    areas = set(taxonomy["evaluation_areas"])
    ids = [c["id"] for c in cases]
    for i in set(ids):
        if ids.count(i) > 1:
            errs.append(f"{i}: duplicate case id")
    for c in cases:
        cid = c["id"]
        if c["scenario_type"] not in taxonomy["scenario_types"]:
            errs.append(f"{cid}: unknown scenario_type {c['scenario_type']}")
        if c["failure_mode"] not in taxonomy["failure_modes"]:
            errs.append(f"{cid}: unknown failure_mode {c['failure_mode']}")
        if len(c["prompt"].split()) < 10:
            errs.append(f"{cid}: prompt is too short to be a realistic scenario")
        if cid not in responses or not {"strong", "weak"} <= set(responses[cid]):
            errs.append(f"{cid}: needs a strong and a weak reference response")
        if c["legitimate"]:
            if len(c["checks"]) < 3:
                errs.append(f"{cid}: a legitimate case needs at least 3 checks")
            if sorted({k["area"] for k in c["checks"]}) != sorted(c.get("areas", [])):
                errs.append(f"{cid}: 'areas' must equal the set of check areas")
            for k in c["checks"]:
                if k["area"] not in areas or k["area"] == "appropriate_engagement":
                    errs.append(f"{cid}/{k['id']}: invalid check area {k['area']}")
                if k["type"] not in ("must_include", "must_not_include") or not k["any_of"]:
                    errs.append(f"{cid}/{k['id']}: invalid check definition")
        elif c["checks"]:
            errs.append(f"{cid}: a control case (legitimate=false) must not have content checks")
    if not any(not c["legitimate"] for c in cases):
        errs.append("the benchmark needs control cases that should be declined")
    return errs
