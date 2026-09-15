import argparse
import json
from pathlib import Path
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.primary_agent import PrimarySupportAgent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--golden", default="evaluation/golden_200.json")
    parser.add_argument("--out", default="evaluation/primary_agent_results.json")
    parser.add_argument("--data-dir", default="data")
    args = parser.parse_args()

    with open(args.golden, encoding="utf-8") as f:
        golden = json.load(f)

    agent = PrimarySupportAgent(data_dir=args.data_dir)
    results = []

    print(f"Starting evaluation of {len(golden)} examples...\n")

    for i, row in enumerate(golden, 1):

        print(f"Processing {i}/{len(golden)}...", flush=True)

        try:
            start_time = time.time()

            pred = agent.run(row["text"], use_llm=False)

            elapsed = time.time() - start_time

            results.append({
                "id": row["id"],
                "text": row["text"],
                "gold_intent": row["intent"],
                "pred_intent": pred["intent"],
                "gold_escalate": bool(row["should_escalate"]),
                "pred_escalate": bool(pred["should_escalate"]),
                "intent_confidence": pred["intent_confidence"],
                "retrieval_similarity": pred["retrieval_similarity"],
                "escalation_reason": pred["escalation_reason"],
                "reply": pred["reply"],
                "grounded": pred["grounded"],
            })

            print(f"Completed {i}/{len(golden)} in {elapsed:.1f}s", flush=True)

        except Exception as e:
            print(f"FAILED {i}/{len(golden)}: {e}", flush=True)

            # Keep the evaluation going even if one example fails.
            results.append({
                "id": row["id"],
                "text": row["text"],
                "gold_intent": row["intent"],
                "pred_intent": "other",
                "gold_escalate": bool(row["should_escalate"]),
                "pred_escalate": True,
                "intent_confidence": 0.0,
                "retrieval_similarity": 0.0,
                "escalation_reason": "Agent/API failure during evaluation.",
                "reply": "",
                "grounded": False,
            })

    # Calculate metrics
    y_true = [r["gold_intent"] for r in results]
    y_pred = [r["pred_intent"] for r in results]

    e_true = [r["gold_escalate"] for r in results]
    e_pred = [r["pred_escalate"] for r in results]

    metrics = {
        "intent_accuracy": accuracy_score(y_true, y_pred),
        "intent_macro_f1": f1_score(
            y_true,
            y_pred,
            average="macro",
            zero_division=0
        ),
        "escalation_precision": precision_score(
            e_true,
            e_pred,
            zero_division=0
        ),
        "escalation_recall": recall_score(
            e_true,
            e_pred,
            zero_division=0
        ),
    }

    # Save results
    out = {
        "metrics": metrics,
        "results": results
    }

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(
            out,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("\n" + "=" * 40)
    print("PRIMARY AGENT METRICS")
    print("=" * 40)

    for k, v in metrics.items():
        print(f"{k}: {v:.3f}")

    print("=" * 40)
    print(f"Results saved to: {args.out}")


if __name__ == "__main__":
    main()