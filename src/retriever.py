import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

data = pd.read_csv("data/spotify_cases.csv")

data = data.dropna(
    subset=["customer_message", "support_reply"]
).reset_index(drop=True)

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Creating embeddings for historical cases...")

embeddings = model.encode(
    data["customer_message"].tolist(),
    show_progress_bar=True
)


def retrieve_similar_cases(message, top_k=3):

    query_embedding = model.encode([message])

    similarities = cosine_similarity(
        query_embedding,
        embeddings
    )[0]

    top_indices = similarities.argsort()[-top_k:][::-1]

    results = []

    for index in top_indices:

        results.append({
            "customer_message": data.iloc[index]["customer_message"],
            "support_reply": data.iloc[index]["support_reply"],
            "similarity": float(similarities[index])
        })

    return results


if __name__ == "__main__":

    message = "Why am I seeing so many ads on Spotify?"

    results = retrieve_similar_cases(message, top_k=3)

    print("\nNEW CUSTOMER:")
    print(message)

    print("\nSIMILAR HISTORICAL CASES:")

    for i, result in enumerate(results, 1):

        print(f"\nCase {i}")

        print("Customer:")
        print(result["customer_message"])

        print("\nSpotify Reply:")
        print(result["support_reply"])

        print(
            "Similarity:",
            round(result["similarity"], 3)
        )