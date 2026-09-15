# Hiver Support Agent — SpotifyCares

An LLM-powered customer-support triage agent for SpotifyCares tweets.

## Overview

The system:

- Classifies incoming customer messages into support intents
- Retrieves similar historical support cases
- Decides whether a case should be escalated
- Generates a grounded support reply using an LLM when available
- Falls back to a safe response when the LLM is unavailable
- Evaluates intent classification and escalation performance
- Includes trivial and TF-IDF baselines
- Includes an LLM reviewer with a four-criterion rubric

## Project Structure

hiver-support-agent/
├── data/
│   ├── training_data.csv
│   ├── spotify_cases.csv
│   └── sample_data.csv
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
│   ├── sampling_notes.md
│   ├── decision_log.md
│   ├── agreement.py
│   ├── failure_analysis.py
│   ├── evaluate_primary_agent.py
│   ├── reviewer.py
│   ├── confidence_intervals.py
│   ├── confidence_intervals.json
│   ├── run_baselines.py
│   ├── baseline_results.json
│   └── primary_agent_results.json
│
├── tests/
├── REPORT.md
├── requirements.txt
├── run_pipeline.py
└── README.md


Large raw data files and generated model embeddings are excluded from GitHub
using `.gitignore`.

## Requirements

* Python 3.9+
* Internet connection for downloading the Sentence Transformer model
* Gemini API key for LLM-generated responses and reviewer evaluation

The deterministic classification, retrieval, and escalation components can
run without Gemini.

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

The project uses customer-support interactions from the Customer Support on
Twitter dataset.

For reproducibility, the repository includes a prepared SpotifyCares dataset:

data/spotify_cases.csv

The repository also includes:

data/sample_data.csv

which contains 500 SpotifyCares customer messages for the sample pipeline.

The historical examples are used for semantic retrieval.

## Run the Primary Pipeline

The main reproducible command is:

python run_pipeline.py --brand SpotifyCares --sample

The sample pipeline processes 500 customer messages and saves results to:

evaluation/pipeline_results.json

## Primary Agent Output

The agent returns structured information containing:

* Intent
* Intent confidence
* Escalation decision
* Escalation reason
* Retrieval similarity
* Generated or fallback reply
* Grounding flag
* Retrieved historical examples

The LLM response-generation path uses Gemini when an API key and available
quota are present. A safe deterministic fallback is used when the LLM is
unavailable.

## Evaluation

Run the deterministic 200-example evaluation:

python evaluation\evaluate_primary_agent.py

Results are written to:

evaluation\primary_agent_results.json

### Metrics

The evaluation measures:

* Intent accuracy
* Intent macro F1
* Escalation precision
* Escalation recall

## Confidence Intervals

95% bootstrap confidence intervals are calculated using 5,000 bootstrap
samples with random seed 42.

Run:

python evaluation\confidence_intervals.py

Results are written to:

evaluation\confidence_intervals.json

### Current Primary Agent Results

| Metric               | Result | 95% Bootstrap CI |
| -------------------- | -----: | ---------------: |
| Intent accuracy      |  45.5% |      38.5%–52.5% |
| Intent macro F1      |  0.449 |      0.377–0.509 |
| Escalation precision |  10.0% |       5.7%–14.6% |
| Escalation recall    |  94.7% |       82.3%–100% |

The confidence intervals are based on the 200-example evaluation set.

## Baselines

Two baselines are included and are actually run end-to-end.

Run:

python evaluation\run_baselines.py

Results are saved to:

evaluation\baseline_results.json

### Results Comparison

| System                       | Intent Accuracy | Macro F1 |
| ---------------------------- | --------------: | -------: |
| Trivial majority baseline    |            2.0% |    0.004 |
| TF-IDF + Logistic Regression |           45.5% |    0.449 |
| Primary Agent                |           45.5% |    0.449 |

The Primary Agent ties the simple TF-IDF baseline on intent metrics because
the deterministic evaluation uses the same TF-IDF + Logistic Regression
classifier for intent prediction.

Therefore, the results do not demonstrate an improvement in intent
classification over the simple baseline. The additional value of the
Primary Agent is in retrieval, response generation, grounding, and
escalation workflow.

### Trivial Baseline

The trivial baseline always predicts the majority intent from the training
set.

### TF-IDF Baseline

The simple baseline uses:

* TF-IDF features
* Unigram and bigram features
* Logistic Regression

## Golden Set

The evaluation uses a 200-example golden set.

Sampling and annotation details are documented in:

evaluation/sampling_notes.md

The sampling process uses stratified candidate selection across the
11-intent taxonomy and a fixed random seed of 42.

The final examples were manually reviewed and assigned intent and
`should_escalate` labels.

The codebook defining the intent categories and edge cases is:

evaluation/codebook.md

## Double-Label Agreement

A 50-example double-labelled set is included in:

evaluation/double_label_50.json

Run:

python evaluation\agreement.py

Agreement is measured using Cohen's kappa.

### Agreement Results

| Criterion  | Agreement | Cohen's κ |
| ---------- | --------: | --------: |
| Intent     |     78.0% |     0.750 |
| Escalation |     98.0% |     0.847 |

Both reported κ values exceed the target threshold of 0.60.

## LLM Reviewer

A separate LLM reviewer is implemented in:

evaluation/reviewer.py

The reviewer evaluates the support-agent output using four criteria:

1. Intent correctness
2. Escalation correctness
3. Grounding
4. Reply helpfulness

Each criterion is scored from 1–5.

The reviewer is configured with:

* Temperature = 0
* Structured JSON output
* Overall score calculated from the four criteria

Run when Gemini API quota is available:

python evaluation\reviewer.py

The reviewer reads:

evaluation\primary_agent_results.json

and writes:

evaluation\reviewer_results.json

Because the available Gemini free-tier request quota limited the number of
LLM calls during development, reviewer results are not presented as a
full-200-example evaluation.

## Failure Analysis

Run:

python evaluation\failure_analysis.py


The analysis identifies common intent-confusion pairs and representative
errors.

The main observed failure modes include:

1. Ambiguous or underspecified messages
2. App technical issues confused with playback issues
3. Payment, account, and subscription overlap
4. Unclear messages being forced into specific intents
5. Premium and playlist/library overlap

Detailed examples and hypotheses are included in `REPORT.md`.

## Limitations

The classifier was trained using a small manually-created seed training set,
so intent classification remains limited.

The primary agent's intent classifier currently matches the simple TF-IDF
baseline rather than outperforming it.

The escalation policy intentionally prioritizes recall for potentially
sensitive cases. This results in high escalation recall but low escalation
precision.

The Gemini free tier imposed a request quota during development. Therefore,
the 200-example deterministic evaluation was run with LLM generation
disabled rather than presenting fallback outputs as genuine LLM evaluation
results.

The live Gemini path was tested separately and successfully produced
structured support output before the quota was exhausted.

## What I Chose Not to Build

To keep the project focused on evaluation and reproducibility, the following
were intentionally outside the scope:

* Production web/mobile UI
* Real-time Twitter/X integration
* Automated account or payment actions
* Production database
* Full human-agent dashboard
* Continuous model retraining
* Production monitoring infrastructure

## Future Work

With another week, I would:

* Expand the labelled training set
* Improve intent boundary definitions
* Add hard negative examples for confusing intent pairs
* Improve the `other` category
* Calibrate classifier confidence
* Tune escalation thresholds using a held-out validation set
* Evaluate the complete LLM pipeline with a larger API quota
* Compare against a stronger supervised Transformer classifier
* Build the reviewer as a separate HTTP service
* Add more automated tests for structured LLM output

## Report

The complete evaluation report is available in:

REPORT.md

It includes:

* Problem framing
* What was intentionally not built
* Results versus both baselines
* Confidence intervals
* Top five failure modes
* Real failure examples and hypotheses
* What is misleading about the headline number
* One-week future work

