import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from pipeline import SCENARIOS, PipelineConfig, run_pipeline, validate_output  # noqa: E402
from pipeline.models import MockLLM  # noqa: E402
from pipeline.prompts import build_prompt  # noqa: E402
from pipeline.runner import summarize  # noqa: E402

TICKETS = [json.loads(l) for l in open(os.path.join(ROOT, "data", "tickets.jsonl"), encoding="utf-8")]
TRUTH = {t["id"]: t["true_category"] for t in TICKETS}
TEXT = "The payments-api is down and customers get error E-503."


def good(**over):
    d = {"category": "outage", "priority": 1, "confidence": 0.9, "entities": ["payments-api", "E-503"]}
    d.update(over)
    return json.dumps(d)


def test_valid_output_passes():
    v = validate_output(good(), TEXT)
    assert v.ok and v.data["category"] == "outage"


def test_validation_reasons():
    assert validate_output("Sure! " + good(), TEXT).reason == "invalid_json"
    assert validate_output("I'm sorry, but I can't help with that request.", TEXT).reason == "refusal"
    assert validate_output(good(priority="high"), TEXT).reason == "schema_error"
    assert validate_output(good(priority=7), TEXT).reason == "schema_error"
    assert validate_output(good(category="made_up"), TEXT).reason == "schema_error"
    assert validate_output(good(confidence=1.5), TEXT).reason == "schema_error"
    assert validate_output(good(confidence=True), TEXT).reason == "schema_error"
    assert validate_output("[1, 2]", TEXT).reason == "schema_error"
    assert validate_output(good(entities=["payments-api", "CUST-9999"]), TEXT).reason == "ungrounded_entity"


def test_json_that_mentions_sorry_is_not_a_refusal():
    assert validate_output(good(), TEXT + " sorry").ok


def test_mock_model_clean_run_is_accurate_and_complete():
    r = run_pipeline(TICKETS, MockLLM({}, 1))
    c = r.counts()
    assert len(r.records) == 200 and c["dead_letter"] == 0 and not r.halted
    acc = [x for x in r.records if x["route"] == "accepted"]
    assert all(x["output"]["category"] == TRUTH[x["id"]] for x in acc)


def test_no_record_is_silently_dropped_in_any_scenario():
    for name in SCENARIOS:
        r = run_pipeline(TICKETS, MockLLM(SCENARIOS[name], 3))
        assert len(r.records) == len(TICKETS), name
        assert sum(r.counts().values()) == len(TICKETS), name
        assert [x["id"] for x in r.records] == [t["id"] for t in TICKETS]


def test_flaky_run_recovers_with_retries_and_keeps_quality():
    r = run_pipeline(TICKETS, MockLLM(SCENARIOS["flaky"], 1))
    assert not r.halted and r.calls > len(TICKETS)            # retries happened
    assert r.counts()["accepted"] > 150
    acc = [x for x in r.records if x["route"] == "accepted"]
    assert all(x["output"]["category"] == TRUTH[x["id"]] for x in acc)  # hallucinated or invalid outputs never get accepted


def test_hallucinated_entity_is_never_accepted():
    llm = MockLLM({"hallucinated_entity": 1.0}, 0)
    r = run_pipeline(TICKETS[:20], llm, PipelineConfig(max_retries=1, breaker_limit=1000))
    assert all(x["route"] != "accepted" for x in r.records)
    assert {x["reason"] for x in r.records} == {"ungrounded_entity"}


def test_refusals_go_to_review_not_to_the_dead_letter_queue():
    security = [t for t in TICKETS if t["true_category"] == "security_alert"][:10]
    r = run_pipeline(security, MockLLM({"over_refusal": 1.0}, 0), PipelineConfig(max_retries=1))
    assert {x["route"] for x in r.records} == {"review"} and {x["reason"] for x in r.records} == {"refusal"}


def test_circuit_breaker_halts_a_failing_model():
    r = run_pipeline(TICKETS, MockLLM({"timeout": 1.0}, 0), PipelineConfig(max_retries=1, breaker_limit=5))
    c = r.counts()
    assert r.halted and c["dead_letter"] == 5 and c["not_processed"] == len(TICKETS) - 5
    assert r.calls == 5 * 2          # no money spent on the records after the breaker opened


def test_empty_input_is_rejected_before_calling_the_model():
    llm = MockLLM({}, 0)
    r = run_pipeline([{"id": "X", "text": "   "}], llm)
    assert r.records[0]["reason"] == "empty_input" and llm.calls == 0


def test_checkpoint_resume_is_idempotent():
    with tempfile.TemporaryDirectory() as d:
        cfg = PipelineConfig(checkpoint_path=os.path.join(d, "run.checkpoint"))
        first = MockLLM({}, 1)
        run_pipeline(TICKETS[:50], first, cfg)
        second = MockLLM({}, 1)
        r = run_pipeline(TICKETS[:80], second, cfg)
        assert first.calls == 50 and second.calls == 30   # only the new 30 records reached the model
        assert len(r.records) == 80


def test_unknown_failure_mode_is_rejected():
    try:
        MockLLM({"gremlins": 0.5})
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_prompt_contains_grounding_instruction_and_ticket():
    p = build_prompt(TEXT)
    assert "literally appear" in p and p.endswith(TEXT)


def test_summary_reports_halt_and_counts():
    r = run_pipeline(TICKETS, MockLLM(SCENARIOS["degraded"], 1))
    s = summarize(r, TRUTH, "degraded")
    assert "circuit breaker halted" in s and "200 records" in s
