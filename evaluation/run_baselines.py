import json
from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score

GOLDEN_FILE = "evaluation/golden_200.json"
TRAINING_FILE = "data/training_data.csv"

import pandas as pd

golden = pd.read_json(GOLDEN_FILE)
golden = golden.dropna(subset=["intent"])
golden["intent"] = golden["intent"].astype(str)

train = pd.read_csv(TRAINING_FILE)

X_train = train["text"].astype(str)
y_train = train["intent"].astype(str)
X_test = golden["text"].astype(str)
y_test = golden["intent"].astype(str)

print("=" * 55)
print("BASELINE EVALUATION")
print("=" * 55)
print(f"Golden examples: {len(golden)}")
print()

# ---------------------------------------------------------
# 1. Trivial baseline: always predict the majority class
# ---------------------------------------------------------
majority_intent = Counter(y_train).most_common(1)[0][0]
trivial_pred = [majority_intent] * len(y_test)

trivial_accuracy = accuracy_score(y_test, trivial_pred)
trivial_f1 = f1_score(y_test, trivial_pred, average="macro", zero_division=0)

print("TRIVIAL BASELINE")
print(f"Majority intent: {majority_intent}")
print(f"Accuracy: {trivial_accuracy:.3f}")
print(f"Macro F1: {trivial_f1:.3f}")
print()

# ---------------------------------------------------------
# 2. Simple baseline: TF-IDF + Logistic Regression
# ---------------------------------------------------------
vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2)
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

model = LogisticRegression(max_iter=1000)
model.fit(X_train_vec, y_train)

simple_pred = model.predict(X_test_vec)

simple_accuracy = accuracy_score(y_test, simple_pred)
simple_f1 = f1_score(y_test, simple_pred, average="macro", zero_division=0)

print("SIMPLE BASELINE: TF-IDF + LOGISTIC REGRESSION")
print(f"Accuracy: {simple_accuracy:.3f}")
print(f"Macro F1: {simple_f1:.3f}")
print()

print("=" * 55)
print("RESULTS TABLE")
print("=" * 55)
print(f"{'System':<35} {'Accuracy':>10} {'Macro F1':>10}")
print("-" * 55)
print(f"{'Trivial majority baseline':<35} {trivial_accuracy:>10.3f} {trivial_f1:>10.3f}")
print(f"{'TF-IDF + Logistic Regression':<35} {simple_accuracy:>10.3f} {simple_f1:>10.3f}")
print("=" * 55)

output = {
    "golden_examples": len(golden),
    "trivial_baseline": {
        "majority_intent": majority_intent,
        "accuracy": trivial_accuracy,
        "macro_f1": trivial_f1
    },
    "simple_baseline": {
        "method": "TF-IDF + Logistic Regression",
        "accuracy": simple_accuracy,
        "macro_f1": simple_f1
    }
}

with open("evaluation/baseline_results.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print("\nSaved to: evaluation/baseline_results.json")
