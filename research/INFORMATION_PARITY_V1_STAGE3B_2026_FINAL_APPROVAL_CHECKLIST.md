# D-118 — Second Owner Approval / Bounded 2026 Execution Checklist

**CURRENT STATUS: D-120 OWNER ACCESS CONFIRMED / 17 SYNTHETIC TESTS PASS; FINAL EXECUTION APPROVAL STILL PENDING. D-088 CLOSED.**

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
- [ ] D-120 documents dated Federal Reserve 2024 prior notice, BLS monthly modified dates and 11 examples (8 prior-schedule candidates, 3 unknown); complete provider-free event-by-event macro provenance or freeze fail-closed missingness coverage/stop rule.
- [ ] D-120 adds fail-closed authorization, cold-start, calendar/version and window tests; integrate into a complete future acquisition wrapper, with separate final approval token and retained no-data/secret policies before any provider call.
- [x] No-provider off-CI Python standard-library tests: **17/17 pass**, including six new D-120 tests for owner-final-execution rejection, calendar as-of, bounded cold start and feature leakage. Exact full-runtime/provider-row tests remain separate.
- [ ] D-120 report/owner-access attestation committed. Continue calendar coverage, exact runtime and acquisition-wrapper checks independently. Rights attestation and bounded cold-start design are recorded; never silently widen.
- [ ] Obtain **new explicit owner approval for completed, versioned execution plan** and record the separate chronology authorization decision.

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
