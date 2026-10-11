# Information Parity V1 — Stage 3B Source Event Construction Batch 06

Status: **AUGUST 28 + 31 FROZEN — MINIMUM SOURCE-ADEQUACY FLOORS REACHED IN THE PARTIAL CORPUS**

Parents:
- D-099 through D-104
- `research/INFORMATION_PARITY_V1_STAGE3B_DECISION_PROCESS_PREREGISTRATION.md`

Badar source pin:
- commit `cc94077c953efa0d048e61d6ba4fbcdd0e3ca79a`
- `dataset/live_trades.csv` blob `24939bf5ad141d38f2aad08c30ab6a077ab10086`

No `derived/` content was used.
No provider market data was queried.

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch06.csv`

## Scope

This bounded batch covers all six pinned XAUUSD trade-table rows on:
- 2026-08-28
- 2026-08-31

and every distinct explicit P3 decision found in the reviewed source sequences.

## ACT result

Rows reviewed:
**6**

Primary-eligible ACT:
**6 / 6**

Direction:
- LONG: **2**
- SHORT: **4**

Evidence:
- E1 DIRECT: **6**

Timing:
- EXACT_M1: **6**

Provenance:
- P1 LIVE_REAL_EXECUTION: **4**
- P2 LIVE_BADAR_COMMITMENT: **2**

### P1 events

`u7KGSeF2lA0#2` is P1 because the stream shows the Exness real terminal and Badar explicitly states that **his trade has been executed** while discussing TradingView/terminal lag.

All three `q6wgyFyzIs0` rows are P1:
- the source is Badar's Exness real web terminal;
- orders/positions are shown at 0.5 lot;
- #1 and #2 are explicit sell-limit commitments;
- #3 is explicitly `I have taken another entry on account`.

`u7KGSeF2lA0#1` and `#3` remain P2 because the per-event source does not tie those particular commitment moments to live/real execution strongly enough to inherit P1 merely from terminal visibility elsewhere in the stream.

## P3 result

New P3 events:
**13**

2026-08-28:
**7**

2026-08-31:
**6**

They are materially distinct sequential decisions rather than repeated labels inside one static wait.

### Aug 28 decision sequence

1. pre-news direct buy cancelled when the last-second close rejects;
2. immediate post-news wait because of server/news risk;
3. later buy opportunity deferred because the stop is too large/risky;
4. later double-low buy requires a sign — otherwise wait;
5. later sell requires the M1 close before commitment;
6. later apparent buy sign is deferred because overhead structure still requires a break/retest;
7. end of session: further trading explicitly rejected as overtrading.

### Aug 31 decision sequence

1. wait for a good M15 sell close;
2. no BOS -> no trade from the current location; wait higher;
3. later doji/unclear close -> wait for the next candle;
4. after closing the prior trade, defer re-entry until another sweep/HTF check;
5. while #3 is open, do not add at the current location; wait for the higher hidden-OB/FVG area with a smaller stop;
6. later possible trap: explicitly do not decide from the first candle; wait for next-candle confirmation.

The #5 event above remains valid P3 despite an existing open position because D-099 explicitly treats decision/account state as part of the policy and permits a concrete `DEFER_WAIT` while considering an add-on. It is not counted as an ACT because the add-on is never shown as taken.

## Cumulative Stage 3B source state through August

ACT:
- total: **62**
- LONG: **29**
- SHORT: **33**
- distinct ACT dates: **21**

P3 REJECT/WAIT:
- total: **41**
- distinct reject dates: **21**

Paired ACT + REJECT dates:
- **21**

## Frozen adequacy floors — current numerical state

### Task A

Required:
- >=40 ACT
- >=40 REJECT/WAIT
- >=20 paired dates

Current:
- ACT = **62 / 40** — met
- REJECT/WAIT = **41 / 40** — met
- paired dates = **21 / 20** — met

### Task B

Required:
- >=40 ACT
- >=20 ACT dates
- >=15 LONG
- >=15 SHORT

Current:
- ACT = **62 / 40** — met
- ACT dates = **21 / 20** — met
- LONG = **29 / 15** — met
- SHORT = **33 / 15** — met

Therefore the **minimum numerical source-evidence floors are now reached** without changing:
- timing cap;
- evidence grades;
- provenance rules;
- negative definition;
- model design.

## Important: do not declare the final Stage 3B source table frozen yet

This is a partial chronological corpus through August.

The pinned Badar source still contains later eligible dates:
- September;
- October.

Stopping source extraction merely because the minimum floors have been crossed would make the empirical teacher dataset depend on the point at which a threshold happened to be reached.

Therefore:

- minimum source adequacy is now **feasible and numerically satisfied in the partial corpus**;
- final source adequacy is **not yet certified**;
- the final `stage3b-source-events-v1.csv` is not yet frozen;
- no market join is authorized.

The remaining pinned source corpus must be completed using the same rules, then:
1. merge all batches;
2. check duplicate/source-row coverage;
3. validate same-plan collapses;
4. validate ACT/P3 temporal conflicts;
5. validate timing widths/timezones;
6. freeze the final CSV and SHA-256;
7. issue the final source-adequacy finding.

Only after that would a separate chronology decision be able to consider D-088.

## Immediate next safe work

Continue chronologically with:
- 2026-09-02
- 2026-09-04

using the identical frozen Stage 3B rules.

Do not reduce source review now that the floors are crossed.
Do not access provider market data.
Do not run model fitting or CI.
