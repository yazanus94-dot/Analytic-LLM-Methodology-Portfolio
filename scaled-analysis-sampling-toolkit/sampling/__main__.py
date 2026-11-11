import argparse
import os
import sys

from .calibration import expected_calibration_error
from .drift import interpret_psi, psi
from .estimation import decide, stratified_estimate
from .planning import find_acceptance_plan, required_sample_size
from .report import build_report, load_calibration, load_strata


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="sampling", description="Statistical toolkit for judging analysis at scale.")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("plan", help="sample size for a margin of error")
    a.add_argument("--margin", type=float, required=True)
    a.add_argument("--rate", type=float, default=0.5, help="expected error rate (0.5 = worst case)")
    a.add_argument("--population", type=int)
    b = sub.add_parser("estimate", help="stratified estimate and decision from strata.csv")
    b.add_argument("csv")
    b.add_argument("--threshold", type=float, required=True)
    c = sub.add_parser("calibration", help="expected calibration error from a confidence_review.csv")
    c.add_argument("csv")
    d = sub.add_parser("drift", help="PSI between two distributions")
    d.add_argument("--expected", required=True, help="comma-separated counts")
    d.add_argument("--actual", required=True)
    e = sub.add_parser("acceptance", help="acceptance sampling plan")
    e.add_argument("--aql", type=float, required=True)
    e.add_argument("--ltpd", type=float, required=True)
    r = sub.add_parser("report", help="write the worked example report")
    r.add_argument("--data", default="data")
    r.add_argument("--out", default="reports/example-analysis.md")
    args = p.parse_args(argv)

    if args.cmd == "plan":
        print(required_sample_size(args.margin, args.rate, population=args.population))
    elif args.cmd == "estimate":
        est = stratified_estimate(load_strata(args.csv))
        print(f"estimate {est['estimate']:.2%}, 95% interval {est['lower']:.2%} to {est['upper']:.2%}")
        print(decide(est, args.threshold))
    elif args.cmd == "calibration":
        conf, ok = load_calibration(args.csv)
        print(f"ECE = {expected_calibration_error(conf, ok):.3f}")
    elif args.cmd == "drift":
        v = psi([float(x) for x in args.expected.split(",")], [float(x) for x in args.actual.split(",")])
        print(f"PSI = {v:.3f} ({interpret_psi(v)})")
    elif args.cmd == "acceptance":
        n, c_ = find_acceptance_plan(args.aql, args.ltpd)
        print(f"review {n} items, accept the batch if {c_} or fewer defects")
    else:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        text = build_report(args.data)
        open(args.out, "w", encoding="utf-8").write(text)
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
