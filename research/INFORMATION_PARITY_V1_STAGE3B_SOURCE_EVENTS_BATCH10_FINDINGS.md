# Information Parity V1 — Stage 3B Source Event Construction Batch 10

Status: **SEP 18 + SEP 21 FROZEN — CONSERVATIVE PERSONAL-COMMITMENT BOUNDARY PRESERVED**

Parents:
- D-099 through D-108
- `research/INFORMATION_PARITY_V1_STAGE3B_DECISION_PROCESS_PREREGISTRATION.md`

Badar source pin:
- commit `cc94077c953efa0d048e61d6ba4fbcdd0e3ca79a`
- `dataset/live_trades.csv` blob `24939bf5ad141d38f2aad08c30ab6a077ab10086`

No `derived/` content was used.
No provider market data was queried.

Artifact:
`research/reference/information-parity-v1/stage3b-source-events-v1-batch10.csv`

## Scope

This batch reviews all four pinned XAUUSD trade-table rows on:
- 2026-09-18
- 2026-09-21

and all distinct explicit Badar P3 decisions retained from the same reviewed source sequences.

## ACT disposition

Source trade rows reviewed:
**4**

Primary-eligible Badar ACT events:
**3**

Direction:
- LONG: **2**
- SHORT: **1**

Provenance:
- P1 LIVE_REAL_EXECUTION: **2**
- P2 LIVE_BADAR_COMMITMENT: **1**

Evidence:
- E1 DIRECT: **2**
- E2 CORROBORATED: **1**

Timing:
- EXACT_M1: **2**
- INTERVAL_2M: **1**

## Sep 18 trade

`fkZjFHTg3GY#1` is a P2 E1 long.

The source directly says:
- `Let's try to [buy] from here`;
- then `I have taken this one`;
- then `I bought it because of the range`.

No broker account is shown, so the decision remains P2.

## Sep 21 trade #1

`qTSedn6hEp8#1` is P1 E2.

The same live source contains:
- Badar's Exness real-account web terminal;
- the current short/range-top position;
- explicit reduced-size ownership language (`I have kept it small`);
- later direct BE/manual-exit management.

The exact commitment second is less clean than trade #2, so the event keeps a two-minute source interval rather than inventing an exact point.

## Sep 21 trade #2

`qTSedn6hEp8#2` is P1 E1.

At 36:58 Badar directly states:
`I am buying it from here`.

The Exness real 0.10-lot XAU/USD position is later visible with dollar-valued SL/P&L.

## Conservative exclusion: qTSedn6hEp8#3

Trade-table row `qTSedn6hEp8#3` is **not** admitted as a primary Badar ACT event.

The source clearly documents:
- a large short idea;
- SL/TP management;
- later `our TP` language;
- the trade logic and result.

But it does not cleanly establish Badar's own current commitment at E1/E2 confidence:
- personal fill is not shown;
- the setup is framed partly as a trade `for the big accounts`;
- the transcript does not contain a comparably direct `I am taking/selling` commitment.

This is exactly where Stage 3B must distinguish:
- a source-authored trade scenario / group plan;
- Badar's own current action commitment.

The row is therefore E3-like for personal ACT ownership and is excluded.

Outcome/TP evidence is not used to upgrade it.

## P3 additions

New explicit P3 events:
**13**

Sep 18:
**6**

Sep 21:
**7**

### Sep 18 sequence

Distinct decisions include:
1. no trading until the structure/supply area is properly formed;
2. do not chase the already-running sell — wait for it to return;
3. considered buy deferred until the M30 close;
4. reject a bullish close inside the sell move as a trap;
5. later sell sign still deferred to the M30/next structure;
6. after the NY-low sweep, the state remains unclear with a large SL, so Badar stops for the day.

### Sep 21 sequence

Distinct decisions include:
1. after exiting trade #1, wait for the 30m close before deciding;
2. reject LTF sell confirmation inside the range;
3. reject chasing the fast 50-pip drop as FOMO;
4. range-low buy remains deferred because there is no strong sign;
5. immediately before trade #2, explicitly wait because there is still no sign;
6. later bearish-OB state makes buying invalid until H1/5m resolves;
7. end-of-stream: do not buy before the lower 4302/4300 area.

These are separate sequential decision states, not repeated copies of one no-trade period.

## Cumulative Stage 3B source state

ACT:
- total: **82**
- LONG: **41**
- SHORT: **41**
- distinct ACT dates: **29**

P3 REJECT/WAIT:
- total: **94**
- distinct reject dates: **29**

Paired ACT + REJECT dates:
- **29**

All D-099 numerical source-adequacy floors remain exceeded.

## Non-table ACT backfill remains separate

This batch does not perform the non-table ACT backfill.

That phase remains mandatory after all pinned trade-table dates are reviewed, because D-099's teacher unit is a source decision event and valid unfilled commitments may be absent from the trade table.

## Overall status

`NUMERICALLY ADEQUATE — FINAL SOURCE CONSTRUCTION/QA STILL IN PROGRESS`

No provider market join is authorized.

## Immediate next safe work

Continue chronologically with the next pinned September source dates:
- 2026-09-22
- 2026-09-23

under the unchanged Stage 3B rules.

After September/October trade-table review completes:
1. run the non-table ACT backfill;
2. merge all batches;
3. audit source-row coverage and exclusions;
4. audit same-plan collapses;
5. audit ACT/P3 temporal conflicts;
6. audit timing/timezones;
7. freeze the final Stage 3B CSV and SHA-256;
8. issue final source-adequacy certification.

No provider market data, model fitting or CI is authorized.
