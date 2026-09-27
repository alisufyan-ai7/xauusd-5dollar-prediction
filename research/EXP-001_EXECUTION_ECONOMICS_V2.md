# EXP-001 Execution Economics V2 — Dukascopy BID/ASK Tick Reconstruction

Status: FROZEN BEFORE EXECUTION

## Purpose

Reconstruct side-aware historical execution for the already-frozen EXP-001 GBT signal policies using Dukascopy XAUUSD tick data containing BID and ASK on each tick.

This is a new execution experiment. It does not alter the predictive model, features, labels, partitions, or score-band definitions.

FINAL_OOS 2025 remains sealed.

## Public-data basis

Dukascopy historical ticks expose both ASK and BID in each tick. The pinned downloader is:

- dukascopy-node@1.50.0
- instrument: xauusd
- timeframe: tick
- UTC
- CSV

Expected tick columns:

- timestamp
- askPrice
- bidPrice
- askVolume
- bidVolume

## Predictive model and partitions

Unchanged from corrected GBT V1:

- TRAIN: 2016-2021
- VALIDATION: 2022
- DEVELOPMENT_TEST: 2023-2024
- FINAL_OOS: 2025 sealed
- separate BUY and SELL GBTs
- every 5th eligible TRAIN row, chronological
- same frozen V2 feature set and GBT hyperparameters

Operational cutoffs are derived from ALL partition-boundary-eligible, feature-complete VALIDATION decision rows, regardless of future label or future coverage_complete flag, at:

- top 10%
- top 5%
- top 2.5%
- top 1%

The raw-score cutoffs are applied unchanged to all partition-boundary-eligible, feature-complete DEVELOPMENT_TEST decision rows.

Operational scoring MUST NOT require coverage_complete because that flag depends on the future 60-minute path. Training labels still require complete forward coverage. Tick reconstruction separately determines whether a scored historical signal has executable tick coverage.

## Tick acquisition minimization

Do not download all 2023-2024 ticks blindly.

Procedure:

1. reproduce fixed DEVELOPMENT_TEST scores from corrected M1 inputs;
2. identify decision timestamps where either BUY or SELL reaches the top-10% cutoff;
3. collect unique UTC calendar dates containing at least one such candidate signal;
4. acquire Dukascopy XAUUSD tick data only for those UTC dates;
5. validate each downloaded tick file;
6. reconstruct all four policies from those tick files;
7. raw tick files are workflow scratch data and are not committed to Git.

Because top 5%, 2.5%, and 1% are strict subsets of top 10%, this covers all frozen policies.

## Executable entry semantics

Signal time is the frozen decision_time_ms from the M1 pipeline.

For a qualifying trade:
- locate the first Dukascopy tick timestamp >= decision_time_ms;
- it must occur within 60 seconds of decision_time_ms or the trade is marked EXECUTION_UNAVAILABLE and excluded from economic claims.

BUY:
- executable entry price = ASK on the entry tick.

SELL:
- executable entry price = BID on the entry tick.

The 60-minute horizon remains anchored to the original decision time, not the fill timestamp.

## Barrier semantics from executable entry

BUY:
- profit target = entry ASK + 5.00;
- adverse barrier = entry ASK - 3.00;
- target is executable when BID >= target;
- adverse is executable when BID <= adverse.

SELL:
- profit target = entry BID - 5.00;
- adverse barrier = entry BID + 3.00;
- target is executable when ASK <= target;
- adverse is executable when ASK >= adverse.

Ticks are processed strictly in timestamp order.

Tick data therefore resolves the same-minute ordering ambiguity that exists in M1 OHLC.

## Expiry semantics

Expiry time = decision_time_ms + 60 minutes.

If neither barrier has fired:
- use the last valid tick at or before expiry;
- the tick must be no more than 5 seconds older than expiry, otherwise mark EXECUTION_UNAVAILABLE.

BUY expiry exit = BID.
SELL expiry exit = ASK.

Barrier exits use the first executable tick that crosses the corresponding level. Gross P&L uses that tick's actual executable quote, so historical gaps beyond the nominal +5/-3 barrier are preserved rather than clipped.

Gross P&L in XAUUSD price units:

BUY:
exit BID - entry ASK.

SELL:
entry BID - exit ASK.

Thus the Dukascopy historical spread is naturally included through executable entry/exit sides.

## Signal/position engine

Evaluate three preregistered modes:

- BUY_ONLY
- SELL_ONLY
- COMBINED

COMBINED:
- if neither direction qualifies: NO TRADE;
- if BUY and SELL both qualify at the same decision time: NO TRADE;
- if exactly one qualifies and no position is open: enter;
- while a position is open, ignore all subsequent signals until exit.

BUY_ONLY and SELL_ONLY:
- only the respective direction is eligible;
- one position at a time;
- ignore additional same-direction signals while open.

No pyramiding.
No averaging.
No reversal while a position is open.

## Additional friction stress

Dukascopy BID/ASK spread is already embedded in P&L.

Apply an additional completed-trade deduction to proxy commission + adverse slippage:

- F0: 0.00 price units
- F05: 0.05
- F10: 0.10
- F20: 0.20

These are stress scenarios, not assertions about a particular Exness account.

No swap is modeled because maximum holding period is 60 minutes.

## Required outputs

For every policy, mode, and friction scenario:

- trades entered
- EXECUTION_UNAVAILABLE count
- TARGET / ADVERSE / EXPIRY counts
- average and median gross P&L
- average and median net P&L
- expectancy in R where 1R = 3 price units
- net-positive trade rate
- profit factor
- cumulative net P&L
- maximum sequential drawdown
- average trades per active day
- average trades per calendar day
- average entry spread
- median entry spread
- p95 entry spread

Report:
- all DEVELOPMENT_TEST
- 2023
- 2024

## Dependence-aware uncertainty

For each mode/policy/friction scenario:

- group completed trades by UTC entry date;
- bootstrap whole entry dates with replacement;
- 1,000 deterministic replicates;
- random seed 1;
- report 95% percentile interval for average net P&L/trade.

## V2 advancement evidence

A mode/policy combination may be nominated for a later FINAL_OOS freeze only if, under F10:

1. average net expectancy is positive in both 2023 and 2024;
2. overall profit factor > 1;
3. day-block bootstrap 95% expectancy interval lower bound > 0;
4. completed trade count is non-trivial;
5. execution-unavailable rate is acceptably low and reported;
6. no 2025 data has been accessed.

Passing this screen does not open 2025 automatically. A separate candidate-freeze document and hash are required first.

## Venue limitation

Dukascopy BID/ASK is not Exness BID/ASK.

Execution Economics V2 tests side-aware market mechanics and historical spread sensitivity using one high-quality historical venue. Exness 2026 MT5 BID/ASK samples are reserved for later broker-specific shadow/demo validation.

## Governance

- 2025 is not downloaded, scored, or inspected.
- No predictive tuning.
- No new score bands.
- No threshold changes after results.
- No direction is promoted post hoc outside the preregistered BUY_ONLY / SELL_ONLY / COMBINED modes.
- Negative results are admissible.
