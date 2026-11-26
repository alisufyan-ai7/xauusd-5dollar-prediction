# Ready-to-Use New Chat Prompt — Chat 05

You are continuing the GitHub-backed project **XAUUSD 5dollar Prediction**. This is **Chat 05**.

Repository: `alisufyan-ai7/xauusd-5dollar-prediction`  
Active branch: `research/information-parity-v1-stage3-preregistration`

GitHub is the source of truth. First fetch branch HEAD fresh, then read:
1. `research/PROJECT_CONTINUITY.md`
2. latest `research/DECISION_LOG.md`
3. `research/NEW_CHAT_HANDOFF.md`
4. `research/PROJECT_DOCUMENTATION_PROTOCOL.md`
5. `research/INFORMATION_PARITY_V1_STAGE3B_2026_D133_PROVIDER_FAILURE_FINDINGS.md`
6. `research/INFORMATION_PARITY_V1_STAGE3B_2026_PROVIDER_TRANSPORT_RECOVERY_PROPOSAL.md`
7. bounded-2026 protocol/checklist/manifests/scripts/tests relevant to current state.

### Frozen project state

- Stage2 accepted 2016–2021 TRAIN.
- D116 teacher: 107 ACT / 143 P3 / 39 paired dates / 47 LONG / 60 SHORT.
- teacher SHA `8089c9d9d4ade14bf1cd037331d298e787276657a2056daf0bbb2c84325433cd`.
- features: 92 GOLD / 155 FULL; SHA `44a73f70a51f3c364ef53c5dc6353443e348e0a86bc9142fa6b8919fbe986104`.
- folds: 39 LODO dates; SHA `56a1c301cfebc78373793db10d7099aab9391b33e1470c869b714261ba677ec5`.
- owner has written Dukascopy automated-data permission; do not ask for paperwork.
- D124 authorized one bounded provider attempt and model fit.
- D132 spent that provider attempt: run 45898796339 / job 140179219355.
- First XAUUSD BID M1 request returned a 0-byte file; no later symbol requested.
- usable market rows = 0; no dataset/model; Stage3B = **NOT TESTED**.
- artifact 15155230246 digest `sha256:1ffaac4dc19f6b4edaf8075ef197a53cd0b182fabf57bf7d7dfe0ace92cf8e14`, contains failure bookkeeping only.
- D133 current plan is disabled/fail-closed; no provider/model/CI execution authorized under D124.
- likely transport cause is compatible with upstream Oct-2026 WAF changes; frozen 1.50.0 transport predates 1.51.1 fixes, but D132's exact HTTP code was not observed.

### Current action boundary

Do **not** rerun D132 or issue any provider request under D124.

A transport-only recovery proposal preserves all science and proposes pinned `dukascopy-node 1.51.1` plus exactly one new recovery attempt. It is **proposal only** until owner explicitly authorizes it.

If owner authorizes the transport recovery:
1. record a new GitHub decision;
2. pin the new transport and add WAF/HTTP diagnostics;
3. run only no-provider/static tests first;
4. execute exactly one new recovery provider attempt inside the same dates/symbols/science;
5. never rescue-tune teacher/features/model/gates;
6. keep 2022–2025, quarantine/shadow, Stage4/5 and broker actions blocked;
7. update all project docs after every material step.

Do not re-ask already-settled licence or general model authorization questions. The only currently needed owner decision is whether to authorize the specifically proposed **one transport-recovery attempt**.
