import argparse
import json
import os
from pathlib import Path

try:
    from google import genai
except ImportError:
    genai = None


RUBRIC = """
Score the support-agent output on four criteria from 1 to 5.

1. intent_correctness
5 = predicted intent clearly matches the customer message
4 = mostly correct with minor ambiguity
3 = plausible but uncertain
2 = probably incorrect
1 = clearly incorrect

2. escalation_correctness
5 = escalation decision is clearly appropriate
4 = mostly appropriate
3 = debatable
2 = probably inappropriate
1 = clearly inappropriate

3. grounding
5 = response is fully supported by the customer message and retrieved examples
4 = mostly grounded
3 = partly grounded
2 = contains unsupported claims
1 = clearly invents facts or policies

4. reply_helpfulness
5 = concise, relevant, safe, and useful
4 = generally helpful
3 = acceptable but generic
2 = minimally useful
1 = unhelpful or misleading
"""


SYSTEM_PROMPT = f"""
You are a strict reviewer evaluating a customer-support triage agent.

{RUBRIC}

Return ONLY valid JSON with exactly these keys:

intent_correctness
escalation_correctness
grounding
reply_helpfulness
overall_score
reason

Each criterion must be an integer from 1 to 5.
overall_score must be the average of the four criterion scores.
reason must briefly explain the scoring.

Do not invent facts.
"""


class Reviewer:

    def __init__(self, model="gemini-3.6-flash"):

        self.model = model
        self.client = None

        if (
            genai is not None
            and os.getenv("GEMINI_API_KEY")
        ):
            self.client = genai.Client(
                api_key=os.getenv("GEMINI_API_KEY")
            )

    def review(self, row):

        if self.client is None:
            return {
                "intent_correctness": None,
                "escalation_correctness": None,
                "grounding": None,
                "reply_helpfulness": None,
                "overall_score": None,
                "reason": "Gemini API unavailable."
            }

        prompt = f"""
{SYSTEM_PROMPT}

Customer message:
{row["text"]}

Gold intent:
{row["gold_intent"]}

Predicted intent:
{row["pred_intent"]}

Gold escalation:
{row["gold_escalate"]}

Predicted escalation:
{row["pred_escalate"]}

Retrieved similarity:
{row["retrieval_similarity"]}

Escalation reason:
{row["escalation_reason"]}

Agent reply:
{row["reply"]}

Grounded flag:
{row["grounded"]}

Review the agent output.
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={
                "temperature": 0,
                "response_mime_type": "application/json",
            },
        )

        return json.loads(response.text)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        default="evaluation/primary_agent_results.json"
    )

    parser.add_argument(
        "--output",
        default="evaluation/reviewer_results.json"
    )

    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)

    reviewer = Reviewer()

    reviewed = []

    print(
        f"Reviewing {len(data['results'])} examples..."
    )

    for i, row in enumerate(
        data["results"],
        1
    ):

        print(
            f"{i}/{len(data['results'])}",
            flush=True
        )

        review = reviewer.review(row)

        reviewed.append({
            "id": row["id"],
            "text": row["text"],
            "gold_intent": row["gold_intent"],
            "pred_intent": row["pred_intent"],
            "gold_escalate": row["gold_escalate"],
            "pred_escalate": row["pred_escalate"],
            "review": review,
        })

    output = {
        "rubric": RUBRIC,
        "reviews": reviewed
    }

    Path(args.output).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        args.output,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"\nSaved reviewer results to {args.output}"
    )


if __name__ == "__main__":
    main()