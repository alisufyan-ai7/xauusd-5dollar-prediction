# Project Documentation and Chat Continuity Protocol

Status: **MANDATORY PROJECT OPERATING RULE**

Repository: `alisufyan-ai7/xauusd-5dollar-prediction`
Active research branch: `research/information-parity-v1-stage3-preregistration`

## 1. GitHub is the source of truth

Chat history is transient. Material project state must live in GitHub. Never rely on a prior chat as the only location for:
- current stage/status;
- frozen decisions and rationale;
- dataset/manifests/hashes;
- branch/commit identities;
- scientific restrictions;
- owner approvals or withheld approvals;
- unresolved blockers;
- exact next work;
- reproducibility/test status;
- provider/data boundaries;
- handoff instructions.

If chat and GitHub disagree, inspect the latest active-branch files and commits before proceeding. Do not silently overwrite a frozen decision; create a new decision/addendum.

## 2. Post-execution documentation checklist

After **every material execution** (code change, research decision, source adjudication, test run, protocol change, data-boundary change, new blocker, blocker resolution, or owner approval), before reporting completion:

1. update `research/DECISION_LOG.md` when a material decision/rule changed;
2. update `research/PROJECT_CONTINUITY.md` with exact current state and immediate next owner-independent work;
3. update `research/NEW_CHAT_HANDOFF.md` so a new chat can resume without prior-chat memory;
4. update `research/NEW_CHAT_PROMPT.md` if current decision/status/next work changed;
5. update `README.md` when high-level project status changed;
6. update any experiment-specific checklist/findings/manifest affected by the work;
7. commit changes on the active research branch;
8. verify the branch HEAD and re-open critical files before claiming completion.

Do not claim an action is committed merely because blobs/trees were created; verify the branch ref moved.

## 3. Chat numbering and rollover

Current conversation at D-123: **Chat 04**.
Next conversation: **Chat 05**.

When a chat approaches practical context limits:
- do not wait until continuity is lost;
- refresh `NEW_CHAT_HANDOFF.md` and `NEW_CHAT_PROMPT.md` first;
- commit and verify them;
- give the user the ready-to-copy prompt from `NEW_CHAT_PROMPT.md`;
- the new chat must read GitHub fresh before taking action.

After rollover, change chat numbers in these files (Chat 05 -> Chat 06, etc.) as part of the first or next material documentation commit.

## 4. New-chat bootstrap rule

A new chat must:
1. inspect branch `research/information-parity-v1-stage3-preregistration` fresh and record current HEAD;
2. read `research/PROJECT_CONTINUITY.md`;
3. read latest entries of `research/DECISION_LOG.md`;
4. read `research/NEW_CHAT_HANDOFF.md`;
5. read the currently relevant protocol/findings/checklist referenced by continuity;
6. inspect actual code/manifests before editing;
7. never assume a result from the handoff if GitHub has changed;
8. continue owner-independent work without asking routine questions.

## 5. Owner-escalation rule

Do not stop for owner input when work is:
- documentation;
- static review;
- code-only implementation;
- deterministic no-provider testing;
- source/provenance review;
- runtime/environment investigation that does not use protected data;
- maintaining manifests/checklists.

Ask the owner only when an explicit owner decision is genuinely required, such as:
- final authorization previously reserved to owner;
- expanding a frozen date/data/source boundary;
- changing the registered scientific experiment in a material way;
- external entitlement/cost/credential action only the owner can provide.

Already-recorded owner decisions must not be re-asked. In particular:
- owner confirmed possession of written Dukascopy automated-data permission/licence;
- **do not request that licence paperwork again**;
- owner approved Option B **in principle only**;
- final 2026 market acquisition/model-fitting approval has **not** been granted.

## 6. Current protection boundary

As of D-123:
- D-088 remains **CLOSED**;
- no 2026 market acquisition or model fitting has been authorized;
- no provider CI run is authorized;
- 2022–2025 remain sealed;
- December shadow remains separately unauthorized;
- no broker/order mutations.

This file is an operating rule, not an authorization to relax those protections.
