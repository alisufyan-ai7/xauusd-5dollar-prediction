# Information Parity V1 — Stage 3B Source Event Construction Batch 08

Status: **SEP 14 + SEP 15 FROZEN — SOURCE CONSTRUCTION CONTINUES ABOVE ALL NUMERICAL FLOORS**

Parents:
- D-099 through D-106
- `research/INFORMATION_PARITY_V1_STAGE3B_DECISION_PROCESS_PREREGISTRATION.md`

Badar source pin:
- commit `cc94077c953efa0d048e61d6ba4fbcdd0e3ca79a`
- `dataset/live_trades.csv` blob `24939bf5ad141d38f2aad08c30ab6a077ab10086`

No `derived/` content was used.
No provider market data was queried.

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch08.csv`

## Scope

This batch reviews all eight pinned XAUUSD trade-table rows on:
- 2026-09-14
- 2026-09-15

and all distinct explicit Badar P3 decisions retained from the same reviewed source sequences.

## ACT disposition

Source trade rows reviewed:
**8**

Independent Badar ACT events:
**6**

Direction:
- LONG: **3**
- SHORT: **3**

Provenance:
- P1 LIVE_REAL_EXECUTION: **0**
- P2 LIVE_BADAR_COMMITMENT: **6**

Evidence:
- E1 DIRECT: **4**
- E2 CORROBORATED: **2**

Timing:
- EXACT_M1: **3**
- INTERVAL_2M: **2**
- INTERVAL_3_TO_5M: **1**

All primary intervals satisfy the frozen <=5-minute timing cap.

## Sep 14 same-plan collapse

`C18mm9p2oW4#1` and `C18mm9p2oW4#2` are one Stage 3B action event:

`S3B-ACT-0070`

The source explicitly describes:
- a small/normal immediate sell;
- plus the larger **main trade** limit at the exact order block.

This is exactly the split-plan case covered by D-099 Section 10.

Counting them as two independent expert decisions would inflate the teacher sample.

## Sep 14 other-person exclusion

`C18mm9p2oW4#4` is excluded from Badar ACT supervision.

At stream 49:32 Badar hands the screen to Zain and leaves for several minutes.

The later short is explicitly Zain's own analysis/trade on Zain's laptop/OANDA chart.

Even though the trade is well documented, it is not a Badar teacher event.

This preserves the frozen authorship boundary.

## Sep 15 low-confidence rows

The source table labels `_DK9mCSob5o#1/#3/#4` low confidence.

That does not exclude them automatically.

Stage 3B adjudicates the source event itself:

- #1: direct `Let's take a small trade` and later `I took an entry`;
- #3: direct `I'm going to take a small trade from here`, explicitly before the main planned sell;
- #4: current short box plus later direct half-risk/current-position discussion after the audio gap.

Therefore:
- #1 and #3 are E1;
- #4 is E2;
- all three are valid P2 action commitments.

No trade outcome is used in this decision.

## P3 result

New explicit Badar P3 events:
**16**

Sep 14:
**5**

Sep 15:
**11**

### Sep 14 sequence

Distinct decisions include:
1. no trade at the initial location;
2. current sell area requires a 1m/3m close — no action without it;
3. later re-entry requires another M3 sell-close/trap confirmation;
4. after the counter-trend long, do not sell because there is no valid sell location yet;
5. later proper sell structure is still deferred for one more close/retrace.

Badar leaves after this point, so Zain's subsequent decisions are not added as P3 Badar events.

### Sep 15 sequence

Distinct decisions include:
1. reject the early sell because rejection makes the market unclear;
2. after the London-high sweep, wait for another sweep/close because the current point is not a valid place;
3. wait while price is in the middle of the range;
4. later M30/M15 sell state remains indecisive;
5. a new M3 signal appears but still lacks a clear sell;
6. at the 4300/FVG area, wait for the required candle close;
7. later wait specifically for a fake breakout/direct sell confirmation;
8. after the small test short, do not add/sell again yet because a higher manipulation/FVG location is preferred;
9. later sell bias remains, but he explicitly refuses the current location;
10. another sell requires the two-step M5 close condition;
11. late session: no good trade exists, so wait for retrace instead of taking the current bullish area.

These are materially distinct market/decision states, not duplicate labels from one continuous wait.

## Cumulative Stage 3B source state

ACT:
- total: **75**
- LONG: **36**
- SHORT: **39**
- distinct ACT dates: **25**

P3 REJECT/WAIT:
- total: **69**
- distinct reject dates: **25**

Paired ACT + REJECT dates:
- **25**

All frozen D-099 numerical adequacy floors remain exceeded.

## Non-table ACT backfill requirement strengthened

Sep 14 independently confirms the Batch 07 QA issue.

At stream 5:19 Badar explicitly places a sell limit near 4302 at a hidden order block.

Price never reaches it, so it does not appear as a filled trade-table row.

Under D-099, a genuinely committed resting order may be an ACT event even without a fill.

Therefore the final Stage 3B V1 corpus cannot be defined as merely:
`all adjudicated rows from dataset/live_trades.csv`.

A complete source-only backfill of valid non-table commitments remains mandatory before final certification.

This is enforcement of the preregistered unit, not a protocol change.

## Overall status

`NUMERICALLY ADEQUATE — FINAL SOURCE CONSTRUCTION/QA STILL IN PROGRESS`

No market join is authorized.

## Immediate next safe work

Continue chronologically with the next pinned September source dates:
- 2026-09-16
- 2026-09-17

under the unchanged Stage 3B rules.

After all pinned September/October trade-table dates are complete:
1. run the non-table ACT backfill;
2. merge every batch;
3. audit source-row coverage and other-person exclusions;
4. audit same-plan collapses;
5. audit ACT/P3 temporal conflicts;
6. audit timing classes/timezones;
7. freeze the final Stage 3B CSV and SHA-256;
8. issue the final source-adequacy certification.

No provider market data, model fitting or CI is authorized.
