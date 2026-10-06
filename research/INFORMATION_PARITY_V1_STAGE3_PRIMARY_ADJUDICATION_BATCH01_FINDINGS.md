# Information Parity V1 — Stage 3 Primary Teacher Adjudication Batch 01 Findings

Status: **PARTIAL SOURCE-ONLY ADJUDICATION — OVERALL D-091 ADEQUACY UNRESOLVED**

Parents:
- `research/INFORMATION_PARITY_V1_STAGE3_PROTOCOL_PREREGISTRATION.md`
- `research/INFORMATION_PARITY_V1_STAGE3_EVIDENCE_ADEQUACY_CLARIFICATION.md`
- `research/INFORMATION_PARITY_V1_STAGE3_SOURCE_TIMESTAMP_AUDIT_V2_FINDINGS.md`
- D-089 through D-092

Badar source pinned at:
`2df3d588c4b6d82761df2ee0c6f6639e82ce3414`

Teacher table blob:
`ea620cb44937f276be2e65ae7da25ae9503be655`

No `derived/` material was used.

## Scope

This batch adjudicates the first 10 chronological `EXACT_M1` V2 candidates only:

- NPUPkMWzKTE#1
- M078bAYBc-E#2
- m0l1wj9IZ2o#3
- suuicaoUvDQ#1
- suuicaoUvDQ#3
- 2c249LLRY_Q#1
- MbUagftbsIw#2
- 9D7wgJCdP5c#1
- 9D7wgJCdP5c#2
- 9D7wgJCdP5c#3

Artifact:
`research/reference/information-parity-v1/stage3-teacher-primary-adjudication-batch01.csv`

## Execution-evidence interpretation

This batch applies the frozen protocol conservatively:

- explicit first-person trade language can establish `BADAR_CONFIRMED` authorship;
- a TradingView position/long-short tool by itself is not proof of a live/real broker fill;
- `LIVE_OR_REAL_CONFIRMED` requires source-layer evidence that the personal order was actually executed live/real, such as a real broker/terminal position or an equally explicit source statement tying the fill to a live account;
- where Badar appears to trade personally but the source does not establish live/real execution, use `FILL_UNCLEAR`;
- where the source explicitly establishes TradingView/paper use, use `PAPER_OR_SIMULATION`;
- where a level/order is presented but Badar's own fill is not confirmed, use `PLAN_OR_SIGNAL_ONLY`.

This is not a new threshold. It is the conservative operational application of the already-frozen Section 5 requirement for a confirmed Badar-owned live/real XAUUSD entry.

## Batch result

All 10 rows have:
`authorship_status = BADAR_CONFIRMED`.

Execution status:
- `FILL_UNCLEAR`: **8**
- `PAPER_OR_SIMULATION`: **1**
- `PLAN_OR_SIGNAL_ONLY`: **1**
- `LIVE_OR_REAL_CONFIRMED`: **0**

Primary eligible rows in this batch:
**0 / 10**

The two July 28 rows are especially informative:
- `suuicaoUvDQ#1` is personal but excluded as paper/simulation because Badar explicitly says live-account trading will start the next day;
- `suuicaoUvDQ#3` is excluded as plan/signal-only because he says he set the limit and that some people took it, but his own fill is not confirmed; the same stream states live-account trading starts tomorrow.

The remaining eight are not called paper merely because TradingView is visible. They remain `FILL_UNCLEAR` because the source does not prove the required live/real fill.

## Scientific guardrail

No row was included or excluded because of:
- win/loss;
- RR;
- TP/SL result;
- later price path;
- profitability.

Outcome/result fields were not used for eligibility.

## Current project implication

Do **not** compute D-091 ADEQUATE/INSUFFICIENT yet.

This is only 10 of 40 exact-M1 candidates. The remaining 30 may contain real-account evidence, including later streams that explicitly show Exness real positions.

Immediate next safe work:
adjudicate the next chronological exact-M1 batch beginning with `HOidQitTyAc#3`, using the same source-only standard.

No market-price lookup, no CI, and no model fitting are authorized by this finding.
