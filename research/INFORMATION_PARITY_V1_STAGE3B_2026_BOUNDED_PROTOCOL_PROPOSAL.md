# Information Parity V1 — Option B Bounded 2026 Badar Teacher–Market Protocol

**D-118: OWNER APPROVAL IN PRINCIPLE RECEIVED; PROPOSAL FOR FINAL REVIEW ONLY. NOT AUTHORIZED TO EXECUTE.**

Authored: 2026-11-27 (Pakistan time). Decision predecessors D-087, D-088, D-097, D-099, D-116, D-117.

## 0. Authorization semantics and stop boundary

The owner explicitly approved preparing a bounded 2026 protocol in principle and explicitly withheld approval to acquire any market data or fit models until separately approving the completed protocol. This file implements *design authority only*. It does **not** reopen D-088 or authorize acquisition, reconstruction, feature building, event-to-market joining, model fitting, performance inspection, provider CI, or use of future reserved dates. The source-only frozen D-116 data is the sole research input used to draft the dates.

An explicit, affirmative **second approval**, recorded as a later decision, is required for execution. Silence, this commit, or GitHub workflow success cannot count as that approval. A separate prospective shadow protocol and authorization are also required before any shadow collection.

## 1. Question and immutable teacher cohort

Hypothesis: is FULL_INFORMATION_PARITY_V1 better than GOLD_PRICE_ONLY at recognizing Badar's 2026 *decision process* (ACT versus explicit REJECT/WAIT, then LONG versus SHORT conditional on ACT), under the previously frozen Stage 3B rules? No $5 price-target outcome or profitability claim is permitted here.

Canonical source-only event CSV:
`research/reference/information-parity-v1/stage3b-source-events-v1.csv`

Teacher SHA-256: `8089c9d9d4ade14bf1cd037331d298e787276657a2056daf0bbb2c84325433cd`

Source row dispositions SHA-256: `bf9fed8d952b9a0195ef1bfa3b036ba1e5489daec1169c7075ac36968a722604`

Pinned source: `alisufyan-ai7/unpack-human-trading-strategies-claude` commit `cc94077c953efa0d048e61d6ba4fbcdd0e3ca79a`; trade table blob `24939bf5ad141d38f2aad08c30ab6a077ab10086`.

Final source counts: **107 ACT** (47 LONG, 60 SHORT), **143 eligible P3**, **39 paired dates**. One provenance-only ineligible P3 remains in the canonical 251 rows. Do not use source IDs, event type metadata, evidence text, risk/management, future outcomes or trade execution results as model predictors.

## 2. Exact proposed UTC date partition

All time bounds are UTC and **half-open** (`start <= t < end`). No data may be fetched or used from these ranges without final authorization.

| Partition | Start inclusive | End exclusive | Permission if later approved |
|---|---|---|---|
| Research warm-up only | `2026-06-01T00:00:00Z` | `2026-07-06T00:00:00Z` | Causal continuity for rolling/previous-day/complete W1 features. Zero teacher labels or evaluation examples |
| Bounded retrospective teacher window | `2026-07-06T00:00:00Z` | `2026-10-09T00:00:00Z` | Market states solely for frozen 39 teacher source dates; source-grouped leave-one-date-out diagnostic |
| Unused quarantine/embargo | `2026-10-09T00:00:00Z` | `2026-12-01T00:00:00Z` | **Do not acquire, join, fit, score, or inspect** |
| Reserved truly prospective shadow | `2026-12-01T00:00:00Z` | `2027-01-01T00:00:00Z` | **No acquisition under this approval**; separate forward protocol/permission required |
| 2022 validation | `2022-01-01T00:00:00Z` | `2023-01-01T00:00:00Z` | SEALED |
| 2023–2024 development test | `2023-01-01T00:00:00Z` | `2025-01-01T00:00:00Z` | SEALED |
| 2025 final OOS | `2025-01-01T00:00:00Z` | `2026-01-01T00:00:00Z` | SEALED |

**Provider acquisition hard fence if finally authorized**: `2026-06-01T00:00:00Z <= t < 2026-10-09T00:00:00Z`; all source reads/download URL/range arguments must be checked against both endpoints before dispatch and normalized outputs checked after acquisition. This is a *130-calendar-day* inclusive date span, not an invitation to scan all available 2026. Market closures and missing data remain missing or causally handled under Stage 2 semantics.

Every acquired/derived datum from June 1 through October 8 is **consumed for retrospective research** and **not eligible to be described as untouched forward shadow evidence**. October 9–November 30 is a no-touch gap, not an additional historical test set. December shadow period remains genuinely future at the date of this proposal (November 27) but requires its own registered capture plan and should not be described as having labels today.

### Exact eligible teacher source dates (39)

`2026-07-06, 2026-07-07, 2026-07-09, 2026-07-10, 2026-07-21, 2026-07-22, 2026-07-23, 2026-07-27, 2026-07-28, 2026-07-29, 2026-07-30, 2026-07-31, 2026-08-03, 2026-08-04, 2026-08-05, 2026-08-06, 2026-08-07, 2026-08-13, 2026-08-17, 2026-08-28, 2026-08-31, 2026-09-02, 2026-09-04, 2026-09-14, 2026-09-15, 2026-09-16, 2026-09-17, 2026-09-18, 2026-09-21, 2026-09-23, 2026-09-24, 2026-09-25, 2026-09-28, 2026-09-29, 2026-09-30, 2026-10-01, 2026-10-02, 2026-10-06, 2026-10-08`

Earliest frozen source event interval starts `2026-07-06T14:10:00Z`; last ends `2026-10-08T13:36:00Z`. Event boundaries are source-only frozen under D-116 and may not be moved by observing provider prices. No other dates may become additional *teacher training labels* in this V1.

**Warm-up note:** June 1 is a conservative proposed causal-lookback start for daily, weekly and rolling information. Before final approval, a deterministic schema-only window-dependency inventory must confirm whether this suffices for every accepted feature. If it does not, **stop and request a new dated approval**; do not expand the provider range silently. No price data should be pulled just to choose the lookback start.

## 3. Market sources: same Stage 2 semantics, no source shopping

Admitted proposal-only source set:

1. **XAUUSD** Dukascopy synchronized M1 BID/ASK OHLC, BID/ASK provider volumes and derived spread, using accepted Stage 2 synchronization and flat-fill flags.
2. **Six Dukascopy FX M1 BID instruments** for `SYNTHETIC_DXY_DUKASCOPY_BID`: EURUSD, USDJPY, GBPUSD, USDCAD, USDSEK, USDCHF. Use accepted Stage 2 six-constituent formula, backwards as-of alignment and **5-minute maximum DXY staleness**; not official ICE DXY.
3. **First-party U.S. scheduled macro release calendars** for the already admitted families: NFP/Employment Situation, CPI, FOMC, GDP, JOLTS, and initial jobless claims (and only another family if the accepted Stage 2 version expressly includes it). ET/US DST exceptions and historical release times must be resolved source-first, not inferred from present-day recurring schedules. No post-event data values.

Proposed *maximum* acquisition scope:
- One coherent provider reconstruction of the closed 130-calendar-day fence.
- Up to **eight logical M1 series** (two XAUUSD quote sides + six FX BID series); no other market symbols.
- No ticks, full order book, real Exness account, trade history, account API, broker orders, future years, or direct DXY/UST substitutions.
- At most **350 MiB cumulative raw provider payload** and **750 MiB normalized/intermediate local payload** across the controlled attempt; if estimates or receipts exceed caps, stop and ask for renewed owner permission.
- At most **one controlled provider acquisition/build attempt** after final authorization, with deterministic local source and no-data fixture tests *before* any CI. Failure does not grant automatic repeat attempts. Provider quota/license/terms, archive availability, and forecasted transfer size must be verified without fetching restricted market rows first.
- Never commit raw licensed provider payloads to GitHub; retain compact digests, range identities, versions, counts, failure/missingness and deletion/retention metadata only.

These numeric caps are **proposed owner-review limits**, not a claim that provider volume will fit or that terms presently permit access. Do not simulate, backfill, interpolate or source-shop away missing inputs for the sake of getting a score.

### Macro point-in-time caveat

For 2026 first-party archive documents, demonstrate that the event was *scheduled/published* and its timing was knowable before each candidate decision time, with retrieved archive identity and version/revision caveats. If an exact event calendar cannot be reconstructed point-in-time, keep explicit missing state where allowed by Stage 2 or stop if source-coverage integrity fails; never import actual/forecast/previous/surprise/revision values.

Excluded: yields/rates, macro surprises, futures order flow, ticks, trading outcomes, or additional contemporary providers. A proposed new feature channel would require a **new preregistration before results**.

## 4. Causality, features and event alignment

Accepted Stage 2 identity:
- run `37474263432`, artifact `11421634040`;
- artifact digest `sha256:41ebcaacaaaddafc6433e787ee9232eccf5128205b8648cecfd20f595d52985a`;
- normalized TRAIN manifest SHA-256 `e9440bb0971c52456d1a79ddaa0144aa36fd758666421392bc4e7203132ea4c9`.

Reproduce **exact accepted Stage 2 V1 semantics**, not merely similar columns. M1 timestamps are UTC bar **starts** and decision state becomes available at M1 close. Completed M3/M5/M15/M30/H1/H4/D1/W1 only; two-right-bar swing confirmation and completed three-bar FVG formation; no partial bars, no future macro schedule changes, backward-as-of DXY max 5 minutes. For source candidate minute `m`, select only market states with `decision_time <= start_of_minute(m)`. No price-based interval disambiguation.

GOLD arm: accepted XAUUSD **BID price-only** OHLC/returns/ranges/completed higher-timeframe prices, confirmed price-derived structure/FVG, previous-day price fields. Remove ASK/spread, provider volume, session/time, DXY, macro, teacher state.

FULL arm: same GOLD fields plus Stage 2 accepted ASK/spread, provider participation volume, session/time state, synthetic DXY and scheduled macro proximity state. No yields, macro outcomes, execution/broker state or teacher/meta identifiers.

**Unfinished requirement before final owner approval:** generate exact machine-readable *flattened feature-column allowlists* from the pinned Stage 2 schema/implementation, with feature types, decision availability time, provenance and content hash. The table families above are the **contract**, not a falsely claimed exact executable allowlist. Any unexpected new columns must fail closed. The same eligible event instances, missing rows, folds and preprocessing apply to GOLD and FULL.

## 5. Frozen teacher-side / model-side protocol (unchanged)

- Task A = ACT versus **source-observed explicit P3 REJECT/WAIT** only; no fabricated arbitrary no-trade minutes.
- Task B = LONG versus SHORT only on eligible ACT; risk tier and entry mode are diagnostics, never selection filters.
- Expand interval of `k` candidate minutes with weight `1/k`; then normalize event mass and class mass per D-099. Pool event probability by unweighted mean of candidate-minute probabilities. Do **not** impute midpoint. Intervals 1–5 M1 minutes.
- One L2 logistic regression per Task and per arm, `C=1.0`, balanced **event-level** class weighting, fixed schema categorical vocabulary + UNKNOWN; training-fold-only missingness flags/median imputation/standardization. Pin solver, exact environment and runtime before execution; no hyperparameter search.
- Group by `source_date`; one held-out date per fold (**39 LODO folds**, subject to frozen eligibility). A date's all streams and events stay together. No random minute-level split and no held-out-date contribution to preprocessing, feature selection or labeling. A model built using the other 38 dates for a given fold is retrospective LODO, **not a strictly future-trained predictor**.
- Compare mean per-date Task A event ROC-AUC, full task A pooled metrics and Task B diagnostics. Use paired date bootstrap 10,000 draws, seed `20261010`. The full frozen Stage 3B gate is +0.03 FULL–GOLD Task A AUC, positive lower 95% CI, Task A Brier no worse than GOLD +0.01, AND Task B balanced accuracy no worse than GOLD -0.02 and Task B Brier no worse than GOLD +0.01. Negative/mixed results must be reported without rescue tuning.

**Important chronology interpretation:** LODO across July–October dates can test reproducible expert-state discrimination under held-out *dates* but does **not** give a prospective trading-performance claim. It also will not justify using a future December shadow window without a new protocol.

## 6. Pre-execution deterministic validation gates

All must pass **off-CI** first using static/fake fixture data; tests are not authorization to fetch market rows:
1. enforce start/end fence for each planned provider URL and each resulting row, hard-deny 2022–2025, quarantine and December;
2. frozen teacher SHA-256, count, source pin, timing widths, and no conflicting ACT/P3 candidate-minute overlaps;
3. 39-date fold partition, exact-once heldout event, no train/held-out date crossover;
4. explicit 1/k weights with total per-event mass 1, correct after per-task class normalization;
5. source-only frozen interval to M1 expansion (no midpoint/price snapping) and event probability mean pooling;
6. exact decision-time causal inequality, HTF/structural availability and previous-day history, DXY staleness, macro event release boundaries, ET/DST;
7. GOLD-only and FULL parity on row IDs and folds; train-only preprocessing and categorical unknown handling;
8. missing data produces explicit indicators rather than future fills; no source-meta/outcome fields into feature vectors;
9. provider budget guards and fail-closed missingness/data-rights reports;
10. no raw provider files or credentials in Git commits or long-lived logs.

Required before final approval: freeze a source clock / data-availability matrix, exact feature allowlists and SHA-256, environment lock, fixed source/release identities, acquisition estimate, retention/deletion plan, deterministic tests/results, run budget, and owner-facing go/no-go checklist. CI only if a dependency-specific issue is impossible to validate off-CI, and no CI/provider job without final authorization.

## 7. Protected shadow plan (design only)

**Proposed shadow interval: Dec 1 00:00 UTC to Jan 1 00:00 UTC (2027).** Zero 2026 Jul–Oct historical training states may be treated as fresh shadow observations. October 9–November 30 remains unacquired, not an opportunistic rescue validation set.

Future capture needs its own prospective protocol freezing **before collection**: timestamped prediction issuance, model artifact ID and hashes, news/calendar availability rules, allowed markets/accounts, integrity and cost assumptions, and how contemporaneous human decision evidence would be gathered (if at all). Do not assume Badar future labels will exist. No live trades or broker mutation is permitted by a shadow capture approval. December data may be used for *measurement only* after a separate authorization, not model fitting or hyperparameter choice. If the prospective period starts without an authorized capture system, it cannot later be relabeled prospective by historical reconstruction.

## 8. Owner final approval boundary

D-118 is **not** the execution-authorizing decision. After completing the preflight deliverables listed above, ask the owner for explicit approval of the exact scope, ideally in these terms:

> I approve the specifically versioned D-118 bounded 2026 teacher-market protocol and the frozen preflight manifests for a single controlled, capped provider-data acquisition and Stage 3B retrospective recognition test covering only June 1–October 8, 2026 UTC; I acknowledge this period loses untouched-forward status. I do not approve the October 9–November 30 gap, December shadow, sealed 2022–2025, live trading, other models, extra sources, or additional runs.

Do **not** request that approval until the outstanding preflight manifests and tests are actually complete and independently reviewed. Only a new signed-off chronology decision may partially supersede D-088 for the exact bounded exception; all other D-088 protections survive.

## 9. Current state

**OPTION_B_DESIGN_APPROVED_IN_PRINCIPLE / EXECUTION_NOT_AUTHORIZED / D-088_CLOSED**.

Next: complete **source-only / code-only preflight artifacts and tests**; no market data, model fitting, CI or broker actions.
