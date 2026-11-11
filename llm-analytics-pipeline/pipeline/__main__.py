import argparse
import json
import os
import sys

from .models import MockLLM
from .runner import PipelineConfig, run_pipeline, summarize
from .scenarios import SCENARIOS


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="pipeline", description="Run the LLM triage and enrichment pipeline on tickets.")
    p.add_argument("--tickets", default="data/tickets.jsonl")
    p.add_argument("--scenario", choices=sorted(SCENARIOS), default="flaky")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--out", default="reports")
    args = p.parse_args(argv)

    tickets = [json.loads(l) for l in open(args.tickets, encoding="utf-8")]
    truth = {t["id"]: t["true_category"] for t in tickets}
    result = run_pipeline(tickets, MockLLM(SCENARIOS[args.scenario], args.seed), PipelineConfig())
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, f"run-{args.scenario}.md")
    open(path, "w", encoding="utf-8").write(summarize(result, truth, args.scenario))
    print(open(path, encoding="utf-8").read())
    return 1 if result.halted else 0


if __name__ == "__main__":
    sys.exit(main())
