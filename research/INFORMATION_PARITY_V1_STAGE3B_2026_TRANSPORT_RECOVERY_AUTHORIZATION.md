# D-134 — Final Owner Authorization for One Stage 3B Provider-Transport Recovery Attempt

**STATUS: AUTHORIZED — ONE TRANSPORT-RECOVERY ATTEMPT ONLY**

Date: 2026-11-27 Pakistan time.

The owner explicitly authorized:

> one Stage 3B provider-transport recovery attempt under the D-133 recovery proposal, using pinned dukascopy-node 1.51.1, while keeping all existing D-124 scientific dates, symbols, teacher data, features, folds, models, thresholds and sealed-period restrictions unchanged.

## Authorized change

The only authorized design change is provider transport:
- old frozen transport: `dukascopy-node 1.50.0`
- recovery transport: **`dukascopy-node 1.51.1`**
- exactly **one new recovery provider attempt**

The recovery attempt may include the D-133-proposed XAUUSD BID sanity request inside the existing D-124 market fence and, if that transport sanity check returns valid data, continue within the **same recovery attempt** to the full frozen eight-series bounded acquisition/build/benchmark.

## Scientific scope remains frozen

Unchanged:
- market window: `2026-06-01T00:00:00Z <= t < 2026-10-09T00:00:00Z`
- teacher SHA: `8089c9d9d4ade14bf1cd037331d298e787276657a2056daf0bbb2c84325433cd`
- feature allowlist: 92 GOLD / 155 FULL, SHA `44a73f70a51f3c364ef53c5dc6353443e348e0a86bc9142fa6b8919fbe986104`
- folds: 39 source-date LODO, SHA `56a1c301cfebc78373793db10d7099aab9391b33e1470c869b714261ba677ec5`
- eight market series only
- D-120 bounded June1 cold start
- D-121 fail-closed macro policy
- L2 logistic Task A / Task B
- event/class weighting and event pooling
- preregistered metrics, bootstrap and advancement thresholds
- raw and normalized byte caps
- no source-shopping, provider-shopping, model-shopping or rescue tuning.

Still forbidden:
- 2022–2025
- `2026-10-09T00:00:00Z` through November 30 2026
- December 2026 shadow
- 2027
- extra symbols/providers/features/model families/hyperparameter searches
- macro actual/forecast/previous/surprise
- Stage4/Stage5 automatic execution
- broker/Exness/order mutation.

## Required implementation sequence

Before the recovery provider call:
1. this exact D-134 commit SHA must be admitted in the recovery execution guard and machine-readable plan;
2. `dukascopy-node 1.51.1` must be pinned exactly;
3. transport diagnostics must distinguish WAF/challenge/HTTP failure from valid empty-market conditions without logging credentials/licence material;
4. no-provider/static regression must pass under the exact frozen runtime;
5. provider/model execution stays disabled until those implementation guards are committed and verified.

After those checks, no further owner approval is required for the single authorized recovery attempt.

No rerun is authorized if the recovery attempt fails.
