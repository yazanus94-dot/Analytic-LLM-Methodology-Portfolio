"""Pipeline: validate input, call the model with retries, validate output, route, checkpoint, summarise."""
from __future__ import annotations

import json
import os
from collections import Counter
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional

from .prompts import build_prompt
from .validate import validate_output

COST_PER_1K_TOKENS = 0.002   # simulated
LATENCY_MS_PER_CALL = 400    # simulated


@dataclass
class PipelineConfig:
    max_retries: int = 2
    confidence_threshold: float = 0.8
    breaker_limit: int = 10          # stop after this many consecutive failed records
    checkpoint_path: Optional[str] = None


@dataclass
class RunResult:
    records: List[dict] = field(default_factory=list)
    halted: bool = False
    calls: int = 0
    tokens: int = 0

    def counts(self) -> Counter:
        return Counter(r["route"] for r in self.records)


def _tokens(text: str) -> int:
    return int(len(text.split()) * 1.3) + 1


def process_record(ticket: dict, llm: Callable[[str], str], cfg: PipelineConfig, stats: RunResult) -> dict:
    text = (ticket.get("text") or "").strip()
    if not text:
        return {"id": ticket.get("id"), "route": "dead_letter", "reason": "empty_input", "attempts": 0}
    prompt, reason = build_prompt(text), ""
    for attempt in range(1, cfg.max_retries + 2):
        stats.calls += 1
        stats.tokens += _tokens(prompt)
        try:
            raw = llm(prompt)
        except TimeoutError:
            reason = "timeout"
            continue
        stats.tokens += _tokens(raw)
        verdict = validate_output(raw, text)
        if verdict.ok:
            d = verdict.data
            route = "accepted" if d["confidence"] >= cfg.confidence_threshold else "review"
            return {"id": ticket["id"], "route": route, "reason": "" if route == "accepted" else "low_confidence",
                    "attempts": attempt, "output": d}
        reason = verdict.reason
    route = "review" if reason == "refusal" else "dead_letter"   # a refusal is a quality issue: keep it visible for people
    return {"id": ticket["id"], "route": route, "reason": reason, "attempts": cfg.max_retries + 1}


def load_checkpoint(path: Optional[str]) -> Dict[str, dict]:
    done: Dict[str, dict] = {}
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                done[r["id"]] = r
    return done


def run_pipeline(tickets: Iterable[dict], llm: Callable[[str], str], cfg: Optional[PipelineConfig] = None) -> RunResult:
    cfg = cfg or PipelineConfig()
    done = load_checkpoint(cfg.checkpoint_path)
    stats, consecutive = RunResult(), 0
    ckpt = open(cfg.checkpoint_path, "a", encoding="utf-8") if cfg.checkpoint_path else None
    try:
        for t in tickets:
            if t.get("id") in done:                       # idempotent resume: never reprocess a finished record
                stats.records.append(done[t["id"]])
                continue
            if stats.halted:
                stats.records.append({"id": t.get("id"), "route": "not_processed", "reason": "circuit_open", "attempts": 0})
                continue
            rec = process_record(t, llm, cfg, stats)
            stats.records.append(rec)
            if ckpt:
                ckpt.write(json.dumps(rec) + "\n"); ckpt.flush()
            consecutive = consecutive + 1 if rec["route"] in ("dead_letter",) else 0
            if consecutive >= cfg.breaker_limit:
                stats.halted = True                        # circuit breaker: stop spending on a failing model
    finally:
        if ckpt:
            ckpt.close()
    return stats


def summarize(result: RunResult, truth: Dict[str, str], scenario: str) -> str:
    n = len(result.records)
    c = result.counts()
    acc_rows = [r for r in result.records if r["route"] == "accepted"]
    correct = sum(1 for r in acc_rows if r["output"]["category"] == truth[r["id"]])
    low = [r for r in result.records if r["route"] == "review" and r.get("output")]
    low_correct = sum(1 for r in low if r["output"]["category"] == truth[r["id"]])
    reasons = Counter(r["reason"] for r in result.records if r["reason"])
    out = [f"# Pipeline Run Summary: {scenario}", "",
           f"**{n} records.** Accepted {c['accepted']}, sent to review {c['review']}, dead-lettered {c['dead_letter']}, "
           f"not processed {c['not_processed']}." + (" **The circuit breaker halted the run.**" if result.halted else ""), "",
           f"Accuracy of accepted records against ground truth: **{(correct / len(acc_rows) if acc_rows else 0):.1%}** ({correct}/{len(acc_rows)}).", "",
           f"Accuracy of low-confidence outputs held for review: **{(low_correct / len(low) if low else 0):.1%}** ({low_correct}/{len(low)}), "
           "which shows what the confidence gate keeps away from automatic acceptance.", "",
           "## Routing", "", "| Route | Records |", "|---|---|"]
    out += [f"| {k} | {c[k]} |" for k in ("accepted", "review", "dead_letter", "not_processed")]
    out += ["", "## Reasons", "", "| Reason | Records |", "|---|---|"]
    out += [f"| {k} | {v} |" for k, v in reasons.most_common()] or ["| none | 0 |"]
    retried = sum(1 for r in result.records if r.get("attempts", 0) > 1)
    out += ["", "## Cost and load (simulated)", "",
            f"- Model calls: **{result.calls}** ({result.calls / max(1, n - c['not_processed']):.2f} per processed record)",
            f"- Records that needed a retry: **{retried}**",
            f"- Estimated tokens: **{result.tokens:,}**, estimated cost: **${result.tokens / 1000 * COST_PER_1K_TOKENS:.2f}**",
            f"- Estimated model time: **{result.calls * LATENCY_MS_PER_CALL / 1000:.0f} s**"]
    return "\n".join(out) + "\n"
