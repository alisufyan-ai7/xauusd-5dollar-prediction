# EXP-002 Sequential Execution Economics V1

Status: FROZEN BEFORE EXECUTION

## Purpose

Test whether the fixed EXP-002 executable-side predictive model produces positive sequential trade economics on DEVELOPMENT_TEST 2023-2024.

FINAL_OOS 2025 remains sealed.

## Frozen predictive model

Reproduce EXP-002 GBT V1 exactly:
- paired synchronized Dukascopy BID/ASK M1 inputs;
- frozen EXP-001 V2 BID-context features plus frozen EXP-002 causal spread features;
- TRAIN 2016-2021 only;
- every 5th eligible chronological TRAIN row;
- separate BUY and SELL HistGradientBoostingClassifier models;
- unchanged hyperparameters from EXP-002 preregistration.

## Frozen score policies

Derive raw-score cutoffs from all partition-boundary-eligible, feature-complete VALIDATION 2022 rows:

- top 10%
- top 5%
- top 2.5%
- top 1%

Apply these absolute cutoffs unchanged to DEVELOPMENT_TEST 2023-2024.

Cutoff derivation does not condition on future label or coverage outcome.

## Trade eligibility

At each DEVELOPMENT_TEST decision timestamp:

1. compute BUY and SELL raw scores;
2. compare to the frozen direction-specific VALIDATION cutoffs;
3. a trade may enter only if the historical executable label path has exact 60-minute BID/ASK coverage;
4. no threshold or model parameter changes are permitted after results.

Rows without exact executable-path coverage are counted as EXECUTION_UNAVAILABLE and do not create a trade.

## Sequential modes

Evaluate:

- BUY_ONLY
- SELL_ONLY
- COMBINED

Rules:

### BUY_ONLY
- only BUY signals are considered;
- one position at a time;
- while open, later BUY signals are ignored.

### SELL_ONLY
- only SELL signals are considered;
- one position at a time;
- while open, later SELL signals are ignored.

### COMBINED
- if neither qualifies: NO TRADE;
- if BUY and SELL both qualify at the same decision time: NO TRADE;
- if exactly one qualifies and no position is open: enter;
- while open, all later signals are ignored until exit.

No pyramiding.
No averaging.
No reversal while open.

## Gross P&L semantics

EXP-002 labels already incorporate executable-side spread geometry.

### SUCCESS
Gross P&L = +5.00 price units.

### FAILURE
Gross P&L = -3.00 price units.

### UNRESOLVED
Use the stored executable 60-minute expiry P&L:
- BUY: expiry BID close - entry ASK open;
- SELL: entry BID open - expiry ASK close.

### AMBIGUOUS
Gross P&L = -3.00 conservatively.

Reason:
M1 cannot determine target/adverse order inside the same bar. Treating AMBIGUOUS as adverse prevents optimistic promotion. Ambiguous counts must be reported separately.

If a policy passes with AMBIGUOUS treated as -3, later tick adjudication may improve precision but is not required to create the pass.

## Exit time semantics

SUCCESS / FAILURE / AMBIGUOUS:
- exit time = terminal M1 bar timestamp + 60 seconds.

UNRESOLVED:
- exit time = decision_time_ms + 60 minutes.

The sequential engine may accept a new signal only at or after the prior trade exit time.

## Additional friction stress

Executable BID/ASK spread is already included in the EXP-002 target and expiry definitions.

Apply additional completed-trade deductions:

- F0 = 0.00
- F05 = 0.05
- F10 = 0.10
- F20 = 0.20 price units per trade

These proxy commission and adverse slippage; they are not claims about one Exness account type.

## Required outputs

For every policy, mode, and friction scenario:

- trades;
- execution-unavailable count;
- SUCCESS / FAILURE / UNRESOLVED / AMBIGUOUS counts;
- average gross P&L;
- median gross P&L;
- average net P&L;
- median net P&L;
- expectancy in R, where 1R = 3 price units;
- net-positive trade rate;
- profit factor;
- cumulative net P&L;
- maximum sequential drawdown;
- active trading days;
- average trades per active day;
- average trades per calendar day.

Report:
- ALL DEVELOPMENT_TEST;
- 2023;
- 2024.

## Dependence-aware uncertainty

For each mode/policy/friction scenario:

- group completed trades by UTC entry date;
- bootstrap whole entry dates with replacement;
- 1,000 deterministic replicates;
- random seed 1;
- report the 95% percentile interval for mean net P&L/trade.

## Advancement rule

A mode/policy combination may be nominated for a separate immutable candidate freeze only if under F10:

1. mean net expectancy > 0 in BOTH 2023 and 2024;
2. overall profit factor > 1;
3. UTC-day bootstrap 95% expectancy interval lower bound > 0;
4. trade count is non-trivial;
5. any AMBIGUOUS observations are already treated conservatively as -3;
6. 2025 remains untouched.

Passing does not automatically open FINAL_OOS.

## Governance

- no 2025 access;
- no predictive tuning;
- no new score bands;
- no direction or policy may be promoted outside this preregistered comparison;
- negative results are admissible;
- no Exness demo/live trading is authorized by this milestone.
