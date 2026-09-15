import json


with open(
    "evaluation/primary_agent_results.json",
    encoding="utf-8"
) as f:
    data = json.load(f)


results = data["results"]

errors = [
    r for r in results
    if r["gold_intent"] != r["pred_intent"]
]


print("=" * 60)
print("FAILURE ANALYSIS")
print("=" * 60)

print(f"\nTotal examples: {len(results)}")
print(f"Misclassified: {len(errors)}")
print(
    f"Error rate: "
    f"{len(errors) / len(results):.1%}"
)


print("\nTOP MISCLASSIFICATION PAIRS")
print("-" * 60)

pairs = {}

for r in errors:

    pair = (
        r["gold_intent"],
        r["pred_intent"]
    )

    pairs[pair] = pairs.get(pair, 0) + 1


for (gold, pred), count in sorted(
    pairs.items(),
    key=lambda x: x[1],
    reverse=True
)[:10]:

    print(
        f"{gold} -> {pred}: {count} examples"
    )


print("\n" + "=" * 60)
print("EXAMPLE FAILURES")
print("=" * 60)

for i, r in enumerate(errors[:10], 1):

    print(f"\n{i}. ID: {r['id']}")

    print(
        f"Gold:      {r['gold_intent']}"
    )

    print(
        f"Predicted: {r['pred_intent']}"
    )

    print(
        f"Confidence: "
        f"{r['intent_confidence']:.3f}"
    )

    print(
        f"Message: {r['text']}"
    )

    print(
        f"Escalate: "
        f"{r['pred_escalate']}"
    )