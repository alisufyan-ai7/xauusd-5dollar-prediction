# Root-Cause Reset — Event-Driven Dynamic Trade Management V1

Status: FROZEN BEFORE NEW EMPIRICAL RESULTS

## Why this reset exists

EXP-001 through EXP-008 repeatedly showed the same pattern:

- rapid downside risk is predictable;
- positive executable trade quality is not robustly predictable;
- every-minute sampling creates heavily clustered pseudo-opportunities;
- fixed +$5 / -$3 / 60-minute labels are nonstationary across volatility regimes;
- richer price-only features and a sequence model did not repair the problem.

The project therefore stops treating every minute as a trade candidate and stops treating a fixed
-$3 stop as a universal truth.

This reset changes the research question from:

"Will +$5 beat -$3 from this arbitrary minute?"

to:

"Has a meaningful directional event occurred, is there evidence of at least ~$5 attainable movement,
what adverse excursion is normal for this setup/regime, and how should the trade be managed once
profit develops?"

FINAL_OOS 2025 remains sealed.

## External research basis

The reset uses the following general principles from public research:

1. Stop-loss effectiveness depends on the return process; fixed stops are not universally beneficial.
   Reference:
   Kathryn M. Kaminski and Andrew W. Lo,
   "When do stop-loss rules stop losses?",
   Journal of Financial Markets 18 (2014), 234-254,
   DOI: 10.1016/j.finmar.2013.07.001.

2. Volatility-adaptive stops are preferable to fixed-dollar stops when the goal is to keep normal
   market noise from triggering an exit.
   Reference:
   Fidelity Learning Center, Average True Range (ATR).

3. Trailing stops can reduce downside risk but tighter stops can reduce mean return / create
   premature exits.
   Reference:
   Bochuan Dai and Ben R. Marshall,
   "Risk reduction using trailing stop-loss rules",
   International Review of Finance 21(4), 2021.

4. Event-driven sampling and volatility-scaled triple-barrier labeling are established approaches
   for avoiding one-label-per-time-bar noise and for making barrier widths conditional on market
   volatility.

These references motivate the method only. They do not determine profitability.

## Core architecture

The new architecture is:

Market
-> event detector
-> directional setup candidate
-> attainable-excursion model
-> dynamic initial stop
-> downside-risk veto
-> trade management state machine
-> deterministic execution

The model must be allowed to return NO_TRADE frequently.

## Event-driven candidate sampling

Do not score every minute.

Primary event detector:
a symmetric CUSUM-style detector applied to causal one-minute BID close changes.

Volatility scale:
- causal ATR15_PROXY, defined as the mean true range of the four most recent completed synthetic 15-minute BID bars;
- each synthetic 15-minute true range uses its high, low, and the close immediately preceding that synthetic bar;
- therefore ATR15_PROXY summarizes approximately one hour of recent volatility at the 15-minute scale.

Standardized price change:
- one-minute BID close change / max(ATR15_PROXY, 1e-6).

Maintain positive and negative cumulative sums.

A positive event occurs when cumulative standardized movement >= +1.0.
A negative event occurs when cumulative standardized movement <= -1.0.

After an event fires, reset both cumulative sums to zero.

Direction:
- positive event => BUY continuation candidate;
- negative event => SELL continuation candidate.

Cooldown:
- 5 calendar minutes after an event.
- no new candidate during cooldown.

This is a single setup family: directional information event / continuation.
Reversal setups are intentionally excluded from V1.

## Opportunity target

The learning target is no longer "profit target before fixed stop."

For each candidate and direction, compute executable path outcomes over the next 60 minutes:

- MFE_60 = maximum favorable executable excursion;
- MAE_60 = maximum adverse executable excursion;
- time_to_MFE_3;
- time_to_MFE_5;
- time_to_MFE_7;
- time_to_MAE_1;
- time_to_MAE_2;
- time_to_MAE_3.

BUY excursions use ASK entry and future BID for executable liquidation.
SELL excursions use BID entry and future ASK for executable liquidation.

Primary opportunity label:

OPPORTUNITY_5 = 1 iff MFE_60 >= $5.

This directly matches the owner's economic objective:
only consider trades where a ~$5 or larger move is plausible.

## Opportunity model

Train BUY and SELL separately.

Input:
- exact BASE48 causal feature vector at the event timestamp;
- event-side information is implicit because models are separate.

Model:
HistGradientBoostingClassifier

Frozen hyperparameters:
- loss = log_loss
- learning_rate = 0.05
- max_iter = 200
- max_leaf_nodes = 15
- max_depth = None
- min_samples_leaf = 100
- l2_regularization = 1.0
- max_bins = 255
- early_stopping = false
- random_state = 1

TRAIN:
2016-2021 event candidates only.

No every-minute rows.

## Dynamic initial stop framework

The initial stop is not a fixed dollar amount.

At each candidate compute:

ATR_PROXY = ATR15_PROXY

Structure invalidation distance:

BUY:
entry ASK - trailing 15-minute BID low

SELL:
trailing 15-minute ASK high - entry BID

Add a volatility buffer of:

0.25 * ATR_PROXY

STRUCTURE_STOP_DISTANCE =
structure invalidation distance + volatility buffer.

VOLATILITY_STOP_DISTANCE =
1.5 * ATR_PROXY.

Primary stop distance:

INITIAL_STOP_DISTANCE =
max(STRUCTURE_STOP_DISTANCE, VOLATILITY_STOP_DISTANCE).

Reason:
- the stop must sit beyond immediate structure invalidation;
- it must also sit beyond ordinary volatility noise.

No arbitrary $3 hard stop.

## Risk/reward admissibility

A candidate is automatically rejected if:

INITIAL_STOP_DISTANCE <= 0

or

INITIAL_STOP_DISTANCE > $5 / 1.5

The latter enforces at least 1.5-to-1 reward/risk against the minimum desired $5 opportunity.

Therefore the maximum admissible initial stop for a $5 minimum objective is:

$3.333333...

If predicted attainable movement later exceeds $5, this rule may be evaluated against the conservative
$5 floor in V1; no wider stop is granted from an optimistic model prediction.

## Downside-risk veto

Retain the strongest repeatable finding from prior experiments:

predict <=5-minute adverse failure / damaging early excursion.

For the reset, define EARLY_DAMAGE as:

MAE reaches INITIAL_STOP_DISTANCE before MFE reaches +$1
and this occurs within 5 minutes.

Train a separate frozen classifier on event candidates.

A trade is eligible only if its predicted EARLY_DAMAGE probability is below a validation-frozen cutoff.

Cutoff:
- Q50 of VALIDATION 2022 risk distribution.

Only one downside cutoff is used in V1 to prevent another threshold search.

## Entry gate

A trade candidate enters only if ALL are true:

1. event detector fired;
2. INITIAL_STOP_DISTANCE passes risk/reward admissibility;
3. calibrated P(OPPORTUNITY_5) >= validation-frozen threshold;
4. EARLY_DAMAGE risk <= validation Q50;
5. no position is already open.

Opportunity threshold selection:

Candidate thresholds:
- 0.50
- 0.60
- 0.70
- 0.80

Fit the opportunity model on TRAIN 2016-2021 only.

Evaluate the four frozen candidate thresholds once on VALIDATION 2022 using the M0 HOLD_TO_5 policy
and the frozen dynamic-stop rule.

Select the LOWEST threshold that satisfies BOTH:
- at least 100 executed VALIDATION trades;
- positive mean VALIDATION NET_F10.

If multiple thresholds satisfy, the lowest is selected to avoid post-hoc preference for a sparse tail.

If no threshold satisfies:
- the reset stops before DEVELOPMENT_TEST;
- 2023-2024 are not evaluated.

Once selected, the threshold is frozen before any DEVELOPMENT_TEST access.

## Trade management policies

The owner explicitly wants +$3 to be usable as a profit-management point while still allowing +$5 or more.

Three policies are preregistered.

### M0 — HOLD_TO_5

- initial dynamic stop as defined above;
- take profit at +$5;
- time exit at 60 minutes;
- no stop movement.

Purpose:
baseline dynamic-stop policy.

### M1 — BE_AT_3

- initial dynamic stop;
- when executable favorable excursion first reaches +$3:
  move stop to entry plus F10 cost buffer in the profitable direction;
- continue holding full position for +$5;
- time exit at 60 minutes.

For BUY:
new stop = entry + $0.10.

For SELL:
new stop = entry - $0.10.

Purpose:
protect the position after a meaningful favorable move while preserving full +$5 upside.

This is the primary management hypothesis.

### M2 — TAKE_3

- initial dynamic stop;
- close the full trade at +$3;
- otherwise stop/time exit normally.

Purpose:
benchmark the owner's suggestion that +$3 may be sufficient.

No partial-close policy in V1 because partial execution depends on eventual broker volume/minimum-size constraints
and would confound the research.

## Optional extension beyond +$5

Not part of V1.

Do not trail beyond +$5 in this reset.

First establish whether event-driven entries plus dynamic stops can produce robust profitability.

If M1 passes robustly, a later separately frozen study may test letting winners run beyond +$5.

## Economic comparison

Evaluate M0 / M1 / M2 with:

- actual executable BID/ASK path;
- F0 / F05 / F10 / F20 friction;
- one global position at a time;
- no pyramiding;
- no averaging;
- no reversal while open.

Primary metric:
F10.

## Advancement gates

A management policy may advance only if ALL:

1. mean NET_F10 >0 in 2023;
2. mean NET_F10 >0 in 2024;
3. overall F10 profit factor >1;
4. UTC-day block-bootstrap 95% lower bound >0;
5. >=250 DEVELOPMENT_TEST trades;
6. >=75 trades in each 2023 and 2024;
7. no quarter contributes >40% of total positive F10 P&L;
8. 2025 remains untouched.

Bootstrap:
- 2,000 replicates;
- seed = 9.

## What this reset is meant to discover

This is not another attempt to find a better classifier on the same labeling problem.

It tests whether profitability emerges when we correct the trading problem itself:

- information-driven event sampling instead of every-minute sampling;
- direct $5 attainability prediction;
- volatility/structure-adaptive stop distance;
- downside-risk veto;
- +$3 as a management trigger rather than a universal exit;
- explicit comparison with full +$3 profit-taking.

## Governance

Do not:
- access 2025;
- add more event thresholds;
- add reversal setups;
- change ATR multiplier after results;
- change the 0.25 volatility buffer after results;
- add extra opportunity thresholds;
- add more breakeven triggers;
- add partial exits;
- loosen advancement gates;
- proceed to Exness demo/live.

A negative result is admissible.

## Exit decision

If none of M0/M1/M2 passes:

Stop the current price-only continuation setup lineage.

Do not run another model variation on it.

The next work would require a genuinely different setup family or timestamp-safe exogenous information,
not another threshold adjustment.
