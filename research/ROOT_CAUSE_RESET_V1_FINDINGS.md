# Root-Cause Reset V1 Findings

Status: COMPLETE — STOPPED AT VALIDATION GATE

Source run: 36629144070

Artifact: root-reset-event-driven-v1

Artifact digest:
sha256:6977df5778c25723952ca67f4e2ad5e18470e9c6598b705331dfcbf393d7024a

FINAL_OOS 2025 was not accessed.

DEVELOPMENT_TEST 2023-2024 was not accessed.

## Core result

The reset stopped at VALIDATION 2022 because no preregistered opportunity threshold qualified.

Selected opportunity threshold:
- none

Thresholds tested:
- 0.50
- 0.60
- 0.70
- 0.80

For every threshold:
- raw qualifying trades = 0
- executed trades = 0

Therefore the workflow correctly stopped before DEVELOPMENT_TEST.

## Event sampling

TRAIN 2016-2021 event candidates:
- 51,185

VALIDATION 2022 event candidates:
- 8,957

This confirms the event-driven sampler produced a substantial candidate population and did not collapse by itself.

## Opportunity-5 ranking

BUY validation:
- events: 4,448
- realized OPPORTUNITY_5 rate: 12.88%
- ROC-AUC: 0.7728
- PR-AUC: 0.3421
- Brier: 0.0981

SELL validation:
- events: 4,509
- realized OPPORTUNITY_5 rate: 12.77%
- ROC-AUC: 0.7592
- PR-AUC: 0.3316
- Brier: 0.0994

Interpretation:
the event-driven $5-attainability model has meaningful ranking ability. The reset did not fail because event sampling or $5 attainability was completely unlearnable.

## Dynamic stop distribution

BUY:
- stop-admissible events: 2,191 / 4,448
- median initial stop: $3.3615
- p10: $2.0411
- p90: $6.6873

SELL:
- stop-admissible events: 2,204 / 4,509
- median initial stop: $3.3694
- p10: $2.0520
- p90: $6.6476

The frozen maximum admissible stop was $3.3333.

Therefore approximately half of validation events were rejected by the reward/risk stop constraint alone.

This is economically coherent: many continuation events require more than about $3.33 of structural/volatility room against a minimum $5 opportunity.

## Excursion distribution

BUY:
- MFE60 median: $1.48
- MFE60 p90: $5.819
- MAE60 median: $2.3095
- MAE60 p90: $6.2907

SELL:
- MFE60 median: $1.519
- MFE60 p90: $5.8362
- MAE60 median: $2.2700
- MAE60 p90: $6.2052

Only about 12.8% of events achieve at least $5 MFE within 60 minutes.

This confirms that $5 opportunities are real but sparse.

## Early-damage model

BUY:
- realized EARLY_DAMAGE rate: 0.629%
- ROC-AUC: 0.7185
- PR-AUC: 0.0146
- validation Q50 risk cutoff: 0.003118

SELL:
- realized EARLY_DAMAGE rate: 0.665%
- ROC-AUC: 0.5533
- PR-AUC: 0.0142
- validation Q50 risk cutoff: 0.003137

Interpretation:
the redesigned EARLY_DAMAGE event is too rare to be a useful primary veto, especially for SELL. Its median-probability cutoff is extremely small and may overconstrain the entry gate.

This differs from the prior fixed-$3 early-failure target, which had a much higher and more learnable event rate.

## Primary failure mechanism

The reset did not fail because the event-driven opportunity model had no signal.

It failed because the preregistered combined gate was too restrictive:

1. OPPORTUNITY_5 base rate is only ~12.8%, so absolute probability thresholds beginning at 0.50 are likely too high for a reasonably calibrated classifier;
2. roughly half of candidates fail the stop-admissibility constraint;
3. the new EARLY_DAMAGE target is extremely rare (~0.6%), producing a very low Q50 risk cutoff;
4. the intersection of all three gates produced zero qualifying validation trades.

This is a gate-design failure, not evidence that event-driven $5 opportunity ranking is useless.

## Governance conclusion

Do not:
- lower the 0.50 threshold inside V1;
- loosen the stop cap inside V1;
- remove the risk veto inside V1;
- access 2023-2024 post hoc;
- access 2025.

V1 is closed as preregistered.

## Next admissible step

Before any V2 economics test, run a VALIDATION-ONLY gate-overlap diagnosis that reports:

- OPPORTUNITY_5 predicted-probability quantiles;
- counts surviving stop-admissibility alone;
- counts surviving opportunity threshold alone;
- counts surviving risk veto alone;
- pairwise and three-way gate intersections;
- realized OPPORTUNITY_5 rate and MFE/MAE by opportunity-score decile;
- same diagnostics separately for BUY and SELL.

No 2023-2024 access is required.

The purpose is to redesign the entry gate from measured validation behavior without pretending V1 passed.

2025 remains sealed.
