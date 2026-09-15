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
    text = message.lower()

    # Always escalate explicit security/fraud/payment-risk signals.
    for phrase in RISK_PHRASES:
        if phrase in text:
            return (
                "ESCALATE",
                f"The message contains a potentially sensitive issue ('{phrase}') that requires human review."
            )

    # Very strong historical evidence can compensate for low TF-IDF
    # confidence when the intent itself is not sensitive.
    if (
        intent not in SENSITIVE_INTENTS
        and retrieval_similarity >= 0.75
        and intent_confidence >= 0.15
    ):
        return (
            "AUTO_HANDLE",
            "A highly similar historical case was found and the predicted intent has sufficient supporting confidence."
        )

    # For weaker retrieval evidence, require normal classifier confidence.
    if intent_confidence < 0.45:
        return (
            "ESCALATE",
            "Intent confidence is below the auto-handling threshold."
        )

    if retrieval_similarity < 0.50:
        return (
            "ESCALATE",
            "No sufficiently similar historical Spotify case was found."
        )

    # Sensitive intents remain conservative.
    if intent in SENSITIVE_INTENTS and intent_confidence < 0.70:
        return (
            "ESCALATE",
            "This is a sensitive account/payment issue and the classifier confidence is not high enough."
        )

    return (
        "AUTO_HANDLE",
        "The intent is sufficiently confident and a similar historical case was found."
    )