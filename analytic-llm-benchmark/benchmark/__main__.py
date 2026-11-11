import argparse
import os
import sys

from .grader import grade_case
from .metrics import evaluate_models
from .models import MODELS
from .report import coverage_markdown, report_markdown
from .schema import load_all, validate_benchmark


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="benchmark", description="Validate and run the analytic LLM benchmark on mock models.")
    p.add_argument("data_dir", nargs="?", default="data")
    p.add_argument("--out", default="reports")
    args = p.parse_args(argv)

    taxonomy, cases, responses = load_all(args.data_dir)
    errs = validate_benchmark(taxonomy, cases, responses)
    if errs:
        print("\n".join(errs))
        return 1
    results = evaluate_models(cases, responses, MODELS, grade_case)
    os.makedirs(args.out, exist_ok=True)
    text = report_markdown(taxonomy, cases, results) + "\n" + coverage_markdown(taxonomy, cases)
    open(os.path.join(args.out, "benchmark-results.md"), "w", encoding="utf-8").write(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
