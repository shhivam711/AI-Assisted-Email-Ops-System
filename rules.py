from typing import Tuple
from email_model import NormalizedEmail
from config import PAYMENT_KEYWORDS, PROMO_SENDERS


# category, rule_id
RuleResult = Tuple[str, str]

ACTION_REQUIRED = "ACTION_REQUIRED"
INFORMATIONAL = "INFORMATIONAL"
PROMOTIONAL = "PROMOTIONAL"
IGNORE = "IGNORE"

def rule_payment_or_invoice(email: NormalizedEmail) -> RuleResult | None:
    text = f"{email.subject} {email.snippet}".lower()

    for word in PAYMENT_KEYWORDS:
        if word in text:
            return ACTION_REQUIRED, f"PAYMENT_KEYWORD:{word}"


    return None


def rule_known_promotions(email: NormalizedEmail) -> RuleResult | None:

    sender = email.sender.lower()

    for brand in PROMO_SENDERS:
        if brand in sender:
            return PROMOTIONAL, "KNOWN_PROMO_SENDER"

    return None


def apply_rules(email: NormalizedEmail) -> RuleResult:
    rules = [
        rule_payment_or_invoice,
        rule_known_promotions,
    ]

    for rule in rules:
        result = rule(email)
        if result is not None:
            return result

    return INFORMATIONAL, "DEFAULT_FALLBACK"

