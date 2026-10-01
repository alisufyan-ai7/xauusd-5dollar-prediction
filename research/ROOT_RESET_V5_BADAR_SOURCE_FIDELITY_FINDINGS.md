# Root-Reset V5 Badar A+ Source-Fidelity — Findings

Status: completed on TRAIN only.

## Governance

Frozen specification:
- `research/ROOT_RESET_V5_BADAR_SOURCE_FIDELITY_PREREGISTRATION.md`

Implementation:
- `scripts/root_reset_v5_badar_source_fidelity.py`

Accepted historical run:
- run: **36783834169**
- workflow: `historical-data-integrity`
- branch: `research/root-reset-v5-badar-source-fidelity`
- head: `d16824615ffa544979c401dfbddefa733701e4f6`
- artifact: `root-reset-v5-badar-source-fidelity`
- artifact digest: `sha256:0c20102adbc73fdde9d3b3c682c195e91cad27ae72f520ea2876c5374753557b`

Only 2016-2021 TRAIN data were accessed.

- 2022 validation: **not accessed**
- 2023-2024 development test: **not accessed**
- 2025 final OOS: **not accessed**

The artifact preserves raw and synchronized SHA-256 identities for the exact TRAIN snapshot.

No post-hoc threshold search or policy substitution was performed.

## Frozen V5 result

Funnel:

- 1,546 NY dates observed
- 541 directionally eligible session-days
- 656 M15 liquidity sweeps
- 369 sweeps overlapping an active H1 FVG
- 137 M15 close-back confirmations
- 32 one-close M5 MSS observations
- 47 one-close M3 MSS observations
- 39 causal M5/M3 MSS + displacement-FVG triggers
- 4 selected M5 triggers
- 35 selected M3 triggers
- 39 valid structural stops
- 39 with a causally known final HTF target
- 21 with structural target distance >= $5
- 9 with target/structural-stop RR >= 3
- 9 proximal-edge limit orders
- 6 fills

All 6 filled trades were triggered on M3.

## Advancement result

The frozen advancement result is:

- entry population pass: **FALSE**
- structural stop pass: **FALSE**
- eligible for future 2022 preregistration: **FALSE**

Therefore V5 stops at TRAIN.

2022 remains sealed.

## Important design finding — the count gate was unreachable upstream

V5 reused V4's requirement of at least **180 filled trades** to advance.

But the unchanged upstream logic produced only **137 M15 close-back confirmations** across the entire six-year TRAIN period.

Therefore, even if every M15 confirmation had converted into an MSS, FVG, qualifying target, qualifying RR, order and fill, V5 still could not have reached 180 filled trades.

The actual source-fidelity lower-timeframe trigger population was smaller still:

- 137 M15 close-backs
- 39 valid M5/M3 MSS + displacement-FVG triggers

Thus no downstream change to:
- target hierarchy,
- RR threshold,
- FVG entry price,
- order expiry,
- or fill rule

could make the current V5 formulation satisfy the frozen 180-trade count gate.

This is a research-design incompatibility between the retained V4 upstream sampler and the reused advancement sample-size requirement.

The appropriate response is **not** to lower the gate post hoc.

## Economic/path evidence — descriptive only because n=6

Overall filled sample:

- n = **6**
- median MFE120 = **$2.60**
- median MAE120 = **$2.97**
- median MFE120 / median MAE120 = **0.876**
- +$5 rate by 120m = **16.7%**
- +$5-before-$3 rate = **16.7%**
- final-target-before-stop rate = **0%**
- 120m mean NET_F10 R = **+0.063R**
- 120m profit factor = **1.084**

These economic aggregates must not be interpreted as evidence of profitability because the sample contains only six trades and is extremely unstable.

The positive mean NET_F10 R is driven by a tiny number of time-exit outcomes while no trade reached the selected final structural target before stop.

By side:

BUY:
- n = 2
- median MFE120 / MAE120 = 3.11
- +$5-before-$3 = 50%

SELL:
- n = 4
- median MFE120 / MAE120 = 0.73
- +$5-before-$3 = 0%

This side split is too small for policy selection and must not be used to choose BUY-only or another post-hoc branch.

## Where the V5 funnel still collapses

The dominant scarcity is already present before entry:

- 137 M15 close-backs -> 39 source-valid M5/M3 MSS + FVG triggers
- 39 triggers -> 21 targets >= $5
- 21 -> 9 target/stop RR >= 3
- 9 orders -> 6 fills

The M3 fallback materially dominates the selected trigger population:

- M3 selected: 35 / 39
- M5 selected: 4 / 39

This is descriptive source-fidelity evidence only.

## Scientific interpretation

V5 resolves several V4 translation issues in a source-grounded way, but the taught A+ sequence remains too sparse under the retained V4 upstream location sampler to create an economically testable population.

The key issue is no longer the midpoint-entry artifact that caused V4 zero fills.

The deeper issue is that the retained upstream condition:

`H1-led direction -> frozen session liquidity -> active H1 FVG -> M15 sweep -> M15 close-back`

is substantially narrower than Badar's source-layer concept of a **marked liquidity/location zone**.

The admitted source layer allows meaningful location to include, depending on setup:
- session highs/lows;
- previous-day high/low;
- H4 swing liquidity;
- H1/H4/D1 OB/FVG/breaker areas;
- other explicitly mapped liquidity pools.

V4/V5 mechanically require a session-liquidity sweep overlapping an active H1 FVG before lower-timeframe confirmation.

That conjunction is a project narrowing, not a complete representation of Badar's source-layer location map.

## Next scientific step

Do **not**:
- lower the 180-trade gate after seeing V5;
- remove the $5 or 1:3 requirements merely to obtain more trades;
- switch to M1/direct-close because the V4 diagnosis showed more candidates;
- tune entry expiry or FVG fractions;
- open 2022.

The next admissible step is a **TRAIN-only source-location coverage audit** before any V6 economic experiment.

Purpose:
determine whether the upstream V4/V5 location sampler itself is the main reason the source-taught A+ setup is too rare.

The audit should keep the lower-timeframe source-fidelity sequence descriptive and compare source-supported **location/liquidity families** without choosing a profitability winner.

At minimum measure causal coverage for:
- session liquidity;
- PDH/PDL using an explicitly documented project day boundary;
- confirmed H4 swing liquidity;
- active H1/H4 FVG location;
- deterministic OB/breaker representations only if their source definition can be frozen without arbitrary tuning.

Questions:
1. How many candidate sweeps/confirmations exist for each source-supported location family?
2. How much overlap exists between families?
3. Is the V4/V5 mandatory `session sweep AND H1 FVG overlap` conjunction responsible for most source-plausible opportunity loss?
4. Does a source-faithful union/hierarchy yield enough TRAIN observations to support a future economic experiment without lowering robustness gates?
5. Which concepts cannot be uniquely mechanized and should remain explicitly excluded rather than tuned?

This audit is diagnostic only:
- no P&L policy selection;
- no 2022-2025 access.

Only after that audit should a separately frozen V6 formulation be considered.

2022-2025 remain sealed.
