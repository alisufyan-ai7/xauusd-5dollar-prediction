# Root-Reset V4 Badar-Core TRAIN Findings

Status: COMPLETE — NO FILLED TRADES

Source run:
36768684222

Artifact:
root-reset-v4-badar-core

Artifact digest:
sha256:eb72f8236c805f7e197ad2f0956db4e7d61405d5f3c6199869a73d2897cc16bd

Scope:
- TRAIN 2016-2021 only
- no 2022 validation access
- no 2023-2024 access
- no 2025 access

## Result

V4 completed successfully but produced zero filled trades.

Therefore:
- the entry-population advancement gate failed;
- S-STRUCT did not pass;
- S-MICRO did not pass;
- no future 2022 validation is authorized from V4.

## Funnel

Across 2016-2021:

- NY dates observed: 1,508
- directionally eligible session-days: 523
- M15 liquidity sweeps: 627
- sweeps overlapping active H1 FVG: 364
- M15 close-back confirmations: 135
- M5 MSS confirmations: 24
- MSS with displacement FVG: 16
- valid structural target: 16
- structural target distance >= $5: 3
- limit orders placed: 3
- limit orders filled: 0

## Yearly MSS / FVG counts

2016:
- M5 MSS: 6
- MSS + displacement FVG: 4

2017:
- M5 MSS: 3
- MSS + displacement FVG: 2

2018:
- M5 MSS: 2
- MSS + displacement FVG: 0

2019:
- M5 MSS: 7
- MSS + displacement FVG: 4
- target >= $5: 1
- order placed: 1

2020:
- M5 MSS: 4
- MSS + displacement FVG: 4
- target >= $5: 2
- orders placed: 2

2021:
- M5 MSS: 2
- MSS + displacement FVG: 2

## Interpretation

This is not evidence that Badar's method is economically negative.

The deterministic V4 translation became too restrictive before entry.

The main bottlenecks were:

1. The frozen two-close M5 MSS requirement after an M15 sweep reduced 135 confirmed M15 traps to only 24 MSS events.

2. Requiring the same MSS leg to contain a mechanically defined M5 displacement FVG reduced this to 16.

3. Requiring the nearest opposing frozen Asian/London liquidity target to be at least $5 reduced 16 candidates to only 3.

4. None of those three midpoint limit orders retraced far enough to fill before expiry.

Thus V4 tested a very narrow subset of Badar's process and did not generate enough observations to evaluate path quality or stop economics.

## What should not be concluded

Do not conclude:
- Badar-Core has negative expectancy;
- S-STRUCT is worse than S-MICRO;
- the source method failed;
- $5 movement is absent after Badar-style setups.

There were no filled trades, so none of those economic questions were actually tested.

## Root-cause implication

The source material shows Badar frequently uses:
- M15/M30 as a context/confirmation gate;
- M1/M3/M5 for execution;
- both direct close entries and FVG retracement entries;
- session liquidity plus higher-timeframe location;
- structural targets that are not necessarily limited to the same day's frozen Asian/London opposite boundary.

V4 intentionally excluded much of that discretion.

The next admissible step should therefore be a TRAIN-only translation diagnosis, not an immediate profitability experiment.

That diagnosis should quantify, without changing trading rules:
- how often one-close versus two-close M5 MSS occurs after V4 M15 confirmation;
- how often M3/M1 structure shift exists when M5 two-close MSS does not;
- how often direct close entry would occur versus midpoint-FVG retracement fill;
- distribution of distances to broader structural liquidity (PDH/PDL, recent H1/H4 swing liquidity) compared with frozen Asian/London opposite liquidity;
- which V4 gate is responsible for excluding source-observed live-style cases.

No 2022-2025 access.

## Governance

Do not loosen V4 gates post hoc and rerun it as if unchanged.

Any V5 must be separately preregistered after a TRAIN-only translation diagnosis.

2022-2025 remain untouched.
