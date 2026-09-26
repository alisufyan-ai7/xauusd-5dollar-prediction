# EXP-001 Preregistration — $5 Directional Target Feasibility

Status: DRAFT / NOT YET EXECUTED

## 1. Objective

Determine whether XAU/USD contains identifiable market states in which a USD 5 directional target is reached before a USD 3 adverse excursion within 60 minutes, using only information available at the decision timestamp.

This experiment is for predictive feasibility research. It is not authorization for live trading.

## 2. Instrument

XAU/USD.

Broker context for later forward/demo validation: Exness.

Historical research data does not need to originate from Exness if a suitable public source is lawfully usable, reproducible, timestamp-sound, and documented for this project.

## 3. Primary outcome definition

At each eligible decision timestamp t, define reference price P(t).

### BUY hypothesis

- Target: P(t) + 5.00 USD
- Adverse barrier: P(t) - 3.00 USD
- Horizon: 60 minutes
- Success: +5.00 target is reached before -3.00 adverse barrier, within horizon
- Failure: -3.00 adverse barrier is reached before +5.00 target, within horizon
- Unresolved: neither barrier is reached within horizon

### SELL hypothesis

- Target: P(t) - 5.00 USD
- Adverse barrier: P(t) + 3.00 USD
- Horizon: 60 minutes
- Success: -5.00 target is reached before +3.00 adverse barrier, within horizon
- Failure: +3.00 adverse barrier is reached before -5.00 target, within horizon
- Unresolved: neither barrier is reached within horizon

Any ambiguity involving same-timestamp target/adverse touches must be resolved using data granularity sufficient to determine ordering. If ordering cannot be established, the sample must be marked ambiguous rather than guessed.

## 4. Decision interval

Initial candidate decision interval: one minute, subject to validation that the admitted data source supports reliable construction without future leakage.

Overlapping observations will not be treated as independent evidence. A separate episode/dependence analysis is required before inferential statistics are accepted.

## 5. Required path metrics

For every labeled sample, compute where supported by source granularity:

- maximum favorable excursion (MFE);
- maximum adverse excursion (MAE);
- time to target;
- time to adverse barrier;
- first barrier touched;
- unresolved/ambiguous status.

## 6. Initial feature families

All features must be timestamp-safe and use data at or before t only.

Candidate families:

- price returns over multiple backward horizons;
- realized volatility and range measures;
- candle body/wick/range structure;
- distance to recent highs/lows;
- breakout/consolidation structure;
- multi-horizon momentum and acceleration;
- trading-session/time-of-day variables;
- scheduled macro-event proximity using fresh public event sources;
- selected cross-market variables only if timestamp alignment can be proven.

No feature is admissible merely because it improves results. Its construction must be documented and leakage-tested.

## 7. Baseline requirement

Before machine learning, compute unconditional and regime-conditional target-before-adverse probabilities.

At minimum segment by:

- session/time of day;
- volatility regime;
- broad trend regime;
- event versus non-event periods, if event data is admitted.

## 8. Model order

Model complexity should increase only after simpler baselines are established:

1. statistical/unconditional baseline;
2. logistic regression or comparable transparent baseline;
3. gradient-boosted tree model;
4. more complex sequence/neural models only if justified by evidence.

## 9. Output and abstention

The system must support NO-TRADE/ABSTAIN behavior.

Research outputs should estimate directional success probability rather than force a BUY or SELL at every eligible timestamp.

Predefined confidence bands for reporting:

- 60–65%
- 65–70%
- 70–75%
- 75–80%
- 80–85%
- 85–90%
- >=90%

These bands are reporting bins, not pre-approved live-entry thresholds.

## 10. Chronological validation

Random train/test splitting is prohibited for the primary evaluation.

Final partition dates will be frozen only after admissible historical coverage is known. The required structure is:

- training period;
- validation period;
- development-test period if needed;
- final untouched out-of-sample period;
- forward shadow/demo period.

The final OOS period must not influence feature selection, model selection, thresholds, or hyperparameters.

## 11. Calibration

Predicted probabilities must be checked against observed out-of-sample frequencies.

Required reporting includes:

- calibration by confidence band;
- signal counts;
- wins/failures/unresolved;
- confidence intervals or an appropriate dependence-aware uncertainty estimate;
- opportunity frequency over time.

## 12. Robustness

Any candidate edge must be stress-tested across:

- calendar subperiods;
- market regimes;
- volatility regimes;
- sessions;
- weekdays;
- event/non-event periods where available;
- reasonable neighboring parameter values.

A result that exists only at one exact threshold or narrow configuration is presumptively fragile.

## 13. Execution separation

EXP-001 answers a prediction question first.

Spread, commission, slippage, execution latency, gaps, and fill modeling are required before any profitability conclusion, but they must not be confused with proof of predictive signal.

## 14. Forward validation

Before live-money capability is considered, a frozen model must produce timestamped shadow/demo predictions before outcomes are known.

Each prediction record should include:

- timestamp;
- observed price;
- direction or abstention;
- predicted probability;
- target;
- adverse barrier;
- expiry;
- model/config version;
- feature/data version identifier.

## 15. Safety state

- No live-money trading.
- No broker account mutation.
- No automated order placement.
- No credentials stored in this repository.
- Exness integration, when eventually implemented, begins in read-only/shadow or demo-safe mode.

## 16. EXP-001 execution prerequisites

EXP-001 must not run until the following are documented:

1. admitted free public historical source;
2. timestamp/timezone convention;
3. raw-data integrity checks;
4. derivation rules for any bars/features;
5. target/adverse touch-order handling;
6. chronological partition plan;
7. immutable experiment/config identifier.

## 17. Failure is an admissible result

If final out-of-sample performance does not materially exceed the appropriate baseline, EXP-001 fails. The result must not be repaired by tuning against the final OOS period.
