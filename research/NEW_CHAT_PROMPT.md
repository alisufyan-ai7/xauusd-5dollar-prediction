# Ready-to-Use New Chat Prompt — Chat 05

Copy/paste the block below into the next chat when Chat 04 is near its practical context limit.

---

You are continuing the GitHub-backed project **XAUUSD 5dollar Prediction**.

This is **Chat 05**. GitHub is the source of truth; do **not** rely on prior-chat memory, summaries, or assumptions when the repository can be read directly.

Repository:
`alisufyan-ai7/xauusd-5dollar-prediction`

Active research branch:
`research/information-parity-v1-stage3-preregistration`

The last verified Chat 04 checkpoint before this prompt was created is commit:
`61937af3196a73cae7551234ee56d334438a8838`

**Important:** that SHA is only a checkpoint. First inspect the branch fresh; if HEAD is newer, use the newer GitHub state.

### Mandatory bootstrap

Before doing new work:
1. fetch the active branch HEAD;
2. read `research/PROJECT_CONTINUITY.md`;
3. read the latest decisions in `research/DECISION_LOG.md`;
4. read `research/NEW_CHAT_HANDOFF.md`;
5. read `research/PROJECT_DOCUMENTATION_PROTOCOL.md`;
6. read the Stage 3B bounded-2026 protocol, latest findings and final-approval checklist referenced by continuity;
7. inspect actual manifests/code/tests relevant to the next task rather than trusting this prompt alone.

### Current scientific/project checkpoint

As of the D-122/D-123 handoff:
- Stage 2 Information Parity V1 on **2016–2021 TRAIN** is accepted.
- Frozen Stage 3B source teacher (D-116): **107 eligible ACT**, **143 eligible P3 REJECT/WAIT**, **39 paired source dates**, **47 LONG / 60 SHORT**.
- Canonical teacher SHA-256:
  `8089c9d9d4ade14bf1cd037331d298e787276657a2056daf0bbb2c84325433cd`.
- Static 2026 feature allowlist: **92 GOLD**, **155 FULL total**; SHA-256:
  `44a73f70a51f3c364ef53c5dc6353443e348e0a86bc9142fa6b8919fbe986104`.
- Frozen source-date fold manifest: **39 LODO folds**; SHA-256:
  `56a1c301cfebc78373793db10d7099aab9391b33e1470c869b714261ba677ec5`.
- Source intervals expand to **343 candidate M1 rows** over 250 primary-eligible source events.
- Option B bounded-2026 protocol is **design-approved in principle only**.
- Proposed market source fence: `2026-06-01T00:00:00Z <= t < 2026-10-09T00:00:00Z`.
- Frozen teacher dates are Jul 6–Oct 8, 2026; Oct 9–Nov 30 quarantine; Dec 1–Dec 31 prospective shadow is separately unauthorized.
- Owner explicitly confirmed having written Dukascopy automated historical-data permission/licence. **Do not ask for licence paperwork again.**
- June 1 structural initialization is a transparently disclosed **bounded cold start**; it is not claimed equivalent to uninterrupted Stage 2 history.
- Point-in-time macro schedule uses source-versioned historical publication evidence or fails closed/unavailable; do not reconstruct missing knowledge from later releases.
- No-provider local synthetic suite currently reports **22/22 PASS** on the available Python 3.13.5 runner.
- Exact designated Stage 3B runtime is CPython 3.12.14 with the pinned lock; it is **not yet exactly reproduced** in the available offline runtime.
- D-122 hardened the approval gate: `AUTHORIZED_FINAL_DECISION_SHAS` is deliberately empty. Editing the JSON plan or inserting a fake SHA cannot authorize execution.
- Machine-readable acquisition plan remains `DESIGN_ONLY_NOT_APPROVED`; provider download/model flags remain false.

### Hard governance boundaries

**D-088 remains CLOSED.**
Do not:
- acquire 2026 provider market data;
- fit Stage 3B models;
- run provider-data CI;
- open sealed 2022–2025 periods;
- acquire the December shadow period;
- place/modify broker orders;
- silently widen dates, sources, features, model family, thresholds or experiment semantics.

The owner previously required a **separate explicit final approval** for the completed bounded 2026 acquisition/model-fitting package. That approval has not been given.

### Immediate owner-independent work

Continue without routine questions:
1. attempt/verify the exact pinned CPython 3.12.14 no-provider runtime in an eligible environment if available;
2. complete/review the future acquisition wrapper and its fail-closed date/symbol/budget/secrets/raw-retention protections **without calling the provider**;
3. finish the no-hindsight macro availability mask/coverage implementation under the frozen fail-closed rule;
4. ensure the exact feature-table schema dry run and parity/leakage guards are ready;
5. keep tests deterministic and off-CI unless an exact-runtime dependency truly requires a justified CI check;
6. update all project docs after each material execution.

Only return to the owner for a decision when the completed, versioned execution package is genuinely ready for the reserved final authorization, or if a new out-of-scope boundary change is unavoidable.

### Documentation discipline

After every material execution:
- update `research/DECISION_LOG.md` if a material decision changed;
- update `research/PROJECT_CONTINUITY.md`;
- update `research/NEW_CHAT_HANDOFF.md`;
- refresh this `research/NEW_CHAT_PROMPT.md` when status/next actions change;
- update `README.md` if high-level status changed;
- commit on the active branch and verify branch HEAD before reporting completion.

Do not blindly trigger CI. Do local deterministic review first and use CI only for a demonstrated need.

Now inspect GitHub fresh and resume the immediate owner-independent work from the authoritative current state.

---
