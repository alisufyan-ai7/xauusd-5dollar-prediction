# Root-Reset V3 — TRAIN-Only Structural Setup Family Screening

Status: FROZEN BEFORE SCREENING RESULTS

## Purpose

The V2 calibration diagnosis showed that continuation-event entries have typical calibrated reward/risk below 1.
The next step therefore changes the setup family before changing the model again.

This milestone screens three mechanically defined price-action setup families on TRAIN 2016-2021 only.

No model is trained.
No validation threshold is selected.
No 2022-2025 data is accessed.

## Public-research motivation

Public literature supports treating support/resistance and breakout behavior as testable hypotheses,
not as guaranteed profitable rules. Intraday support/resistance can have predictive content, but empirical
studies do not establish universal excess returns, and breakout/retest filters can fail in some datasets.

Therefore all three families below are screened prospectively and symmetrically.

## Data

Source:
- synchronized Dukascopy XAUUSD M1 BID+ASK

Years:
- 2016-2021 only

Do NOT download or access 2022, 2023, 2024, or 2025 for this screening.

For events near the end of each calendar year:
- require the full 60-minute post-entry path to exist inside the same year;
- otherwise discard the candidate.

## Shared causal volatility scale

Reuse V1 ATR15_PROXY exactly:
- mean true range of the four most recent completed synthetic 15-minute BID bars;
- all components available at decision time.

## Shared executable path measurement

Candidate decision occurs after the setup-confirmation M1 bar closes.
Entry is next M1 open.

BUY:
- entry = ASK next-bar open
- MFE = max future BID high - entry
- MAE = entry - min future BID low

SELL:
- entry = BID next-bar open
- MFE = entry - min future ASK low
- MAE = max future ASK high - entry

Horizon:
- 60 minutes
- exact contiguous synchronized M1 coverage required

For each candidate also record:
- MFE30 / MAE30
- MFE60 / MAE60
- whether +$3 is reached
- whether +$5 is reached
- whether +$7 is reached
- whether +$3 occurs before -$3
- whether +$5 occurs before -$3
- time to first +$3 / +$5 / -$3

These are descriptive path metrics, not trade rules.

## Shared de-clustering

After any accepted candidate in a setup family:
- suppress new candidates from that same family for 15 minutes.

BUY and SELL share the same family cooldown.

This prevents one market episode from producing many adjacent pseudo-opportunities.

## Stateful setup semantics

For Family A and Family C:
- maintain at most one pending BUY setup and one pending SELL setup at a time;
- while a direction has a pending setup, ignore new triggers of that same direction;
- the pending setup ends only by confirmation, explicit invalidation, or window expiry;
- an accepted candidate activates the family-level 15-minute cooldown for both directions.

# Family A — Breakout-Retest Continuation

## Breakout level

At breakout bar i:
- trailing resistance = maximum BID high over the preceding 60 completed M1 bars, excluding i
- trailing support = minimum BID low over the preceding 60 completed M1 bars, excluding i

Require ATR15_PROXY available.

## BUY breakout

Breakout bar:
- BID close > resistance + 0.10 * ATR15_PROXY
- BID open <= resistance

After breakout, freeze that resistance level and ATR value.

Retest window:
- next 10 completed M1 bars.

A BUY retest-confirmation occurs at the first bar j in the window satisfying:
- BID low <= frozen resistance + 0.15 * frozen ATR
- BID close >= frozen resistance + 0.10 * frozen ATR

Decision:
- close of bar j
- BUY entry next M1 ASK open

If BID close < frozen resistance - 0.25 * frozen ATR before confirmation:
- invalidate the setup.

## SELL breakout

Symmetric:
- close < support - 0.10 ATR
- open >= support
- retest high >= support - 0.15 ATR
- confirmation close <= support - 0.10 ATR
- invalidate if close > support + 0.25 ATR.

# Family B — Sweep-Reclaim Reversal

At candidate bar i:

Reference:
- trailing 60-minute BID high/low excluding current bar.

## BUY sweep-reclaim

Require:
- BID low < trailing support - 0.10 * ATR15_PROXY
- BID close > trailing support + 0.05 * ATR15_PROXY
- BID close > BID open

Decision:
- close of current bar
- BUY entry next M1 ASK open

## SELL sweep-reclaim

Require:
- BID high > trailing resistance + 0.10 * ATR15_PROXY
- BID close < trailing resistance - 0.05 * ATR15_PROXY
- BID close < BID open

Decision:
- close of current bar
- SELL entry next M1 BID open

No extra wick-ratio condition is allowed in V3.

# Family C — Impulse-Pullback Continuation

## Impulse detection

At bar i, evaluate the preceding 15-minute path ending at i.

Net move:
- BID close[i] - BID close[i-15]

Path length:
- sum(abs(BID close[k] - BID close[k-1])) for k=i-14..i

Efficiency:
- abs(net move) / max(path length, 1e-6)

Impulse requires:
- abs(net move) >= 1.50 * ATR15_PROXY
- efficiency >= 0.65

Direction:
- positive net => BUY impulse
- negative net => SELL impulse

Freeze:
- impulse start close
- impulse end close
- impulse amplitude = abs(net move)
- ATR15_PROXY at impulse completion.

## Pullback window

Observe the next 10 completed M1 bars.

BUY:
- retracement fraction = (impulse end close - current BID close) / amplitude

SELL:
- retracement fraction = (current BID close - impulse end close) / amplitude

A valid pullback must enter:
- 0.25 <= retracement fraction <= 0.50

Invalidate if:
- retracement fraction > 0.60

## Confirmation

After a valid pullback has occurred, candidate fires on the first subsequent bar within the original
10-bar window satisfying:

BUY:
- BID close > previous-bar BID high

SELL:
- BID close < previous-bar BID low

Decision:
- confirmation-bar close
- entry next M1 executable open.

# Screening metrics

For each family overall and separately by year 2016-2021 report:

- candidates
- BUY count
- SELL count
- median MFE30 / MAE30
- median MFE60 / MAE60
- mean MFE60 / MAE60
- median event-level MFE60 / max(MAE60, 0.10)
- +$3 rate
- +$5 rate
- +$7 rate
- +$3-before-$3 rate
- +$5-before-$3 rate
- median time to +$3 among hits
- median time to +$5 among hits
- median time to -$3 among hits

## Stability score

For each year compute:

YEAR_PATH_EDGE =
median(MFE60 - MAE60)

Family eligibility requires ALL:

1. >=600 total candidates;
2. >=60 candidates in every year 2016-2021;
3. YEAR_PATH_EDGE >0 in at least 4 of 6 years;
4. median of the six YEAR_PATH_EDGE values >0;
5. overall median MFE60 / median MAE60 >=1.10.

## Family selection

If zero families are eligible:
- select none;
- stop before 2022.

If one family is eligible:
- select it.

If multiple families are eligible:
rank by:
1. highest minimum yearly YEAR_PATH_EDGE;
2. then highest median yearly YEAR_PATH_EDGE;
3. then highest +$5-before-$3 rate;
4. then largest total candidate count.

The selected family is only a candidate for a later 2022 validation experiment.

This TRAIN-only screening does NOT authorize:
- model fitting;
- stop/target selection;
- validation access;
- demo/live trading.

## Governance

Do not:
- alter family definitions after results;
- add more setup families;
- tune thresholds;
- merge BUY/SELL asymmetrically;
- inspect 2022-2025;
- promote a family that fails eligibility.

Negative results are admissible.

If all three families fail:
- the next step must add genuinely new timestamp-safe exogenous information before generating candidates,
  not keep inventing additional price-only patterns.
