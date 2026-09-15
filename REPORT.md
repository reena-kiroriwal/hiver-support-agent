Hiver Support Agent — Evaluation Report
1. Problem Framing

This project builds a support-triage agent for SpotifyCares customer tweets. The system classifies incoming customer messages into 11 support intents, retrieves similar historical Spotify support cases, generates a grounded response when possible, and decides whether the request should be automatically handled or escalated to a human.

The intent taxonomy contains:

playback_issue
app_technical_issue
account_login
premium_subscription
payment_billing
music_availability
playlist_library
feature_request
availability_region
general_question
other

The system uses a TF-IDF + Logistic Regression classifier for intent prediction and a Sentence Transformer retriever over historical SpotifyCares cases. Escalation uses deterministic safety rules combined with classifier confidence and retrieval similarity. The LLM component is implemented using Gemini for response generation and structured review.

What I chose NOT to build

To keep the project focused on the evaluation requirements, I did not build:

a production web/mobile user interface
a real-time Twitter/X integration
automated account or payment actions
a production database
a full human-agent dashboard
continuous model retraining
a large-scale production monitoring system

The focus was instead placed on reproducibility, evaluation quality, escalation safety, and failure analysis.

2. Data and Golden Set

The project uses the Customer Support on Twitter dataset and extracts SpotifyCares customer-support interactions.

A prepared dataset of approximately 4,948 unique customer messages was obtained after removing missing and duplicate messages.

A 200-example golden set was created using stratified candidate selection across the 11-intent taxonomy, followed by manual assignment of final intent and escalation labels. A fixed random seed of 42 was used for sampling and final shuffling.

The repository includes:

data/sample_data.csv
data/spotify_cases.csv
data/training_data.csv
evaluation/golden_200.json
evaluation/codebook.md
evaluation/sampling_notes.md

The other category was retained explicitly rather than forcing unclear messages into a specific support intent.

3. Evaluation Method

The evaluation measures:

Intent accuracy
Intent macro F1
Escalation precision
Escalation recall

Confidence intervals were calculated using 5,000 bootstrap samples with random seed 42.

The primary evaluation was run on all 200 golden examples.

4. Results
System comparison
System	Intent Accuracy	Macro F1
Trivial majority baseline	2.0%	0.004
TF-IDF + Logistic Regression	45.5%	0.449
Primary Agent	45.5%	0.449

The primary agent's deterministic intent evaluation uses the same TF-IDF + Logistic Regression classifier as the simple baseline. Therefore, the primary agent does not outperform the simple baseline on intent classification.

This is an important result rather than a hidden limitation: the value of the primary agent is primarily in its retrieval, response generation, grounding, and escalation workflow, rather than a demonstrated improvement in intent classification.

Primary Agent escalation results
Metric	Result	95% Bootstrap CI
Intent Accuracy	45.5%	38.5%–52.5%
Macro F1	0.449	0.377–0.509
Escalation Precision	10.0%	5.7%–14.6%
Escalation Recall	94.7%	82.3%–100%

The escalation policy prioritizes high recall because missing a sensitive account, payment, or security issue is considered more costly than escalating some safe requests unnecessarily.

The resulting trade-off is clear: escalation recall is high, but precision is low.

5. Inter-Annotator Agreement

A 50-example double-labelled set was evaluated using Cohen's κ.

Label	Agreement	Cohen's κ
Intent	78.0%	0.750
Escalation	98.0%	0.847

Both κ values exceed the target threshold of 0.6.

6. LLM Judge

A separate reviewer was implemented with a four-criterion rubric:

Intent correctness
Escalation correctness
Grounding
Reply helpfulness

Each criterion is scored from 1–5, with an overall score calculated from the four criteria.

The reviewer is configured with:

temperature = 0

and requests structured JSON output.

The reviewer is implemented separately from the primary evaluation harness so that model outputs can be audited independently.

Due to the free-tier LLM request quota, a full 200-example reviewer run was not used as evidence. No unsupported reviewer scores are reported.

7. Top Five Failure Modes
8. Ambiguous or underspecified messages

Example:

“Will this be a forever thing? Or how long will this last?”

The message does not contain enough information to identify a precise support intent. The classifier predicted music_availability while the gold label was general_question.

Hypothesis: Short conversational tweets often lack the explicit keywords needed by a small supervised classifier.

2. App technical issues confused with playback issues

Example:

“y isn’t spotify working”

The gold label was app_technical_issue, but the classifier predicted another category.

Hypothesis: Users frequently describe technical failures using generic language such as “not working,” while playback and application failures share overlapping vocabulary.

3. Payment, account, and subscription issues overlap

Example:

“why am I not getting premium after being charged?”

The message contains both payment and subscription concepts, making the correct category difficult for the classifier.

Hypothesis: Several taxonomy categories are semantically adjacent, especially payment_billing, premium_subscription, and account_login.

4. other messages are sometimes forced into specific intents

Example:

“what is this?? ... why does spotify keep doing this”

The classifier predicted music_availability even though the message was labelled other.

Hypothesis: The classifier must choose one of the defined classes even when the message does not contain enough evidence. The explicit other category helps annotation quality but does not completely prevent forced predictions.

5. Premium and playlist/library requests can overlap

Example:

“WHY IS THIS ON MY DISCOVER WEEKLY...”

The gold label was playlist_library, while the classifier predicted music_availability.

Hypothesis: Spotify-specific feature names and content references can resemble music-availability problems without actually indicating missing content.

8. What Is Misleading About My Headline Number?

The headline 45.5% intent accuracy can make the system look like a general-purpose support classifier with moderate performance.

That interpretation is misleading.

The primary agent's intent classifier is the same TF-IDF + Logistic Regression model used by the simple baseline. Therefore, the 45.5% score is not evidence that the complete LLM-powered support workflow improves classification.

In addition, accuracy hides substantial variation between intents. Short and ambiguous messages are particularly difficult, and the model can confidently choose a neighbouring category.

The more informative interpretation is that this is an early-stage triage system with 45.5% intent accuracy but high escalation recall (94.7%), trading automation coverage for safety.

9. What I Would Do With One More Week

With another week, I would focus on:

Expand the labelled training set beyond the small seed dataset.
Add hard negative examples between confusing pairs such as payment/subscription and technical/playback.
Improve the other category with more diverse examples.
Tune escalation thresholds using a held-out validation set rather than manually selected thresholds.
Run a larger LLM-judge evaluation when sufficient API quota is available.
Compare the TF-IDF classifier with a stronger supervised Transformer classifier.
Add calibration and confidence intervals for per-intent performance.
Build the reviewer as a separate HTTP service matching the intended production architecture.
10. Conclusion

The project demonstrates a reproducible support-triage pipeline with classification, historical retrieval, response generation, structured escalation, automated evaluation, baselines, agreement measurement, confidence intervals, and failure analysis.

The main result is deliberately mixed: the primary agent matches rather than beats the simple TF-IDF baseline on intent classification, while its escalation policy achieves 94.7% recall at the cost of low precision.

This makes the current system better viewed as a conservative support-triage prototype rather than a production-ready autonomous support agent.