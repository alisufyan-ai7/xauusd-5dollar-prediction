# EXP-001 M1 Labeling Specification

Status: IMPLEMENTED FOR TESTING

## Frozen decision semantics

For each M1 bar with start timestamp `t_bar`:

- reference price = that bar's **close**;
- decision time = `t_bar + 60 seconds`;
- the decision bar's own high/low is never used to determine the future outcome;
- scanning begins at the next chronological M1 bar;
- horizon = 60 calendar minutes from decision time;
- BUY target = reference + USD 5;
- BUY adverse = reference - USD 3;
- SELL target = reference - USD 5;
- SELL adverse = reference + USD 3.

This avoids using price movement that happened before the decision/entry price existed.

## Directional terminal states

For BUY and SELL independently:

- `SUCCESS`: target touched in an earlier bar than adverse;
- `FAILURE`: adverse touched in an earlier bar than target;
- `AMBIGUOUS`: target and adverse both touched within the same M1 bar, so OHLC cannot establish ordering;
- `UNRESOLVED`: neither barrier touched within the available bars inside the 60-minute calendar horizon.

No assumed OHLC intrabar path is permitted.

## Gap handling

The horizon is calendar-time based, not "next 60 observed rows."

If bars are missing, the scanner does not extend the window to compensate.

Each output row therefore includes:

- `bars_observed`;
- `coverage_complete`.

Incomplete coverage is retained for auditing but must not be silently treated as equivalent to a fully observed unresolved outcome in later statistical analysis.

## MFE / MAE

For each direction, MFE and MAE are measured from the reference price over observed future bars up to and including the terminal bar. For unresolved observations they cover all observed bars inside the horizon.

For ambiguous terminal bars, MFE and MAE include that ambiguous bar, but no barrier ordering is inferred.

## Timing precision

M1 OHLC cannot reveal the exact second of a touch. Therefore the implementation stores:

- terminal bar offset;
- terminal bar start timestamp.

It does not invent sub-minute time-to-touch values.

## Tick adjudication

A later tick-level stage may resolve M1 `AMBIGUOUS` observations. Until then they remain excluded from success/failure claims.
