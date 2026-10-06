# Information Parity V1 — Stage 3 Primary Teacher Adjudication Batch 02 Findings

Status: **PARTIAL SOURCE-ONLY ADJUDICATION — FIRST PRIMARY-ELIGIBLE ROWS FOUND**

Parents:
- `research/INFORMATION_PARITY_V1_STAGE3_PROTOCOL_PREREGISTRATION.md`
- `research/INFORMATION_PARITY_V1_STAGE3_PRIMARY_ADJUDICATION_BATCH01_FINDINGS.md`
- D-089 through D-093

Pinned Badar source:
- commit `2df3d588c4b6d82761df2ee0c6f6639e82ce3414`
- `dataset/live_trades.csv` blob `ea620cb44937f276be2e65ae7da25ae9503be655`

No `derived/` content was used.

## Scope

This batch adjudicates the next 10 chronological exact-M1 candidates:
- HOidQitTyAc#3
- KsWpzeJhAVk#2
- OCBsHuFhjUQ#1
- OCBsHuFhjUQ#3
- OCBsHuFhjUQ#4
- OCBsHuFhjUQ#5
- gfP4EW1IfVE#2
- NIDMLJuBPwk#1
- W2oZdVu2rxE#2
- B83jlxwuo10#1

Artifact:
`research/reference/information-parity-v1/stage3-teacher-primary-adjudication-batch02.csv`

## Batch result

Authorship:
- `BADAR_CONFIRMED`: **10 / 10**

Execution:
- `LIVE_OR_REAL_CONFIRMED`: **2**
- `FILL_UNCLEAR`: **8**

Primary eligible:
- **2 / 10**

No paper/simulation or plan-only label was assigned in this batch where the source did not justify that stronger exclusion; ambiguous TradingView/test evidence stays `FILL_UNCLEAR`.

## First confirmed primary rows

### NIDMLJuBPwk#1 — 2026-08-07 — LONG

Primary eligible:
`true`

Why:
- Badar says `I have taken my trade`;
- source note identifies XAUUSD on an Exness terminal plus a second account;
- transcript describes the Exness terminal lagging by two candles;
- he compares the same trade across accounts;
- he reports a realised close on one account and states he closed it on his mobile phone.

This is direct source-layer evidence of a personal broker/account execution, not just a TradingView drawing.

Resolved entry minute:
`2026-08-07T12:34:00Z`

### B83jlxwuo10#1 — 2026-09-04 — LONG

Primary eligible:
`true`

Why:
- source note explicitly identifies an Exness real web terminal;
- the terminal is described as `Real, Badar` with balance 10,507.24 USD;
- Badar refers to `my live account`;
- a 0.1-lot buy limit is placed with visible dollar SL/TP;
- the NFP spike fills/stops the order with slippage.

Resolved fill minute:
`2026-09-04T12:30:00Z`

## Conservative exclusions

The other eight rows are Badar-authored trade decisions but remain `FILL_UNCLEAR`.

Examples:
- `HOidQitTyAc#3`: explicit buy and BE management, but no source tie to a live broker fill;
- `KsWpzeJhAVk#2`: explicit re-sell and exit, but TradingView-only evidence;
- `OCBsHuFhjUQ#4`: explicitly described as testing the Baba strategy; source does not establish whether the test was live versus simulation;
- `gfP4EW1IfVE#2`: explicit `I am selling` and `full TP`, but no live-account execution evidence;
- `W2oZdVu2rxE#2`: he references having shown live accounts generally, but does not tie this specific trade to one.

The rule is per-row execution provenance. A trader having a live account elsewhere does not automatically make every TradingView trade a live/real fill.

## Cumulative adjudicated state

Across Batches 01 and 02:
- exact-M1 candidates adjudicated: **20**
- primary eligible found: **2**
- primary eligible LONG: **2**
- primary eligible SHORT: **0**

This is **not** the final D-091 evidence-adequacy result.

Reasons:
1. 20 exact-M1 V2 candidates remain unadjudicated;
2. additional currently interval-only source rows have not been exhaustively frame-reviewed for possible exact-M1 promotion.

Therefore do not infer `INSUFFICIENT` merely from the current 2/20 primary count.

## Guardrails

Eligibility did not use:
- outcome;
- RR;
- TP/SL success;
- later price path;
- profitability.

No market-price lookup was used.

## Next safe work

Continue with the next chronological exact-M1 batch beginning `B83jlxwuo10#5` / the subsequent V2 candidates, prioritizing explicit Exness/real-account evidence.

D-088 remains controlling:
no 2026 XAUUSD market reconstruction or model fitting is authorized.
