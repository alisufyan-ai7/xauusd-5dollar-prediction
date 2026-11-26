# New Chat Handoff — Chat 04 -> Chat 05

D134 owner authorization: exactly one transport-only recovery using pinned dukascopy-node 1.51.1; all D-124 science unchanged, no rerun.

D135 preflight PASS: run **45901246019**, job **140187267884**; exact runtime/package/browser verified, 30/30 deterministic tests and synthetic pipeline PASS, no market-provider request.

D136: one-time recovery workflow/trigger is active. It is bound to exact D134 SHA, D135 preflight identity, exact trigger contents and GITHUB_RUN_ATTEMPT=1. It first requests XAUUSD BID Jun1→Jun2 sanity; only success allows full frozen eight-series acquisition and benchmark in the same attempt.

Immediate work: poll D136; never rerun it. Record transport diagnostics on failure or frozen scientific result only if all eight inputs validate and model fitting completes. Stage4/5 and sealed periods remain blocked.
