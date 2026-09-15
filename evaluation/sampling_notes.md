# Golden Set Sampling Notes

## Source Dataset

The golden set was created from the prepared SpotifyCares historical
customer-support dataset:

`data/spotify_cases.csv`

Rows with missing customer messages and duplicate customer messages were
removed before sampling.

Approximately 4,948 unique customer messages were available after filtering.

## Golden Set

A total of 200 examples were selected for the golden set.

The sampling plan targeted 15 examples for each of the 11 intent categories,
followed by 35 additional randomly selected examples.

The 11 intent categories were:

- playback_issue
- app_technical_issue
- account_login
- premium_subscription
- payment_billing
- music_availability
- playlist_library
- feature_request
- availability_region
- general_question
- other

## Stratification

The sample was stratified across the project's 11 intent categories to
ensure broad coverage of the taxonomy.

The selected examples were then manually reviewed and assigned their final
gold intent labels and `should_escalate` labels.

The provisional classifier labels used during candidate selection were
treated only as sampling aids and were not used as the final gold labels.

## Random Seed

A fixed random seed of 42 was used throughout the sampling process:

- selecting candidates for each intent category
- selecting the additional 35 examples
- shuffling the final 200 examples

Using a fixed seed makes the sampling process reproducible when the same
source data and classifier are used.

## Annotation

Each selected example was manually assigned:

- a final intent label
- a `should_escalate` label

The final annotations are stored in:

`evaluation/golden_200.json`

## Time Range

The sampling script did not apply an explicit date-range filter. Therefore,
the golden set represents the available SpotifyCares interactions in the
prepared dataset rather than a separately defined time window.

## Reproducibility

The repository contains the prepared SpotifyCares data, golden set, sampling
documentation, and evaluation scripts needed to reproduce the evaluation
workflow.