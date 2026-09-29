# EXP-007 — Causal Sequence Model V1

Status: FROZEN BEFORE EMPIRICAL RESULTS

## Purpose

Test whether a genuinely sequence-aware model can extract executable trade-quality information
that the tree models and hand-crafted representations in EXP-005/EXP-006 could not.

EXP-007 changes the model family and input representation while keeping the executable target,
downside-risk target, economic thresholds, sequential execution semantics, and advancement gates
conceptually unchanged.

FINAL_OOS 2025 remains sealed.

## Motivation

EXP-005/006 established:

- <=5-minute adverse-barrier failure is strongly rankable;
- direct executable-P&L prediction remains near zero correlation;
- adding 36 causal hand-crafted path features did not improve the edge;
- sequential economics remain negative;
- tiny positive subsets are inadmissible.

Therefore EXP-007 tests whether the missing information is in the ordered intraminute path itself,
rather than in additional summary statistics.

## Data and partitions

Use synchronized Dukascopy XAUUSD M1 BID+ASK.

Chronological partitions:
- TRAIN: 2016-2021
- VALIDATION: 2022
- DEVELOPMENT_TEST: 2023-2024
- FINAL_OOS: 2025 — SEALED
- 2026: later forward/shadow only

No EXP-007 development workflow may request, read, label, construct sequences from, score,
summarize, or inspect 2025.

## Executable semantics

Reuse EXP-005/006 unchanged.

BUY:
- entry next M1 ASK open;
- SUCCESS if BID reaches entry +5 before entry -3;
- FAILURE if BID reaches entry -3 first.

SELL:
- entry next M1 BID open;
- SUCCESS if ASK reaches entry -5 before entry +3;
- FAILURE if ASK reaches entry +3 first.

Horizon:
- exactly 60 calendar minutes;
- synchronized coverage required.

Economic outcomes:
- SUCCESS = +5
- FAILURE = -3
- UNRESOLVED = actual executable 60-minute expiry P&L
- AMBIGUOUS excluded from fitting and treated as -3 in evaluation

EARLY_FAILURE:
- unchanged from EXP-005/006;
- 1 iff FAILURE reaches adverse barrier within <=5 minutes after executable entry.

## Benchmark

The completed EXP-006 BASE48 tree result remains the historical benchmark.

EXP-007 does not rerun/tune that benchmark for advancement.

## Sequence input

Each scored decision uses exactly the trailing 60 completed synchronized M1 bars ending at
the decision-feature bar t.

One additional immediately preceding synchronized M1 bar is retained only to compute the
one-minute close-change channel for the first of the 60 model timesteps. That predecessor
is causal and is not itself passed as a model timestep.

No future bar is included.

For each of the 60 bars construct six channels from synchronized BID/ASK:

1. BID one-minute close change
2. BID high-low range
3. BID close-open body
4. BID upper wick
5. BID lower wick
6. close spread = ASK close - BID close

### Causal per-sequence normalization

For each 60-bar sequence:

scale =
median(BID high-low range across the 60 observed bars)

If scale < 1e-6, use 1e-6.

Channels 1-6 are divided by this scale.

No normalization parameter is estimated from VALIDATION or DEVELOPMENT_TEST.

This creates dimensionless local path inputs and avoids relying on absolute gold price level.

## Static causal context

In addition to the 60x6 sequence, the model receives the exact frozen BASE48 feature vector
from EXP-005.

BASE48 values are normalized using TRAIN-only robust statistics:

z_j = (x_j - TRAIN median_j) / max(TRAIN IQR_j, 1e-6)

Then clip each z_j to [-10,+10].

TRAIN medians/IQRs are computed only from the deterministic EXP-007 training sample described below.

No VALIDATION/DEVELOPMENT statistics enter normalization.

## Model family

Train BUY and SELL independently.

For each direction train two separate neural networks with the same frozen encoder architecture:

- direct executable gross-P&L regressor;
- <=5-minute EARLY_FAILURE classifier.

Framework:
- PyTorch CPU.

### Frozen temporal encoder

Input shape:
- 6 channels x 60 timesteps.

Architecture:

1. Conv1d(6, 16, kernel_size=5, padding=2)
2. ReLU
3. Conv1d(16, 32, kernel_size=5, dilation=2, padding=4)
4. ReLU
5. AdaptiveAvgPool1d(1)
6. flatten -> 32 sequence features
7. concatenate normalized BASE48 static vector -> 80 features
8. Linear(80, 32)
9. ReLU

Output head:
- regression: Linear(32,1)
- classifier: Linear(32,1) logits

No dropout.
No batch normalization.
No attention.
No recurrent layers.

Reason:
use a small fixed causal sequence learner with enough capacity to detect local path motifs
without introducing a large architecture search surface.

## Training sample

Eligible TRAIN rows:
- 2016-2021 only;
- partition-boundary eligible;
- coverage complete;
- BASE48 feature complete;
- exact trailing 60 synchronized contiguous M1 bars plus the immediately preceding causal bar available;
- AMBIGUOUS excluded.

Sampling:
- every 20th eligible chronological row independently for BUY and SELL.

The 20-row thinning interval is frozen before results to keep CPU training bounded and deterministic.

No alternative thinning interval may be tested in EXP-007.

## Targets

### Direct-P&L network

Target:
- SUCCESS +5
- FAILURE -3
- UNRESOLVED actual executable expiry P&L

Loss:
- mean squared error.

Prediction clipped to [-3,+5].

DIRECT_NET_F10 =
predicted gross P&L -0.10.

### EARLY_FAILURE network

Target:
- binary EARLY_FAILURE.

Loss:
- BCEWithLogitsLoss.

No class weighting.

## Optimization

For all four networks:

- optimizer = Adam
- learning_rate = 0.001
- weight_decay = 0.0001
- batch_size = 512
- epochs = 8
- shuffle = false
- torch manual seed = 7
- numpy seed = 7
- deterministic CPU execution requested where supported

No early stopping.
No learning-rate scheduler.
No hyperparameter search.

The final epoch model is used.

## Validation-derived downside gates

For BUY and SELL separately derive from VALIDATION 2022 EARLY_FAILURE predictions:

- EF_Q50
- EF_Q25
- EF_Q10

Definitions unchanged:
lower predicted risk is better.

No additional risk cutoff.

## Policy arms

- A_SEQ_DIRECT_ONLY
- B_SEQ_DIRECT_EF_Q50
- C_SEQ_DIRECT_EF_Q25
- D_SEQ_DIRECT_EF_Q10

All are eligible for advancement.

## Frozen direct-score thresholds

Reuse unchanged:

- T0: DIRECT_NET_F10 > 0.00
- T25: >= +0.25
- T50: >= +0.50
- T75: >= +0.75

No additional thresholds.

## Direction conflict rule

Unchanged:

- neither qualifies => NO_TRADE
- exactly one qualifies => that direction
- both qualify:
  - choose larger DIRECT_NET_F10 only if absolute difference >=0.25
  - otherwise NO_TRADE

## Sequential execution

Unchanged:

- one global position at a time;
- no pyramiding;
- no averaging;
- no reversal while open;
- suppress later qualifiers until current exit.

## Required predictive diagnostics

For BUY and SELL separately on:

- VALIDATION 2022
- DEVELOPMENT_TEST overall
- 2023
- 2024

Direct regressor:
- MAE
- RMSE
- mean predicted / realized gross P&L
- Pearson correlation
- realized NET_F10 by predicted-score decile
- fixed DIRECT_NET_F10 bands

EARLY_FAILURE:
- base rate
- ROC-AUC
- PR-AUC
- Brier
- risk deciles vs realized rate

Training diagnostics:
- final epoch regression loss
- final epoch classifier loss
- exact training-row count
- exact sequence/channel/static dimensions

## Required sequential economics

For:
- A/B/C/D sequence policy arms
- T0/T25/T50/T75
- BUY_ONLY / SELL_ONLY / COMBINED

report:
- raw qualifiers
- executed trades
- suppression ratio
- outcome counts
- EARLY_FAILURE count/share
- F0/F05/F10/F20
- overall DEVELOPMENT_TEST
- 2023
- 2024
- each quarter
- profit factor
- cumulative P&L
- max drawdown
- active days
- trade frequency
- holding-time quantiles

## Dependence-aware uncertainty

For every sequence policy:

- group DEVELOPMENT_TEST trades by UTC entry date
- bootstrap whole dates with replacement
- 2,000 replicates
- seed = 7
- report 95% percentile CI of mean NET_F10

## Advancement rule

A sequence policy may advance only if ALL:

1. mean NET_F10 >0 in 2023
2. mean NET_F10 >0 in 2024
3. overall F10 profit factor >1
4. UTC-day bootstrap 95% lower bound >0
5. >=250 DEVELOPMENT_TEST trades
6. >=75 trades in each of 2023 and 2024
7. no single quarter contributes >40% of total positive F10 P&L
8. AMBIGUOUS treated as -3
9. 2025 untouched

Passing does not automatically open 2025.

If multiple policies pass, retain all passers for a separate immutable pre-OOS freeze.

## Governance

EXP-007 must not:

- access 2025;
- tune convolution architecture;
- tune epochs, learning rate, batch size, weight decay, or thinning;
- add/remove channels after results;
- alter BASE48 static context;
- add external event/news data;
- change the <=5-minute EARLY_FAILURE definition;
- add risk quantiles;
- add score thresholds;
- introduce post-hoc regime filters;
- proceed to Exness demo/live.

Negative results are admissible.

## Exit states

A. NO POLICY PASSES
- keep 2025 sealed;
- diagnose whether sequence model learned useful downside/quality structure;
- next experiment may add separately preregistered exogenous context or change target formulation.

B. ONE OR MORE POLICIES PASS
- keep 2025 sealed;
- freeze all passers separately;
- perform implementation, determinism, and leakage audit before any FINAL_OOS access.

2025 remains sealed in all cases.
