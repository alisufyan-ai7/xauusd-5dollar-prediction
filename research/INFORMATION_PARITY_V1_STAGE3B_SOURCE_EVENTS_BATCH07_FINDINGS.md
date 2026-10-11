# Information Parity V1 — Stage 3B Source Event Construction Batch 07

Status: **SEP 2 + SEP 4 FROZEN — NUMERICAL ADEQUACY REMAINS COMFORTABLY ABOVE FLOORS**

Parents:
- D-099 through D-105
- `research/INFORMATION_PARITY_V1_STAGE3B_DECISION_PROCESS_PREREGISTRATION.md`

Badar source pin:
- commit `cc94077c953efa0d048e61d6ba4fbcdd0e3ca79a`
- `dataset/live_trades.csv` blob `24939bf5ad141d38f2aad08c30ab6a077ab10086`

No `derived/` content was used.
No provider market data was queried.

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch07.csv`

## Scope

This batch reviews all eight pinned XAUUSD trade-table rows on:
- 2026-09-02
- 2026-09-04

and all distinct explicit P3 decisions retained from the same reviewed source sequences.

## ACT disposition

Source trade rows reviewed:
**8**

Independent ACT events:
**7**

Direction:
- LONG: **4**
- SHORT: **3**

Provenance:
- P1 LIVE_REAL_EXECUTION: **5**
- P2 LIVE_BADAR_COMMITMENT: **2**

Timing:
- EXACT_M1: **6**
- INTERVAL_2M: **1**

### Sep 2

All three XAUUSD trade-table rows become P1 events.

The stream source directly shows Badar's Exness real web terminal and the current dollar-valued positions/orders.

This includes:
- market buy at the M1/M5 close;
- resting buy limit at the 4378 OB/gap;
- later small re-entry at the same lower structure.

The resting-limit event uses the **commitment minute**, not its later fill minute, because Stage 3B predicts decision commitment.

### Sep 4 same-plan collapse

`B83jlxwuo10#2` and `B83jlxwuo10#3` become one source decision:

`S3B-ACT-0067`

Reason:
the transcript says the main/major portion was closed while a small trade from the **same place** continued.

This is position partition/retention inside one original sell decision, not an independent later opportunity.

The source row keys remain attached:
`B83jlxwuo10#2;B83jlxwuo10#3`.

### Sep 4 provenance

`B83jlxwuo10#1` remains P1:
the buy limit is visibly placed on Badar's Exness real account.

`B83jlxwuo10#5` remains P1:
it is the already source-confirmed live-real personal entry.

The #2/#3 collapsed decision and #4 remain P2 because the per-event source does not justify inheriting live-real status merely from other trades in the same stream.

## P3 additions

New explicit P3 events:
**12**

Sep 2:
**6**

Sep 4:
**6**

### Sep 2 examples

The distinct policy decisions include:
- wait for price to reach the intended lower area;
- reject an otherwise good sign because the SL is about 100 pips;
- reject a sell because the short-term structure is still buy / sweep is unconvincing;
- do not trade outside the selected area;
- require the M1 close before buying;
- later reject a weak sell sign until a stronger M5 close exists.

### Sep 4 examples

The distinct policy decisions include:
- cancel the direct pre-news market buy after the last-second rejection;
- do not trade immediately after NFP;
- explicitly do not buy the live trap state;
- do not chase a buy at the top despite a 3m buy sign;
- wait for the sell close before #5;
- stop for the Friday after the final trade.

These are current-opportunity decisions, not arbitrary non-entry minutes.

## Cumulative Stage 3B source state

ACT:
- total: **69**
- LONG: **33**
- SHORT: **36**
- distinct ACT dates: **23**

P3 REJECT/WAIT:
- total: **53**
- distinct reject dates: **23**

Paired ACT + REJECT dates:
- **23**

Both D-099 numerical adequacy gates remain met.

## Newly explicit final-QA requirement: non-table ACT backfill

D-099 allows a **committed resting order** to count as an ACT event even if it never fills.

The trade table naturally contains executed/observed trade rows and can therefore omit some unfilled but genuine Badar commitments.

Example on Sep 2:
the source note records a new sell limit typed on the live terminal above the market that never fills.

This Batch 07 keeps its ACT scope consistent with the ongoing chronological **trade-table row review**.

Before the final Stage 3B source table can be certified, a dedicated source-only backfill must therefore scan all pinned live streams for:
- explicitly placed but unfilled limit orders;
- explicit committed market actions that were omitted from the trade table;
- other D-099-valid ACT commitments not represented by a source row.

That backfill must apply the same:
- P1/P2 rules;
- E1/E2 evidence rule;
- <=5-minute timing cap;
- same-plan collapse rule.

It must occur **before** the final merge/hash and before any provider market join.

## Why this does not alter the preregistration

The backfill does not introduce a new label type.

It enforces the already frozen D-099 definition:
the Stage 3B unit is a source decision event, not merely a filled trade-table row.

## Overall status

`NUMERICALLY ADEQUATE — FINAL SOURCE CONSTRUCTION/QA STILL IN PROGRESS`

No market join is authorized.

## Immediate next safe work

Continue chronologically with:
- 2026-09-14
- 2026-09-15

under the unchanged source rules.

After all September/October trade-table dates are complete:
1. run the non-table ACT backfill;
2. merge all source batches;
3. audit duplicate/source-row coverage;
4. audit same-plan collapses;
5. audit ACT/P3 temporal conflicts;
6. audit timing/timezone fields;
7. freeze the final Stage 3B event-table hash;
8. issue final source-adequacy certification.

No provider market data, model fitting or CI is authorized.
