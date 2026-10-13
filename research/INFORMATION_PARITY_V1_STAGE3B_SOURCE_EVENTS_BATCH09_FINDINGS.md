# Information Parity V1 — Stage 3B Source Event Construction Batch 09

Status: **SEP 16 + SEP 17 FROZEN — SOURCE CONSTRUCTION CONTINUES ABOVE ALL NUMERICAL FLOORS**

Parents:
- D-099 through D-107
- `research/INFORMATION_PARITY_V1_STAGE3B_DECISION_PROCESS_PREREGISTRATION.md`

Badar source pin:
- commit `cc94077c953efa0d048e61d6ba4fbcdd0e3ca79a`
- `dataset/live_trades.csv` blob `24939bf5ad141d38f2aad08c30ab6a077ab10086`

No `derived/` content was used.
No provider market data was queried.

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch09.csv`

## Scope

This batch reviews all six pinned XAUUSD trade-table rows on:
- 2026-09-16
- 2026-09-17

and all distinct explicit Badar P3 decisions retained from the same reviewed source sequences.

## ACT disposition

Source trade rows reviewed:
**6**

Independent primary-eligible Badar ACT events:
**4**

Direction:
- LONG: **3**
- SHORT: **1**

Provenance:
- P1 LIVE_REAL_EXECUTION: **1**
- P2 LIVE_BADAR_COMMITMENT: **3**

Evidence:
- E1 DIRECT: **4**

Timing:
- EXACT_M1: **2**
- INTERVAL_2M: **1**
- INTERVAL_3_TO_5M: **1**

All primary timing intervals satisfy the frozen <=5-minute cap.

## Sep 16 ambiguous trade #2 excluded

`y2Oun9g9abk#2` is excluded from primary Badar ACT supervision.

The source is internally contradictory:
- Badar describes a possible M1 sell and says `I will sell it here`;
- one minute later he explicitly says `Don't take it now... I'm not taking it`;
- he then says `someone has sold it`;
- later language about profit/two trades does not uniquely resolve whether this was Badar's own executed decision or viewers/another position.

That is an E3-like ownership/action ambiguity.

Stage 3B therefore does not force the row into P2 merely because the trade table contains it.

Outcome claims are not used to resolve the ambiguity.

## Sep 17 same-plan collapse

`6trb-6A2t6Q#1` and `6trb-6A2t6Q#2` collapse into one Stage 3B ACT event:

`S3B-ACT-0078`

The source explicitly shows:
- an initial 0.22-lot Exness long from the M1 demand zone;
- a second 0.22-lot add-on after a new M1 confirmation;
- Badar saying: `If you combine the two, then the average rate will be the same`;
- coordinated TP/BE management across the pair.

This is one scaled long plan rather than two independent decision opportunities.

Because both positions are visible in the Exness real terminal, the collapsed event is P1.

## Sep 17 later long remains separate

`6trb-6A2t6Q#3` occurs roughly half an hour later after a materially new M15 sell-trap/rejection state.

It is therefore a new decision event, not an add-on to the earlier demand-zone plan.

Its OANDA chart does not establish a real account, so it remains P2.

## P3 result

New explicit P3 events:
**12**

Sep 16:
**6**

Sep 17:
**6**

### Sep 16 sequence

Distinct decisions include:
1. no plan before FOMC data;
2. reject buying the first post-news dump because the required stop is too large;
3. later do not take the potential sell until the M5/M10 close;
4. reject a normal buy from the second-leg demand state because the signal can be trapped;
5. require M1 confirmation before the later sell ACT;
6. end-of-stream sell idea remains conditional on a new M1 close.

### Sep 17 sequence

Distinct decisions include:
1. do not sell the upper supply immediately because the stop would be too large;
2. do not buy the top before the H4 close;
3. reject a weak M1 signal after the H4 decision phase;
4. later FVG/OB sell is deferred until another sweep clarifies the state;
5. later M5/M3 sell closes remain insufficient because the structure is still a single/unclear arrangement;
6. the H1 short plan is finally rejected when the required inverse/down close does not occur.

These are materially distinct market states rather than repeated labels from one continuous waiting period.

## Non-table ACT backfill remains mandatory

Sep 17 contains another explicit example:

Badar says:
- `I would like to put a limit on this point`;
- then `I'm putting a limit on this place`.

No fill is shown and the order is absent from the trade table.

This is exactly the source class that the already-required non-table ACT backfill must review after chronological trade-table construction is finished.

It is not inserted into Batch 09 because the current phase remains the frozen trade-table-row review plus P3 extraction.

## Cumulative Stage 3B source state

ACT:
- total: **79**
- LONG: **39**
- SHORT: **40**
- distinct ACT dates: **27**

P3 REJECT/WAIT:
- total: **81**
- distinct reject dates: **27**

Paired ACT + REJECT dates:
- **27**

All D-099 numerical source-adequacy floors remain exceeded.

## Overall status

`NUMERICALLY ADEQUATE — FINAL SOURCE CONSTRUCTION/QA STILL IN PROGRESS`

No provider market join is authorized.

## Immediate next safe work

Continue chronologically with the next pinned September source dates:
- 2026-09-18
- 2026-09-21

under the unchanged Stage 3B rules.

After all pinned September/October trade-table dates are complete:
1. run the non-table ACT backfill;
2. merge every batch;
3. audit source-row coverage and ambiguous/other-person exclusions;
4. audit same-plan collapses;
5. audit ACT/P3 temporal conflicts;
6. audit timing classes and timezone conversion;
7. freeze the final Stage 3B CSV and SHA-256;
8. issue final source-adequacy certification.

No provider market data, model fitting or CI is authorized.
