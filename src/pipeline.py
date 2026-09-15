from classifier import predict_intent
from retriever import retrieve_similar_cases
from escalation import decide


def support_agent(message):
    # Step 1: classify the customer message
    intent, confidence = predict_intent(message)

    # Step 2: find similar historical cases
    cases = retrieve_similar_cases(message, top_k=3)

    best_similarity = cases[0]["similarity"]

    # Step 3: decide whether AI can handle it
    decision, reason = decide(
        intent,
        confidence,
        best_similarity,
        message
    )

    return {
        "message": message,
        "intent": intent,
        "confidence": round(confidence, 3),
        "historical_cases": cases,
        "decision": decision,
        "reason": reason
    }


if __name__ == "__main__":

    message = input("\nCustomer message: ")

    result = support_agent(message)

    print("\n--- SUPPORT AGENT RESULT ---")
    print("Intent:", result["intent"])
    print("Confidence:", result["confidence"])
    print("Decision:", result["decision"])
    print("Reason:", result["reason"])

    print("\nSimilar historical cases:")

    for i, case in enumerate(result["historical_cases"], 1):
        print(f"\nCase {i}:")
        print(case["customer_message"])
        print("Similarity:", round(case["similarity"], 3))