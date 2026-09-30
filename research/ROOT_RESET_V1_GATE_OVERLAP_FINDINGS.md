# Root-Reset V1 Gate-Overlap Diagnosis Findings

Status: COMPLETE

Source run: 36687708188

Artifact:
root-reset-v1-gate-overlap-diagnosis

Artifact digest:
sha256:36042e68550ed055ee20067703c33efffeafbf10ad8075e84ce6ea71ca405a22

Scope:
- TRAIN 2016-2021 used for fitting;
- VALIDATION 2022 used for diagnosis;
- DEVELOPMENT_TEST 2023-2024 NOT accessed;
- FINAL_OOS 2025 NOT accessed.

## Core finding

The dominant V1 bottleneck is the interaction between the $5-opportunity score and the dynamic-stop admissibility rule.

Higher OPPORTUNITY_5 scores identify larger favorable excursions, but those same events also have much larger adverse excursion / volatility and almost always require stops wider than the frozen $3.333 maximum.

Therefore the fixed minimum-$5 / fixed-1.5R admissibility cap systematically removes the very events most likely to achieve $5.

The early-damage veto is secondary.

## BUY

Validation events:
- 4,441

### Opportunity ranking

P(OPPORTUNITY_5):
- p50: 0.0814
- p75: 0.1504
- p90: 0.2721
- p95: 0.3537
- p99: 0.4956
- max: 0.6624

Realized OPPORTUNITY_5 rate by threshold:
- >=0.10: 23.74%
- >=0.15: 30.77%
- >=0.20: 35.48%
- >=0.25: 40.84%
- >=0.30: 44.75%
- >=0.40: 48.23%
- >=0.50: 53.49%

The score is clearly monotonic and useful.

### Stop admissibility

Stop-admissible:
- 2,182 / 4,441
- 49.13%

But realized OPPORTUNITY_5:
- admissible: 5.27%
- rejected: 20.23%

This is the critical inversion.

The stop rule disproportionately rejects the good $5-opportunity events.

### Score deciles

Bottom decile:
- OPPORTUNITY_5 rate: 2.03%
- stop-admissible share: 97.52%

Top decile:
- OPPORTUNITY_5 rate: 42.47%
- stop-admissible share: 0.45%
- median MFE60: $3.856
- mean MFE60: $5.358
- median MAE60: $4.362
- mean MAE60: $5.748

As opportunity quality rises, stop admissibility collapses.

### Early-damage veto

Risk Q50:
- 0.003156

Realized EARLY_DAMAGE:
- all events: 0.63%
- stop-admissible: 1.28%
- below risk Q50: 0.25%
- above risk Q50: 1.05%

Risk ranking has some separation, but the event is very rare.

### Three-way intersection

At diagnostic opportunity threshold 0.10:
- opportunity-only: 1,820
- opportunity + stop + risk: 101
- three-way realized OPPORTUNITY_5 rate: 12.87%

The full gate removes the opportunity enrichment:
23.74% opportunity rate before the stop/risk gates becomes only 12.87% after all gates.

At 0.15:
- three-way count: 15

At >=0.40:
- three-way count: 0.

## SELL

Validation events:
- 4,497

### Opportunity ranking

P(OPPORTUNITY_5):
- p50: 0.0947
- p75: 0.1871
- p90: 0.3470
- p95: 0.4308
- p99: 0.5699
- max: 0.7114

Realized OPPORTUNITY_5:
- >=0.10: 21.60%
- >=0.15: 26.16%
- >=0.20: 30.43%
- >=0.25: 34.31%
- >=0.30: 37.65%
- >=0.40: 43.14%
- >=0.50: 51.85%
- >=0.60: 62.50%
- >=0.70: 100%, but n=2

Again the opportunity model is strongly monotonic.

### Stop admissibility

Stop-admissible:
- 2,198 / 4,497
- 48.88%

Realized OPPORTUNITY_5:
- admissible: 5.23%
- rejected: 20.05%

Same inversion as BUY.

### Score deciles

Bottom decile:
- OPPORTUNITY_5: 1.78%
- stop-admissible: 98.44%

Top decile:
- OPPORTUNITY_5: 40.44%
- stop-admissible: 0.22%
- median MFE60: $3.906
- mean MFE60: $5.835
- median MAE60: $4.706
- mean MAE60: $5.722

The highest-quality $5-move states also require the largest adverse room.

### Early-damage veto

Risk Q50:
- 0.003219

Realized EARLY_DAMAGE:
- all: 0.62%
- stop-admissible: 1.27%
- below risk Q50: 0.60%
- above risk Q50: 0.65%

For SELL the risk model provides little useful separation in validation.

### Three-way intersection

At opportunity threshold 0.10:
- opportunity-only: 2,144
- full three-way: 109
- realized OPPORTUNITY_5 in full intersection: 11.93%

At 0.15:
- full intersection: 21

At >=0.30:
- zero full-intersection trades.

Again, stop/risk conditioning destroys the opportunity enrichment.

## Root cause

The V1 stop design assumed that a trade expected to make at least $5 should always maintain at least 1.5:1 reward/risk against that fixed $5 floor.

That assumption is incompatible with the observed gold path distribution.

The strongest $5-move states are high-volatility states:
- they produce larger MFE;
- they also produce larger MAE;
- they require wider structural/volatility stops.

Therefore a fixed $5 reward floor combined with a hard $3.333 stop ceiling creates selection bias toward quiet states that rarely achieve $5.

This is the opposite of the desired behavior.

## Implication for V2

Do not simply loosen the $3.333 stop cap.

V2 should make reward and risk jointly regime-adaptive.

A candidate should be evaluated using:
- predicted attainable favorable excursion;
- predicted adverse excursion / structural invalidation;
- expected reward/risk based on those two conditional distributions.

The minimum desired market opportunity can remain ~$5, but the execution target and initial stop should not be forced into a fixed $5:$3.33 geometry.

The early-damage veto should also be redesigned or demoted because the V1 target is too rare, especially for SELL.

## Governance

Do not:
- access 2023-2024 yet;
- access 2025;
- retroactively loosen V1;
- select a diagnostic threshold as a trading threshold.

Next:
specify Root-Reset V2 using joint favorable/adverse excursion modeling and dynamic reward/risk.

2025 remains sealed.
