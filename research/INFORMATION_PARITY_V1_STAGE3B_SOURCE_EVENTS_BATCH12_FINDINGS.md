# Information Parity V1 — Stage 3B Source Event Construction Batch 12

Status: **SEP 24 + SEP 25 FROZEN — SIGNAL-ONLY AND PRE-STREAM ROWS KEPT OUT OF PRIMARY ACT**

Parents:
- D-099 through D-110
- `research/INFORMATION_PARITY_V1_STAGE3B_DECISION_PROCESS_PREREGISTRATION.md`

Badar source pin:
- commit `cc94077c953efa0d048e61d6ba4fbcdd0e3ca79a`
- `dataset/live_trades.csv` blob `24939bf5ad141d38f2aad08c30ab6a077ab10086`

No `derived/` content was used.
No provider market data was queried.

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch12.csv`

## Scope

This batch reviews all four pinned XAUUSD trade-table rows on:
- 2026-09-24
- 2026-09-25

and all distinct explicit Badar P3 decisions retained from the same reviewed source sequences.

## ACT disposition

Source trade rows reviewed:
**4**

Primary Badar ACT events:
**2**

Direction:
- LONG: **0**
- SHORT: **2**

Provenance:
- P1 LIVE_REAL_EXECUTION: **0**
- P2 LIVE_BADAR_COMMITMENT: **2**

Evidence:
- E1 DIRECT: **2**

Timing:
- EXACT_M1: **2**

### Sep 24 trade #1 retained

`U5CphnzaXio#1` is a direct P2 short.

After the 5m, 10m and 15m sell-close sequence, Badar says:

`I am selling it from here for now`

No per-event real-account evidence is shown, so it remains P2.

### Sep 24 trade #2 excluded as signal-only

`U5CphnzaXio#2` is not a Badar ACT event.

Badar clearly explains the optional M1 re-sell for viewers, but later says:

`I didn't put it like that`

The setup subsequently reaches its target, but outcome does not convert a signalled/viewer trade into Badar's personal commitment.

The same explicit no-action statement is retained as a P3 decision.

### Sep 25 trade #1 excluded as pre-stream

`1E65DgTFxe0#1` is a strong documented trade:
- shared to Discord/groups;
- large H1-context short;
- later result/management shown.

But the decision occurred roughly 40-60 minutes before the stream.

The stream reviews the already-running/completed trade; it does not expose the contemporaneous live commitment moment required for a Stage 3B primary ACT event.

Therefore it remains excluded, consistent with earlier pre-stream exclusions.

### Sep 25 trade #2 retained

`1E65DgTFxe0#2` is P2 E1.

At 22:17 Badar states:
- `I will take a risk to sell it`;
- `I will take a little less`;
- `I have already sold it from here`.

This is a direct current short commitment with explicit reduced-risk language.

## P3 result

New explicit Badar P3 events:
**13**

Sep 24:
**6**

Sep 25:
**7**

### Sep 24 sequence

Distinct decisions include:
1. after the daily-low sweep, no trade at the current location — wait/retrace;
2. pre-trade #1, wait for the 15m close / another confirmation;
3. reject a marked FVG/location as not good enough for an add-on;
4. the optional M1 re-sell is not personally placed by Badar;
5. later add-on remains conditional on a fresh trap-candle/5m close;
6. late-session new-entry idea is rejected because price has already gone and it is now late.

### Sep 25 sequence

Distinct decisions include:
1. wait for retrace into the gap before re-selling;
2. do not sell from the current low;
3. wait for a sweep into the stronger FVG/POI;
4. immediately before trade #2, do not trade every gap — require confirmation;
5. later second re-entry requires a high sweep and confirmation pattern;
6. explicitly no interest in the counter-trend buy;
7. Friday stop: no more trades after the completed sequence.

These are materially distinct current decision states, not arbitrary no-entry minutes.

## Cumulative Stage 3B source state

ACT:
- total: **85**
- LONG: **41**
- SHORT: **44**
- distinct ACT dates: **32**

P3 REJECT/WAIT:
- total: **114**

Paired ACT + REJECT dates:
- **32**

All D-099 numerical source-adequacy floors remain exceeded.

## Source-row disposition implications

This batch adds two more examples that must appear in the final coverage audit:

- `U5CphnzaXio#2` — source-table trade/signalled setup, but Badar explicitly did **not** place it;
- `1E65DgTFxe0#1` — documented Badar trade, but decision occurred pre-stream and therefore lacks the required contemporaneous live decision event.

The final coverage audit must distinguish these from:
- primary ACT;
- other-person;
- ambiguous;
- same-plan collapsed;
- non-XAUUSD;
- non-table backfill events.

## Overall status

`NUMERICALLY ADEQUATE — FINAL SOURCE CONSTRUCTION/QA STILL IN PROGRESS`

No market join is authorized.

## Immediate next safe work

Continue chronologically with:
- 2026-09-28
- 2026-09-29

under the unchanged Stage 3B rules.

After September/October trade-table review completes:
1. run the mandatory non-table ACT backfill;
2. merge all batches;
3. build the explicit source-row disposition/coverage audit;
4. audit same-plan collapses;
5. audit ACT/P3 temporal conflicts;
6. audit timing/timezones;
7. freeze the final Stage 3B CSV and SHA-256;
8. issue final source-adequacy certification.

No provider market data, model fitting or CI is authorized.
