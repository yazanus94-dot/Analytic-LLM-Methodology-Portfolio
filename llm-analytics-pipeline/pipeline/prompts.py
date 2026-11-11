CATEGORIES = ("outage", "performance", "security_alert", "access_request", "billing", "feature_question")

TRIAGE_PROMPT = """You are an IT incident triage assistant. Read the ticket and answer with JSON only.
Schema: {{"category": one of {categories}, "priority": integer 1 (urgent) to 4 (low), "confidence": number 0 to 1,
"entities": list of system names, error codes and customer ids that appear in the ticket text}}.
Only list entities that literally appear in the ticket. Do not add explanations.
TICKET: {text}"""


def build_prompt(text: str) -> str:
    return TRIAGE_PROMPT.format(categories=list(CATEGORIES), text=text)


def extract_ticket(prompt: str) -> str:
    return prompt.split("TICKET:", 1)[1].strip()
