# Information Parity V1 — Stage 3 Primary Teacher Adjudication Batch 03 Findings

Status: **PARTIAL SOURCE-ONLY ADJUDICATION — TWO MORE PRIMARY-ELIGIBLE ROWS**

Parents:
- `research/INFORMATION_PARITY_V1_STAGE3_PROTOCOL_PREREGISTRATION.md`
- `research/INFORMATION_PARITY_V1_STAGE3_PRIMARY_ADJUDICATION_BATCH02_FINDINGS.md`
- D-089 through D-094

Pinned Badar source:
- commit `2df3d588c4b6d82761df2ee0c6f6639e82ce3414`
- `dataset/live_trades.csv` blob `ea620cb44937f276be2e65ae7da25ae9503be655`

No `derived/` content was used.

## Scope

This batch adjudicates the next 10 chronological exact-M1 V2 candidates:
- B83jlxwuo10#5
- C18mm9p2oW4#1
- C18mm9p2oW4#3
- qTSedn6hEp8#2
- OpMzvMNNrHM#2
- OpMzvMNNrHM#3
- U5CphnzaXio#1
- 1E65DgTFxe0#2
- WUblCihXgPU#1
- WUblCihXgPU#2

Artifact:
`research/reference/information-parity-v1/stage3-teacher-primary-adjudication-batch03.csv`

## Batch result

Authorship:
- `BADAR_CONFIRMED`: **9**
- `OTHER_PERSON`: **1**

Execution:
- `LIVE_OR_REAL_CONFIRMED`: **2**
- `FILL_UNCLEAR`: **8**

Primary eligible:
- **2 / 10**

## Confirmed primary rows

### B83jlxwuo10#5 — 2026-09-04 — SHORT

Primary eligible:
`true`

Evidence is per-trade rather than merely general account ownership:
- the stream source identifies execution on Badar's Exness real web terminal;
- #5 is a first-person entry/management sequence;
- immediately during #5, Badar discusses the 1:14 trade and ~300-pip profit;
- he then says he is looking at his dashboard, cannot show the dashboard, and states `I am making a profit`.

Resolved entry minute:
`2026-09-04T12:57:00Z`

### qTSedn6hEp8#2 — 2026-09-21 — LONG

Primary eligible:
`true`

Evidence:
- Badar explicitly says `I am buying it from here`;
- source frames show his Exness **real-account** web terminal;
- frame 45:40 shows the XAU/USD position at **0.10 lot**, entry 4351.531, dollar stop-loss exposure and live P&L;
- the source note tracks the position and later BE stop.

Resolved entry minute:
`2026-09-21T13:41:00Z`

## Explicit other-person exclusion

### OpMzvMNNrHM#2

`authorship_status = OTHER_PERSON`

The stream is showing **Zain's** laptop / OANDA chart for this trade. The source note explicitly states:

`Zain brother has done the trade`.

Badar explains/teaches the setup, but this row is not admitted as a Badar-owned teacher entry.

## Conservative fill-unclear rows

Seven Badar-authored rows remain `FILL_UNCLEAR`:
- C18mm9p2oW4#1
- C18mm9p2oW4#3
- OpMzvMNNrHM#3
- U5CphnzaXio#1
- 1E65DgTFxe0#2
- WUblCihXgPU#1
- WUblCihXgPU#2

These rows contain first-person trade and management language, but the pinned source does not establish per-row live/real execution strongly enough for the frozen primary-teacher rule.

A broker-looking chart, position tool, TP/SL discussion, or personal profit/loss narration is not upgraded to `LIVE_OR_REAL_CONFIRMED` unless the source ties that row to an actual live/real account or terminal.

## Cumulative state after Batches 01–03

- exact-M1 candidates adjudicated: **30 / 40**
- primary eligible: **4**
- primary eligible LONG: **3**
- primary eligible SHORT: **1**
- exact-M1 candidates remaining: **10**

This remains a partial adjudication.

Do **not** declare D-091 `INSUFFICIENT` yet because:
1. the final 10 V2 exact-M1 candidates remain;
2. interval-only rows have not yet been exhaustively source-frame-reviewed for additional exact-M1 promotions.

## Scientific guardrails

No eligibility decision used:
- outcome;
- result R;
- TP/SL success;
- later market path;
- profitability.

No 2026 market-price lookup was used.

## Next safe work

Adjudicate the final 10 current V2 exact-M1 candidates:
- WUblCihXgPU#3
- CPGcMydNbbQ#1 through #5
- PYPzCJV-YXE#1
- PxDGTxs-Cvc#1, #2 and #4

Only after that batch should the project assess whether further interval-only timestamp promotion is scientifically necessary before the first final D-091 adequacy determination.

D-088 remains controlling:
no 2026 XAUUSD market reconstruction or model fitting is authorized.
