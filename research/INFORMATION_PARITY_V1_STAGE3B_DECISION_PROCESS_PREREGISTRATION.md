# Information Parity V1 — Stage 3B Badar Decision-Process Supervision Preregistration

Status: **FROZEN SOURCE/ANALYSIS PROTOCOL — EMPIRICAL MARKET JOIN BLOCKED BY D-088**

Date frozen: 2026-10-10

Parents:
- D-087 — accepted Information Parity V1 Stage 2
- D-088 — 2026 chronology blocker
- D-097 — original exact-live-entry Stage 3 evidence result = INSUFFICIENT / NOT TESTED
- D-098 — full Badar source-corpus rescan
- `research/BADAR_FULL_SOURCE_CORPUS_RESCAN_FINDINGS.md`

Development branch:
`research/information-parity-v1-stage3-preregistration`

## 1. Purpose

Stage 3B is a **new experiment design**.

It does not revise, rescue or reinterpret the frozen D-089/D-097 exact-live-broker-entry benchmark.

The new question is:

> Given the causal market-information state available at a decision time, can a machine reproduce Badar's observed **decision process** — especially ACT versus explicitly REJECT/WAIT, and LONG versus SHORT conditional on acting — better with FULL_INFORMATION_PARITY_V1 than with GOLD_PRICE_ONLY?

Stage 3B is still a recognition/imitation benchmark.

It is **not**:
- a profitability test;
- a +$5/-$3 target experiment;
- an execution optimizer;
- a stop-loss optimizer;
- a risk-sizing optimizer;
- evidence that Badar is an optimal teacher;
- authorization to access 2022-2025 XAUUSD;
- authorization to acquire/join 2026 provider XAUUSD.

No trade outcome may determine teacher inclusion, labels, weights or filters.

## 2. Why Stage 3B is scientifically distinct from Stage 3

The original Stage 3 asked whether exact M1, confirmed Badar-owned live/real fills could be recognized.

That benchmark was finalized under D-097 as:

`INSUFFICIENT / NOT TESTED`

The full-corpus rescan in D-098 found a broader supervision opportunity:

- first-person Badar decision commitments are more numerous than confirmed broker fills;
- many source times are interval-censored rather than truly unknowable;
- live streams contain explicit considered-but-rejected opportunities;
- risk tier and management are part of the observed policy;
- instructional/replay content is valuable as semantic evidence but has a different trust level.

Stage 3B therefore changes the **teacher construct**, not the result of Stage 3.

This is allowed only because the new construct is being preregistered as a separate experiment before any 2026 market join or empirical model result is observed.

## 3. Frozen source identities

### 3.1 Accepted Information Parity identity

Accepted Stage 2 run:
- run `37474263432`
- artifact `11421634040`
- artifact digest:
  `sha256:41ebcaacaaaddafc6433e787ee9232eccf5128205b8648cecfd20f595d52985a`
- normalized full-TRAIN manifest SHA-256:
  `e9440bb0971c52456d1a79ddaa0144aa36fd758666421392bc4e7203132ea4c9`

The accepted materialized layer is 2016-2021 TRAIN.

Any later authorized 2026 reconstruction must reproduce the **same accepted feature semantics** unless a separately preregistered Information Parity addendum says otherwise.

### 3.2 Badar source identity for Stage 3B V1

Repository:
`alisufyan-ai7/unpack-human-trading-strategies-claude`

Pinned source commit:
`cc94077c953efa0d048e61d6ba4fbcdd0e3ca79a`

Pinned `dataset/live_trades.csv` blob:
`24939bf5ad141d38f2aad08c30ab6a077ab10086`

This Stage 3B V1 teacher corpus does **not** automatically roll forward with the Badar daily tracker.

New Badar material after this commit requires an explicit versioned source-update decision before it can enter the Stage 3B V1 primary dataset.

### 3.3 Provenance boundary

Badar repository rules remain controlling:

- everything outside `derived/` = source-layer evidence of what Badar said/showed, subject to transcript/observation uncertainty;
- everything inside `derived/` = Claude interpretation and prohibited as Badar-authored supervision.

The Badar repository is read-only for this project.

## 4. Current source snapshot — descriptive only

At the Stage 3B source pin:

- live-stream index: **46 streams**;
- current trade table: **123 rows**;
- XAUUSD rows: **122**;
- XAUUSD source dates: **39**;
- XAUUSD direction:
  - 53 LONG;
  - 69 SHORT;
- XAUUSD source evidence confidence:
  - 17 high;
  - 65 medium;
  - 40 low;
- high+medium XAUUSD trade-table subset:
  - 82 rows;
  - 37 dates;
  - 37 LONG;
  - 45 SHORT.

The source repository also contains:
- 257 indexed non-live long-video/Short items in the current top-level index;
- individual stream notes/transcripts;
- contact-sheet evidence;
- **1,331 full-resolution single stream frames covering all 46 indexed streams**.

These counts are known before the Stage 3B preregistration and are descriptive.

They are not profitability evidence.

The evidence-adequacy floors below are design safeguards, not claims that observations above a threshold become mathematically sufficient.

## 5. Core Stage 3B unit: a source decision event

The primary unit is no longer a broker fill minute.

It is a **source decision event**.

A decision event means source evidence shows Badar personally evaluated a concrete XAUUSD opportunity and either:

- committed to an action;
- explicitly rejected/deferred the action;
- or, for secondary policy description, changed management of an existing position.

Each event receives one immutable `event_id` in the project-derived adjudication table.

Every event must retain exact source references sufficient to audit the adjudication.

## 6. Source provenance classes

Each event gets exactly one `provenance_class`.

### P1 — LIVE_REAL_EXECUTION

Badar-owned live/real broker execution is explicitly confirmed.

Examples of acceptable evidence:
- broker terminal/account visible;
- explicit real-account statement tied to the position;
- fill/position visibly active in a real terminal.

P1 is the strongest execution evidence.

### P2 — LIVE_BADAR_COMMITMENT

During a live stream, Badar personally commits to an XAUUSD action, but live/real broker fill is not required.

Examples:
- "I am buying/selling here";
- places or explicitly commits to a limit;
- draws/activates a position as his own current trade;
- takes a test position;
- explicitly commits a split/scaled entry.

A generic scenario, forecast arrow, possible future setup or signal advertisement is not P2.

### P3 — LIVE_BADAR_REJECTION

During a live stream, Badar explicitly evaluates a concrete current XAUUSD opportunity and chooses not to act yet or not to act at all.

Examples:
- "middle — no trade";
- wait for H1/M30/M15 close;
- stop is too large;
- no logical SL;
- entry is late / do not chase;
- news risk;
- existing trade already running;
- RR is inadequate;
- confirmation is weak;
- session/day is over.

P3 supplies the primary hard-negative class.

### P4 — REPLAY_OR_BACKTEST_DEMO

Badar makes decisions on historical replay/backtest material.

P4 is **not** eligible for primary empirical evaluation.

It may support:
- ontology construction;
- semantic checks;
- source-label interpretation;
- future auxiliary-supervision work only under a separate implementation addendum.

### P5 — INSTRUCTIONAL_EXAMPLE

Static educational charts, Shorts, diagrams or retrospective examples.

P5 is semantic evidence only in Stage 3B V1.

It is not a primary empirical row.

### PX — EXCLUDED

Exclude from Badar primary supervision:
- other-person/student trades;
- unclear authorship;
- generic signal-group advertising;
- promotional performance screenshots;
- purely hypothetical examples with no current decision;
- content under `derived/`.

## 7. Evidence quality grade

Provenance and evidence quality are separate.

Each event receives:

### E1 — DIRECT

At least one direct source-layer observation clearly supports:
- Badar ownership;
- action/rejection semantics;
- direction when relevant;
- and timing interval.

Examples:
- direct transcript statement plus visible chart;
- visible current order/position plus source note;
- explicit rejection statement tied to the displayed setup.

### E2 — CORROBORATED

The event is strongly supported but requires combining two consistent source elements such as:
- note + transcript;
- note + frames;
- transcript + stream-time mapping.

No material field may depend on outcome or later price path.

### E3 — INFERRED_OR_AMBIGUOUS

Material semantics depend on inference, ambiguous authorship, uncertain action status or unresolved source conflict.

E3 is excluded from the primary benchmark.

Primary Stage 3B events require E1 or E2.

The Badar repository's existing `confidence` field remains audit metadata only. It is not automatically equivalent to E1/E2/E3.

## 8. Event types

Primary action event types:

- `COMMIT_LONG`
- `COMMIT_SHORT`
- `HARD_REJECT`
- `DEFER_WAIT`

Secondary descriptive event types:

- `MANAGE_REDUCE_RISK`
- `MANAGE_MOVE_BE`
- `MANAGE_PARTIAL`
- `MANAGE_MANUAL_EXIT`
- `MANAGE_TRAIL_OR_TIGHTEN`
- `MANAGE_EXTEND_TARGET`
- `MANAGE_PULL_TARGET`
- `MANAGE_HOLD`

A management event cannot be relabeled as a new entry unless the source explicitly shows a new entry decision.

## 9. Action commitment semantics

A Stage 3B positive represents **decision commitment**, not guaranteed fill.

A `COMMIT_LONG` or `COMMIT_SHORT` requires:

1. XAUUSD/gold context;
2. Badar confirmed as decision owner;
3. current live-stream decision, not replay;
4. explicit commitment to act;
5. unambiguous direction;
6. E1 or E2 evidence;
7. a source-supported time interval meeting the primary timing rule.

A resting limit may count as an action commitment even if it never fills.

A merely discussed possible limit does not count unless Badar explicitly commits/places it.

A position tool by itself is insufficient when ownership/commitment is unclear.

Trade outcome, RR, SL size and later market path do not determine eligibility.

## 10. Split/scaled entries and duplicate decisions

Do not inflate the teacher count by treating one plan as many independent decisions.

Rules:

- entries explicitly described as split/scaled pieces of one plan collapse to one action event;
- multiple same-direction source rows inside one source interval collapse when they represent one plan;
- a later re-entry after a stop/manual exit or a genuinely new confirmation is a new event;
- simultaneous opposite-direction ambiguity excludes the event from primary Task B;
- all underlying source row keys remain attached for audit.

## 11. Hard-negative semantics

Stage 3B does **not** label arbitrary non-entry minutes as NO-TRADE.

A primary negative must be a P3 source event where Badar explicitly evaluated the current opportunity.

Allowed `reject_reason` values:

- `MID_RANGE`
- `NO_VALID_POI`
- `WAIT_HTF_CLOSE`
- `SL_TOO_LARGE`
- `NO_LOGICAL_SL`
- `LATE_DO_NOT_CHASE`
- `NEWS_OR_EVENT_RISK`
- `EXISTING_POSITION`
- `RR_INADEQUATE`
- `CONFIRMATION_WEAK_OR_ABSENT`
- `SESSION_OR_DAY_STOP`
- `OTHER_EXPLICIT_REJECTION`

`DEFER_WAIT` is a valid negative at the time it is observed even if Badar later acts after the awaited condition occurs.

A generic statement such as "be patient" is not a hard negative unless tied to a concrete current opportunity.

## 12. Timing is interval-censored, not midpoint-imputed

Each source event receives:

- `interval_start_utc`
- `interval_end_utc`
- `interval_width_minutes`
- `timing_class`
- `timezone_evidence`

Allowed primary timing classes:

- `EXACT_M1` — one unique M1 minute;
- `INTERVAL_2M` — two possible M1 minutes;
- `INTERVAL_3_TO_5M` — three to five possible M1 minutes.

Auxiliary only:

- `INTERVAL_6_TO_15M`

Excluded from primary empirical evaluation:

- wider than 15 minutes;
- unresolved market-time mapping;
- source intervals crossing materially conflicting decisions;
- intervals whose timezone cannot be source-resolved.

The **primary Stage 3B window cap is 5 M1 minutes**.

Rationale:
- it keeps timing uncertainty within one M5 execution horizon;
- it is fixed before any market join;
- it avoids treating long vague periods as one precise decision.

Do not:
- choose the midpoint;
- snap to a visually convenient price;
- use later provider market data to resolve the source timestamp;
- move the interval after seeing model scores.

## 13. Source-time hierarchy

Resolve time source-only.

Preferred evidence order:

1. visible chart/broker time tied to the action;
2. source note with explicit chart time and timezone;
3. transcript/stream time plus a source-established chart-clock mapping for that stream;
4. full-resolution source frames and their indexed stream times.

Timezone conversion must use the source-specific timezone evidence.

Never assume one universal chart offset across all streams.

New full-resolution single frames at the pinned Badar commit may be used to improve source timing, because they are source-layer evidence and do not query market prices.

## 14. Primary source event-table schema

Before any market join, build a versioned project-derived table containing at minimum:

- `event_id`
- `source_date`
- `stream_id`
- `source_row_keys`
- `event_type`
- `direction`
- `provenance_class`
- `evidence_grade`
- `timing_class`
- `interval_start_utc`
- `interval_end_utc`
- `interval_width_minutes`
- `timezone_evidence`
- `broker_execution_status`
- `entry_mode`
- `risk_tier_source`
- `reject_reason`
- `management_action`
- `source_evidence_refs`
- `primary_task_a_eligible`
- `primary_task_b_eligible`
- `exclusion_reason`
- `badar_repo_commit`
- `teacher_table_blob`
- `adjudication_version`

Free-text notes may exist for audit but are never model inputs.

Outcome/result fields should not be copied into the primary event table unless a later audit requires a quarantined provenance column. They are never model inputs or filters.

## 15. Primary empirical tasks

### Task A — ACT versus explicit REJECT/WAIT

Positive:
- eligible `COMMIT_LONG`
- eligible `COMMIT_SHORT`

Negative:
- eligible `HARD_REJECT`
- eligible `DEFER_WAIT`

Question:

> Does the market-information state distinguish moments when Badar commits from moments when he explicitly decides not to commit?

This is the primary Stage 3B hypothesis task.

### Task B — direction conditional on ACT

Population:
eligible Task A positive events only.

Target:
- LONG
- SHORT

Question:

> Conditional on a Badar commitment, does FULL recover his chosen direction better than GOLD?

Task B is mandatory corroborating evidence.

### Task C — risk tier

Diagnostic only.

Use only events with explicit source evidence for risk class.

Frozen labels:
- `STANDARD_OR_FULL`
- `REDUCED_OR_HALF`

Do not infer risk class solely from eventual P&L.

Do not infer account percentage when account identity/balance is ambiguous.

### Task D — entry mode

Diagnostic only.

Frozen labels:
- `MARKET_OR_CLOSE`
- `RESTING_LIMIT`
- `SPLIT_OR_SCALED`
- `TEST_POSITION`

If ambiguous, exclude from Task D.

### Management policy

Management events are extracted now because they are part of the teacher policy.

They are **not** part of the Stage 3B primary FULL-vs-GOLD advancement gate.

A later management-learning experiment requires a separate preregistration that includes causal position state such as own entry, current SL, remaining size and realized/unrealized risk.

## 16. Instructional/replay evidence use in Stage 3B V1

P4/P5 material may be used to:
- define label ontology;
- interpret Badar terminology;
- cross-check whether a live event description is semantically consistent;
- enumerate candidate causal information channels.

P4/P5 may **not**:
- add primary Task A positives;
- add primary Task A negatives;
- add primary Task B evaluation rows;
- contribute empirical market-model training rows in Stage 3B V1.

This prevents hindsight/teaching selection from contaminating the primary live-decision benchmark.

Any representation pretraining on replay/instructional examples requires a separate preregistered addendum.

## 17. Source-only evidence-adequacy gate

The adequacy gate is evaluated **before any 2026 market join**.

### Task A adequacy

Require at least:

- 40 primary ACT events;
- 40 primary explicit REJECT/WAIT events;
- 20 distinct source dates that each contain at least one ACT and at least one REJECT/WAIT event.

### Task B adequacy

Require at least:

- 40 primary ACT events;
- 20 distinct ACT source dates;
- 15 LONG events;
- 15 SHORT events.

Both Task A and Task B gates must be met before the primary Stage 3B benchmark is statistically interpreted.

These are pragmatic design floors, not power theorems and not profitability thresholds.

If a gate is missed:

`SOURCE_EVIDENCE_INSUFFICIENT / NOT TESTED`

Do not:
- widen the 5-minute primary timing cap;
- admit E3 events;
- use P4/P5 as primary rows;
- add arbitrary stream minutes as negatives;
- filter by outcome;
- lower the floors merely to force execution.

A materially changed teacher design requires a new preregistration.

## 18. Event-to-market alignment after a future chronology authorization

Stage 3B currently forbids this join.

If later separately authorized, each event interval maps to all causal M1 Information Parity decision states whose decision minute falls inside the frozen interval.

For a minute `m`:

the usable state is the latest row satisfying:

`decision_time <= start_of_minute(m)`

The unfinished current M1 candle is never used.

No state closing after the candidate minute may enter the feature vector.

No provider market data may be used to shrink or move the teacher interval.

## 19. Interval-expanded weak-label training

No midpoint label is created.

For an event containing `k` possible M1 minutes:

- expand it to those `k` candidate minute rows;
- assign each candidate row base event weight `1/k`;
- therefore every source event has total weight 1 regardless of interval width.

Interpretation:

> absent finer source evidence, the latent action/rejection minute has a uniform prior across the source-supported interval.

This prevents a 5-minute interval from counting as five independent teacher events.

### Class balancing

Task A:
- after event normalization, scale positive event mass to 0.5 total;
- scale negative event mass to 0.5 total.

Task B:
- after event normalization, scale LONG event mass to 0.5;
- scale SHORT event mass to 0.5.

Do not use row-count-based class balancing after interval expansion.

## 20. Event-level prediction from interval rows

For primary evaluation, convert minute probabilities back to one event probability.

For event interval `I`:

`p_event = mean(p_minute for minute in I)`

Mean pooling is frozen because it matches the uniform latent-minute treatment used during training and does not automatically reward longer intervals.

Exact-M1 events reduce to one minute probability.

Mandatory non-gating sensitivity reports:
- exact-M1 events only;
- 2-minute intervals;
- 3-5-minute intervals;
- all primary intervals.

Do not select the best timing stratum after seeing results.

## 21. Frozen comparison arms

The arms remain intentionally simple.

### GOLD_PRICE_ONLY

May use causal XAUUSD price-derived state only:

- BID OHLC;
- causal returns/ranges admitted by the Information Parity pipeline;
- completed multi-timeframe price bars;
- causal price-derived swings/FVGs/structure;
- previous-day price state;
- deterministic structural fields derived solely from XAUUSD price.

Exclude:
- ASK/spread;
- provider volume;
- session/time fields;
- DXY;
- macro-event state;
- source text;
- Badar annotations;
- outcomes;
- setup IDs.

### FULL_INFORMATION_PARITY_V1

Use the exact same event rows plus all accepted Stage 2 V1 channels:

- all GOLD_PRICE_ONLY fields;
- synchronized BID/ASK and spread state;
- provider-volume state;
- session/time state;
- synthetic DXY state;
- scheduled macro-event state.

Still exclude:
- Badar text/annotations;
- setup IDs;
- outcomes/results;
- source IDs as model features;
- teacher action history;
- future macro actual/forecast/previous/surprise;
- unadmitted yield/rate channels.

D-098 observed that Badar sometimes checks US yields.

Yields are **not** silently added to Stage 3B FULL because they are not part of accepted Stage 2 V1.

If later evidence warrants a yield channel, that requires a separate Information Parity addendum before use.

## 22. Fixed model architecture

Use the same architecture for GOLD and FULL.

Task A:
**L2-regularized binary logistic regression**

Task B:
**L2-regularized binary logistic regression**

Frozen settings:
- `C = 1.0`;
- L2 penalty;
- no hyperparameter search;
- no feature selection from held-out results;
- no model-family search;
- deterministic solver/runtime to be pinned before empirical execution;
- numeric missingness indicator;
- training-fold-only median imputation;
- training-fold-only standardization;
- fixed schema-derived categorical one-hot vocabulary plus UNKNOWN.

Sample weights are the event-normalized and class-normalized weights from Section 19.

Preprocessing statistics must be learned using training dates only.

For scaling, use the union of unique training-fold market rows touched by eligible source intervals; do not let duplicated interval expansions alter preprocessing statistics.

## 23. Grouping and leakage protection

Primary group key:

`source_date`

All events from the same source date remain in one fold.

All streams on one date remain together.

Primary evaluation:
**leave-one-source-date-out**

No random row-level split.

No event from a held-out date may contribute:
- preprocessing statistics;
- model fitting;
- threshold selection;
- interval adjudication changes.

Teacher intervals, provenance and eligibility must be frozen before the market join.

## 24. Task A metrics

For every held-out source date containing at least one ACT and one REJECT/WAIT event:

- compute event-level ROC-AUC.

Primary Task A score:

**unweighted mean per-date event ROC-AUC**

Secondary:
- pooled out-of-fold event ROC-AUC;
- pooled average precision;
- event Brier score;
- event log loss;
- class counts by date;
- interval-width counts;
- reject-reason counts.

The same event set is used for GOLD and FULL.

## 25. Task B metrics

On out-of-fold ACT events:

- balanced accuracy at threshold 0.5;
- ROC-AUC for LONG probability;
- Brier score;
- log loss;
- confusion matrix.

Also report by source date where both LONG and SHORT exist when numerically defined.

Do not tune the 0.5 classification threshold.

## 26. Hierarchical joint diagnostic

Report, but do not use as the primary gate:

For an ACT event and its true direction,

`p_joint = mean(p_ACT_minute * p_true_direction_minute)`

This asks whether the hierarchy both:
1. recognizes that Badar acts;
2. assigns probability to the direction he chose.

The joint diagnostic cannot rescue a failed primary Task A result.

## 27. Uncertainty estimation

FULL versus GOLD is compared using paired source-date resampling.

Bootstrap:
- resampling unit = source date;
- 10,000 resamples;
- fixed seed = `20261010`;
- resample eligible dates with replacement.

Primary bootstrap statistic:
difference in mean per-date Task A event ROC-AUC.

Report percentile 95% confidence interval.

No minute-level bootstrap is allowed.

## 28. Frozen Stage 3B advancement rule

The result cannot be interpreted unless Section 17 is `ADEQUATE` and a future chronology decision authorizes the market join.

When empirically run, Stage 3B primary result is `PASS` only if:

1. source evidence is adequate;
2. `FULL - GOLD >= +0.03` absolute on mean per-date Task A event ROC-AUC;
3. the paired 95% date-bootstrap lower bound for that delta is > 0;
4. FULL Task A event Brier is not worse than GOLD by more than 0.01;
5. Task B does not materially regress:
   - FULL balanced accuracy must be at least GOLD - 0.02;
   - FULL Task B Brier must not be worse than GOLD by more than 0.01.

If Task A passes 2-4 but Task B violates criterion 5:

`MIXED — ACTION INFORMATION IMPROVED, DIRECTION DEGRADED`

This is not a Stage 3B PASS.

If evidence is adequate but Task A criteria fail:

`NEGATIVE FOR FROZEN STAGE 3B HYPOTHESIS`

That means only:

> under this frozen teacher construct, intervals, hard negatives, feature arms and diagnostic model, FULL did not demonstrate the preregistered improvement over GOLD.

It does **not** prove:
- profitable XAUUSD trading is impossible;
- Information Parity contains no useful information;
- a nonlinear future architecture can never benefit;
- Badar is unlearnable.

## 29. Mandatory non-gating sensitivity reports

Report without changing the primary rule:

1. exact-M1 events only;
2. interval-width strata;
3. P1 live-real events separately when enough exist for a meaningful descriptive table;
4. P2 live commitments separately;
5. reject reason by category;
6. E1 versus E2 evidence grade.

These are diagnostic.

They cannot replace the frozen primary result.

## 30. Explicit prohibitions

After market data are joined or any model result is visible, do not:

- alter teacher intervals;
- relabel ACT/REJECT based on later price behavior;
- drop losing Badar decisions;
- add only winning instructional examples;
- relax E1/E2;
- widen the 5-minute primary cap;
- replace hard negatives with easier arbitrary minutes;
- change C;
- change model family;
- tune class weights;
- add features because they improve held-out results;
- choose only favorable dates;
- change the +0.03 advancement threshold.

Any follow-on change is a new preregistered experiment.

## 31. Profitability and economic modeling remain separate

Stage 3B does not answer whether Badar's actions make money.

It does not use:
- win/loss;
- result R;
- TP/SL outcome;
- MFE/MAE;
- +$5/-$3 path target.

Profitability requires a later economic experiment with:
- explicit executable BUY/SELL/NO-TRADE semantics;
- spread/slippage assumptions;
- risk and position sizing;
- target/stop policy;
- opportunity frequency;
- chronological validation;
- sealed final OOS.

A Stage 3B PASS would show improved **expert-decision information**, not profitability.

## 32. Chronology gate remains fully closed

D-088 remains controlling.

Current governance:
- 2016-2021 = TRAIN;
- 2022 = sealed validation;
- 2023-2024 = sealed development test;
- 2025 = sealed final OOS;
- 2026 remains reserved and is not authorized for provider market reconstruction by this document.

Therefore this preregistration authorizes **no**:
- 2026 XAUUSD acquisition;
- 2026 DXY/provider join;
- Stage 3B model fitting;
- CI provider-data run.

The Stage 3B source dataset may be built using only the pinned Badar source repository.

## 33. Reproducibility gate before any future empirical execution

Before a chronology decision may authorize a Stage 3B market join, freeze:

1. source event adjudication CSV and SHA-256;
2. source adequacy findings;
3. ACT/REJECT/date/LONG/SHORT counts;
4. all source timing intervals;
5. source-event evidence references;
6. exact GOLD feature list;
7. exact FULL feature list;
8. Stage 3B environment lock;
9. deterministic interval-expansion tests;
10. deterministic event-weight tests;
11. deterministic LODO split tests;
12. deterministic event-pooling tests;
13. explicit chronology authorization.

No CI is required merely to create the source-only event table unless an implementation-specific exact-runtime dependency later makes it necessary.

## 34. Immediate next safe action

The next action after this preregistration is **source-only Stage 3B teacher construction**.

Build:

`research/reference/information-parity-v1/stage3b-source-events-v1.csv`

using only source-layer material at the pinned Badar commit.

Priority order:

1. adjudicate current live action commitments from the stream trade table and stream notes;
2. extract explicit live hard-negative/reject events from stream notes/transcripts/frames;
3. use the new full-resolution single frames to tighten intervals where source evidence supports it;
4. collapse split/scaled entries according to Section 10;
5. assign provenance, evidence grade and timing class;
6. compute the Section 17 source-evidence adequacy result;
7. write findings durably.

Do **not** access market data while doing this.
