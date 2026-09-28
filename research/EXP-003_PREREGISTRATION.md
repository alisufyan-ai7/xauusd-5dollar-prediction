# EXP-003 — Economic Outcome / Expected Value Model V1

Status: FROZEN BEFORE EMPIRICAL RESULTS

## Purpose

Test whether XAU/USD trade opportunities can be ranked by **expected executable economic value** rather than by probability of SUCCESS alone.

EXP-003 is a new experiment descended from EXP-002.

It is motivated by the frozen EXP-002 diagnosis:

- SUCCESS-probability ranking retained predictive discrimination;
- high-score regions still contained too many adverse-barrier FAILURES;
- UNRESOLVED expiry P&L was not the dominant loss source;
- classifier score was not reliably monotonic in executable P&L;
- adjacent high-score observations were highly clustered and frequently represented the same market episode.

EXP-003 therefore models the full executable outcome distribution and evaluates decisions at the opportunity/trade level.

FINAL_OOS 2025 remains sealed.

## Data

Primary historical source remains:

- Dukascopy public XAUUSD M1 BID;
- Dukascopy public XAUUSD M1 ASK;
- synchronized using the frozen EXP-002 sparse-side synchronization rules;
- UTC;
- 2016-2024 only for non-sealed research.

No 2025 data may be requested, downloaded, labeled, featurized, scored, summarized, or inspected by EXP-003 development workflows.

## Chronological partitions

Unchanged:

- TRAIN: 2016-2021
- VALIDATION: 2022
- DEVELOPMENT_TEST: 2023-2024
- FINAL_OOS: 2025 — SEALED
- 2026: reserved for later forward/shadow work

No label horizon may cross a partition boundary.

## Executable path semantics

Reuse EXP-002 executable-side semantics unchanged.

At decision bar t:

1. features use information available through close of bar t;
2. decision time = t + 60 seconds;
3. executable entry = next M1 bar open at decision time.

BUY:
- enter ASK open;
- SUCCESS if BID reaches entry +5 before BID reaches entry -3;
- FAILURE if BID reaches entry -3 first.

SELL:
- enter BID open;
- SUCCESS if ASK reaches entry -5 before ASK reaches entry +3;
- FAILURE if ASK reaches entry +3 first.

Horizon:
- 60 calendar minutes;
- exact synchronized BID/ASK M1 coverage required.

UNRESOLVED:
- neither barrier reached in 60 minutes;
- executable expiry P&L uses the frozen EXP-002 side-aware 60th-bar close.

AMBIGUOUS:
- target and adverse touched in the same M1 before order can be determined;
- excluded from model fitting;
- treated conservatively as -3 in economic evaluation unless later adjudicated with ticks.

## Feature policy

EXP-003 V1 reuses the exact frozen EXP-002 feature vector.

No new market-context feature engineering is permitted in V1.

Reason:
the experiment is testing whether changing the **prediction objective** fixes the economic mismatch. Simultaneously changing features would confound attribution.

Frozen feature families therefore remain:

- returns/momentum;
- realized volatility;
- true-range/attainability;
- compression/expansion;
- range location;
- slope/persistence;
- directional agreement;
- candle structure;
- impulse/pullback;
- acceleration/consistency;
- current-day range position;
- round-number distance;
- session transition;
- session volatility;
- causal BID/ASK spread features.

## Model architecture

Train BUY and SELL independently.

Each direction has two frozen components.

### Component A — Three-class outcome model

Target classes:

- SUCCESS
- FAILURE
- UNRESOLVED

AMBIGUOUS rows are excluded from fitting.

Model:
- HistGradientBoostingClassifier
- multiclass log loss
- learning_rate = 0.05
- max_iter = 200
- max_leaf_nodes = 15
- max_depth = None
- min_samples_leaf = 200
- l2_regularization = 1.0
- max_bins = 255
- early_stopping = false
- random_state = 1

TRAIN thinning:
- every 5th eligible chronological TRAIN row, using the same deterministic indexing principle as EXP-002.

No hyperparameter search.

### Component B — UNRESOLVED expiry-P&L model

Training population:
- TRAIN rows whose realized class is UNRESOLVED only.

Target:
- frozen executable 60-minute expiry P&L.

Model:
- HistGradientBoostingRegressor
- loss = squared_error
- learning_rate = 0.05
- max_iter = 200
- max_leaf_nodes = 15
- max_depth = None
- min_samples_leaf = 200
- l2_regularization = 1.0
- max_bins = 255
- early_stopping = false
- random_state = 1

No hyperparameter search.

Predicted unresolved P&L is clipped at [-3.0,+5.0] before entering the EV equation.

Reason:
the unresolved path has not hit either barrier, so an extrapolated prediction outside the barrier range is not economically coherent for this 60-minute decision.

## Expected executable value

For each direction and timestamp:

EV_GROSS =
  5 * P(SUCCESS)
  - 3 * P(FAILURE)
  + P(UNRESOLVED) * predicted_unresolved_expiry_PnL

Primary friction-adjusted score:

EV_F10 = EV_GROSS - 0.10

where 0.10 price units/trade is the frozen EXP-002 F10 additional friction stress.

This score is the primary ranking variable for EXP-003.

The model itself does not choose BUY/SELL. A deterministic decision policy acts on BUY EV_F10 and SELL EV_F10.

## Validation calibration diagnostics

On VALIDATION 2022 only, report:

For the three-class classifier:
- multiclass log loss;
- Brier score per class;
- predicted-vs-realized class shares by probability decile.

For unresolved regression:
- MAE;
- RMSE;
- mean prediction;
- mean realized expiry P&L;
- decile calibration by predicted unresolved P&L.

For EV:
- correlation between EV_F10 and realized F10 P&L;
- realized F10 P&L by EV decile;
- monotonicity diagnostics.

These are descriptive diagnostics only.

No recalibration model or post-hoc transformation may be added in EXP-003 V1.

## Frozen decision policies

EXP-003 preregisters four absolute EV_F10 candidate thresholds:

- T0: EV_F10 > 0.00
- T25: EV_F10 >= +0.25
- T50: EV_F10 >= +0.50
- T75: EV_F10 >= +0.75

These thresholds are fixed **before any EXP-003 model result**.

They are not selected from DEVELOPMENT_TEST.

Purpose:
measure whether requiring a larger predicted economic margin creates robust abstention.

No additional EV threshold may be introduced after results.

## Direction conflict rule

At an eligible decision timestamp:

- neither BUY nor SELL meets the policy threshold => NO TRADE;
- exactly one meets threshold => that direction is eligible;
- both meet threshold:
  - choose the direction with the larger EV_F10 only if the difference is >= 0.25 price units;
  - otherwise => NO TRADE.

The 0.25 conflict margin is frozen before results.

## Opportunity-level / clustering treatment

Raw minute-by-minute qualifying observations are **not** counted as independent trade opportunities.

Operational evaluation uses one global position at a time.

### Opportunity start

An opportunity begins when:
- there is no open position;
- the deterministic policy produces an eligible BUY or SELL.

The trade enters immediately at the frozen executable next-bar open already represented by the row's label semantics.

### Opportunity suppression

While a position is open:
- all later qualifying observations are ignored;
- no pyramiding;
- no averaging;
- no reversal.

After exit:
- the next eligible timestamp may start a new opportunity immediately.

This makes the executed trade sequence—not the raw minute count—the primary economic sample.

Raw signal counts and suppression ratios must still be reported.

## Economic realization

For each executed trade:

SUCCESS:
- gross = +5.00

FAILURE:
- gross = -3.00

UNRESOLVED:
- gross = actual stored executable expiry P&L

AMBIGUOUS:
- gross = -3.00 conservatively

Primary net:
- NET_F10 = gross - 0.10

Additional stress reporting:
- F0 = gross
- F05 = gross -0.05
- F10 = gross -0.10
- F20 = gross -0.20

## Required evaluation

Report separately for each threshold T0/T25/T50/T75:

- BUY_ONLY
- SELL_ONLY
- COMBINED conflict-rule policy

For:
- VALIDATION 2022
- DEVELOPMENT_TEST overall
- 2023
- 2024
- each 2023-2024 quarter

Metrics:
- raw qualifying observations;
- executed trades;
- suppression ratio;
- SUCCESS / FAILURE / UNRESOLVED / AMBIGUOUS counts;
- mean and median gross P&L;
- mean and median F10 P&L;
- profit factor;
- cumulative P&L;
- max drawdown;
- active trading days;
- trades per active day;
- trades per calendar day;
- median / p25 / p75 / p90 holding time.

## Dependence-aware uncertainty

For each policy/mode:

- group completed DEVELOPMENT_TEST trades by UTC entry date;
- bootstrap whole UTC entry dates with replacement;
- 2,000 deterministic replicates;
- random seed = 3;
- report 95% percentile CI of mean NET_F10 per trade.

## Primary advancement rule

A threshold/mode combination may be nominated for a separate immutable pre-OOS candidate freeze only if ALL of the following hold:

1. mean NET_F10 > 0 in 2023;
2. mean NET_F10 > 0 in 2024;
3. overall F10 profit factor > 1;
4. UTC-day bootstrap 95% CI lower bound for mean NET_F10 > 0;
5. at least 250 executed DEVELOPMENT_TEST trades overall;
6. at least 75 executed trades in each of 2023 and 2024;
7. no single calendar quarter contributes more than 40% of total positive F10 P&L;
8. AMBIGUOUS rows are conservatively treated as -3;
9. 2025 remains untouched.

Passing does not automatically open 2025.

If more than one policy passes, no winner is chosen post hoc in this milestone. All passing policies are retained for a separately preregistered candidate-freeze decision.

## Secondary diagnostic requirements

Regardless of pass/fail, report:

- realized FAILURE probability by EV_F10 decile;
- realized SUCCESS probability by EV_F10 decile;
- unresolved rate and unresolved mean P&L by EV_F10 decile;
- 2023 vs 2024 EV calibration;
- raw-signal clustering/suppression;
- session / volatility / spread decomposition for descriptive diagnosis only.

These diagnostics may motivate a future experiment but may not change EXP-003 V1 policies.

## Governance

EXP-003 V1 must not:

- access 2025;
- search model hyperparameters;
- add new features;
- add new thresholds after seeing results;
- promote a regime filter post hoc;
- promote BUY-only or SELL-only solely because it looks best;
- reinterpret failed gates;
- proceed to Exness demo/live trading.

Negative results are fully admissible.

## Exit states

EXP-003 V1 ends in one of:

A. NO POLICY PASSES
- keep 2025 sealed;
- diagnose;
- redesign only through a new preregistered experiment.

B. ONE OR MORE POLICIES PASS
- keep 2025 sealed;
- create a separate immutable candidate-freeze milestone;
- audit implementation and leakage before any FINAL_OOS access.

2025 remains sealed in either case.
