# Hiver Support Agent — SpotifyCares

An LLM-powered customer-support triage agent for SpotifyCares tweets.

The system:

- Classifies incoming customer messages into support intents
- Retrieves similar historical support cases
- Decides whether a case should be escalated
- Generates a grounded support reply using an LLM when available
- Falls back to a safe response when the LLM is unavailable

## Project Structure

hiver-support-agent/
├── data/
│   ├── training_data.csv
│   ├── spotify_cases.csv
│   ├── spotify_case_embeddings.npy
│   └── twcs.csv
│
├── src/
│   ├── primary_agent.py
│   ├── classifier.py
│   ├── retriever.py
│   ├── escalation.py
│   └── intents.py
│
├── evaluation/
│   ├── golden_200.json
│   ├── double_label_50.json
│   ├── codebook.md
│   ├── decision_log.md
│   ├── agreement.py
│   ├── failure_analysis.py
│   ├── evaluate_primary_agent.py
│   ├── reviewer.py
│   └── primary_agent_results.json
│
├── tests/
├── requirements.txt
└── README.md

## Requirements

* Python 3.9+
* Internet connection for downloading the Sentence Transformer model
* Gemini API key for LLM-generated responses

The deterministic classification, retrieval, and escalation components can run without Gemini.

## Installation

Create and activate a virtual environment if desired:

python -m venv .venv

### Windows

.venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

## API Key

Set the Gemini API key as an environment variable.

### Windows CMD

set GEMINI_API_KEY=YOUR_API_KEY

### PowerShell

$env:GEMINI_API_KEY="YOUR_API_KEY"

Never commit the API key to GitHub.

## Dataset

The project uses customer-support interactions from the Customer Support on Twitter dataset.

For reproducibility, the project includes Spotify-related customer/support examples in:

data/spotify_cases.csv

The historical examples are used for semantic retrieval.

## Run the Primary Agent

Run:

python src\primary_agent.py

The example query is:

Why can't I update my payment details?

The agent returns structured JSON containing:

* Intent
* Intent confidence
* Escalation decision
* Escalation reason
* Retrieval similarity
* Generated/fallback reply
* Grounding flag
* Retrieved historical examples

## Required Pipeline Command

The intended sample pipeline command is:

python run_pipeline.py --brand SpotifyCares --sample

## Evaluation

Run the 200-example deterministic evaluation:

python evaluation\evaluate_primary_agent.py

Results are written to:

evaluation/primary_agent_results.json

Metrics:

* Intent accuracy
* Intent macro F1
* Escalation precision
* Escalation recall

## Baselines

Two baselines are included.

### 1. Trivial Baseline

Always predicts the majority intent.

### 2. TF-IDF Baseline

Uses:

* TF-IDF features
* Unigram and bigram features
* Logistic Regression

Run the classifier with:

python src\classifier.py

## Human Agreement

The double-labelled set contains 50 examples.

Run:

python evaluation\agreement.py

Agreement is measured using Cohen's kappa.

### Current Results

| Criterion  | Agreement | Cohen's κ |
| ---------- | --------: | --------: |
| Intent     |     78.0% |     0.750 |
| Escalation |     98.0% |     0.847 |

Both exceed the target κ ≥ 0.60.

## Failure Analysis

Run:

python evaluation\failure_analysis.py

The analysis identifies common intent-confusion pairs and representative errors.

## LLM Reviewer

The reviewer uses a four-criterion rubric:

1. Intent correctness
2. Escalation correctness
3. Grounding
4. Reply helpfulness

Each criterion is scored from 1–5.

The reviewer is configured with:

* Temperature = 0
* Structured JSON output

Run when Gemini API quota is available:

python evaluation\reviewer.py

## Current Evaluation Results

The 200-example deterministic pipeline produced:

| Metric               | Result |
| -------------------- | -----: |
| Intent accuracy      |  45.5% |
| Intent macro F1      |  0.449 |
| Escalation precision |   9.5% |
| Escalation recall    | 100.0% |

The escalation policy intentionally prioritizes recall for potentially sensitive cases. This produces many false-positive escalations.

## Limitations

The classifier was trained using a small manually-created seed training set, so intent classification remains limited.

The Gemini free tier also imposed a request quota during evaluation. Therefore, the 200-example evaluation was run with LLM generation disabled rather than presenting fallback outputs as genuine LLM evaluation results.

The live Gemini path was tested separately and successfully produced structured support output before the quota was exhausted.

## Future Work

Potential improvements include:

* Expand the labelled training set
* Improve intent boundary definitions
* Add confidence calibration
* Tune escalation thresholds using a validation set
* Evaluate the full LLM pipeline with a larger API quota
* Improve the `other` category
* Add automated tests for structured LLM output
* Evaluate confidence intervals for reported metrics



