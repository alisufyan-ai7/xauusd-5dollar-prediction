# Information Parity V1 — Stage 3 Decision-Recognition Protocol Preregistration

Status: **FROZEN PROTOCOL — EMPIRICAL EXECUTION BLOCKED BY D-088**

Parent:
- `research/INFORMATION_PARITY_V1_ROADMAP.md`
- `research/INFORMATION_PARITY_V1_STAGE3_TEACHER_TIME_DOMAIN_FEASIBILITY.md`
- D-087 accepted Information Parity V1 Stage 2
- D-088 teacher time-domain blocker

Development branch:
`research/information-parity-v1-stage3-preregistration`

## 1. Purpose

Stage 3 tests one question:

> Does the frozen Information Parity V1 market state contain enough causal information to recognize Badar-like entry moments better than a frozen gold-price-only baseline?

This is an expert-decision recognition benchmark, not a profitability experiment.

Stage 3 does not:
- predict the EXP-001 +$5/-$3 economic label;
- use Badar trade outcomes as targets;
- optimize stops, targets, risk or execution;
- claim that every Badar trade is optimal;
- access sealed 2022-2025 XAUUSD;
- authorize 2026 XAUUSD acquisition under the current chronology.

D-088 remains controlling: the current Badar teacher rows are all in 2026, which is still reserved for later forward/shadow comparison. This preregistration defines the protocol only. It does not resolve that chronology conflict.

## 2. Frozen identities

### Accepted Information Parity layer

Accepted Stage 2 run:
- run: `37474263432`
- artifact ID: `11421634040`
- artifact digest: `sha256:41ebcaacaaaddafc6433e787ee9232eccf5128205b8648cecfd20f595d52985a`
- normalized full-TRAIN manifest SHA-256:
  `e9440bb0971c52456d1a79ddaa0144aa36fd758666421392bc4e7203132ea4c9`

The accepted layer covers 2016-2021 TRAIN only and preserves continuous causal state across calendar years.

### Badar source layer

Repository:
`alisufyan-ai7/unpack-human-trading-strategies-claude`

Pinned source commit:
`2df3d588c4b6d82761df2ee0c6f6639e82ce3414`

Pinned source table:
`dataset/live_trades.csv`

Pinned source-table blob:
`ea620cb44937f276be2e65ae7da25ae9503be655`

Provenance boundary:
- outside `derived/` = source-layer evidence of what Badar said/showed, subject to transcription/observation uncertainty;
- inside `derived/` = Claude interpretation and prohibited as Badar supervision.

The source table currently contains 119 rows across 43 streams, all dated 2026.

## 3. Teacher-row identity

The immutable source-row key is:

`(stream_id, trade_no)`

The original source row must be retained byte-for-byte or by pinned source identity in any later adjudication artifact.

The following source fields are audit metadata only and are **not model inputs**:
- entry;
- SL;
- TP1/TP2;
- planned RR;
- outcome;
- result_r;
- notes;
- source evidence-confidence rating;
- setup_id.

Specific restrictions:
- `confidence` is evidence/readability confidence, not Badar's trading confidence;
- `setup_id` is a researcher-added organizational index, not a Badar-authored target;
- outcome/result fields must never be used to decide whether a row is included.

## 4. Source-only teacher adjudication

Before any market join, every source row must receive one frozen adjudication record using only source-layer evidence.

Required adjudication fields:

- `stream_id`
- `trade_no`
- `source_date`
- `instrument_source`
- `direction_source`
- `authorship_status`
- `execution_status`
- `timestamp_status`
- `entry_minute_utc` when resolvable
- `primary_teacher_eligible`
- `exclusion_reason`
- `source_evidence_refs`
- `badar_repo_commit`
- `teacher_table_blob`
- `adjudication_version`

Allowed `authorship_status`:
- `BADAR_CONFIRMED`
- `OTHER_PERSON`
- `UNCLEAR`

Allowed `execution_status`:
- `LIVE_OR_REAL_CONFIRMED`
- `PAPER_OR_SIMULATION`
- `PLAN_OR_SIGNAL_ONLY`
- `FILL_UNCLEAR`

Allowed `timestamp_status`:
- `EXACT_M1`
- `INTERVAL_ONLY`
- `UNRESOLVED`

The adjudication file itself is project interpretation. It must cite the source-layer note/transcript/frame evidence used for each decision and must never be represented as something Badar authored.

## 5. Primary teacher eligibility

A row is a primary Stage 3 positive only when all conditions hold:

1. instrument is XAUUSD / gold;
2. `authorship_status = BADAR_CONFIRMED`;
3. `execution_status = LIVE_OR_REAL_CONFIRMED`;
4. direction is unambiguous LONG or SHORT;
5. `timestamp_status = EXACT_M1`;
6. the entry occurs inside a source-observed stream window;
7. no source conflict makes the entry identity materially ambiguous.

Primary exclusions therefore include:
- BTC or other non-XAUUSD instruments;
- student/viewer trades;
- paper/TradingView simulation trades;
- planning boxes or signals with no confirmed personal fill;
- rows with unclear authorship;
- rows whose source evidence cannot resolve one unique M1 entry minute.

The source-table evidence-confidence label alone does not include or exclude a row. Eligibility is field-specific and evidence-specific.

No exclusion may depend on:
- whether the trade won or lost;
- RR;
- eventual MFE/MAE;
- later market path;
- whether a later model classifies the row correctly.

## 6. Timestamp-resolution hierarchy

Market-chart time is preferred over relative YouTube stream time.

Resolution order:

1. an exact market-chart entry/fill timestamp visible in a source frame or explicitly recorded in the source stream note;
2. an exact source-table `chart_time` with an explicit UTC offset or explicit New York time;
3. a chart time whose timezone is unambiguously established for that specific stream by source-layer evidence.

Relative `stream_time` is used to locate evidence inside the video. It is not by itself a market timestamp unless the same source evidence ties it to a unique chart minute.

Rules:
- never assume one fixed chart timezone for every stream;
- use the explicit offset/timezone shown or documented for that stream;
- New York conversion must use `America/New_York`, not a hard-coded UTC offset;
- a string containing `~`, an interval/range, “about”, or equivalent uncertainty remains an interval unless source frames/notes independently narrow it to one M1 minute;
- do not choose a midpoint of an interval;
- do not round an uncertain timestamp toward a convenient market feature.

For a resolved entry occurring in minute `m`, the teacher decision state is the latest Information Parity decision row with:

`decision_time <= start_of_minute(m)`

Equivalently, the current minute's unfinished M1 bar is never used. No market information closing after the observed entry minute may enter the teacher state.

If source evidence only resolves a range spanning more than one M1 minute, the row is not a primary teacher positive.

## 7. Multiple entries in one minute

For the opportunity-recognition task:
- multiple eligible Badar entries in the same M1 minute and same direction collapse to one positive decision minute;
- all underlying source-row keys remain attached for audit.

If source evidence shows opposite-direction Badar entries within the same M1 minute, that minute is excluded from the primary benchmark as directionally ambiguous.

The direction task operates only on positive decision minutes with one unambiguous direction.

## 8. Source-observed non-trade controls

A non-trade control means:

> Badar was source-observed during the stream, but no logged Badar entry is evidenced at that decision minute.

It does **not** mean “bad setup” or “Badar would never trade here.”

Candidate control window:
- only the reliably observed market-time window of an in-scope stream;
- one candidate per M1 decision minute;
- never outside the stream simply because the calendar day is known.

The primary control set uses **all** mechanically eligible observed no-entry M1 minutes. There is no random negative subsampling in the primary benchmark.

Remove from the negative pool:
1. every eligible positive entry minute;
2. every minute containing any logged trade row, even when that row is excluded as student/paper/unclear;
3. every minute inside the full source-supported timestamp interval of an unresolved or interval-only trade row;
4. minutes whose stream market-time mapping itself is unresolved.

This quarantine prevents uncertain positives from being mislabeled as negatives.

## 9. Grouping and leakage protection

Evaluation group key:

`source_date`

All streams and all candidate minutes from the same source calendar date remain in the same fold.

No date may contribute:
- positive rows to training and controls to testing;
- one stream to training and another same-day stream to testing.

Primary grouped evaluation is **leave-one-source-date-out** cross-validation.

Each eligible source date is held out exactly once. Preprocessing and model fitting for that fold may use only the other dates.

There is no random row-level split.

## 10. Minimum teacher evidence-adequacy gate

This is an **experimental adequacy gate**, not a profitability gate and not an information-sufficiency hypothesis test.

Do not fit the Stage 3 recognition benchmark unless the frozen source-only adjudication yields at least:

- 40 primary positive decision minutes;
- 20 distinct eligible source dates;
- 15 LONG positives;
- 15 SHORT positives.

These floors are pragmatic preregistered minimums intended to prevent an unstable grouped benchmark from being driven by a very small number of correlated streams/dates or by a severely one-sided direction sample. They are not theorem-derived cutoffs at which 39 observations are scientifically useless and 40 become sufficient, and they do not imply any minimum number of profitable trades.

The evidence-adequacy result has only two states:

- `ADEQUATE`: all four floors are met, so the frozen Stage 3 recognition benchmark may be statistically interpreted subject to the separate chronology gate;
- `INSUFFICIENT`: one or more floors are not met, so the current Badar teacher evidence is too sparse for the frozen benchmark to support a reliable recognition conclusion.

`INSUFFICIENT` means **inconclusive due to teacher evidence**. It does not mean:
- Information Parity V1 lacks useful information;
- Badar's method is unlearnable;
- XAUUSD is unmodellable;
- a profitable trading system cannot be built;
- later economic modeling is scientifically disproven.

If the evidence-adequacy gate is `INSUFFICIENT`:
- do not run the frozen Stage 3 empirical benchmark;
- do not relax timestamp/authorship standards;
- do not add paper/student/uncertain rows merely to reach the threshold;
- do not alter the floors after observing the shortfall solely to force execution.

A new teacher source or a materially different recognition design requires a new preregistered decision.

## 11. Benchmark tasks

### Task A — opportunity recognition

Binary target:
- 1 = eligible Badar entry decision minute;
- 0 = source-observed no-entry control minute.

Primary question:
Can the model rank actual Badar entry minutes above matched same-stream/day no-entry minutes?

### Task B — direction recognition

Run only on eligible positive decision minutes.

Target:
- LONG
- SHORT

Question:
Can the richer information state recover Badar's observed direction better than the frozen price-only baseline?

### Explicitly not a Stage 3 target

Do not model:
- trade outcome;
- result R;
- TP/SL achievement;
- +$5/-$3 path outcome;
- profit;
- win rate;
- setup_id;
- evidence confidence.

## 12. Frozen comparison arms

### GOLD_PRICE_ONLY

May use only causal XAUUSD BID price information and price-derived state:
- BID OHLC;
- causal returns/ranges already present in Stage 2;
- completed M3/M5/M15/M30/H1/H4/D1/W1 price bars;
- confirmed price-derived swings/FVGs;
- previous-day price state;
- other deterministic structural fields whose only source is XAUUSD price.

Exclude:
- ASK/spread fields;
- provider volume;
- session/time-of-day fields;
- DXY;
- macro schedule/event state;
- trade/risk state;
- any Badar annotation other than the target label.

### FULL_INFORMATION_PARITY_V1

Use the same XAUUSD price fields plus all accepted Stage 2 V1 market/exogenous channels:
- synchronized BID/ASK and spread state;
- Dukascopy provider-volume state;
- session state;
- synthetic DXY state;
- scheduled macro-event state.

Still exclude:
- trade/risk template fields;
- Badar outcome/RR/SL/TP/setup annotations;
- macro actual/forecast/previous/surprise;
- rate/yield channel;
- any source not admitted in Stage 2.

The two arms must use the **same candidate rows, folds, preprocessing logic and model architecture**.

## 13. Fixed recognition architecture

Stage 3 uses a deliberately simple fixed diagnostic architecture:

**L2-regularized logistic regression**

Separate classifiers are fitted for:
- Task A opportunity;
- Task B direction.

Frozen training semantics:
- numeric missingness gets an explicit missing indicator;
- numeric values are imputed using the training-fold median only;
- numeric values are standardized using training-fold mean/std only;
- categorical values use a fixed schema-derived one-hot vocabulary plus an UNKNOWN category;
- L2 regularization;
- `C = 1.0`;
- balanced class weighting;
- no feature selection using held-out results;
- no hyperparameter search;
- no early stopping tuned on held-out dates.

The exact library/runtime version must be pinned in a Stage 3 implementation addendum before execution, but changing the algorithm, regularization type, C, class weighting or preprocessing after seeing Stage 3 results is prohibited.

This is a recognition benchmark, not the final Stage 5 economic architecture.

## 14. Metrics

All predictions used for evaluation must be out-of-fold predictions from the frozen leave-one-date-out procedure.

### Task A primary metric

For every held-out date containing at least one positive and one control:
- compute ROC-AUC within that date.

Primary score:
- unweighted mean of per-date ROC-AUC.

This prevents dates with more stream minutes from dominating the benchmark.

### Task A secondary metrics

Report:
- pooled out-of-fold average precision;
- pooled out-of-fold ROC-AUC;
- Brier score;
- log loss;
- positive prevalence;
- eligible positives and controls by date.

### Task B metrics

Report on pooled out-of-fold eligible positives:
- balanced accuracy;
- ROC-AUC for LONG probability where both classes exist;
- Brier score;
- log loss;
- confusion matrix.

Do not tune a probability threshold. Classification reporting uses 0.5.

## 15. Uncertainty estimate

Compare FULL versus GOLD using paired source-date resampling.

Bootstrap:
- resampling unit = source date;
- 10,000 resamples;
- fixed seed = `20261006`;
- resample dates with replacement;
- recompute the difference in mean per-date opportunity ROC-AUC.

Report the percentile 95% confidence interval.

No minute-level bootstrap is allowed because minutes within one stream/day are dependent.

## 16. Frozen recognition-hypothesis advancement rule

Section 10 must first return `ADEQUATE`. Evidence adequacy is a prerequisite for interpretation; it is not itself a hypothesis PASS.

Only after evidence is adequate and the separate chronology gate authorizes execution does Stage 3 test the recognition hypothesis.

The recognition hypothesis is `PASS` only if:

1. Section 10 is `ADEQUATE`;
2. `FULL - GOLD >= +0.03` absolute on mean per-date Task A ROC-AUC;
3. the 95% paired date-bootstrap confidence interval lower bound for that Task A delta is > 0;
4. FULL Task A Brier score is not worse than GOLD by more than 0.01.

If Section 10 is `INSUFFICIENT`, the recognition hypothesis is **NOT TESTED / INCONCLUSIVE**, not FAIL.

If evidence is adequate but criteria 2-4 are not met, the result is a **negative result for this frozen recognition hypothesis**:

> Under this teacher dataset, representation, candidate construction and fixed diagnostic model, FULL_INFORMATION_PARITY_V1 did not demonstrate the preregistered improvement over GOLD_PRICE_ONLY.

That negative result does **not** establish that profitable XAUUSD trading is impossible. Stage 3 does not use profitability as a target and cannot make that claim.

Task B direction results are mandatory evidence but are secondary to the Stage 3 recognition-hypothesis rule. They must be reported without changing the Task A rule.

A negative Task A recognition result cannot be rescued by:
- choosing another model family after seeing the result;
- changing C;
- changing the negative-sampling rule;
- dropping difficult dates;
- filtering losing Badar trades;
- tuning on outcomes.

A negative recognition result should trigger a separately documented diagnosis of possibilities such as teacher noise, missing information, representation limits or model-capacity limits. It must not trigger an arbitrary threshold/model search.

Later claims about profitability require separate economic targets, execution assumptions, chronological validation and sealed OOS evaluation. Stage 3 alone neither proves nor disproves profitability.

## 17. Missingness and row parity

GOLD and FULL must be evaluated on exactly the same teacher/control rows.

A row is not removed merely because DXY or macro context is missing.

Model-facing missingness must be represented causally via:
- null/imputation from training-fold statistics;
- explicit missing indicators.

Do not fill missing DXY or macro state with future observations.

## 18. Teacher metadata is audit-only

The benchmark may retain source metadata for descriptive reporting:
- stream;
- date;
- source evidence references;
- account/live/paper status;
- observed direction;
- source evidence confidence.

It may not feed free-text notes, source IDs, video IDs, setup labels, future outcomes or post-entry management into the model.

This prevents the classifier from recognizing a video/trade identifier instead of market state.

## 19. Reproducibility requirements before execution

Before any empirical Stage 3 run, commit and freeze:

1. the source-only teacher adjudication table and its SHA-256;
2. eligible positive count/date/direction summary;
3. stream observation-window table and its SHA-256;
4. exact feature-column lists for GOLD and FULL;
5. Stage 3 environment lock;
6. deterministic dataset-builder tests;
7. exact chronology authorization resolving D-088;
8. acquisition/build plan for any newly authorized market period.

Only after those are frozen may one Stage 3 empirical benchmark be run.

## 20. Current chronology gate

This document does **not** authorize a Stage 3 empirical run.

Under D-088:
- 2016-2021 is the accepted Information Parity TRAIN layer;
- 2022 remains sealed validation;
- 2023-2024 remain sealed development test;
- 2025 remains sealed final OOS;
- 2026 remains reserved for later forward/shadow comparison.

The current Badar teacher dataset is 2026-only.

Therefore:
**no 2026 XAUUSD acquisition, reconstruction, model fitting or benchmark execution is authorized by this preregistration.**

## 21. Immediate next safe work

While the chronology blocker remains unresolved, the next safe Stage 3 task is source-only:

1. build the deterministic teacher adjudication table from the pinned Badar source layer;
2. resolve entry-minute evidence without market-price lookup;
3. build the stream observation-window metadata table;
4. report whether the frozen minimum teacher-evidence gate can be met.

That work may use only the pinned Badar source-layer notes/transcripts/frames and repository metadata. It must not query or acquire 2026 XAUUSD market data.
