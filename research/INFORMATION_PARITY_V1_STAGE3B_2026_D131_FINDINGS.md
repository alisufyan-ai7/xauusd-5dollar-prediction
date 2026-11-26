# D-131 — Correct Pre-Provider Guard Ordering and Rehearse Again Without Provider Data

**STATUS AT COMMIT: D-130 STOPPED BEFORE PROVIDER; CORRECTED ORDER UNDER NO-PROVIDER REGRESSION TEST**

D-130 workflow:
- run **45898387479**
- job **140177881034**
- conclusion **FAILURE BEFORE CHECKOUT**
- failing step: `One-attempt immutable trigger guard`
- cause: trigger-file existence was checked before `actions/checkout`.
- provider acquisition/build/model steps: **all skipped**.
- artifact 15154104349 contains only failure bookkeeping; it is not scientific evidence and not a provider-data artifact.

Therefore the single D-124 provider acquisition attempt remains **unspent**.

D-131 moves checkout before the immutable-trigger guard. The production workflow's exact future trigger payload is versioned forward to **D-132**. A regression assertion now verifies that the Checkout step appears before the trigger guard in the production workflow.

D-131 triggers only the exact-runtime synthetic no-provider rehearsal again. It does not modify the real provider trigger path and therefore cannot start provider acquisition. If this regression rehearsal passes, D-132 may replace the current trigger file with the exact D-132 payload and execute the single real provider attempt.
