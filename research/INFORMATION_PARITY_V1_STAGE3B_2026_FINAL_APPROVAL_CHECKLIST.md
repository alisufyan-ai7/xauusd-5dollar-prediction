# D-118 — Second Owner Approval / Bounded 2026 Execution Checklist

**CURRENT STATUS: D-119 CODE-ONLY PREFLIGHT COMPLETE; NOT READY FOR EXECUTION APPROVAL. D-088 CLOSED.**

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
- [ ] Exact pins/model solver documented in Stage 3B lock; **pending** installation and reproducibility checks under CPython 3.12.14 (local tests used Python 3.13.5 stdlib only).
- [x] Commit exact source-only 39-date fold manifest, hash and synthetic candidate-minute/weight/event-pooling fixtures; 11 local no-provider tests pass.
- [ ] Resolve June 1 warm-up: Stage 2 has unbounded last-swing/FVG memory; **cannot certify** 35-day warm-up as exact continuous-state parity without new state/cold-start/authorized-history decision.
- [ ] Obtain explicit rights/terms clearance for automated Dukascopy acquisition (Bank TCU restrict bots without prior express written consent), verify quota/entitlement; only a coarse TRAIN-derived 2026 size estimate exists.
- [ ] Complete event-by-event point-in-time macro calendar publication/revision proof; primary 2026 BLS/Fed/BEA/DOL archive pages reviewed but historical as-of versions not certified.
- [ ] Expand code-only date/symbol/budget guards into a future acquisition wrapper with mandatory independent authorization token, retention/deletion and secrets handling; no provider work permitted.
- [x] Run deterministic **off-CI no-provider** guard tests: 11/11 pass, covering date fences, folds, 1/k, parity, missingness-related manifest guards, causal availability and calendar/DST. Full runtime/provider-row tests remain separate.
- [ ] D-119 report is committed; resolve independently recorded provider rights, calendar as-of, infinite-state warm-up, exact runtime and acquisition wrapper blockers before final review. Never quietly widen.
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
