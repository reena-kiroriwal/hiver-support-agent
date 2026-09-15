import json
from sklearn.metrics import cohen_kappa_score


with open(
    "evaluation/double_label_50.json",
    encoding="utf-8"
) as f:
    data = json.load(f)


annotator1_intent = [
    row["annotator_1_intent"]
    for row in data
]

annotator2_intent = [
    row["annotator_2_intent"]
    for row in data
]

annotator1_escalate = [
    row["annotator_1_escalate"]
    for row in data
]

annotator2_escalate = [
    row["annotator_2_escalate"]
    for row in data
]


intent_kappa = cohen_kappa_score(
    annotator1_intent,
    annotator2_intent
)

escalation_kappa = cohen_kappa_score(
    annotator1_escalate,
    annotator2_escalate
)


intent_agreement = sum(
    a == b
    for a, b in zip(
        annotator1_intent,
        annotator2_intent
    )
) / len(data)

escalation_agreement = sum(
    a == b
    for a, b in zip(
        annotator1_escalate,
        annotator2_escalate
    )
) / len(data)


print("DOUBLE-LABEL AGREEMENT")
print("----------------------")

print(
    f"Intent agreement: "
    f"{intent_agreement:.1%}"
)

print(
    f"Intent Cohen's kappa: "
    f"{intent_kappa:.3f}"
)

print()

print(
    f"Escalation agreement: "
    f"{escalation_agreement:.1%}"
)

print(
    f"Escalation Cohen's kappa: "
    f"{escalation_kappa:.3f}"
)