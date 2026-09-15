import pandas as pd

CSV = "data/twcs.csv"
OUTPUT = "data/spotify_cases.csv"

print("Step 1: Finding SpotifyCares replies...")

support_parts = []

for chunk in pd.read_csv(
    CSV,
    usecols=[
        "tweet_id",
        "author_id",
        "inbound",
        "text",
        "in_response_to_tweet_id"
    ],
    chunksize=100000
):
    mask = (
        (chunk["author_id"] == "SpotifyCares")
        & (chunk["inbound"] == False)
        & (chunk["in_response_to_tweet_id"].notna())
    )

    if mask.any():
        part = chunk.loc[
            mask,
            ["tweet_id", "in_response_to_tweet_id", "text"]
        ].copy()

        part["customer_tweet_id"] = (
            part["in_response_to_tweet_id"].astype("int64")
        )

        part = part.rename(columns={"text": "support_reply"})

        support_parts.append(
            part[["tweet_id", "customer_tweet_id", "support_reply"]]
        )

replies = pd.concat(support_parts, ignore_index=True)

print("Spotify replies found:", len(replies))

customer_ids = set(replies["customer_tweet_id"])

print("Step 2: Finding the matching customer messages...")

customer_parts = []

for chunk in pd.read_csv(
    CSV,
    usecols=["tweet_id", "inbound", "text"],
    chunksize=100000
):
    mask = (
        (chunk["inbound"] == True)
        & (chunk["tweet_id"].isin(customer_ids))
    )

    if mask.any():
        customer_parts.append(
            chunk.loc[mask, ["tweet_id", "text"]]
        )

customers = pd.concat(customer_parts, ignore_index=True)

customers = customers.rename(
    columns={"text": "customer_message"}
)

print("Customer messages found:", len(customers))

print("Step 3: Creating customer → Spotify reply pairs...")

cases = replies.merge(
    customers,
    left_on="customer_tweet_id",
    right_on="tweet_id",
    how="inner"
)

cases = cases[
    ["customer_tweet_id", "customer_message", "support_reply"]
]

cases = cases.drop_duplicates(
    subset=["customer_message", "support_reply"]
)

cases = cases.sample(
    frac=1,
    random_state=42
).head(5000)

cases.to_csv(OUTPUT, index=False)

print("\nDONE!")
print("Historical cases saved:", len(cases))
print("File:", OUTPUT)

print("\nExample:")
print("CUSTOMER:", cases.iloc[0]["customer_message"])
print("SPOTIFY REPLY:", cases.iloc[0]["support_reply"])