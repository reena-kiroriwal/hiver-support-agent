RISK_PHRASES = [
    "hacked",
    "stolen",
    "fraud",
    "unauthorized",
    "without permission",
    "someone used my",
    "someone accessed",
    "account compromised",
    "don't recognize this charge",
    "do not recognize this charge",
    "charged twice",
    "charged multiple times",
]

SENSITIVE_INTENTS = [
    "payment_billing",
    "premium_subscription",
    "account_login",
]


def decide(intent, intent_confidence, retrieval_similarity, message):
    """
    Decide whether the AI should handle the request
    or send it to a human.
    """

    text = message.lower()

    # 1. Explicitly risky/security-related language
    for phrase in RISK_PHRASES:
        if phrase in text:
            return (
                "ESCALATE",
                f"The message contains a potentially sensitive issue "
                f"('{phrase}') that requires human review."
            )

    # 2. Low confidence
    if intent_confidence < 0.45:
        return (
            "ESCALATE",
            "The intent classifier is not sufficiently confident."
        )

    # 3. Weak historical evidence
    if retrieval_similarity < 0.50:
        return (
            "ESCALATE",
            "No sufficiently similar historical Spotify case was found."
        )

    # 4. Sensitive intent gets a stricter confidence requirement
    if intent in SENSITIVE_INTENTS and intent_confidence < 0.70:
        return (
            "ESCALATE",
            "This is a sensitive account/payment issue and "
            "the classifier confidence is not high enough."
        )

    return (
        "AUTO_HANDLE",
        "The intent is sufficiently confident and a similar "
        "historical Spotify case was found."
    )