# EXP-001 Execution Economics V1

Status: FROZEN BEFORE EXECUTION

## Purpose

Translate the corrected predictive signal into a deterministic, non-sealed trade-level economic proxy before any FINAL_OOS opening.

This milestone answers:

> If the already-frozen GBT score policies had been acted on sequentially, what gross and cost-stressed expectancy would they have produced on 2023-2024?

This is not a broker-exact backtest because the admitted Dukascopy M1 history is BID-only and does not contain historical Exness ASK/spread/slippage.

FINAL_OOS 2025 remains strictly sealed.

## Frozen predictive model

Reproduce corrected GBT V1 exactly:

- TRAIN: 2016-2021
- every 5th eligible TRAIN row, chronological
- separate BUY and SELL HistGradientBoostingClassifier models
- loss: log_loss
- learning_rate: 0.05
- max_iter: 200
- max_leaf_nodes: 15
- min_samples_leaf: 200
- l2_regularization: 1.0
- max_bins: 255
- early_stopping: false
- random_state: 1
- same frozen V2 feature list

## Operational score cutoffs

Candidate policies remain:

- top 10%
- top 5%
- top 2.5%
- top 1%

For operational correctness, each raw-score cutoff is derived from ALL eligible, feature-complete VALIDATION decision rows for that direction, regardless of future label.

Reason:
A live system cannot know in advance whether a future path will become AMBIGUOUS. Earlier research evaluation excluded AMBIGUOUS rows for outcome metrics; execution selection must not condition on future outcome availability.

The resulting absolute raw-score cutoffs are then applied unchanged to DEVELOPMENT_TEST.

No new percentile bands are introduced.

## Signal and position semantics

Evaluation population:
- DEVELOPMENT_TEST 2023-2024 only.
- 2025 is never read.

At each decision time:
1. calculate BUY and SELL raw GBT scores;
2. compare each to its direction-specific frozen VALIDATION cutoff;
3. if neither qualifies: NO TRADE;
4. if both qualify at the same decision time: NO TRADE due directional conflict;
5. if exactly one qualifies and no position is open: enter that direction;
6. while a position is open, ignore every subsequent signal until the current position exits.

Only one global XAUUSD position may be open at a time.

No pyramiding.
No averaging.
No opposite-direction reversal while a position is open.

## Entry-price proxy

Entry reference is the corrected EXP-001 decision-bar BID close.

This is a signal-price economic proxy, not an assertion that a live BUY can fill at BID.

Historical spread/ASK is unavailable in the admitted dataset. Spread, commission, and slippage are therefore represented through frozen all-in round-trip cost stress scenarios below.

## Gross exit semantics

For a selected trade:

### SUCCESS
Gross price-unit P&L = +5.00.

Exit time is the terminal barrier bar end.

### FAILURE
Gross price-unit P&L = -3.00.

Exit time is the terminal barrier bar end.

### AMBIGUOUS
Gross price-unit P&L = -3.00 conservatively.

Reason:
M1 OHLC cannot establish whether target or adverse barrier touched first. Treating the ambiguous trade as the adverse outcome avoids optimistic ordering.

Exit time is the ambiguous terminal bar end.

### UNRESOLVED
Close at the end of the exact 60-minute horizon.

BUY gross P&L:
expiry BID close - reference price.

SELL gross P&L:
reference price - expiry BID close.

The unresolved trade is therefore not automatically treated as a -3 loss.

## Cost stress scenarios

Apply an all-in round-trip price-unit deduction per completed trade:

- C0: $0.00
- C10: $0.10
- C20: $0.20
- C30: $0.30
- C50: $0.50

Net price-unit P&L = gross P&L - cost.

These scenarios intentionally stress the predictive edge without claiming to reproduce one exact Exness account type.

They proxy the combined effect of bid/ask spread, commission, and slippage.

No swap is modeled because the maximum holding period is 60 minutes.

## Cost-model limitation

The all-in cost overlay changes realized P&L but does not move the historical barrier-touch path.

Therefore Execution Economics V1 is a screening test.

Before live deployment, Exness demo/shadow validation must use contemporaneous bid/ask quotes and actual account-specific commission rules.

## Required outputs

For each candidate policy:

### Direction-specific
- BUY-only
- SELL-only

### Combined sequential engine
- BUY and SELL signals together
- conflict => NO TRADE
- one global position at a time

For each mode and cost scenario report:

- number of trades
- SUCCESS / FAILURE / UNRESOLVED / AMBIGUOUS counts
- average gross P&L
- median gross P&L
- average net P&L
- median net P&L
- expectancy in R, where 1R = $3 price units
- win rate where net P&L > 0
- profit factor
- cumulative net P&L in price units
- maximum sequential drawdown
- active trading days
- average trades per active day
- average trades per calendar day

Report separately for:
- all DEVELOPMENT_TEST
- 2023
- 2024

## Dependence-aware uncertainty

For combined sequential trades under each candidate policy and cost scenario:

- group completed trades by UTC entry date;
- bootstrap whole entry dates with replacement;
- 1,000 deterministic replicates;
- random seed 1;
- report 95% percentile interval for mean net P&L per trade.

## Advancement rule

This milestone does not automatically choose the policy with the highest historical expectancy.

A candidate may advance to final pre-OOS freeze only if:

1. corrected predictive evidence remains intact;
2. net mean expectancy is positive in BOTH 2023 and 2024 under at least C20;
3. combined DEVELOPMENT_TEST bootstrap 95% expectancy interval lower bound is above 0 under at least C20;
4. profit factor is above 1 under at least C20;
5. trade count is non-trivial;
6. no 2025 information has been used.

C30 and C50 are stress evidence, not mandatory pass conditions.

## Governance

- No 2025 access.
- No model changes.
- No new score percentile bands.
- No cost-scenario changes after results.
- No account-specific Exness claim is made from BID-only history.
- Negative economic results are admissible.
