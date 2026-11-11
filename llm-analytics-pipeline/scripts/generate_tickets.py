"""Generate synthetic IT incident tickets with ground-truth labels (deterministic)."""
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
SYSTEMS = ["payments-api", "auth-service", "billing-db", "search-index", "mobile-gateway", "report-engine"]

TEMPLATES = {
    "outage": [("The {sys} is down and customers get error {code}.", 1), ("{sys} is unavailable since this morning, error {code} on every request from {cust}.", 1)],
    "performance": [("{sys} is very slow, latency above 5 seconds for {cust}.", 3), ("Dashboards from {sys} take minutes to load for {cust}.", 3)],
    "security_alert": [("Suspicious login attempts on {sys} for account {cust}, possible unauthorized access.", 1), ("{cust} reported a phishing email that links to {sys}.", 2)],
    "access_request": [("{cust} needs a password reset for {sys}.", 4), ("Please grant {cust} permission to use {sys}.", 4)],
    "billing": [("{cust} was charged twice, please refund the invoice for {sys}.", 3), ("Invoice from {sys} shows the wrong amount for {cust}.", 3)],
    "feature_question": [("How do I export data from {sys}? Asked by {cust}.", 4), ("Is it possible to schedule reports in {sys}? Question from {cust}.", 4)],
}


def main(n=200, seed=7):
    rnd = random.Random(seed)
    cats = list(TEMPLATES)
    rows = []
    for i in range(1, n + 1):
        cat = rnd.choice(cats)
        tpl, prio = rnd.choice(TEMPLATES[cat])
        text = tpl.format(sys=rnd.choice(SYSTEMS), code=f"E-{rnd.choice([500, 502, 503, 504])}", cust=f"CUST-{rnd.randint(1000, 9999)}")
        if rnd.random() < 0.12:  # ambiguous tickets that touch two categories
            text += " It is also slow and the invoice looks wrong."
        rows.append({"id": f"T-{i:04d}", "text": text, "true_category": cat, "true_priority": prio})
    with open(os.path.join(HERE, "..", "data", "tickets.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return rows


if __name__ == "__main__":
    print(len(main()), "tickets written")
