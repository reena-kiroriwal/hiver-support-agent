import json
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

INPUT = "evaluation/primary_agent_results.json"
OUTPUT = "evaluation/confidence_intervals.json"

with open(INPUT, encoding="utf-8") as f:
    data = json.load(f)

results = data["results"]
n = len(results)
rng = np.random.default_rng(42)
B = 5000

y_true = np.array([r["gold_intent"] for r in results], dtype=object)
y_pred = np.array([r["pred_intent"] for r in results], dtype=object)
e_true = np.array([r["gold_escalate"] for r in results], dtype=bool)
e_pred = np.array([r["pred_escalate"] for r in results], dtype=bool)

scores = {
    "intent_accuracy": [],
    "intent_macro_f1": [],
    "escalation_precision": [],
    "escalation_recall": [],
}

for _ in range(B):
    idx = rng.integers(0, n, size=n)

    scores["intent_accuracy"].append(
        accuracy_score(y_true[idx], y_pred[idx])
    )
    scores["intent_macro_f1"].append(
        f1_score(y_true[idx], y_pred[idx], average="macro", zero_division=0)
    )
    scores["escalation_precision"].append(
        precision_score(e_true[idx], e_pred[idx], zero_division=0)
    )
    scores["escalation_recall"].append(
        recall_score(e_true[idx], e_pred[idx], zero_division=0)
    )

ci = {}
for metric, values in scores.items():
    values = np.array(values)
    ci[metric] = {
        "estimate": float(np.mean(values)),
        "lower_95": float(np.percentile(values, 2.5)),
        "upper_95": float(np.percentile(values, 97.5)),
        "bootstrap_samples": B,
        "seed": 42,
    }

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(ci, f, indent=2)

print("95% bootstrap confidence intervals")
print("=" * 45)
for metric, value in ci.items():
    print(
        f"{metric}: {value['estimate']:.3f} "
        f"(95% CI {value['lower_95']:.3f} - {value['upper_95']:.3f})"
    )
print(f"\nSaved to: {OUTPUT}")
