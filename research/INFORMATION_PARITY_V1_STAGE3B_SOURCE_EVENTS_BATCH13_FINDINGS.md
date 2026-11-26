# Information Parity V1 — Stage 3B Source Event Construction Batch 13

Status: **SEP 28 + SEP 29 FROZEN — ALL EIGHT TRADE-TABLE ROWS RESOLVE TO BADAR ACT EVENTS**

Parents:
- D-099 through D-111
- `research/INFORMATION_PARITY_V1_STAGE3B_DECISION_PROCESS_PREREGISTRATION.md`

Badar source pin:
- commit `cc94077c953efa0d048e61d6ba4fbcdd0e3ca79a`
- `dataset/live_trades.csv` blob `24939bf5ad141d38f2aad08c30ab6a077ab10086`

No `derived/` content was used.
No provider market data was queried.

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch13.csv`

## Scope

This batch reviews all eight pinned XAUUSD trade-table rows on:
- 2026-09-28
- 2026-09-29

and all distinct explicit Badar P3 decisions retained from the same reviewed source sequences.

## ACT disposition

Source trade rows reviewed:
**8**

Primary Badar ACT events:
**8**

Direction:
- LONG: **2**
- SHORT: **6**

Provenance:
- P1 LIVE_REAL_EXECUTION: **0**
- P2 LIVE_BADAR_COMMITMENT: **8**

Evidence:
- E1 DIRECT: **7**
- E2 CORROBORATED: **1**

No same-plan collapse is applied in this batch.

### Sep 28

All three rows are Badar-owned current commitments:
- #1 counter-trend long: direct `Let's buy from here`;
- #2 M1 sweep/close-back re-entry long: Badar states he put it at the candle base and manages the current trade;
- #3 with-trend short: direct `I'm doing a sell here`, with split-entry risk planning.

The fact that #1/#2 are counter-trend does not affect eligibility. Direction/trend quality and later outcome are not teacher-inclusion criteria.

### Sep 29 repeated shorts are distinct decisions

All five rows are retained as independent Badar ACT events.

They are not one split plan:
- #1 is the first M5/M1-confirmed short;
- #2 is a re-entry after the first decision reaches the BE/manipulation state;
- #3 follows a new higher sweep and a wider-risk decision;
- #4 occurs after another distinct higher-range sweep while the stream is on Zain's chart;
- #5 follows the 10:00 NY data/H1-high sweep and is explicitly a new short.

These are separate sequential opportunities, not simultaneous pieces of one entry.

### Sep 29 trade #4: Zain laptop does not make it Zain-owned

The displayed chart for #4 is Zain's laptop/TVC feed.

However, Badar:
- plans and manages the current short;
- discusses its partial/TP path;
- explicitly says `my SL was on 64.74, this is on 63.75`.

That directly links the displayed/copy trade to Badar's own corresponding decision.

Therefore #4 is:
- Badar P2;
- E2 corroborated;
- not OTHER_PERSON.

No live-real broker account is shown for Badar, so it is not P1.

## P3 result

New explicit P3 events:
**16**

Sep 28:
**9**

Sep 29:
**7**

### Sep 28 sequence

The retained decisions include:
1. do not sell after the extended drop; wait for a retrace/higher location;
2. current low location cannot be sold;
3. explicitly reject a blind/current-location buy;
4. wait for a high sweep before considering the next sell;
5. middle-of-range state has neither a sell nor buy area;
6. before the first long, wait for the confirming close rather than blindly taking the trap-prone state;
7. later buy-trap/supply state still requires a good sell close;
8. immediately before trade #3, refuse the direct sell and wait for another higher sweep;
9. after the final short is running, refuse Zain's request for another trade and stop adding decisions for the day.

### Sep 29 sequence

The retained decisions include:
1. after the first M5 condition, defer because the M1 candle is too large; wait for the next close-back;
2. after trade #1, stop trading the manipulated state until a new 1m sell close appears;
3. after trade #3, wait for another higher sweep before the next sell;
4. explicitly reject buying at the top and require a sell location/confirmation instead;
5. immediately before trade #5, do not take direct risk until the H1 high sweep is checked;
6. late high-volume/wickless push: explicitly do not sell without better confirmation;
7. end the session rather than overtrade the breakout state.

These are materially distinct sequential decisions rather than arbitrary non-entry minutes.

## Cumulative Stage 3B source state

ACT:
- total: **93**
- LONG: **43**
- SHORT: **50**
- distinct ACT dates: **34**

P3 REJECT/WAIT:
- total: **130**

Paired ACT + REJECT dates:
- **34**

All D-099 numerical source-adequacy floors remain exceeded.

## Timing note for Sep 29

The source note/table gives minute-level chart times for every trade row but not a single exact stream-zero second.

Therefore:
- direct ACT rows with source-table minute anchors use exact or bounded <=3-minute decision windows;
- P3 decisions derived from transcript offsets use conservative <=2-minute intervals anchored to nearby source-table chart times.

No midpoint timestamp is invented.

## Overall status

`NUMERICALLY ADEQUATE — FINAL SOURCE CONSTRUCTION/QA STILL IN PROGRESS`

No provider market join is authorized.

## Immediate next safe work

Continue chronologically with:
- 2026-09-30
- 2026-10-01

under the unchanged Stage 3B rules.

After all remaining trade-table dates are complete:
1. run the mandatory non-table ACT backfill;
2. merge all batches;
3. build the explicit source-row disposition/coverage audit;
4. audit same-plan collapses;
5. audit ACT/P3 temporal conflicts;
6. audit timing/timezones;
7. freeze the final Stage 3B CSV and SHA-256;
8. issue final source-adequacy certification.

No provider market data, model fitting or CI is authorized.
