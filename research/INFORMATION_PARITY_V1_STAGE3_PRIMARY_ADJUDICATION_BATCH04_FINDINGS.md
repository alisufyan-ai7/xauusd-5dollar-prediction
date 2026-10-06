# Information Parity V1 — Stage 3 Primary Teacher Adjudication Batch 04 Findings

Status: **CURRENT V2 EXACT-M1 POOL FULLY ADJUDICATED — OVERALL EVIDENCE ADEQUACY STILL PENDING INTERVAL-ONLY FEASIBILITY**

Parents:
- `research/INFORMATION_PARITY_V1_STAGE3_PROTOCOL_PREREGISTRATION.md`
- `research/INFORMATION_PARITY_V1_STAGE3_PRIMARY_ADJUDICATION_BATCH03_FINDINGS.md`
- D-089 through D-095

Pinned Badar source:
- commit `2df3d588c4b6d82761df2ee0c6f6639e82ce3414`
- `dataset/live_trades.csv` blob `ea620cb44937f276be2e65ae7da25ae9503be655`

No `derived/` content was used.

## Scope

This batch adjudicates the final 10 current V2 exact-M1 candidates:
- WUblCihXgPU#3
- CPGcMydNbbQ#1
- CPGcMydNbbQ#2
- CPGcMydNbbQ#3
- CPGcMydNbbQ#4
- CPGcMydNbbQ#5
- PYPzCJV-YXE#1
- PxDGTxs-Cvc#1
- PxDGTxs-Cvc#2
- PxDGTxs-Cvc#4

Artifact:
`research/reference/information-parity-v1/stage3-teacher-primary-adjudication-batch04.csv`

## Batch result

Authorship:
- `BADAR_CONFIRMED`: **10 / 10**

Execution:
- `FILL_UNCLEAR`: **10**
- `LIVE_OR_REAL_CONFIRMED`: **0**

Primary eligible:
- **0 / 10**

## Important per-stream findings

### WUblCihXgPU#3

Badar explicitly enters, moves to break-even and says he booked TP1. However, the source does not tie this specific row to a live/real broker account. A later dollar-profit statement is not unambiguously attributable to this exact position/account.

### CPGcMydNbbQ#1–#5

These are all Badar-authored trade decisions.

The source repeatedly contains first-person entry/management language. Trade #4 is shown while working on Zain's laptop, but Badar says `my SL`; unlike the previously excluded `OpMzvMNNrHM#2`, there is no explicit source statement that Zain owns #4.

Therefore:
- authorship stays `BADAR_CONFIRMED`;
- execution stays `FILL_UNCLEAR`.

No CPG row is upgraded merely because the interface looks broker-like or because Badar discusses personal risk management.

### PYPzCJV-YXE#1

Badar presents and manages the position as his own and states account-risk percentages, but the source evidence is a chart/position tool without a per-row live/real terminal/account tie.

Status:
`FILL_UNCLEAR`.

### PxDGTxs-Cvc#1/#2/#4

These are Badar-authored trades/entries.

The same stream later contains an explicitly shown Exness real-account sell (#5), but that does **not** retroactively prove that earlier chart positions #1/#2/#4 were filled on the same live account.

Under the frozen per-row provenance rule, all three remain:
`FILL_UNCLEAR`.

## Full current V2 exact-M1 adjudication result

All **40 / 40** V2 exact-M1 candidates are now adjudicated.

Primary eligible:
- total: **4**
- LONG: **3**
- SHORT: **1**
- distinct primary dates: **3**

The four current primary rows are:
- `NIDMLJuBPwk#1` — LONG — 2026-08-07;
- `B83jlxwuo10#1` — LONG — 2026-09-04;
- `B83jlxwuo10#5` — SHORT — 2026-09-04;
- `qTSedn6hEp8#2` — LONG — 2026-09-21.

No same-minute/same-direction collapse reduces these four.

## Evidence-adequacy arithmetic

D-091 requires:
- >=40 primary positives;
- >=20 eligible source dates;
- >=15 LONG;
- >=15 SHORT.

Relative to the current primary set, reaching `ADEQUATE` would require at minimum:
- **36 additional primary-eligible positives**;
- enough of those to add at least **17 new eligible dates**;
- at least **12 additional LONG** positives;
- at least **14 additional SHORT** positives.

The current V2 exact-M1 pool by itself is therefore:

`INSUFFICIENT`

But the overall source corpus is **not yet finally classified** under D-091, because 79 source-table rows remain outside the current exact-M1 set and some may be promotable through source-only timestamp review.

## Why overall D-091 is not yet final

A final `INSUFFICIENT` determination is justified only after showing that the remaining interval-only source evidence cannot supply the missing 36 / 17 dates / 12 LONG / 14 SHORT without relaxing the frozen rules.

The next review should therefore be a **feasibility-bound scan**, not a blind frame-by-frame review of all 79 rows.

For each interval-only row, determine from source metadata/notes whether it has both:
1. plausible `LIVE_OR_REAL_CONFIRMED` evidence;
2. plausible source evidence capable of resolving one unique M1 entry minute.

Rows failing either condition cannot rescue the D-091 gate and need no exhaustive frame adjudication.

If the maximum possible eligible set after that conservative feasibility scan is below any frozen floor, D-091 can be finalized as `INSUFFICIENT / NOT TESTED` without unnecessary further review.

## Scientific guardrails

No eligibility decision used:
- trade outcome;
- result R;
- TP/SL success;
- later price path;
- profitability.

No 2026 market-price lookup was used.

## Next safe work

Perform the source-only interval-row feasibility-bound scan described above.

D-088 remains controlling:
- no 2026 XAUUSD market reconstruction;
- no model fitting;
- no CI;
- 2022-2025 remain sealed.
