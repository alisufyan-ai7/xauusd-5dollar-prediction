# New Chat Handoff — Chat 04 -> Chat 05

**Current chat:** Chat 04  
**Next chat:** Chat 05  
**Repository:** `alisufyan-ai7/xauusd-5dollar-prediction`  
**Active branch:** `research/information-parity-v1-stage3-preregistration`

Read `research/NEW_CHAT_PROMPT.md` and `research/PROJECT_DOCUMENTATION_PROTOCOL.md`.

## Current state after D-134

D132 spent the original D-124 provider attempt: first XAUUSD BID M1 request returned a zero-byte file, no usable market rows, no dataset/model, Stage3B **NOT TESTED**. D133 closed that path fail-closed.

The owner has now explicitly authorized **one transport-only recovery attempt** under D-133:
- pin `dukascopy-node 1.51.1`;
- keep the exact D-124 dates, eight symbols, D116 teacher, GOLD/FULL features, 39 LODO folds, L2 logistic models, metrics/thresholds and sealed periods unchanged;
- same-attempt XAUUSD BID sanity request is permitted;
- if sanity succeeds, continue in that same attempt to the full frozen bounded acquisition/build/benchmark;
- no rerun.

Provider access is still disabled until the exact D-134 commit SHA is admitted to the recovery guard/manifest, WAF/HTTP diagnostics and fail-closed tests are implemented, and exact-runtime no-provider regression passes. Once those prerequisites pass, do **not** ask the owner again for this recovery attempt.

2022–2025, Oct9–Nov30, December shadow, 2027, extra providers/symbols/features/models, Stage4/5 and broker actions remain blocked.
