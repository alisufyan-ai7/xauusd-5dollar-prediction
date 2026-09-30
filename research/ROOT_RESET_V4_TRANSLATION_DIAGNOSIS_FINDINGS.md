# Root-Reset V4 Translation Diagnosis — Findings

Status: completed on TRAIN only.

## Scope and governance

This diagnosis is the execution of:

- `research/ROOT_RESET_V4_TRANSLATION_DIAGNOSIS.md`
- `scripts/diagnose_root_reset_v4_translation.py`

Only 2016-2021 TRAIN data were accessed.

- 2022 validation: **not accessed**
- 2023-2024 development test: **not accessed**
- 2025 final OOS: **not accessed**

No profitability policy is selected here. No P&L optimization, threshold search, or sealed-period access was performed.

The Badar-source provenance boundary remains unchanged:

- material outside `derived/` in `alisufyan-ai7/unpack-human-trading-strategies-claude` is source-layer evidence of what Badar said/showed, subject to transcript/observation uncertainty;
- material inside `derived/` is Claude interpretation only and is not attributed to Badar.

## Final accepted run

Accepted historical run:

- run: **36779728544**
- workflow: `historical-data-integrity`
- branch: `research/root-reset-v4-badar-core`
- head: `2e7f90df1f14e54feaaccf99a02d095cdf00fe17`
- artifact: `root-reset-v4-translation-diagnosis`
- artifact digest: `sha256:5117a388941a535721fb2fe314df78f1a42e9ba96d8a73b0920a81288ec0bad2`

The artifact contains:

- `translation-diagnosis.json`
- `badar-core-train.json`
- `translation-data-sha256.txt`

A same-snapshot reproducibility guard ran the frozen V4 reference and the diagnosis sequentially on the same synchronized TRAIN files and asserted that their M15 close-back population was identical.

The frozen V4 reference reproduced the original V4 funnel exactly:

- 1,508 NY dates
- 627 M15 liquidity sweeps
- 364 sweeps overlapping active H1 FVG
- 135 M15 close-back confirmations
- 24 M5 two-close MSS
- 16 MSS + displacement FVG
- 16 valid structural targets
- 3 session-liquidity targets >= $5
- 3 midpoint limit orders
- 0 fills

The accepted run's raw provider SHA-256 identities also match the original V4 acquisition identities recorded by run 36768684222.

## Technical run history

The first diagnosis attempt, run **36772401002**, failed technically with:

`KeyError: 'mss_time'`

The cause was an adapter assumption: frozen V4 returns the M5 bar index `j` when a two-close MSS exists without a displacement FVG, but only returns `mss_time` when the FVG also exists. The diagnosis now derives the MSS timestamp from the already-returned `j` in that no-FVG case. This does not change the frozen two-close MSS rule.

A reporting-only correction was also made so the artifact emits the preregistered midpoint fill rate, median wait-to-fill, and direct-entry-without-midpoint-fill measurements.

An initial rerun also exposed that the diagnosis had omitted V4's candidate-spacing/blocking semantics, causing it to count later M15 confirmations that V4 would not have reconsidered while its frozen downstream attempt was active. That was corrected without changing any diagnosis alternative.

Some intermediate reruns reacquired a transiently different provider snapshot. Their scientific numbers are **not used**. The accepted run prevents this ambiguity by running frozen V4 and the diagnosis on the same files and asserting equality of the frozen M15 population.

## Frozen question 1 — one-close M5 vs V4 two-close M5

From the same 135 frozen M15 close-back confirmations:

| confirmation translation | count | share of 135 |
| --- | ---: | ---: |
| V4 two-close M5 MSS (C2) | 24 | 17.8% |
| one-close M5 MSS (C1) | 33 | 24.4% |

One-close M5 recovers **9** confirmations that the V4 two-close M5 translation misses.

This is a translation-coverage result only, not evidence that one-close M5 is economically superior.

## Frozen question 2 — M3/M1 recovery when M5 two-close misses

Counts from the same 135 M15 confirmations:

| confirmation translation | count | share of 135 |
| --- | ---: | ---: |
| one-close M3 (C3) | 47 | 34.8% |
| one-close M1 (C4) | 83 | 61.5% |

Among confirmations where V4 C2 is absent, **63** are recovered by at least one of M3 or M1.

That is:

- 63 / 135 = **46.7%** of the frozen M15 population;
- 63 / 111 = **56.8%** of the cases missed by V4's two-close M5 gate.

C3 and C4 overlap, so their raw counts must not be added.

This result is source-plausible: the admitted source layer documents M1 as Badar's most common observed execution timeframe, with M3/M5 also used for confirmation. It does not by itself select a V5 confirmation policy.

## Frozen question 3 — direct-close entry vs FVG-midpoint retracement

The diagnosis measures direct executable entry at the next M1 open after confirmation and, separately, whether a same-timeframe FVG exists and its midpoint fills within 30 minutes.

| confirmation | direct entries | FVG available | midpoint fills | fill rate given FVG | median wait to midpoint fill | direct exists but midpoint does not fill |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| C1 one-close M5 | 33 | 16 | 9 | 56.3% | 10.0 min | 24 / 33 = 72.7% |
| C2 V4 two-close M5 | 24 | 16 | 9 | 56.3% | 3.0 min | 15 / 24 = 62.5% |
| C3 one-close M3 | 47 | 19 | 10 | 52.6% | 3.0 min | 37 / 47 = 78.7% |
| C4 one-close M1 | 83 | 32 | 17 | 53.1% | 5.0 min | 66 / 83 = 79.5% |

For the exact V4 two-close confirmation population, a direct-close executable entry exists in all 24 C2 cases, while only 9 midpoint retracement fills occur among 16 cases that even form the required displacement FVG.

This explains an important translation loss: mandatory FVG formation plus midpoint retracement materially reduces source-plausible executable opportunities relative to a direct candle-close entry.

This does **not** mean direct entry is profitable or should be selected.

## Frozen question 4 — broader structural target availability

For C2 direct entries, session-only target availability at >= $5 is relatively sparse among the cases where each target exists:

| target family | n with target in direction | median distance | share >= $5 |
| --- | ---: | ---: | ---: |
| Asian opposite liquidity | 21 | $3.34 | 19.0% |
| London opposite liquidity | 23 | $3.31 | 21.7% |
| previous UTC-day high/low | 16 | $5.27 | 50.0% |
| H1 confirmed swing liquidity | 23 | $3.92 | 26.1% |
| H4 confirmed swing liquidity | 17 | $6.52 | 64.7% |

For **8 of 24 C2 direct entries (33.3%)**, all available Asian/London session targets are below $5 while at least one broader structural target from previous-day/H1/H4 liquidity is >= $5.

The same broader-target recovery measure is:

- C1: 8 / 33 = 24.2%
- C2: 8 / 24 = 33.3%
- C3: 13 / 47 = 27.7%
- C4: 13 / 83 = 15.7%

Therefore the V4 session-only target translation excludes some cases that have source-plausible broader liquidity >= $5.

No target family is selected as a profitability policy here.

## Frozen question 5 — which V4 translation gate removes the most source-plausible cases?

By absolute count after the frozen M15 close-back stage, the largest first-order loss is the **V4 two-close M5 MSS requirement**:

- 135 M15 confirmations -> 24 two-close M5 MSS
- **111 cases removed (82.2%)**

The diagnosis shows that 63 of those C2-missed cases have an M3 and/or M1 one-close confirmation.

Other severe later restrictions remain:

- 24 C2 MSS -> 16 displacement FVG: 8 removed
- 16 displacement-FVG cases -> 3 session targets >= $5 in frozen V4: 13 removed
- 3 frozen V4 midpoint orders -> 0 fills

The zero-fill outcome is therefore not attributable to one isolated gate. It is the cumulative result of:

1. coarse/two-close lower-timeframe confirmation,
2. mandatory displacement FVG plus midpoint retracement,
3. session-only structural targeting >= $5.

The **largest absolute population loss** is the two-close M5 confirmation gate, while the session-target and midpoint rules compound the restriction at the end of the funnel.

## Source-layer interpretation

The source layer supports treating these as translation-fidelity questions rather than arbitrary relaxations:

- `PLAYBOOK.md` documents H1 as the analysis pivot and M5/M3 execution, with M1/M2 refinement and use of M3 when M5 does not produce a clean execution structure.
- `LIVE_TRADING_OBSERVATIONS.md` documents M1 as the most common observed live execution timeframe and says market orders on a candle close were the default, while resting limits were also used and sometimes missed.
- observed live triggers include sweep/close-back followed by M1 close, retrace into hidden OB/FVG on 1-3m close, and strong M1 close entered directly.

These source observations do not imply that every observed discretionary variant should be made mechanical.

## Scientific conclusion

D-059 is strengthened rather than reversed.

V4's zero fills were primarily a **translation-coverage problem before economic evaluation**. The diagnosis identifies three source-fidelity mismatches with material coverage effects:

- the V4 two-close M5 confirmation is much narrower than lower-timeframe execution observed in the admitted source layer;
- mandatory FVG-midpoint retracement loses many otherwise executable close-based entries;
- session-only targets omit some broader source-plausible liquidity that is >= $5.

The diagnosis does **not** establish profitability for C1, C3, C4, direct entry, midpoint entry, or any broader target family.

## Next scientific step

Do **not** choose whichever diagnostic alternative produced the most candidates.

Before any V5 economic experiment, define one source-grounded V5 translation from the admitted source layer using evidence strength and observed execution practice rather than diagnostic outcome counts, then preregister it on TRAIN only.

The V5 specification should explicitly resolve:

- confirmation timeframe/close rule;
- whether FVG/OB is mandatory confirmation, an entry location, or optional confluence;
- direct-close versus retracement entry;
- structural target hierarchy across session, previous-day, H1 and H4 liquidity;
- deterministic stop placement;
- one-attempt/candidate-spacing semantics.

Only after that specification is frozen should a new TRAIN economic run be executed.

2022-2025 remain sealed.
