# Information Parity V1 — Stage 3B Source Event Construction Batch 01

Status: **PARTIAL SOURCE-ONLY TEACHER CONSTRUCTION — ACTION EVENTS ONLY**

Parent:
- D-099
- `research/INFORMATION_PARITY_V1_STAGE3B_DECISION_PROCESS_PREREGISTRATION.md`

Badar source pin:
- commit `cc94077c953efa0d048e61d6ba4fbcdd0e3ca79a`
- `dataset/live_trades.csv` blob `24939bf5ad141d38f2aad08c30ab6a077ab10086`

No `derived/` material was used.
No market/provider data was queried.

## Scope

Batch 01 reviews the earliest clear live XAUUSD action commitments in the pinned corpus.

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch01.csv`

This is an intermediate construction artifact. It is not yet the final:
`stage3b-source-events-v1.csv`.

## Result

Source trade rows represented:
**12**

Stage 3B source events after same-plan collapse:
**11**

Primary Task A eligible ACT events:
**11**

Primary Task B eligible direction events:
**11**

Direction:
- LONG: **8**
- SHORT: **3**

Distinct source dates:
**8**

Provenance:
- P1 LIVE_REAL_EXECUTION: **1**
- P2 LIVE_BADAR_COMMITMENT: **10**

Evidence:
- E1 DIRECT: **9**
- E2 CORROBORATED: **2**

Timing:
- EXACT_M1: **5**
- INTERVAL_2M: **4**
- INTERVAL_3_TO_5M: **2**

All intervals satisfy the frozen <=5-minute primary timing cap.

## Interval endpoint convention

For Stage 3B construction artifacts:

- `interval_start_utc` = start of the first candidate M1 minute;
- `interval_end_utc` = start of the last candidate M1 minute;
- both endpoints are inclusive;
- `interval_width_minutes` is the count of candidate M1 minutes.

Example:
14:54 through 14:55 has width 2.

No midpoint timestamp is created.

## Same-plan collapse

`m0l1wj9IZ2o#1` and `m0l1wj9IZ2o#2` are represented as one event:

`S3B-ACT-0009`

Reason:
Badar first commits a reduced-risk sell and, about two minutes later in the same immediate zone/idea, explicitly calls the second position `another trade with a small risk`.

Under D-099 Section 10, this is a split/add-on decision plan rather than two independent teacher opportunities.

The two source-row keys remain attached for audit.

## Important exclusion from this batch: pre-stream broker history is not a live decision event

`E2Vu2bndWRc#1` and `E2Vu2bndWRc#2` are visible in Exness closed-order history and are strong execution evidence.

They are **not** admitted as Stage 3B action events because:
- both decisions occurred before the stream;
- the source shows the completed executions but not Badar's contemporaneous decision commitment/context.

This illustrates the Stage 3B distinction:
confirmed broker execution alone does not automatically make a useful decision-process teacher event.

## P1 finding

`CqEhHmcjeyQ#2` is classified P1 because the same current live decision is tied by source evidence to Badar's live account:
the transcript states that his live account is on the trade while he manages it.

Other events are not upgraded merely because a real account is shown elsewhere in the stream.

P1/P2 is evaluated per event.

## Ordering note

This batch began with early high/medium-confidence source-table rows only as a review-order convenience.

The repository's `confidence` field is not a Stage 3B eligibility rule.

Later batches must review low-confidence trade-table rows where direct source notes/transcripts/full-resolution frames may still support E1/E2 labels.

## No adequacy conclusion yet

D-099 source adequacy requires:
- >=40 ACT;
- >=40 explicit REJECT/WAIT;
- >=20 paired ACT+REJECT dates;
- Task B >=40 ACT / >=20 dates / >=15 LONG / >=15 SHORT.

This batch contains only ACT construction.

Therefore current Stage 3B adequacy remains:

`UNRESOLVED — SOURCE EVENT CONSTRUCTION IN PROGRESS`

## Immediate next safe work

Continue action-event construction chronologically from the remaining July live-trade rows, preserving:
- per-event provenance;
- <=5-minute source timing;
- same-plan collapse;
- no outcome-based eligibility.

After a meaningful ACT corpus is built, begin P3 explicit hard-negative extraction from the same live source dates.

No market join or CI is needed for this work.
