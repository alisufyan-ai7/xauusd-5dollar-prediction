# Ready-to-Use New Chat Prompt — Chat 05

Continue **XAUUSD 5dollar Prediction** from GitHub; fetch the active branch HEAD fresh.

Current durable state:
- D116 teacher: 107 ACT / 143 P3 / 39 dates; SHA `8089c9d9d4ade14bf1cd037331d298e787276657a2056daf0bbb2c84325433cd`.
- features: 92 GOLD / 155 FULL; SHA `44a73f70a51f3c364ef53c5dc6353443e348e0a86bc9142fa6b8919fbe986104`.
- 39-fold SHA `56a1c301cfebc78373793db10d7099aab9391b33e1470c869b714261ba677ec5`.
- frozen market scope Jun1–Oct9 exclusive, eight series, D120 bounded cold start, D121 macro fail closed, frozen L2 logistic benchmark/gates.
- D132 original 1.50.0 attempt failed with zero-byte first XAUUSD BID file; no model.
- D134 authorized one 1.51.1 transport-only recovery.
- D135 no-market-provider preflight passed.
- D136 recovery run **45901570026** / job **140188341343** consumed that recovery: the fixed XAUUSD BID Jun1→Jun2 sanity endpoint returned **plain HTTP 403, WAF token=no**. No file saved, full acquisition never started, no model.
- D137 freezes the result as **provider-access failure / Stage3B NOT TESTED** and disables all recovery provider/model execution.

Artifact D136: ID **15156486347**, digest `sha256:3c12148febd6ae8f624510541440750064a52b5a301d42a5e6b62888eb119742`; only sanitized JSON/log/hash evidence, no market/model data.

Do not rerun D132 or D136 and do not make another Dukascopy market request under old authorizations.

Safe next work: owner-independent repository/upstream research and design of a new **provider-access strategy**. Any future live provider attempt requires a new explicit owner authorization after that strategy is frozen. Keep 2022–2025, Oct9–Nov30, December shadow, 2027, Stage4/5 and broker actions blocked.
