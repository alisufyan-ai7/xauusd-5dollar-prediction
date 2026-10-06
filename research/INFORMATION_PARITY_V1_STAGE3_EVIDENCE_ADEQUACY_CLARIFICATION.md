# Information Parity V1 — Stage 3 Evidence-Adequacy Clarification

Status: **FROZEN BEFORE ANY STAGE 3 EMPIRICAL EXECUTION**

Purpose:
clarify the scientific meaning of the sample floors and recognition advancement rule in the Stage 3 preregistration.

## 1. What the 40 / 20 / 15 / 15 floors mean

The frozen floors are:

- 40 eligible positive decision minutes;
- 20 distinct eligible source dates;
- 15 LONG positives;
- 15 SHORT positives.

They are minimum **teacher-evidence adequacy** floors for the specific grouped Badar-recognition benchmark.

They were chosen conservatively and pragmatically to reduce three obvious risks:

1. too few positive examples for a diagnostic classifier;
2. too few independent-ish source-date groups for leave-one-date-out evaluation and date-level uncertainty estimation;
3. a direction sample so imbalanced that LONG/SHORT recognition becomes almost uninterpretable.

The date floor matters separately from the trade-count floor because multiple trades from one stream/day are correlated and cannot be treated as independent observations.

The LONG/SHORT floors concern Task B direction recognition. They are not trade quotas for a profitable strategy.

## 2. What the floors do not mean

The floors are not:
- a mathematical boundary proving adequacy at 40 and inadequacy at 39;
- a power theorem guaranteeing a particular effect will be detected;
- a profitability threshold;
- a minimum winning-trade count;
- evidence that a profitable system requires at least this many Badar trades.

The project may later preregister a formal power/simulation analysis for a subsequent experiment. That would be a new design step, not a retroactive justification for changing these floors after seeing results.

## 3. Correct status language

For Section 10:

- all floors met -> `ADEQUATE`;
- any floor missed -> `INSUFFICIENT`.

If `INSUFFICIENT`, the Stage 3 recognition hypothesis is:

`NOT TESTED / INCONCLUSIVE`

It is not `FAIL`.

The reason is that an inadequate teacher sample says something about the available evidence, not necessarily about the underlying machine information or the existence of profitable opportunities.

## 4. Recognition failure is still not profitability failure

If teacher evidence is `ADEQUATE`, the frozen FULL-vs-GOLD benchmark may be executed once separately authorized.

If FULL then fails the preregistered +0.03 / paired-CI / Brier criteria, the valid conclusion is limited to the frozen hypothesis:

> the richer Information Parity representation did not demonstrate the preregistered improvement over GOLD_PRICE_ONLY for recognizing these observed Badar entry moments under the fixed diagnostic architecture.

That does not prove:
- the richer information has zero economic value;
- a nonlinear or later decision architecture could never use it;
- Badar is an optimal teacher;
- profitable trading is impossible.

Any follow-on experiment motivated by such a negative result requires a new preregistration rather than post-hoc rescue tuning.

## 5. Profitability belongs to later economic evaluation

Profitability requires a different chain of evidence:
- explicit BUY / SELL / NO-TRADE decision semantics;
- fixed economic target and adverse barrier;
- execution/spread assumptions;
- opportunity frequency;
- calibration/selection policy;
- chronological validation;
- frozen final OOS evaluation.

Stage 3 deliberately does not optimize or evaluate profit.

Therefore neither:
- evidence inadequacy,
nor:
- failure of the Stage 3 recognition hypothesis

may be translated into the statement:

`a profitable XAUUSD system cannot be built`.

## 6. Governance consequence

D-089 and D-090 are interpreted under this clarification.

D-088 remains unchanged:
- no 2026 XAUUSD acquisition;
- no 2026 market reconstruction;
- no Stage 3 empirical fitting until chronology is separately authorized.

The current 35 exact-M1 / 16-date / 14-LONG / 21-SHORT metadata result is an **intermediate evidence audit**, not a profitability result and not a Stage 3 recognition FAIL.
