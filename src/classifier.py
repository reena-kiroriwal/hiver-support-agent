import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


# Load our labelled examples
data = pd.read_csv("data/training_data.csv")

X = data["text"]
y = data["intent"]


# Convert text into numbers
vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2)
)

X_vectorized = vectorizer.fit_transform(X)


# Train the classifier
model = LogisticRegression(
    max_iter=1000
)

model.fit(X_vectorized, y)


def predict_intent(message):
    """
    Predict the intent of a new customer message.
    """

    message_vectorized = vectorizer.transform([message])

    prediction = model.predict(message_vectorized)[0]

    probabilities = model.predict_proba(message_vectorized)[0]

    confidence = max(probabilities)

    return prediction, confidence


if __name__ == "__main__":

    test_messages = [
        "My songs are not playing",
        "I cannot login to my account",
        "I was charged twice",
        "Can you add lyrics?",
    ]

    for message in test_messages:

        intent, confidence = predict_intent(message)

        print("\nCustomer:", message)
        print("Intent:", intent)
        print("Confidence:", round(confidence, 3))