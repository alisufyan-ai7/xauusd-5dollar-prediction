# EXP-006 Causal Path-State Representation V1 Findings

Status: COMPLETE — NO PATH84 POLICY PASSES

Source run: 36467825948

Artifact: exp006-causal-path-state-v1

FINAL_OOS 2025 was not accessed.

## Core result

No REP_B_PATH84 policy passed the frozen advancement rule.

Passing policies:
- none

The enriched causal path-state representation did not materially improve predictive diagnostics and generally worsened sequential economics.

## Representation comparison

### BUY

BASE48 DEVELOPMENT_TEST:
- direct-P&L Pearson: +0.0031
- EARLY_FAILURE ROC-AUC: 0.8859
- EARLY_FAILURE PR-AUC: 0.2671

PATH84 DEVELOPMENT_TEST:
- direct-P&L Pearson: -0.0038
- EARLY_FAILURE ROC-AUC: 0.8858
- EARLY_FAILURE PR-AUC: 0.2658

Delta:
- direct-P&L Pearson: -0.0068
- EARLY_FAILURE ROC-AUC: approximately unchanged
- EARLY_FAILURE PR-AUC: -0.0013

### SELL

BASE48 DEVELOPMENT_TEST:
- direct-P&L Pearson: -0.0018
- EARLY_FAILURE ROC-AUC: 0.8791
- EARLY_FAILURE PR-AUC: 0.2441

PATH84 DEVELOPMENT_TEST:
- direct-P&L Pearson: +0.0025
- EARLY_FAILURE ROC-AUC: 0.8796
- EARLY_FAILURE PR-AUC: 0.2433

Delta:
- direct-P&L Pearson: +0.0044
- EARLY_FAILURE ROC-AUC: +0.0005
- EARLY_FAILURE PR-AUC: -0.0008

Interpretation:
the 36 added path-state features did not create meaningful direct-P&L predictability and did not materially improve early-failure ranking.

## PATH84 sequential economics

### DIRECT_ONLY T0

BUY_ONLY:
- 983 trades
- mean NET_F10: -0.5212
- profit factor: 0.7252
- bootstrap 95% CI: [-0.7336, -0.3070]

SELL_ONLY:
- 2,224 trades
- mean NET_F10: -0.5074
- profit factor: 0.7190
- bootstrap 95% CI: [-0.6593, -0.3548]

COMBINED:
- 3,074 trades
- mean NET_F10: -0.5161
- profit factor: 0.7182
- bootstrap 95% CI: [-0.6491, -0.3927]

These are worse than BASE48 T0.

### DIRECT_ONLY T25

BUY_ONLY:
- 233 trades
- mean NET_F10: -0.4533

SELL_ONLY:
- 754 trades
- mean NET_F10: -0.4450

COMBINED:
- 972 trades
- mean NET_F10: -0.4420

Still negative.

### DIRECT_ONLY T50

BUY_ONLY:
- 51 trades
- mean NET_F10: -1.1445

SELL_ONLY:
- 231 trades
- mean NET_F10: -0.4645

COMBINED:
- 282 trades
- mean NET_F10: -0.5875

No improvement.

## PATH84 with early-failure gates

The downside-risk gates again reduce sample size sharply.

### Q50 / T0

BUY_ONLY:
- 33 trades
- mean NET_F10: -0.6866

SELL_ONLY:
- 245 trades
- mean NET_F10: -0.4477

COMBINED:
- 276 trades
- mean NET_F10: -0.4766

### Q50 / T50

SELL_ONLY and COMBINED:
- 8 trades
- mean NET_F10: +1.6328
- bootstrap lower bound remains below zero
- sample size far below frozen minimum

This tiny positive subset is not admissible evidence and must not be promoted.

### Q25 / Q10

Trade counts collapse further and no policy satisfies the frozen advancement gates.

## Main interpretation

EXP-006 provides a clean negative representation result.

Adding causal path-efficiency, sign-reversal, jump-concentration, local-extrema recency, and synthetic-bar structure across 5/15/30/60/120/240-minute windows:

1. did not improve direct executable-P&L prediction;
2. did not materially improve rapid-failure classification;
3. generally worsened sequential economics;
4. produced only tiny isolated positive subsets that fail preregistered sample-size and uncertainty requirements.

Therefore the current limitation is unlikely to be solved by adding more hand-crafted price-path features to the same gradient-boosted-tree setup.

No EXP-006 candidate should advance.

Do not:
- open 2025;
- cherry-pick Q50/T50 SELL;
- add more path windows post hoc;
- drop unfavorable PATH84 features;
- tune the current tree models using these results;
- proceed to Exness demo/live.

## Next implication

The next experiment should change a more fundamental dimension than hand-crafted path features.

Reasonable separately preregistered directions include:
- a genuinely sequence-aware model operating on causal M1/M5 path tensors;
- a different target focused on conditional target-before-adverse hazard;
- or adding timestamp-safe exogenous event/session context.

Because early-failure ranking remains strong while trade-quality prediction remains weak, the next experiment should preserve downside-risk modeling but change the model family or information source.

2025 remains sealed.
