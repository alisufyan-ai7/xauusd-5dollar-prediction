# EXP-001 Gradient-Boosted Trees Milestone V1

Status: FROZEN BEFORE EXECUTION

## Purpose

Test whether nonlinear interactions among the already-frozen V2 expert features improve chronological prediction of:

- BUY: +$5 before -$3 within 60 minutes;
- SELL: -$5 before +$3 within 60 minutes.

This milestone follows Logistic V1 and does not change labels, partitions, or feature definitions.

## Data partitions

- TRAIN: 2016-2021 — model fitting only.
- VALIDATION: 2022 — first chronological evaluation.
- DEVELOPMENT_TEST: 2023-2024 — second chronological evaluation.
- FINAL_OOS: 2025 — strictly not accessed.
- AMBIGUOUS excluded.
- SUCCESS = 1.
- FAILURE and UNRESOLVED = 0.
- Rows require complete outcome coverage, partition eligibility, and V2 feature completeness.

## Frozen feature set

Use exactly the same numeric V2 feature list as EXP-001 Logistic V1.

No features may be added, removed, or transformed after seeing GBT V1 results.

## Direction handling

Fit two independent models:

- BUY using buy_label.
- SELL using sell_label.

## Model class

Use scikit-learn HistGradientBoostingClassifier.

Frozen configuration:

- loss: log_loss
- learning_rate: 0.05
- max_iter: 200
- max_leaf_nodes: 15
- max_depth: null
- min_samples_leaf: 200
- l2_regularization: 1.0
- max_bins: 255
- early_stopping: false
- random_state: 1

No class weighting.
No hyperparameter search.
No threshold tuning.

## Memory strategy

The preserved V2 checkpoint is reused.

Training may use deterministic temporal thinning of TRAIN rows if necessary to fit GitHub-hosted runner memory constraints, but:
- thinning rule must be fixed before results;
- validation and development-test evaluation must use all eligible rows;
- if thinning is used, select every 5th eligible TRAIN row in chronological order.

The default run should first attempt the every-5th TRAIN sample directly.

## Evaluation

For BUY and SELL separately report on TRAIN, VALIDATION, DEVELOPMENT_TEST:

- row count;
- positives/base rate;
- ROC-AUC;
- PR-AUC;
- Brier score;
- log loss;
- 10-bin calibration table;
- predicted-probability quantiles;
- success rate/count/share above descriptive cutoffs 0.20, 0.30, 0.40, 0.50, 0.60.

Also report:
- feature importances via permutation importance on a fixed chronological sample of VALIDATION capped at 50,000 rows;
- top 15 features by mean importance.

The importance analysis is descriptive only and must not be used to retune GBT V1.

## Comparison to Logistic V1

Compare chronologically against the already-completed Logistic V1 on:
- ROC-AUC;
- PR-AUC;
- Brier;
- log loss;
- high-score tail success rates.

The GBT milestone is informative even if it fails to outperform the linear baseline.

## Governance

- 2025 remains sealed.
- No feature/hyperparameter/threshold changes after seeing GBT V1 without opening a new documented experiment iteration.
- A negative result is admissible.
