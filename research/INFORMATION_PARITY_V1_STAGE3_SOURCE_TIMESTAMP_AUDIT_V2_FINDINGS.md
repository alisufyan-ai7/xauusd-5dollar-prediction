# Information Parity V1 — Stage 3 Source Timestamp Audit V2 Findings

Status: **TIMESTAMP SUB-AUDIT REACHES NUMERIC FLOORS — PRIMARY EVIDENCE ADEQUACY STILL UNRESOLVED**

Parent:
- `research/INFORMATION_PARITY_V1_STAGE3_PROTOCOL_PREREGISTRATION.md`
- `research/INFORMATION_PARITY_V1_STAGE3_EVIDENCE_ADEQUACY_CLARIFICATION.md`
- D-090
- D-091

No market-price lookup was used.

## Frozen source identity

Badar source repository:
`alisufyan-ai7/unpack-human-trading-strategies-claude`

Pinned commit:
`2df3d588c4b6d82761df2ee0c6f6639e82ce3414`

Pinned teacher table:
`dataset/live_trades.csv`

Teacher-table blob:
`ea620cb44937f276be2e65ae7da25ae9503be655`

No `derived/` content was used.

## V2 artifact

`research/reference/information-parity-v1/stage3-teacher-timestamp-audit-v2.csv`

Blob:
`de7f9647a18aa018ca00dc727c141f02d74fd2f4`

V1 remains preserved unchanged.

## Five exact-M1 promotions

The targeted source transcript/frame review promoted five V1 `INTERVAL_ONLY` rows without using market prices:

- `HOidQitTyAc#3` — LONG — **18:01 UTC+4**. Transcript [61:20] says `Let's take a trade from here`; exact stream anchor 0:00=16:59:43 resolves the call to 18:01:03; the source frame sheet shows the corresponding position tool by 63:00.
- `qTSedn6hEp8#2` — LONG — **17:41 UTC+4**. Transcript [36:58] says `I am buying it from here`; exact anchor 0:00=17:04:05 resolves the call to 17:41:03; source frame evidence shows the position tool, and the source note later shows the Exness real position.
- `NPUPkMWzKTE#1` — SHORT — **18:11 UTC+4**. Transcript [8:00] says `Let's also do a sell here` and `I've done it`; exact anchor 0:00=18:03:16 resolves the statement to 18:11:16; the source frame shows the position tool at 8:40.
- `m0l1wj9IZ2o#3` — SHORT — **17:33 UTC+4**. Transcript [21:43] says `I am selling` and `I am taking this from here, from this exact place`; exact anchor 0:00=17:11:53 resolves it to 17:33:36; the position tool is visible by 23:00.
- `PYPzCJV-YXE#1` — SHORT — **18:15 UTC+5**. A source frame at stream 3:00 shows 18:12:10 UTC+5, fixing 0:00 at 18:09:10; transcript [5:56] says the M15 shifted south and `one trade is directly from here`, resolving the decision to 18:15:06; the corresponding position tool is visible by 6:20.

## Timestamp-only totals

Before authorship/live-execution filtering:

- exact-M1 candidates: **40**
- source dates: **21**
- LONG: **16**
- SHORT: **24**

The timestamp sub-audit therefore clears the numerical 40 / 20 / 15 / 15 floors.

This is **not** yet a D-091 `ADEQUATE` result.

D-091 applies to primary eligible positives only after:
- Badar authorship adjudication;
- live/real execution adjudication;
- frozen exclusions;
- same-minute same-direction collapse.

Current overall status:

`UNRESOLVED — PRIMARY ELIGIBILITY NOT YET ADJUDICATED`

## Conservative non-promotions

The review deliberately left ambiguous rows unresolved. Examples:
- `9d7IHhIAi6M#1`: source evidence tightly brackets the limit fill around 18:42 but does not eliminate a prior-minute fill with enough certainty for this strict audit;
- `6trb-6A2t6Q#1/#2`: real Exness positions are clear, but the verbal call and later position visibility span more than one possible minute;
- `fkZjFHTg3GY#1`: source statements and position-tool appearance do not pin one unique execution minute.

The timestamp rule was not relaxed merely to cross the numeric floor.

## Next safe gate

Take the 40 exact-M1 V2 candidates and perform source-only:
1. `authorship_status`;
2. `execution_status`;
3. frozen exclusions;
4. same-minute same-direction collapse;
5. first true D-091 `ADEQUATE` / `INSUFFICIENT` determination.

D-088 remains in force:
- no 2026 XAUUSD market reconstruction;
- no model fitting;
- 2022-2025 remain sealed;
- no CI is required for this source-evidence work.
