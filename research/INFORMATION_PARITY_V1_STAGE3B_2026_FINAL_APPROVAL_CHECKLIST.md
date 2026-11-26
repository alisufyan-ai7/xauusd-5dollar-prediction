# D-118 — Second Owner Approval / Bounded 2026 Execution Checklist

**CURRENT STATUS: D-124 FINAL OWNER AUTHORIZATION GRANTED; EXACT RUNTIME/IMPLEMENTATION PREFLIGHT MUST PASS BEFORE PROVIDER EXECUTION. D-088 PARTIALLY SUPERSEDED ONLY FOR THIS BOUNDED EXCEPTION.**

Protocol: `research/INFORMATION_PARITY_V1_STAGE3B_2026_BOUNDED_PROTOCOL_PROPOSAL.md`.

## Already verified without provider market acquisition

- [x] Option B **design approval in principle** from owner, expressly excluding market data and model fitting.
- [x] D-116 teacher source identity and SHA-256 committed; 107 ACT, 143 eligible P3, 39 paired dates.
- [x] Exact 39 teacher dates bounded Jul 6–Oct 8 2026; no labeling outside.
- [x] Proposed market acquisition fence Jun 1–Oct 9 2026 UTC exclusive; warm-up restricted Jun 1–Jul 6.
- [x] Quarantined Oct 9–Dec 1 2026 (no access); shadow Dec 1 2026–Jan 1 2027 (separate approval).
- [x] Parent Stage 2 semantic and D-099 Stage 3B frozen evaluation requirements identified.
- [x] Proposed source list, budget ceilings, denial rules and prospective shadow separation documented.

## Must finish *before presenting final execution approval*

- [x] Freeze static GOLD (92) and FULL (155) column allowlists, types/provenance/availability and SHA-256; forbid teacher/outcome/leakage columns. Runtime table-column matching still must pass before provider execution.
- [ ] Exact Stage 3B CPython 3.12.14/pandas 3.0.6/numpy 2.5.3 environment still requires isolated runner validation; Python 3.13.5 locally imports pinned sklearn 1.8.0, scipy 1.17.0, joblib 1.5.3 and threadpoolctl 3.6.0 without fitting.
- [x] Commit exact source-only 39-date fold manifest, hash and synthetic candidate-minute/weight/event-pooling fixtures; 11 local no-provider tests pass.
- [x] Design resolution D-120: bounded June 1 source-history cold start, unknown pre-window swing/FVG state, causal accumulation only; discloses that this differs from full-history Stage 2 continuity and must be included in final owner approval. No source-range expansion.
- [x] Owner explicitly confirms holding written Dukascopy automation permission/licence; **no recurring paperwork request**. The future acquisition still must respect the existing licence scope, quota and capped budget (not independently checked here).
- [x] D-121 freezes a **fail-closed no-calendar fallback**: if full 2026 point-in-time family/year schedule is not certified, macro_schedule_available=0 for all 2026 teacher rows; dependent macro values explicitly unavailable (bounded-source reduced-macro diagnostic, disclosed for final approval). 11 prior-event examples remain evidence inventory only.
- [ ] D-121 adds machine-readable no-network acquisition plan and strict final-owner-decision SHA gate; full future acquisition wrapper integration and exact runtime checks must pass before any provider calls (do not run CI/provider now).
- [x] No-provider off-CI Python stdlib tests: **22/22 pass**, including D-120 and four D-121 plan/approval/hash/runtime-inspection checks. No model was fitted. Exact pinned-runtime tests remain separate.
- [x] D-121 consolidated owner-access attestation, calendar absence fallback, bounded cold-start, source hashes, 21 fixture tests and no-provider acquisition design. Remaining technical reproducibility checks are explicit, not new owner-input requests.
- [x] **D-124 final owner authorization granted** for the exact bounded acquisition/model package; no further owner approval required for that package. Exact D-124 commit SHA must be admitted in the executable guard before provider access.

## Not part of this approval

- 2022–2025 evaluation unlock.
- October 9–November 30 2026 data.
- December 2026 or 2027 shadow acquisition.
- Any real-money orders, Exness mutations, profit optimization or additional strategy/model searches.
- CI or provider runs prior to explicit final approval.

**No one should interpret the checked design-only items as permission to run provider jobs.**


## D-119 new evidence and reproducibility identities

- Feature allowlist: `research/reference/information-parity-v1/stage3b-2026-feature-allowlists-v1.json` SHA-256 `44a73f70a51f3c364ef53c5dc6353443e348e0a86bc9142fa6b8919fbe986104`.
- Frozen teacher/folds: `research/reference/information-parity-v1/stage3b-2026-teacher-folds-v1.json` SHA-256 `56a1c301cfebc78373793db10d7099aab9391b33e1470c869b714261ba677ec5`.
- Runtime lock proposal `requirements/information-parity-stage3b-2026.lock.txt`.
- Local no-provider guard tests: `scripts/stage3b_2026_preflight.py`, `tests/test_stage3b_2026_preflight.py`; 11/11 passed on Python 3.13.5 standard library.
- Findings: `research/INFORMATION_PARITY_V1_STAGE3B_2026_PREFLIGHT_QA_FINDINGS.md` and provider/calendar rights `research/INFORMATION_PARITY_V1_STAGE3B_2026_PROVIDER_CALENDAR_RIGHTS_REVIEW.md`.


## D-120 evidence

- Owner attested the existing provider permission; do **not** request licence documents again.
- `research/INFORMATION_PARITY_V1_STAGE3B_2026_D120_FINDINGS.md`.
- `research/reference/information-parity-v1/stage3b-2026-macro-asof-evidence-v1.json` (11 example events; not full calendar).
- `scripts/stage3b_2026_addendum.py` and `tests/test_stage3b_2026_addendum.py` (6 additional tests, 17/17 total).
- Proposed June1 bounded cold-start explicitly disclosed for the final scientific sign-off; **no extension to dates before June1**.


## D-121 freeze

- No-provider acquisition plan `research/reference/information-parity-v1/stage3b-2026-acquisition-preflight-v1.json` with `owner_final_execution_approval_commit=null`.
- `scripts/stage3b_2026_execution_preflight.py` and `tests/test_stage3b_2026_execution_preflight.py` (4 more tests, 22/22 overall).
- `research/INFORMATION_PARITY_V1_STAGE3B_2026_D121_FINDINGS.md`.
- Outstanding: exact CPython3.12.14 environment verification and complete acquisition-wrapper integration; final owner approval is a distinct future decision. No provider acquisition, fitting or CI.


## D-124 final authorization

- [x] Owner authorizes bounded 2026 market acquisition and frozen Stage 3B fitting/evaluation without further approval requests.
- [x] Scope remains Jun1–Oct9 half-open UTC, eight frozen M1 series, one capped attempt, D-120 cold start, D-121 macro fail-closed semantics.
- [x] Targeted exact-runtime/provider CI is allowed when technically necessary for this bounded package.
- [x] D-125 admits exact D-124 authorization SHA `c99ad84e4b7254d074b96df7a5f4c371ccbe01c2` into the machine-readable plan and `AUTHORIZED_FINAL_DECISION_SHAS`; exact-runtime no-provider preflight triggered.


## D-125 exact-runtime gate

- [x] D-124 SHA admitted as the sole execution token.
- [x] Machine-readable plan changed to FINAL_APPROVED for the exact bounded package; broker remains false.
- [x] Path-isolated exact-runtime no-provider workflow created/triggered.
- [x] D-126 exact-runtime CI PASS: run 45896702785 / job 140172268991; CPython3.12.14 frozen lock verified, 22/22 tests pass, no provider data/model fit.


## D-127 pipeline implementation gate

- [x] Strict bounded provider/date/symbol/raw-size validator implemented.
- [x] Bounded cold-start causal information-layer builder implemented.
- [x] Frozen D-116 teacher-to-market join implemented for 250 eligible events / expected 343 candidate minutes.
- [x] Frozen GOLD/FULL 39-date LODO logistic benchmark, bootstrap and advancement rule implemented.
- [x] One-attempt production provider workflow implemented **without its trigger file**.
- [x] Synthetic exact-runtime end-to-end rehearsal workflow and trigger committed.
- [x] D-127 synthetic rehearsal PASS: run 45897637362 / job 140175383322; complete real-teacher/fake-market pipeline exercised successfully.
- [x] Real provider attempt remains unspent through D-128; unexpected production Actions record 45897634530 had zero jobs/no runner/no provider command.


## D-128 production trigger hardening

- [x] Removed brittle GITHUB_RUN_NUMBER guard after zero-job workflow record consumed run number 1.
- [x] Production workflow requires D-124 execution commit marker + exact one-time trigger contents + GITHUB_RUN_ATTEMPT=1 before provider step.
- [x] Fixed workflow workspace context so YAML does not depend on runner context at job-level env.
- [ ] Actual one-time provider trigger file remains absent until D-129.


## D-129 production-workflow parse validation

- [x] D-128 synthetic revalidation PASS: run 45897995539 / job 140176557797.
- [x] Root cause of zero-job production records identified: malformed unindented heredoc in workflow YAML; zero provider jobs/requests.
- [x] Production workflow repaired with indentation-safe exact trigger comparison.
- [x] Validation-only trigger content prepared; D-129 commit intentionally lacks execution marker so provider job must skip.
- [x] D-129 production workflow parsed cleanly: run 45898223471 concluded skipped, no provider job.
- [x] D-130 replaces placeholder once with exact frozen provider trigger and required execution marker; single real attempt is now triggered.


## D-130 real execution

- [x] D-129 parser validation clean/skipped.
- [x] Exact D-130 trigger payload committed with D-124 authorization SHA and bounded scope.
- [x] Commit message contains required `[STAGE3B_PROVIDER_EXECUTE_D124]` marker.
- [ ] Poll and record the single real provider/build/benchmark workflow. **No rerun.**
- [ ] Verify compact artifact contains reports/manifests only and raw/derived provider payloads were removed.
- [ ] Record frozen scientific result and keep Stage4/5 blocked unless separately authorized.


## D-131 pre-provider ordering repair

- [x] D-130 failure inspected: run 45898387479 / job 140177881034 failed before checkout.
- [x] Confirmed all provider acquisition, dataset build and model fitting steps skipped.
- [x] Single D-124 provider acquisition attempt remains unspent.
- [x] Checkout moved before immutable trigger-file guard.
- [x] Pipeline test now asserts checkout precedes trigger guard.
- [x] Future exact execution payload versioned to D-132.
- [ ] D-131 no-provider regression rehearsal must PASS before D-132 trigger.
