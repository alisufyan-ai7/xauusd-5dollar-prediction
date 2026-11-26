# D-119 — Stage 3B Option B Owner-Independent Off-CI Preflight Findings

Status: **STATIC FEATURE/FOLD CONTRACTS FROZEN; NO-PROVIDER TESTS PASSED; EXECUTION STILL BLOCKED**.

All work is source-only, code-only, public documentation and synthetic fixtures. No 2026 provider quote acquisition, CI, model fitting, broker execution or 2022–2025 sealed access.

## Durable source and feature identities

| Item | Path | SHA-256 |
|---|---|---|
| Frozen Badar source teacher | `research/reference/information-parity-v1/stage3b-source-events-v1.csv` | `8089c9d9d4ade14bf1cd037331d298e787276657a2056daf0bbb2c84325433cd` |
| Exact source-derived feature allowlist | `research/reference/information-parity-v1/stage3b-2026-feature-allowlists-v1.json` | `44a73f70a51f3c364ef53c5dc6353443e348e0a86bc9142fa6b8919fbe986104` |
| Exact source-date LODO/fold manifest | `research/reference/information-parity-v1/stage3b-2026-teacher-folds-v1.json` | `56a1c301cfebc78373793db10d7099aab9391b33e1470c869b714261ba677ec5` |
| No-provider guard module | `scripts/stage3b_2026_preflight.py` | `a7c005000108ebf66ce18f04483ee615113d41cba0799cd92b5ecbfefb8052a3` |
| No-provider tests | `tests/test_stage3b_2026_preflight.py` | `bf9bd71c6e2db6a27774888140dccbd98be124bbca452a779ada8825ac4161ad` |

Stage 2 frozen source inspected: `scripts/build_information_parity_stage2_year.py`, `scripts/build_synthetic_dxy_stage2.py`, `research/INFORMATION_PARITY_V1_STAGE2_SCHEMA.json`, `requirements/information-parity-stage2.lock.txt`. The new manifest lists **92 GOLD predictors**, plus **63 FULL-only predictors** (155 FULL total), using field-qualified source table names; excludes all absolute timestamps, teacher IDs, outcomes, trade/risk template, unadmitted channels. GOLD's 92 are a strict subset of FULL's 155. Source availability and schema-fixed categories are declared. **This is a static allowlist, not evidence that a later unseen 2026 normalized dataset has all fields.** Exact missingness must be audited later.

The environment is specified in `requirements/information-parity-stage3b-2026.lock.txt` with CPython 3.12.14, inherited Stage 2 pandas/numpy/requests and pinned sklearn/scipy/model solver. **An exact Python 3.12.14 install/solver run has NOT been performed.** Local deterministic guard tests ran with Python 3.13.5 standard library only; sklearn was not imported or fitted. No CI needed for these checks.

## Actual off-CI deterministic tests

Executed on local synthetic fixtures, command:
`python -m unittest discover -s tests -v`

**11 tests PASSED, 0 failures**. Covered:
- UTC fence/rejection of 2022–2025, October quarantine, December shadow, invalid symbol, reversed range, non-UTC request;
- 350 MiB/750 MiB/one-attempt caps;
- inclusive 1–5 minute source interval/1-k weighting and mean probability pooling;
- latest eligible pre-minute state, no current-minute unfinished candle;
- date-grouped LODO, duplicate-event rejection;
- correct event-level class balancing and no row parity mismatch;
- point-in-time calendar publication precondition and unknown family;
- NYC/London summer/winter DST offsets;
- source-count and 39-fold synthetic cohort fixture;
- explicit predictor allowlist/forbidden field guards.

The exact committed Python guard and test contents were compared to locally executed byte hashes (shown above). The tests intentionally make **no network calls and fit no model**.

## Static audit of real frozen source cohort

Read frozen D-116 CSV plus new fold manifest through the GitHub connection only:
- **251 events, 250 eligible** (107 ACT / 143 P3).
- **343 expanded candidate M1 rows** across all eligible events.
- Event-normalized **sum of weights approximately 250** (floating point round-off).
- Exactly **39 held-out source-date folds**, covering all 250 eligible events once, no train/test date overlap.
- All eligible source intervals satisfy 1–5 minute caps.
- 92 GOLD / 155 FULL feature names are unique and schema-qualified.
- **No provider price row was retrieved**. Thus this is not a live causality/no-leakage proof on real quotes.

## Independent execution blockers discovered

1. **Provider legal/access gate:** Dukascopy Bank's public website TCU contain explicit automated-access restrictions; no prior express written consent or license for the proposed automated download was available. See `research/INFORMATION_PARITY_V1_STAGE3B_2026_PROVIDER_CALENDAR_RIGHTS_REVIEW.md`.
2. **Warm-up state parity gate:** the Stage 2 builder's unbounded active FVG and last-swing memory mean June 1 is not provably sufficient from schema alone. Separate scientific resolution/date approval required if continuous-state parity is intended.
3. **Historical macro schedule as-of gate:** primary agency archives exist but no complete event-by-event published-before-decision manifest has been certified.
4. **Exact pinned runtime gate:** the frozen full sklearn + Python 3.12.14 environment and solver have not been installed/tested together. Stdlib guard tests passing does not substitute for that.
5. **Execution authorization gate:** owner's Option B approval is in principle **only**. D-088 stays CLOSED, and no provider run/Stage 3B fit is permitted until all other gates and a new explicit final owner decision pass.

## Next owner-independent steps possible

Further official-public calendar source-version reconstruction, restricted code-only exact-environment builds where permitted, and refinement of scientifically defensible cold-start versus longer-history options may proceed without provider data. However automated provider acquisition requires legal authorization and owner permission once the full protocol is approved.

Source evidence adequacy was certified in D-116, but Stage 3B empirical recognition remains **NOT TESTED**. No advancement to Stage 4/5.
