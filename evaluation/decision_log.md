# Decision Log

## 1. Chose SpotifyCares as the brand
Selected SpotifyCares because the source dataset contains a large number of Spotify support interactions.

## 2. Used historical customer-support pairs
Customer messages were paired with corresponding Spotify support replies to create realistic retrieval evidence.

## 3. Used 11 intent categories
The taxonomy separates playback, technical, account, subscription, billing, music availability, playlists, features, regional availability, general questions, and other.

## 4. Kept an explicit `other` category
Ambiguous or unrelated messages are not forced into a specific support intent.

## 5. Used TF-IDF + Logistic Regression as the simple baseline
This provides a lightweight and reproducible text-classification baseline.

## 6. Used bigrams
Unigrams and bigrams were selected to capture short phrases such as payment-related and account-related expressions.

## 7. Used Sentence Transformers for retrieval
Semantic embeddings were used because support messages can express the same issue with different wording.

## 8. Cached historical embeddings
Embeddings are stored locally so subsequent pipeline runs do not repeatedly encode the full historical dataset.

## 9. Used deterministic escalation rules
Sensitive phrases, low classifier confidence, weak retrieval similarity, and sensitive intents can trigger escalation.

## 10. Prioritized escalation recall
The escalation policy intentionally favors catching potentially sensitive cases even when this creates additional false escalations.

## 11. Used an LLM for response generation
Gemini is used to generate concise grounded support responses using retrieved historical examples.

## 12. Used structured JSON output
The LLM is instructed to return a fixed JSON schema so the application can validate and parse its output reliably.

## 13. Deterministic escalation remains the source of truth
The LLM cannot override the escalation decision because safety-critical routing should remain predictable.

## 14. Added an LLM fallback
If the LLM is unavailable, the system returns a safe generic response rather than crashing.

## 15. Evaluated the deterministic pipeline separately
Because the Gemini free tier imposed a 20-request quota, the 200-example evaluation was run without LLM calls to measure the underlying classification/retrieval/escalation pipeline without fabricating unavailable LLM results.