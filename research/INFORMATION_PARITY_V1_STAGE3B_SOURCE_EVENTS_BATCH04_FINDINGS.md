# Information Parity V1 — Stage 3B Source Event Construction Batch 04

Status: **AUGUST 6-7 SOURCE SUB-BATCH FROZEN — TASK B NOW NEEDS ONLY THREE MORE DISTINCT ACT DATES**

Parents:
- D-099 through D-102
- `research/INFORMATION_PARITY_V1_STAGE3B_DECISION_PROCESS_PREREGISTRATION.md`

Badar source pin:
- commit `cc94077c953efa0d048e61d6ba4fbcdd0e3ca79a`
- `dataset/live_trades.csv` blob `24939bf5ad141d38f2aad08c30ab6a077ab10086`

No `derived/` content was used.
No provider market data was queried.

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch04.csv`

## Scope

This batch covers every pinned XAUUSD trade-table row dated:
- 2026-08-06
- 2026-08-07

Rows reviewed:
**8**

Disposition:
- **8 / 8** become primary-eligible Stage 3B ACT events;
- no same-plan collapse was required;
- no row is excluded.

## Batch ACT result

ACT:
**8**

Direction:
- LONG: **4**
- SHORT: **4**

Timing:
- EXACT_M1: **5**
- INTERVAL_2M: **2**
- INTERVAL_3_TO_5M: **1**

Evidence:
- E1 DIRECT: **8**

Provenance:
- P1 LIVE_REAL_EXECUTION: **1**
- P2 LIVE_BADAR_COMMITMENT: **7**

All timing intervals satisfy the frozen <=5-minute cap.

## P1 event: NIDMLJuBPwk#1

`S3B-ACT-0051` is P1.

At the action moment Badar says:
`I have taken my trade`

The same source sequence then directly discusses:
- the Exness terminal;
- a second account;
- inconsistent position state across accounts;
- checking/closing on his mobile.

This is both:
- an observed Badar decision commitment;
- source-confirmed real/live execution.

The action time remains the source decision minute, not a later broker-close time.

## NIDMLJuBPwk#2 remains P2

Trade #2 has a directly observed limit commitment and subsequent:
`Entry is in`

However, this specific row is not automatically promoted to P1 solely because trade #1 in the same stream used a confirmed real terminal.

Stage 3B continues to apply execution provenance per event.

## Risk-tier observations

Explicit reduced-risk evidence is preserved for:
- `ldrw26fGZOE#2` — half risk;
- `ldrw26fGZOE#3` — keep risk less after several entries;
- `ldrw26fGZOE#4` — small / half-risk instruction;
- `NIDMLJuBPwk#1` — half risk around NFP;
- `NIDMLJuBPwk#2` — half-risk label / reduced stop-risk discussion.

Risk tier is diagnostic only and does not affect ACT eligibility.

## P3 hard negatives

Two new paired P3 events are frozen.

### 2026-08-06 — NO_VALID_POI

After the first move, Badar explicitly says not to buy yet:

`you don't have to buy now. At least let it come into this area. Before that, no buying.`

This is a source-defined WAIT at a current opportunity.

### 2026-08-07 — NEWS_OR_EVENT_RISK

Before NFP:

`before the news... this is a bit dangerous... you can't take the decision.`

This is a direct current-opportunity defer decision caused by scheduled-event risk.

Neither event is an arbitrary no-trade minute.

## Cumulative Stage 3B source state

ACT:
- total: **52**
- LONG: **25**
- SHORT: **27**
- distinct ACT dates: **17**

P3 REJECT/WAIT:
- total: **17**
- distinct reject dates: **17**

Paired ACT + REJECT dates:
- **17**

## Frozen adequacy progress

### Task A

Required:
- >=40 ACT
- >=40 REJECT/WAIT
- >=20 paired dates

Current:
- ACT = **52 / 40** — met
- REJECT/WAIT = **17 / 40** — not met
- paired dates = **17 / 20** — not met

### Task B

Required:
- >=40 ACT
- >=20 ACT dates
- >=15 LONG
- >=15 SHORT

Current:
- ACT = **52 / 40** — met
- ACT dates = **17 / 20** — not met
- LONG = **25 / 15** — met
- SHORT = **27 / 15** — met

Task B now needs only:
**3 additional distinct eligible ACT dates**

The remaining August source dates after this batch are:
- 2026-08-13
- 2026-08-17
- 2026-08-28
- 2026-08-31

Therefore the Task B 20-date floor is still plausibly reachable without changing any rule.

Task A remains the harder evidence gate because the corpus needs:
- 23 additional explicit REJECT/WAIT events;
- 3 additional paired dates.

Once the paired-date floor is reached, additional P3 events may come from already-paired dates; they do not need to create new dates.

## Overall status

`UNRESOLVED — SOURCE EVENT CONSTRUCTION IN PROGRESS`

Do not access provider market data yet.

## Immediate next safe work

Continue the remaining August source dates in bounded form.

Next sub-batch:
- 2026-08-13
- 2026-08-17

This contains 6 pinned XAUUSD trade-table rows across two dates.

For those dates:
1. adjudicate ACT events;
2. add at least one explicit P3 hard negative where supported;
3. begin retaining additional valid P3 events beyond one-per-date, because Task A now needs reject-event count as well as date coverage.

No CI or model fitting is needed.
