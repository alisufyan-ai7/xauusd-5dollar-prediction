# Ready-to-Use New Chat Prompt — Chat 05

Continue **XAUUSD 5dollar Prediction** from GitHub. Fetch the active branch HEAD fresh and treat GitHub as source of truth.

Repository: `alisufyan-ai7/xauusd-5dollar-prediction`  
Branch: `research/information-parity-v1-stage3-preregistration`

Read PROJECT_CONTINUITY, DECISION_LOG, NEW_CHAT_HANDOFF, PROJECT_DOCUMENTATION_PROTOCOL, D133 failure findings, D133 recovery proposal, D134 authorization, and D135 recovery implementation findings plus current manifests/scripts/tests/workflows.

Frozen science remains unchanged: D116 teacher SHA `8089c9d9d4ade14bf1cd037331d298e787276657a2056daf0bbb2c84325433cd`; 92 GOLD / 155 FULL feature SHA `44a73f70a51f3c364ef53c5dc6353443e348e0a86bc9142fa6b8919fbe986104`; 39-fold SHA `56a1c301cfebc78373793db10d7099aab9391b33e1470c869b714261ba677ec5`; Jun1–Oct9 exclusive; eight market series; bounded cold start; macro fail closed; frozen L2 logistic benchmark/gates.

D132 original provider attempt returned zero bytes on first XAUUSD BID request; no model fit, Stage3B NOT TESTED. Do not rerun D132.

D134 explicitly authorizes one new transport-only recovery attempt using pinned dukascopy-node 1.51.1 with no scientific changes and no rerun.

D135 implements the recovery but **provider execution remains disabled** until its exact-runtime no-market-provider preflight passes. It adds selective WAF/HTTP diagnostics, classification/redaction, ephemeral WAF cache, a same-attempt XAUUSD BID Jun1→Jun2 sanity request, and the unchanged full eight-series acquisition/build path.

Immediate work:
1. inspect/poll the D-135 exact-runtime no-provider recovery preflight;
2. if PASS, record it, then enable/trigger exactly one D-134 recovery provider attempt without asking the owner again;
3. never rerun the recovery attempt;
4. record scientific result only if all eight market files validate and the frozen benchmark actually fits;
5. keep sealed periods, Stage4/5 and broker actions blocked.
