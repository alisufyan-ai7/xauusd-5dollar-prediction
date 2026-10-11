# Information Parity V1 — Stage 3B Source Event Construction Batch 05

Status: **AUGUST 13 + 17 FROZEN — MULTIPLE HARD NEGATIVES NOW RETAINED PER DATE**

Parents:
- D-099 through D-103
- `research/INFORMATION_PARITY_V1_STAGE3B_DECISION_PROCESS_PREREGISTRATION.md`

Badar source pin:
- commit `cc94077c953efa0d048e61d6ba4fbcdd0e3ca79a`
- `dataset/live_trades.csv` blob `24939bf5ad141d38f2aad08c30ab6a077ab10086`

No `derived/` material was used.
No provider market data was queried.

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch05.csv`

## Scope

This batch covers all six pinned XAUUSD trade-table rows on:
- 2026-08-13
- 2026-08-17

and begins the D-103-required expansion from one hard negative per date to **multiple distinct P3 decisions per date**.

## ACT disposition

Six source rows reviewed.

Primary-eligible ACT events:
**4**

Excluded from primary ACT:
**2**

### Included

2026-08-13:
- `W2oZdVu2rxE#1` — COMMIT_LONG
- `W2oZdVu2rxE#2` — COMMIT_LONG

Both are E2 because the current position boxes and subsequent direct trade-management statements corroborate Badar ownership/commitment, while the exact verbal commitment second is not clean enough for E1.

2026-08-17 NY:
- `IQ4J5GJJK5Q#1` — COMMIT_SHORT
- `IQ4J5GJJK5Q#2` — COMMIT_SHORT

Both are E1 direct:
- #1: `I will take the market from here... I will take it for 1 minute`;
- #2: explicit placement of the sell limit at the swept high.

### Excluded London chart-box rows

`JJOGnPBF67I#1` and `JJOGnPBF67I#2` are not primary ACT events.

Reason:
- the stream transcript is nearly empty;
- the source shows position-tool boxes and plausible trade management;
- but the source does not establish Badar's personal current commitment strongly enough to distinguish an executed/current teacher decision from a chart/planning box at E1/E2 confidence.

They therefore remain E3-like ambiguous candidate rows and are excluded under D-099.

The later NY comment about an early buy is consistent with the London long but does not uniquely establish Badar's contemporaneous London commitment.

## Timing

Included ACT timing:
- EXACT_M1: **2**
- INTERVAL_2M: **2**

All are within the frozen primary cap.

The two Aug 13 intervals preserve the genuine source uncertainty around the first visible active box and surrounding commitment language; no midpoint is invented.

## Multiple P3 events per date

Batch 05 adds **11 explicit P3 events**:
- Aug 13: **6**
- Aug 17: **5**

These are not repeated copies of one continuous no-trade state.

Each occurs after a materially new market/decision transition.

### Aug 13 sequence

Distinct decisions include:
1. wait for another close before the first buy;
2. after the first trade exits, do not re-buy without a new sign;
3. later uncertainty -> wait ten minutes;
4. later demand evaluation -> wait for M5 close;
5. later HTF decision -> wait for H1 close;
6. after two losses -> stop trading for the day.

The last event is:
`SESSION_OR_DAY_STOP`

which is explicitly allowed by D-099's hard-negative ontology.

### Aug 17 sequence

Distinct decisions include:
1. after the first TP, defer a direct re-sell until the 2m close;
2. reject selling directly into a fast bullish impulse;
3. after the news-driven reversal, wait for another close before considering a buy;
4. later no-confirmation state -> do not buy without the required M1 close;
5. London-session fragment -> wait for the low/structure break before opening on M1.

All are current-opportunity decisions, not arbitrary no-entry minutes.

## Cumulative Stage 3B source state

ACT:
- total: **56**
- LONG: **27**
- SHORT: **29**
- distinct ACT dates: **19**

P3 REJECT/WAIT:
- total: **28**
- distinct reject dates: **19**

Paired ACT + REJECT dates:
- **19**

## Frozen adequacy progress

### Task A

Required:
- >=40 ACT
- >=40 REJECT/WAIT
- >=20 paired dates

Current:
- ACT = **56 / 40** — met
- REJECT/WAIT = **28 / 40** — not met
- paired dates = **19 / 20** — not met

Remaining Task A shortfall:
- **12** additional explicit P3 events;
- **1** additional paired date.

### Task B

Required:
- >=40 ACT
- >=20 ACT dates
- >=15 LONG
- >=15 SHORT

Current:
- ACT = **56 / 40** — met
- ACT dates = **19 / 20** — not met
- LONG = **27 / 15** — met
- SHORT = **29 / 15** — met

Remaining Task B shortfall:
- **1** additional distinct ACT date.

## Immediate implication

The next new eligible ACT date can simultaneously:
- complete the Task B 20-date gate;
- complete the Task A 20 paired-date gate if at least one valid P3 exists on that date.

After that, Stage 3B source adequacy will depend only on accumulating the remaining explicit P3 event count.

## Immediate next safe work

Continue with:
- 2026-08-28
- 2026-08-31

These are the final two August source dates.

For the next date reached:
1. adjudicate ACT events;
2. secure at least one valid P3 to test whether both 20-date gates close;
3. continue collecting every distinct valid P3 decision, not merely one per date.

No provider market join, CI or fitting is authorized.
