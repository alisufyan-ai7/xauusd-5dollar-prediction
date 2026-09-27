# EXP-002 Economic Failure Diagnosis V1 Findings

Status: COMPLETE

Source run: 36328166429

Artifact: exp002-economic-failure-diagnosis-v1

FINAL_OOS 2025 was not accessed.

## Core diagnosis

The main economic failure mechanism is excessive adverse-barrier FAILURE frequency inside high classifier-score regions.

UNRESOLVED trades are not the primary drag. Their average executable expiry P&L is generally positive in the selected tails.

Signal clustering is also extreme: high-score observations are often repeated measurements of the same market episode rather than independent opportunities.

## BUY top 1%

Raw qualifying signals with complete executable paths:
- n = 6,922
- mean gross P&L = -0.5308
- SUCCESS = 28.69%
- FAILURE = 66.61%
- UNRESOLVED = 4.68%
- AMBIGUOUS = 0.01%
- mean UNRESOLVED expiry P&L = +0.7162

Year split:
- 2023 mean gross = -0.3049
- 2024 mean gross = -0.5998

The negative expectancy is therefore dominated by the high FAILURE share, not unresolved expiry behavior.

## SELL top 1%

Raw qualifying signals with complete executable paths:
- n = 7,102
- mean gross P&L = -0.1511
- SUCCESS = 34.19%
- FAILURE = 62.64%
- UNRESOLVED = 3.13%
- AMBIGUOUS = 0.04%
- mean UNRESOLVED expiry P&L = +0.6422

Year split:
- 2023 mean gross = +0.3345
- 2024 mean gross = -0.2792

SELL top 1% therefore shows material temporal instability rather than uniformly negative behavior.

## Score vs economic value

Classifier score is not reliably monotonic with economic value.

BUY:
- top-10% internal score slices remained negative throughout;
- the very highest slice was approximately -0.5588 mean gross.

SELL:
- the highest top-10% score slice improved to approximately -0.1224 mean gross;
- still negative overall.

This confirms that probability-of-SUCCESS ranking is not equivalent to expected executable P&L ranking.

## Regime observations

BUY top 1%:
- ASIA mean gross: -0.9006
- EUROPE: -0.7776
- US: -0.4575
- HIGH-volatility: -0.5326
- MID-volatility: -0.2219
- LOW-volatility: -1.2659
- highest spread-percentile quartile: -0.7401

SELL top 1%:
- ASIA: -0.5522
- EUROPE: -0.5142
- US: -0.0849
- 2023 positive overall, 2024 negative overall
- spread quartiles all negative, though Q4 was least negative at -0.0758

These are descriptive diagnostic findings only and must not be used for post-hoc regime filtering.

## Signal clustering

BUY top 1%:
- raw signals = 6,975
- 72.47% occur within 1 minute of the previous same-direction signal
- 86.48% within 5 minutes
- 91.30% within 15 minutes
- sequential engine executed 1,636 trades
- suppression ratio = 76.54%

SELL top 1%:
- raw signals = 7,162
- 75.60% within 1 minute
- 87.89% within 5 minutes
- 92.33% within 15 minutes
- sequential engine executed 1,442 trades
- suppression ratio = 79.87%

Therefore score-band sample counts substantially overstate the number of distinct trade episodes.

## Holding-time pattern

Top-1% sequential trades show strongly negative very-early outcomes.

BUY_ONLY:
- <=5m mean gross = -1.6397
- >5m to <=15m = +0.0283
- >15m to <=30m = +0.8689
- >30m to <=60m = +1.1485

SELL_ONLY:
- <=5m mean gross = -1.1465
- >5m to <=15m = +0.2201
- >15m to <=30m = +0.5633
- >30m to <=60m = +0.5848

This indicates many losing setups fail quickly, while surviving setups become economically better with time. This is diagnostic evidence, not permission to add a holding-time filter.

## Conclusion

EXP-002 fails economically mainly because:

1. the binary classifier rewards probability of SUCCESS but does not sufficiently penalize probability of early FAILURE;
2. score ranking is not monotonic in expected executable P&L;
3. 2024 materially degrades SELL relative to 2023;
4. high-score observations are heavily clustered and non-independent;
5. unresolved expiry P&L is generally not the main problem.

This supports designing EXP-003 around explicit economic outcome modeling rather than another SUCCESS-probability threshold search.

2025 remains sealed.
