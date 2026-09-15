import json

INPUT_FILE = "evaluation/golden_200_firstpass.json"
OUTPUT_FILE = "evaluation/golden_review.csv"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

rows = []

for item in data:
    text = item["text"].lower()

    # Flag likely ambiguous cases for human review.
    uncertain = False

    if item["provisional_intent"] in ["other", "general_question"]:
        uncertain = True

    if len(text.split()) <= 5:
        uncertain = True

    if "?" in text and item["provisional_intent"] == "other":
        uncertain = True

    if item["should_escalate"]:
        uncertain = True

    rows.append({
        "id": item["id"],
        "text": item["text"],
        "provisional_intent": item["provisional_intent"],
        "firstpass_intent": item["intent"],
        "should_escalate": item["should_escalate"],
        "review_needed": uncertain
    })

with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
    import csv

    writer = csv.DictWriter(
        f,
        fieldnames=rows[0].keys()
    )

    writer.writeheader()
    writer.writerows(rows)

print("Review file created:")
print(OUTPUT_FILE)

print()
print(
    "Examples requiring focused human review:",
    sum(row["review_needed"] for row in rows)
)