# Root-Reset V4 — Badar-Core TRAIN-Only Entry Experiment

Status: FROZEN BEFORE EMPIRICAL RESULTS

## Purpose

Root-Reset V3 showed that three generic price-only pattern families were adverse-dominant in every TRAIN year.

The owner has now explicitly admitted:
`alisufyan-ai7/unpack-human-trading-strategies-claude`
as a research source.

V4 tests one narrow, source-grounded hypothesis extracted from Badar Tanveer's source layer:

> higher-timeframe directional context + meaningful session liquidity + H1 FVG location +
> liquidity sweep/trap + close-based confirmation + lower-timeframe MSS/displacement +
> retracement into the displacement FVG may create a materially better XAUUSD entry population.

This is NOT a test of all of Badar's teaching.
It is NOT based on Claude's derived rulebook.

## Source boundary

Badar source repository:
`alisufyan-ai7/unpack-human-trading-strategies-claude`

Allowed source-layer evidence:
- PLAYBOOK.md
- LIVE_TRADING_OBSERVATIONS.md
- dataset/live_trades.csv
- notes/**
- transcripts/**

Anything under `derived/` is excluded from defining V4.

Source-supported principles used:
- H1 is a key direction/POI timeframe;
- trade from meaningful liquidity/location rather than mid-range;
- session highs/lows are liquidity;
- sweep/trap should precede entry;
- candle closes matter more than wicks for structure confirmation;
- M15/M30 can gate lower-timeframe execution;
- MSS/displacement followed by FVG retracement is a recurring entry sequence;
- stop is structurally beyond sweep in the taught method;
- very tight micro execution stops also appear in live trading;
- structural liquidity, not an arbitrary fixed dollar amount, is the natural target.

Operational details below are this project's deterministic translation where Badar did not specify a unique numerical rule.

## Data boundary

Use only synchronized Dukascopy XAUUSD BID/ASK M1:
- 2016
- 2017
- 2018
- 2019
- 2020
- 2021

Do NOT download, inspect, or access:
- 2022 VALIDATION
- 2023-2024 DEVELOPMENT_TEST
- 2025 FINAL_OOS

No ML model is trained in V4.

## Timezone/session definitions

Use IANA timezone rules.

Tokyo anchor:
- 00:00 UTC.

London open:
- 08:00 Europe/London local time.

New York open:
- 08:00 America/New_York local time.

For each NY trading day:
- Asian range = 00:00 UTC through the London open, excluding the London-open minute;
- London range = London open through NY open, excluding the NY-open minute;
- both ranges are frozen at the NY open.

Execution window:
- 09:00 through 10:30 America/New_York local time.

Fixed news-time exclusion:
- do not accept a confirmation bar ending from 09:55 through 10:10 New York time.
- This is a conservative time-only exclusion for common 10:00 US releases; V4 does not yet use a historical event calendar.

Rationale:
Badar teaches the first 2-3 hours after session opens as active windows, while the admitted live observations show most NY live entries occurred 09:00-10:30 NY.

No candidate outside this window.

Session-range completeness:
- Asian and London ranges each require at least 95% of their expected M1 minutes;
- no internal synchronized-data gap may exceed 5 minutes;
- otherwise that NY date is excluded.

## Causal bars

Derive completed:
- D1
- H4
- H1
- M15
- M5

from synchronized BID M1 for structure/location.

Executable entries and adverse/favorable paths use BID/ASK correctly.

No incomplete higher-timeframe candle may be used.

Deterministic bar alignment/completeness:
- M5/M15/H1 bars are UTC-clock aligned and require exactly 5/15/60 synchronized M1 rows;
- H4 bars are UTC-clock aligned at 00:00/04:00/08:00/12:00/16:00/20:00 and require four complete H1 bars;
- D1 bars use UTC calendar days and require at least 20 complete H1 bars;
- an incomplete bar is omitted from structure/FVG logic;
- these UTC D1/H4 alignments are project operationalizations, not attributed to Badar.

## Higher-timeframe directional context

Use a deterministic two-close BOS state separately on D1, H4, and H1.

### Confirmed swing

For each timeframe:
- a swing high is a bar whose high is strictly greater than the highs of the two bars immediately before it and greater than or equal to the highs of the two bars immediately after it;
- a swing low is symmetric;
- the swing becomes known only after the two right-side bars have completed.

### BOS state

Bullish BOS:
- two consecutive completed closes above the most recent confirmed swing high.

Bearish BOS:
- two consecutive completed closes below the most recent confirmed swing low.

State at decision time:
- direction of the most recent bullish or bearish BOS event.

### V4 directional gate

BUY only if:
- H1 state = bullish;
- H4 state != bearish;
- D1 state != bearish.

SELL only if:
- H1 state = bearish;
- H4 state != bullish;
- D1 state != bullish.

This intentionally gives H1 priority while preventing clear H4/D1 opposition.

If H1 state is unknown:
- no candidate.

## H1 FVG point of interest

Use completed H1 bars only.

Bullish H1 FVG:
- high[t-2] < low[t];
- zone = [high[t-2], low[t]].

Bearish H1 FVG:
- low[t-2] > high[t];
- zone = [high[t], low[t-2]].

A FVG is active from completion of bar t.

Invalidation:
- bullish FVG invalid if a later completed H1 close is below the lower zone boundary;
- bearish FVG invalid if a later completed H1 close is above the upper zone boundary.

Age limit:
- only FVGs created within the preceding 72 completed H1 hours are eligible.

If multiple eligible FVGs overlap the sweep:
- use the most recently created FVG.

V4 excludes order blocks because their source definitions are less mechanically unique.
This is a deliberate narrowing, not a claim that Badar ignores OBs.

## Liquidity pools

V4 uses only frozen session liquidity:
- Asian high
- Asian low
- London high
- London low

PDH/PDL are excluded in V4 because the admitted source explicitly notes ambiguity in the day-boundary convention.

### Directional liquidity

BUY candidate:
- sweep of Asian low OR London low.

SELL candidate:
- sweep of Asian high OR London high.

If both same-direction pools are swept in the same event:
- record both;
- use the more extreme swept level only for descriptive reporting.

## M15 sweep/trap confirmation

ATR15_PROXY:
- mean true range of the four most recent completed M15 BID bars.

Require ATR15_PROXY > 0.

Operational sweep buffer:
- 0.05 * ATR15_PROXY.

BUY confirmation M15 bar:
- low < liquidity_level - 0.05*ATR15_PROXY;
- close > liquidity_level;
- bar overlaps an active bullish H1 FVG:
  bar low <= FVG upper boundary AND bar high >= FVG lower boundary.

SELL:
- high > liquidity_level + 0.05*ATR15_PROXY;
- close < liquidity_level;
- overlaps an active bearish H1 FVG.

The M15 close is the first confirmation gate.
No entry occurs yet.

One pending setup per direction at a time.

Pending setup expires after 30 minutes if no valid M5 MSS is confirmed.

## M5 MSS / displacement

After the M15 sweep confirmation, inspect completed M5 bars only.

### Pre-sweep reference swing

At the moment of M15 confirmation:
- BUY reference = most recent confirmed M5 swing high;
- SELL reference = most recent confirmed M5 swing low;
- same 2-left / 2-right causal swing rule.

### MSS confirmation

BUY:
- two consecutive completed M5 closes above the frozen reference swing high.

SELL:
- two consecutive completed M5 closes below the frozen reference swing low.

The second close completes the MSS.

No M1-only MSS is accepted in V4.

## Displacement FVG

A valid M5 FVG must be created by the MSS leg.

BUY:
- among the second MSS-close bar and the two immediately preceding M5 bars,
  there must be a bullish 3-bar FVG:
  high[k-2] < low[k].

SELL:
- bearish:
  low[k-2] > high[k].

If more than one exists:
- use the most recent.

If none exists:
- reject the setup.

## Entry

Entry is a resting limit at the midpoint of the selected M5 displacement FVG.

BUY:
- limit uses executable ASK;
- fill when a future ASK low <= limit.

SELL:
- limit uses executable BID;
- fill when a future BID high >= limit.

Entry order becomes active immediately after the M5 MSS confirmation bar closes.

Expiry:
- 30 minutes after MSS confirmation;
- or 10:30 NY;
- whichever comes first.

No chasing:
- if not filled by expiry, candidate is missed/unfilled.

## Target

Primary structural target = nearest opposing frozen session-liquidity level beyond the entry.

BUY:
- candidate levels = Asian high and London high strictly above entry;
- choose the lowest qualifying level.

SELL:
- candidate levels = Asian low and London low strictly below entry;
- choose the highest qualifying level.

If no opposing frozen session level lies beyond entry:
- reject.

Owner-opportunity gate:
- structural target distance must be >= $5.00.

This preserves the project's objective while allowing target distance to be structural rather than fixed.

## Stop definitions — measured, not optimized

V4 measures two fixed hypotheses.

### S-STRUCT — taught structural invalidation

BUY:
- stop = sweep extreme low - 0.05*ATR15_PROXY.

SELL:
- stop = maximum executable ASK high during the confirming M15 sweep interval + 0.05*ATR15_PROXY.

BUY structural sweep extreme uses BID low because a long stop liquidates on BID.
SELL uses ASK high because a short stop liquidates on ASK.

### S-MICRO — live-style micro execution invalidation

BUY:
- stop = minimum BID low across the two completed M5 bars that form the required two-close MSS confirmation
  - 0.05*ATR15_PROXY.

SELL:
- stop = maximum ASK high across those same two M5 confirmation bars
  + 0.05*ATR15_PROXY.

The M5 displacement FVG must be created no later than the second MSS-close bar; the micro stop therefore uses information fully known at MSS completion.

If either stop is on the wrong side of entry or distance <= 0:
- that stop hypothesis is invalid for the candidate.

No stop-distance cap.

No stop is widened.

## Post-entry path

Measure executable paths for:
- 60 minutes;
- 120 minutes;
- or until 11:30 NY, whichever is earliest for 120-minute analysis.

BUY:
- favorable on future BID highs;
- adverse on future BID lows.

SELL:
- favorable on future ASK lows;
- adverse on future ASK highs.

Conservative fill-bar and same-bar ordering:
- the limit fill is detected from the first executable M1 bar touching the limit;
- if that fill bar also touches the stop, count an immediate stop;
- a target touch in the fill bar is ignored because its ordering relative to the limit fill is unknowable;
- ordinary post-fill path measurement begins with the next M1 bar;
- on later bars, if target and stop are both touched in the same M1 bar, count stop first.

Report separately for S-STRUCT and S-MICRO:
- target-before-stop;
- stop-before-target;
- unresolved;
- realized gross R at target/stop/time exit;
- NET_F10 using $0.10 round-trip friction.

Time exit:
- executable opposite-side close at horizon.

Post-entry path validity:
- every analyzed M1 minute must be present in the synchronized BID/ASK series;
- any >1-minute gap before the relevant horizon invalidates that horizon for the candidate.

No break-even, trailing, partials, re-entry, or discretionary early exit in V4.

## De-clustering / daily cap

At most:
- first qualifying BUY setup per NY date;
- first qualifying SELL setup per NY date;
- maximum 2 filled trades per NY date.

A pending or unfilled setup does not block the opposite direction.

After a filled trade:
- suppress further same-direction setups for that NY date.

## Required funnel diagnostics

For each year and overall report counts at every stage:

1. NY dates observed
2. directionally eligible session-days
3. M15 liquidity sweeps
4. sweeps overlapping active H1 FVG
5. M15 close-back confirmations
6. M5 MSS confirmations
7. MSS with displacement FVG
8. valid structural target exists
9. target distance >= $5
10. limit orders placed
11. limit orders filled
12. S-STRUCT valid
13. S-MICRO valid

This funnel is mandatory so a negative result identifies the bottleneck.

## Required path diagnostics

For filled entries overall, by BUY/SELL, and by year:

- count
- structural target distance mean/median/p25/p75
- MFE60 / MAE60 mean/median
- MFE120 / MAE120 mean/median
- median MFE60 / median MAE60
- median MFE120 / median MAE120
- +$3 rate
- +$5 rate
- +$7 rate
- +$5-before-$3 rate

For each stop hypothesis:
- median stop distance
- median structural target / stop RR
- target-before-stop rate at 60m
- target-before-stop rate at 120m
- mean NET_F10 R at 60m
- mean NET_F10 R at 120m
- profit factor at 120m
- yearly mean NET_F10 R
- yearly target-before-stop rate

## TRAIN-only advancement gate

V4 may justify a separately preregistered 2022 validation experiment only if the ENTRY POPULATION satisfies ALL:

1. >= 180 filled trades total;
2. >= 20 filled trades in every year 2016-2021;
3. overall median MFE120 / median MAE120 >= 1.10;
4. median of yearly (median MFE120 - median MAE120) > 0;
5. positive yearly path edge in at least 4 of 6 years;
6. overall +$5-before-$3 rate >= 35%.

AND at least one stop hypothesis satisfies ALL:

7. overall mean NET_F10 R at 120m > 0;
8. 120m profit factor > 1;
9. positive yearly mean NET_F10 R in at least 4 of 6 years;
10. no single year mean NET_F10 R < -0.35R.

Stop-hypothesis handling:
- S-STRUCT is the source-faithful primary hypothesis.
- S-MICRO is a separately reported live-execution hypothesis.
- If both pass, BOTH remain candidates; no winner is selected on TRAIN.
- Any later 2022 validation must preregister how multiplicity is handled before access.

If entry-population gates fail:
- stop V4;
- do not access 2022.

If entry-population gates pass but neither stop hypothesis passes:
- do not access 2022;
- conclude entry quality improved but execution geometry remains unresolved.

## Governance

Do not:
- use Claude-derived rulebook parameters;
- add OB logic after seeing results;
- change session window;
- change sweep buffer;
- change FVG age;
- change MSS rule;
- change limit-entry price;
- change target selection;
- change $5 opportunity gate;
- add news trades;
- add DXY after results;
- add counter-trend trades;
- tune stops;
- access 2022-2025.

Negative results are admissible.

## Interpretation boundary

Passing V4 would not prove Badar's method profitable.
It would only show that this source-grounded deterministic translation creates a materially better TRAIN entry population than the previously failed generic setup families.

Failure would mean this deterministic translation does not capture a robust edge and would motivate either:
- timestamp-safe exogenous context (news/DXY/rates), or
- acknowledgement that important discretionary information in Badar's live process was not captured mechanically.
