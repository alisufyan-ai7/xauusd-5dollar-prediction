# EXP-001 Calibration and Abstention Milestone V1

Status: FROZEN BEFORE EXECUTION

## Purpose

Keep the already-frozen GBT V1 model unchanged and test whether its raw scores can be converted into more useful probabilities and robust abstention bands.

This milestone does not alter:
- labels;
- V2 features;
- TRAIN / VALIDATION / DEVELOPMENT_TEST partitions;
- GBT hyperparameters;
- TRAIN thinning rule.

FINAL_OOS 2025 remains strictly sealed.

## Model reproduction

Reproduce GBT V1 exactly:

- HistGradientBoostingClassifier
- learning_rate 0.05
- max_iter 200
- max_leaf_nodes 15
- min_samples_leaf 200
- l2_regularization 1.0
- max_bins 255
- early_stopping false
- random_state 1
- every 5th eligible TRAIN row, chronological

Fit separate BUY and SELL models.

## Calibration method

Use Platt-style logistic calibration only.

Procedure:
1. Train frozen GBT V1 on TRAIN only.
2. Generate raw GBT probabilities for all eligible VALIDATION rows.
3. Convert raw probability p to logit log(p / (1-p)), clipped to [1e-6, 1-1e-6].
4. Fit one unregularized-equivalent logistic calibration mapping per direction on VALIDATION:
   - sklearn LogisticRegression
   - C = 1e6
   - solver = lbfgs
   - max_iter = 1000
   - random_state = 1
5. Apply the fixed calibrator to DEVELOPMENT_TEST without refitting.

VALIDATION calibrated metrics are in-sample for the calibrator and must be identified as such.
DEVELOPMENT_TEST calibrated metrics are the primary out-of-time calibration evidence.

No isotonic regression and no calibration-method search in V1.

## Abstention / rank-band study

Raw GBT score ranking is retained for abstention analysis.

Derive fixed raw-score cutoffs from VALIDATION quantiles corresponding to:
- top 50%;
- top 30%;
- top 20%;
- top 10%;
- top 5%;
- top 2.5%;
- top 1%.

For each direction:
- compute the raw-score cutoff on VALIDATION;
- report count, share, realized success rate, and mean calibrated probability in VALIDATION;
- apply that exact raw-score cutoff unchanged to DEVELOPMENT_TEST;
- report the same metrics there.

These are descriptive research bands, not live trading thresholds.

## Calibration evaluation

Report raw and calibrated, separately for VALIDATION and DEVELOPMENT_TEST:

- n;
- base rate;
- Brier score;
- log loss;
- ROC-AUC;
- PR-AUC;
- 10-bin calibration table.

Discrimination metrics should remain unchanged by monotonic Platt calibration except for numerical ties.

## Stability checks

For each fixed VALIDATION-derived abstention band report:
- VALIDATION success rate;
- DEVELOPMENT_TEST success rate;
- absolute difference;
- DEVELOPMENT_TEST opportunity share.

Also report whether realized success is monotonic as selectivity increases.

## Governance

- 2025 is not read, summarized, or used.
- No threshold is selected for live trading in this milestone.
- No calibration method, feature, GBT parameter, or percentile band may be changed after results without a new documented iteration.
- Weak or negative calibration is admissible.
