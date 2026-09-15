import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from google import genai
except ImportError:
    genai = None


# -------------------------
# Allowed intents
# -------------------------

INTENTS = [
    "playback_issue",
    "app_technical_issue",
    "account_login",
    "premium_subscription",
    "payment_billing",
    "music_availability",
    "playlist_library",
    "feature_request",
    "availability_region",
    "general_question",
    "other",
]


# -------------------------
# Escalation rules
# -------------------------

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


SENSITIVE_INTENTS = {
    "payment_billing",
    "premium_subscription",
    "account_login",
}


# -------------------------
# LLM system prompt
# -------------------------

SYSTEM_PROMPT = """You are a Spotify customer-support triage agent.

Classify the customer message into exactly one intent:

playback_issue
app_technical_issue
account_login
premium_subscription
payment_billing
music_availability
playlist_library
feature_request
availability_region
general_question
other

Use the retrieved historical Spotify support examples as grounding.

Do not invent policies, refunds, availability, prices, or account facts.

Return ONLY valid JSON with exactly these keys:
intent, reply, grounded, escalation_reason.

intent must be one of the allowed labels.
grounded must be true or false.
escalation_reason must be a string or null.
"""


# -------------------------
# Primary Support Agent
# -------------------------

class PrimarySupportAgent:

    def __init__(self, data_dir="data", model="gemini-3.6-flash"):

        self.data_dir = Path(data_dir)
        self.model = model

        # -------------------------
        # Load training data
        # -------------------------

        train = pd.read_csv(
            self.data_dir / "training_data.csv"
        )

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2)
        )

        X = self.vectorizer.fit_transform(
            train["text"]
        )

        self.classifier = LogisticRegression(
            max_iter=1000
        )

        self.classifier.fit(
            X,
            train["intent"]
        )

        # -------------------------
        # Load Spotify cases
        # -------------------------

        cases = pd.read_csv(
            self.data_dir / "spotify_cases.csv"
        )

        cases = cases.dropna(
            subset=["customer_message"]
        ).drop_duplicates(
            "customer_message"
        )

        self.case_texts = (
            cases["customer_message"]
            .astype(str)
            .tolist()
        )

        # -------------------------
        # Sentence Transformer
        # -------------------------

        self.embedder = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        cache = (
            self.data_dir /
            "spotify_case_embeddings.npy"
        )

        if (
            cache.exists()
            and len(
                np.load(
                    cache,
                    mmap_mode="r"
                )
            ) == len(self.case_texts)
        ):

            self.case_embeddings = np.load(
                cache
            )

        else:

            self.case_embeddings = (
                self.embedder.encode(
                    self.case_texts,
                    normalize_embeddings=True,
                    show_progress_bar=True
                )
            )

            np.save(
                cache,
                self.case_embeddings
            )

        # -------------------------
        # Gemini
        # -------------------------

        self.client = None

        if (
            genai is not None
            and os.getenv("GEMINI_API_KEY")
        ):

            self.client = genai.Client(
                api_key=os.getenv("GEMINI_API_KEY")
            )


    # -------------------------
    # Intent classification
    # -------------------------

    def classify(self, message):

        vec = self.vectorizer.transform(
            [message]
        )

        probs = self.classifier.predict_proba(
            vec
        )[0]

        idx = int(
            np.argmax(probs)
        )

        return (
            self.classifier.classes_[idx],
            float(probs[idx])
        )


    # -------------------------
    # Historical retrieval
    # -------------------------

    def retrieve(self, message, k=3):

        q = self.embedder.encode(
            [message],
            normalize_embeddings=True
        )

        sims = cosine_similarity(
            q,
            self.case_embeddings
        )[0]

        idxs = np.argsort(sims)[::-1][:k]

        return [
            {
                "text": self.case_texts[int(i)],
                "similarity": float(sims[i])
            }
            for i in idxs
        ]


    # -------------------------
    # Escalation
    # -------------------------

    def decide_escalation(
        self,
        intent,
        confidence,
        similarity,
        message
    ):
        text = message.lower()

        # Always escalate explicit security/fraud/payment-risk signals.
        for phrase in RISK_PHRASES:
            if phrase in text:
                return (
                    True,
                    f"Sensitive issue detected: {phrase}"
                )

        # Strong historical evidence can compensate for lower
        # classifier confidence for non-sensitive intents.
        if (
            intent not in SENSITIVE_INTENTS
            and similarity >= 0.75
            and confidence >= 0.15
        ):
            return (
                False,
                "Strong historical match with sufficient intent support."
            )

        # For weaker evidence, use the normal confidence threshold.
        if confidence < 0.45:
            return (
                True,
                "Intent confidence is below the auto-handling threshold."
            )

        if similarity < 0.50:
            return (
                True,
                "No sufficiently similar historical case was found."
            )

        # Stay conservative for sensitive intents.
        if (
            intent in SENSITIVE_INTENTS
            and confidence < 0.70
        ):
            return (
                True,
                "Sensitive account/payment intent with insufficient confidence."
            )

        return False, None


    # -------------------------
    # Fallback reply
    # -------------------------

    def _fallback_reply(self, escalate):

        if escalate:

            return (
                "This issue needs additional review by support. "
                "Please use the official Spotify support channel "
                "so the account-specific details can be checked."
            )

        return (
            "Thanks for reaching out. We can help with this "
            "Spotify issue. Please follow the relevant Spotify "
            "support guidance for your account."
        )


    # -------------------------
    # Main agent
    # -------------------------

    def run(self, message, use_llm=True):

        # -------------------------
        # Classify
        # -------------------------

        intent, confidence = self.classify(
            message
        )

        # -------------------------
        # Retrieve historical cases
        # -------------------------

        retrieved = self.retrieve(
            message,
            3
        )

        top_similarity = (
            retrieved[0]["similarity"]
        )

        # -------------------------
        # Decide escalation
        # -------------------------

        escalate, reason = (
            self.decide_escalation(
                intent,
                confidence,
                top_similarity,
                message
            )
        )

        # -------------------------
        # Base result
        # -------------------------

        result = {

            "intent": intent,

            "intent_confidence": confidence,

            "should_escalate": escalate,

            "escalation_reason": reason,

            "retrieval_similarity": top_similarity,

            "reply": None,

            "grounded": False,

            "retrieved_cases": retrieved
        }

        # -------------------------
        # No Gemini available
        # -------------------------

        if self.client is None or not use_llm:

            result["reply"] = (
                self._fallback_reply(
                    escalate
                )
            )

            return result

        # -------------------------
        # Build evidence
        # -------------------------

        evidence = "\n\n".join(

            f"Historical example {i+1} "
            f"(similarity={x['similarity']:.3f}): "
            f"{x['text']}"

            for i, x in enumerate(
                retrieved
            )
        )

        # -------------------------
        # Build prompt
        # -------------------------

        prompt = f"""{SYSTEM_PROMPT}

Customer message:
{message}

Classifier intent:
{intent}

Classifier confidence:
{confidence:.3f}

Deterministic escalation decision:
{escalate}

Escalation reason:
{reason}

Retrieved historical examples:

{evidence}

Write a concise support reply grounded only
in the customer message and retrieved examples.

If escalation is true, do not claim that
the issue is resolved.

Return JSON only.
"""

        # -------------------------
        # Gemini call
        # -------------------------

        payload = None

        try:

            response = self.client.models.generate_content(

                model=self.model,

                contents=prompt,

                config={
                    "temperature": 0,
                    "response_mime_type": "application/json",
                },
            )

            payload = json.loads(
                response.text
            )

        except Exception:

            print(
                "Gemini unavailable. "
                "Using fallback response."
            )

            payload = {

                "intent": intent,

                "reply": self._fallback_reply(
                    escalate
                ),

                "grounded": False,

                "escalation_reason": reason
            }

        # -------------------------
        # Validate LLM output
        # -------------------------

        if payload.get("intent") not in INTENTS:

            payload["intent"] = intent

        result["reply"] = payload.get(
            "reply",
            self._fallback_reply(
                escalate
            )
        )

        result["grounded"] = bool(
            payload.get(
                "grounded",
                True
            )
        )

        # -------------------------
        # Deterministic escalation
        # remains source of truth
        # -------------------------

        result["should_escalate"] = (
            escalate
        )

        result["escalation_reason"] = (
            reason
        )

        return result


# -------------------------
# Test the agent
# -------------------------

if __name__ == "__main__":

    agent = PrimarySupportAgent()

    message = (
        "Why can't I update my payment details?"
    )

    print(
        json.dumps(
            agent.run(message),
            indent=2,
            ensure_ascii=False
        )
    )