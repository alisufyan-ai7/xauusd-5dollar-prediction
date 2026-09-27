# EXP-001 Initial Feature and Baseline Stage

Status: IMPLEMENTED FOR NON-SEALED PARTITIONS

## Timestamp rule

The decision occurs at the close of M1 bar t. Every feature uses bar t or earlier only. No future bar is admissible.

## Initial features

- close-to-close returns: 1m, 5m, 15m, 60m;
- current candle range/body/upper wick/lower wick;
- rolling 15m and 60m high-low range;
- distance to 15m/60m rolling highs and lows;
- 15m and 60m root-mean-square one-minute price changes;
- UTC hour and weekday;
- fixed UTC session bucket: ASIA / EUROPE / US / LATE.

A row is feature-complete only when the required 60-minute history is contiguous.

## Baseline eligibility

Rows used in baseline summaries must have:

- partition in TRAIN, VALIDATION, or DEVELOPMENT_TEST;
- complete 60-minute forward outcome coverage;
- complete 60-minute feature history;
- partition-boundary eligibility.

Ambiguous labels are excluded from the denominator of success-rate calculations but counted separately.

Two descriptive rates are reported:

1. success / all non-ambiguous eligible states, where unresolved is a non-success;
2. success / resolved states (SUCCESS + FAILURE) only.

## Regime baselines

Initial descriptive segmentation:

- fixed UTC session;
- 60m realized-volatility tertiles, with thresholds learned from TRAIN only;
- coarse 60m momentum bucket: DOWN (< -$1), FLAT (-$1 to +$1), UP (> +$1).

These are baselines, not approved trading thresholds.

## Final OOS

2025 FINAL_OOS is forbidden as input to this stage.
