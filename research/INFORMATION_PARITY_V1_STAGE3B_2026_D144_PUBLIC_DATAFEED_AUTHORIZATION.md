# D-144 — Owner Authorization for One D-140 Credential-Free Public Datafeed Attempt

**STATUS: AUTHORIZED / ONE ATTEMPT ONLY / NO RERUN**

Owner authorization, recorded verbatim:

> **I authorize one Stage 3B provider-access attempt under D-140 using the preregistered DUKASCOPY_PUBLIC_DATAFEED_DIRECT_M1_V1 representation, limited to the frozen eight logical M1 series and 2026-06-01T00:00:00Z <= t < 2026-10-09T00:00:00Z, with exactly eight June 1 sanity GETs first, a hard maximum of 1,050 GETs, 350 MiB raw data, 750 MiB normalized/intermediate data, one attempt, zero retries after provider failure, and no alternate host or source. All existing D-124 teacher data, 92/155 features, 39 LODO folds, models, thresholds, date boundaries, sealed periods, and broker restrictions remain unchanged. No rerun is authorized.**

## Scope

This authorization applies only to the D-140 source representation:

`DUKASCOPY_PUBLIC_DATAFEED_DIRECT_M1_V1`

Frozen market series:
1. XAUUSD BID
2. XAUUSD ASK
3. EURUSD BID
4. USDJPY BID
5. GBPUSD BID
6. USDCAD BID
7. USDSEK BID
8. USDCHF BID

Frozen provider fence:
- start inclusive: `2026-06-01T00:00:00Z`
- end exclusive: `2026-10-09T00:00:00Z`

Frozen execution ceilings:
- exactly 8 June 1 sanity GETs before any full acquisition;
- hard maximum 1,050 GETs total;
- 350 MiB raw payload;
- 750 MiB normalized/intermediate payload;
- one provider attempt;
- zero retries after provider failure;
- no alternate host, mirror, VPN, proxy, provider or representation inside the attempt.

## Scientific invariants

D-144 changes provider access only. It does not change:
- D-116 teacher corpus;
- 92 GOLD / 155 FULL feature allowlists;
- 39 leave-one-date-out folds;
- D-120 bounded cold-start semantics;
- D-121 macro fail-closed policy;
- fixed L2 logistic models;
- event weighting/pooling;
- bootstrap/metrics/advancement thresholds;
- 2022-2025 sealed periods;
- 2026-10-09 through 2026-11-30 quarantine;
- December shadow restrictions;
- broker/order prohibitions.

D-132 and D-136 remain consumed and must never be rerun.

## Execution gate

This authorization alone does not make a provider request. The exact D-144 commit SHA must first be admitted into a new D-140 execution guard, deterministic no-provider tests must pass, and the provider workflow must remain impossible to trigger until that technical gate is accepted.

No further routine owner approval is required for this exact D-144 package. Any failure consumes the authorized attempt; no rerun is authorized.
