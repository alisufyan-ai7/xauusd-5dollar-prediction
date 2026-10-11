# Information Parity V1 — Stage 3B Source Event Construction Batch 02

Status: **ALL JULY LIVE TRADE ROWS REVIEWED; FIRST P3 HARD-NEGATIVE SET FROZEN**

Parent:
- D-099
- D-100
- `research/INFORMATION_PARITY_V1_STAGE3B_DECISION_PROCESS_PREREGISTRATION.md`

Badar source pin:
- commit `cc94077c953efa0d048e61d6ba4fbcdd0e3ca79a`
- `dataset/live_trades.csv` blob `24939bf5ad141d38f2aad08c30ab6a077ab10086`

No `derived/` material was used.
No provider market data was queried.

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch02.csv`

## Scope

Batch 02 does two things:

1. finishes Stage 3B ACT adjudication for every remaining July XAUUSD trade-table row at the frozen source pin;
2. freezes one explicit P3 REJECT/WAIT event on each July source date that already contains an eligible ACT event.

## July ACT completion

The pinned trade table contains **31 July XAUUSD rows**.

Disposition after Batches 01-02:
- 29 trade rows represented by Stage 3B ACT events;
- those 29 rows produce **28 independent ACT events** after the D-099 same-plan collapse;
- 2 rows (`E2Vu2bndWRc#1/#2`) remain excluded because they are pre-stream Exness-history fills without contemporaneous source decision evidence.

No July trade-table row remains unreviewed.

### Batch 02 ACT additions

New ACT events:
**17**

Direction:
- LONG: **8**
- SHORT: **9**

Evidence:
- E1 DIRECT: **13**
- E2 CORROBORATED: **4**

Timing:
- EXACT_M1: **10**
- INTERVAL_2M: **6**
- INTERVAL_3_TO_5M: **1**

All admitted intervals satisfy the frozen <=5-minute primary timing cap.

### Why low-confidence trade-table rows can still enter Stage 3B

Several low-confidence table rows become valid Stage 3B P2 events because the teacher target is **decision commitment**, not confirmed fill/outcome.

Examples:
- `suuicaoUvDQ#1`: direct `I am buying` plus later `I exited in profit`;
- `MbUagftbsIw#2`: direct `Let's buy a little less`;
- `9D7wgJCdP5c#3`: direct `Let's sell it from here`.

The repository's legacy `confidence` field therefore remains audit metadata, not an eligibility gate.

### Paper/simulation remains visible as provenance

The July 28 events are admitted as P2 decision commitments but carry:

`broker_execution_status = PAPER_OR_SIMULATION`

because the same stream explicitly says live-account trading will begin the next day.

Stage 3B therefore preserves the difference between:
- decision-process evidence;
- broker-execution evidence.

## First P3 hard-negative set

Batch 02 adds **12 P3 events**, exactly one on each July ACT date.

They are explicit current-opportunity rejections/waits, not arbitrary no-trade minutes.

Reject-reason counts:
- CONFIRMATION_WEAK_OR_ABSENT: 3
- SL_TOO_LARGE: 3
- MID_RANGE: 2
- LATE_DO_NOT_CHASE: 1
- NO_VALID_POI: 1
- WAIT_HTF_CLOSE: 1
- NO_LOGICAL_SL: 1

Examples:
- Jul 27: `This is the center... we will not trade from here`;
- Jul 30: buy rejected because there is no logical place for the stop;
- Jul 10: post-spike trade rejected because the required stop would be about 500 pips;
- Jul 31: a sell is deferred until proper confirmation.

These are precisely the hard negatives intended by D-099.

## Cumulative Stage 3B source corpus after Batch 02

ACT:
- total: **28**
- LONG: **16**
- SHORT: **12**
- distinct ACT dates: **12**

P3 REJECT/WAIT:
- total: **12**
- distinct reject dates: **12**

Paired ACT + REJECT dates:
- **12**
- 2026-07-06
- 2026-07-07
- 2026-07-09
- 2026-07-10
- 2026-07-21
- 2026-07-22
- 2026-07-23
- 2026-07-27
- 2026-07-28
- 2026-07-29
- 2026-07-30
- 2026-07-31

Provenance among ACT:
- P1 LIVE_REAL_EXECUTION: **1**
- P2 LIVE_BADAR_COMMITMENT: **27**

## Adequacy status

D-099 requires:

Task A:
- >=40 ACT;
- >=40 REJECT/WAIT;
- >=20 paired dates.

Current:
- ACT = **28 / 40**
- REJECT/WAIT = **12 / 40**
- paired dates = **12 / 20**

Task B:
- >=40 ACT;
- >=20 ACT dates;
- >=15 LONG;
- >=15 SHORT.

Current:
- ACT = **28 / 40**
- ACT dates = **12 / 20**
- LONG = **16 / 15**
- SHORT = **12 / 15**

Current overall status:

`UNRESOLVED — SOURCE EVENT CONSTRUCTION IN PROGRESS`

The direction floor is already met for LONG but not yet SHORT; all count/date gates still require later source dates.

## Immediate next safe work

Continue source-only ACT construction into August, while simultaneously extracting P3 hard negatives from the same new dates.

Priority:
1. build enough ACT events to learn whether the 40/20/15/15 Task B gate is reachable;
2. keep one or more explicit P3 events on each ACT date where source evidence permits;
3. use full-resolution frames when transcript/note timing needs tightening;
4. never manufacture arbitrary no-trade negatives.

No market join, fitting or CI is authorized.
