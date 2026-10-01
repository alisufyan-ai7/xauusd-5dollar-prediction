# Root-Reset V5 — Badar A+ Source-Fidelity TRAIN-Only Experiment

Status: **FROZEN BEFORE EMPIRICAL RESULTS**

## Purpose

Root-Reset V4 did not produce an economic sample because its deterministic translation collapsed before entry.

The accepted TRAIN-only V4 translation diagnosis (run 36779728544; D-061) showed that the main coverage losses were caused by:
- the added V4 requirement for two M5 closes;
- a midpoint-only FVG retracement entry;
- session-only structural targeting.

The diagnosis did **not** select a profitable alternative.

V5 therefore does not choose the diagnostic branch with the most candidates. It returns to the admitted Badar source layer and freezes one narrower translation of the taught S01 / A+ setup before seeing any V5 economic result.

The V5 hypothesis is:

> H1-led directional/location context + session-liquidity sweep into active H1 FVG + M15 close-back confirmation + a source-valid M5/M3 close-based MSS that creates a clean FVG + retracement to the FVG proximal edge + structural stop beyond the sweep + a source-marked HTF liquidity target with at least $5 distance and at least 1:3 reward/risk may create an economically testable TRAIN population.

This is not a test of every discretionary variant used by Badar.

## Source boundary

Authorized Badar repository:
`alisufyan-ai7/unpack-human-trading-strategies-claude`

Allowed evidence for defining V5:
- `PLAYBOOK.md`
- `LIVE_TRADING_OBSERVATIONS.md`
- `dataset/live_trades.csv`
- `notes/**`
- `transcripts/**`

Everything in `derived/` is excluded from defining V5 and must not be attributed to Badar.

### Source evidence resolving the V5 translation

The main source-layer evidence used is:

- `notes/videos/dOdvKLaBPaA.md`:
  - liquidity zone first;
  - sweep -> momentum shift;
  - MSS checked on M3/M5/M15;
  - M1 MSS described as unreliable in the course;
  - enter at the FVG/fresh OB created by the shift;
  - SL beyond the sweep.

- `notes/videos/6en-a8-p48w.md`:
  - H1 -> M30/M15 -> M5/M3 execution;
  - no clean FVG means no trade;
  - when M5 gives no clean FVG, use M3;
  - SL beyond the sweep;
  - TP1 about 1:3 at a structural level.

- `notes/videos/CzyCyduZqOk.md`:
  - sweep -> MSS -> FVG;
  - entry at the **start/proximal edge of the FVG**;
  - SL beyond the sweep/MSS origin.

- `notes/videos/TYY0aNKVnZ8.md`:
  - close-based MSS;
  - M5 to M3 refinement;
  - enter at the FVG created by the MSS;
  - fixed SL and low trade frequency.

- `PLAYBOOK.md`, S01:
  - M15/M5 MSS with M3 fallback;
  - a close beyond the swing is the minimum MSS event, while 2-3 closes are described as better confirmation;
  - valid FVG is mandatory for this A+ translation;
  - entry at the FVG proximal edge / start;
  - SL beyond sweep plus buffer;
  - minimum RR about 1:3;
  - final target at next HTF liquidity.

- `LIVE_TRADING_OBSERVATIONS.md` documents many M1/direct-close executions in live trading, but the source layer also records that these are more discretionary and that the course calls M1 MSS unreliable. Therefore V5 does **not** choose M1/direct-close merely because the diagnosis produced more such candidates.

Where Badar does not provide one unique mechanical definition, the operational rule below is explicitly a project translation.

## Data boundary

Use only synchronized Dukascopy XAUUSD BID/ASK M1:
- 2016
- 2017
- 2018
- 2019
- 2020
- 2021

Do not access:
- 2022 VALIDATION
- 2023-2024 DEVELOPMENT_TEST
- 2025 FINAL_OOS

No ML model is trained in V5.

Every accepted V5 historical run must preserve compact SHA-256 identities for the raw and synchronized 2016-2021 files in its artifact.

## Frozen upstream logic

V5 keeps V4 unchanged through the M15 close-back confirmation.

This means V5 reuses, without modification:

- IANA timezone/session definitions;
- Asian and London frozen ranges;
- 09:00-10:30 New York execution window;
- 09:55-10:10 New York time-only news exclusion;
- synchronized-bar completeness requirements;
- D1/H4/H1 causal structure construction;
- H1-led directional gate;
- active H1 FVG construction, invalidation and 72-hour age limit;
- Asian/London directional liquidity pools;
- ATR15 proxy and 0.05*ATR15 sweep buffer;
- M15 sweep through session liquidity;
- M15 close back through the swept level;
- overlap of the M15 sweep bar with an active same-direction H1 FVG.

The accepted V4 same-snapshot reference produced 135 such M15 confirmations on the recorded TRAIN snapshot. V5 is not required to reproduce the same count on a future provider snapshot, but its workflow must record that snapshot identity.

## Lower-timeframe source-fidelity confirmation

After a valid M15 close-back, create a pending setup for at most 30 minutes or until 10:30 New York, whichever comes first.

Derive complete UTC-clock-aligned M5 and M3 bars from synchronized BID M1.

### Frozen pre-confirmation reference swings

At the M15 confirmation timestamp, freeze separately for M5 and M3:

- BUY reference = most recent confirmed swing high;
- SELL reference = most recent confirmed swing low.

Use the same causal 2-left / 2-right swing definition already used in V4.

The reference does not move while the setup is pending.

### MSS rule

A source-valid MSS needs **one completed candle close** beyond the frozen reference:

BUY:
- close > frozen swing high.

SELL:
- close < frozen swing low.

Rationale:
the source describes the close as the minimum event and says 2-3 closes are stronger/better confirmation. V4 converted that preference into a mandatory two-close gate; V5 removes that added requirement while retaining close-based confirmation.

### M5/M3 hierarchy

Both M5 and M3 are allowed source timeframes.

Causal selection:
- scan completed M5 and M3 bars after the M15 confirmation;
- the first timeframe to complete a valid MSS **with a valid displacement FVG** becomes the trigger;
- if M5 and M3 both become valid at the exact same timestamp, prefer M5;
- no lookahead is allowed to ignore an already-valid M3 event in hope of a later M5 event.

This operationalizes M5 as the primary execution timeframe with M3 as the documented fallback while preserving real-time causality.

M1 MSS is not used in V5.

## Mandatory displacement FVG

The selected M5/M3 MSS must create a clean three-candle FVG in the MSS leg.

For the trigger bar j, inspect j, j-1, j-2 and choose the most recent qualifying FVG whose third candle has completed after the M15 confirmation.

BUY bullish FVG:
- high[k-2] < low[k];
- zone = [high[k-2], low[k]].

SELL bearish FVG:
- low[k-2] > high[k];
- zone = [high[k], low[k-2]].

If no valid FVG exists with the MSS:
- that MSS event is not an entry trigger;
- continue scanning causally until pending expiry.

No order-block alternative is added in V5 because its mechanical definition is less unique.

## Entry — proximal FVG edge, not midpoint

V5 uses the source-described **start/proximal edge** of the selected displacement FVG.

BUY:
- limit = upper boundary of the bullish FVG, i.e. the first edge encountered on a retracement from above.

SELL:
- limit = lower boundary of the bearish FVG, i.e. the first edge encountered on a retracement from below.

This replaces V4's midpoint rule, which was a project narrowing rather than a uniquely source-specified entry.

The limit becomes active only after the trigger bar has completed.

Executable fill:
- BUY fills on ASK low <= limit;
- SELL fills on BID high >= limit.

Expiry:
- 30 minutes after trigger completion;
- or 10:30 New York;
- whichever occurs first.

No chasing and no direct market entry are allowed in V5.

## Stop — source-taught structural invalidation

V5 uses one stop hypothesis only.

BUY:
- stop = confirming M15 sweep BID low - 0.05*ATR15_PROXY.

SELL:
- stop = executable ASK high over the confirming M15 interval + 0.05*ATR15_PROXY.

The stop must be on the correct side of entry with positive distance.

No stop-distance cap.
No widening.
No micro-stop alternative in V5.

Reason:
the taught A+ sequence consistently places the stop beyond the sweep. The live micro-stop variants are not used to create multiplicity in this source-fidelity experiment.

## Structural target hierarchy

V5 distinguishes intraday session liquidity from the final HTF target.

### Intermediate session liquidity — descriptive only

Record the nearest opposing Asian/London session liquidity beyond entry as an intermediate structural level when present.

It is not used as the final V5 exit and no partial-close rule is simulated.

### Final target candidates

Use only levels that are causally known at entry:

BUY:
- previous UTC-day high;
- most recent confirmed H1 swing high above entry;
- most recent confirmed H4 swing high above entry.

SELL:
- previous UTC-day low;
- most recent confirmed H1 swing low below entry;
- most recent confirmed H4 swing low below entry.

Previous UTC-day is a project operationalization of PDH/PDL because the source does not uniquely specify the broker/day boundary.

If multiple final target candidates exist:
- choose the nearest qualifying target in the trade direction.

### Project opportunity and source RR gates

The selected final structural target must satisfy BOTH:

1. distance from executable entry >= **$5.00**;
2. target distance / structural stop distance >= **3.00**.

If no causally known final structural target satisfies both:
- reject the candidate before placing the entry order.

This combines the project objective with the source-taught minimum RR for the A+ setup.

No target family is selected post hoc.

## Executable path and outcome

Use the same BID/ASK execution semantics as V4.

After fill, measure:
- 60-minute path;
- 120-minute path;
- capped at 11:30 New York for the 120-minute analysis.

BUY:
- favorable/target on BID;
- adverse/stop on BID.

SELL:
- favorable/target on ASK;
- adverse/stop on ASK.

Conservative ordering:
- if the fill bar also touches stop, count immediate stop;
- ignore a fill-bar target touch because ordering relative to the limit fill is unknown;
- after the fill bar, if target and stop are both touched in one M1 bar, count stop first.

Time exit:
- executable opposite-side close at the horizon.

Report NET_F10 using $0.10 round-trip friction.

No break-even, trailing, partial close, manual candle-close exit, add-on, or re-entry is simulated.

These management omissions are intentional so V5 tests entry/initial-geometry quality before adding discretionary management.

## Candidate spacing / de-clustering

At most one pending setup per direction at a time.

When a pending M15 setup has no valid M5/M3 trigger:
- block same-direction reconsideration until its 30-minute pending window expires.

When an entry order is placed but does not fill:
- block same-direction reconsideration until the order expiry.

After a filled trade:
- suppress further same-direction entries for that New York date.

Maximum:
- first filled BUY per NY date;
- first filled SELL per NY date;
- at most 2 filled trades per NY date.

This preserves the low-frequency/de-clustered research design and prevents repeated counting of the same liquidity event.

## Required funnel diagnostics

Report overall and by year:

1. NY dates observed
2. directionally eligible session-days
3. M15 liquidity sweeps
4. sweeps overlapping active H1 FVG
5. M15 close-back confirmations
6. M5 one-close MSS events
7. M3 one-close MSS events
8. valid M5/M3 MSS + displacement FVG triggers
9. triggers selected from M5
10. triggers selected from M3
11. valid final HTF structural target exists
12. target distance >= $5
13. target/structural-stop RR >= 3
14. proximal-edge limit orders placed
15. proximal-edge limit orders filled
16. valid structural stops
17. count with intermediate session liquidity before final target

## Required path/economic diagnostics

Overall, by side, and by year:

- filled-trade count;
- M5 vs M3 trigger count;
- entry wait-to-fill median/p75;
- structural stop distance median/p25/p75;
- final target distance median/p25/p75;
- structural target/stop RR median/p25/p75;
- MFE60 / MAE60 mean/median;
- MFE120 / MAE120 mean/median;
- median MFE60 / median MAE60;
- median MFE120 / median MAE120;
- +$3 rate at 120m;
- +$5 rate at 120m;
- +$7 rate at 120m;
- +$5-before-$3 rate at 120m;
- final-target-before-stop rate at 60m and 120m;
- mean NET_F10 R at 60m and 120m;
- 120m profit factor;
- yearly mean NET_F10 R;
- yearly target-before-stop rate.

## TRAIN-only advancement gate

To avoid tuning the gate after V4, V5 reuses the substantive V4 robustness requirements.

V5 may justify a separately preregistered 2022 validation experiment only if ALL entry-population gates pass:

1. >= 180 filled trades total;
2. >= 20 filled trades in every year 2016-2021;
3. overall median MFE120 / median MAE120 >= 1.10;
4. median of yearly (median MFE120 - median MAE120) > 0;
5. positive yearly path edge in at least 4 of 6 years;
6. overall +$5-before-$3 rate >= 35%.

AND the single structural-stop policy satisfies ALL:

7. overall mean NET_F10 R at 120m > 0;
8. 120m profit factor > 1;
9. positive yearly mean NET_F10 R in at least 4 of 6 years;
10. no single year mean NET_F10 R < -0.35R.

If the entry-population gates fail:
- stop V5;
- do not access 2022.

If entry-population gates pass but the structural-stop policy fails:
- do not access 2022;
- conclude that source-fidelity entry coverage improved but execution geometry remains economically unresolved.

## Governance

Do not after results:
- change the frozen V4 upstream logic;
- replace M5/M3 with M1;
- require or remove additional MSS closes;
- make FVG optional;
- switch to direct market entry;
- change proximal edge to midpoint or another fraction;
- add OB logic;
- change final-target families;
- change the $5 gate;
- change the 1:3 RR gate;
- add a stop cap;
- add micro stops;
- add break-even/partials/trailing;
- add DXY, yields, news-event data, or other exogenous context;
- access 2022-2025.

Any such change requires a separate diagnosis or preregistration.

Negative results are admissible.

## Interpretation boundary

Passing V5 would not prove Badar's method profitable.

It would show only that a stricter source-fidelity translation of the taught A+ sequence creates a sufficiently large and stable TRAIN sample with acceptable executable path/economic geometry to justify one separately frozen 2022 validation test.

Failure would mean at least one of:
- the taught A+ source sequence remains too rare/mechanically brittle on the available M1 history;
- the retained V4 upstream location gate still removes too much discretionary context;
- important discretionary information (OB selection, candle quality, exact liquidity map, news handling, DXY/rates, manual risk management) is not captured mechanically.

2022-2025 remain sealed.
