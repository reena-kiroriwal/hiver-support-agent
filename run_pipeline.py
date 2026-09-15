import argparse
import json
import os
import pandas as pd

from src.primary_agent import PrimarySupportAgent


def main():
    parser = argparse.ArgumentParser(description="Hiver Support Agent Pipeline")
    parser.add_argument("--brand", required=True)
    parser.add_argument("--sample", action="store_true")
    args = parser.parse_args()

    if args.brand.lower() != "spotifycares":
        print("Currently supported brand: SpotifyCares")
        return

    if args.sample:
        input_file = "data/sample_data.csv"
    else:
        input_file = "data/spotify_cases.csv"

    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return

    df = pd.read_csv(input_file)

    # Support either "text" or "customer_message"
    if "text" in df.columns:
        messages = df["text"].dropna().tolist()
    elif "customer_message" in df.columns:
        messages = df["customer_message"].dropna().tolist()
    else:
        print("CSV must contain a 'text' or 'customer_message' column.")
        return

    agent = PrimarySupportAgent()

    results = []

    print(f"\nBrand: {args.brand}")
    print(f"Input file: {input_file}")
    print(f"Messages: {len(messages)}")
    print("\nRunning pipeline...\n")

    for i, message in enumerate(messages, start=1):
        result = agent.run(message)
        results.append(result)

        print(
            f"[{i}/{len(messages)}] "
            f"{result['intent']} | "
            f"{'ESCALATE' if result['should_escalate'] else 'AUTO_HANDLE'}"
        )

    output_file = "evaluation/pipeline_results.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\nPipeline completed!")
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()