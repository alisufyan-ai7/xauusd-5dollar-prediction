# Stage 3B 2026 — Provider Transport Recovery Proposal

**STATUS: CONSUMED — D-136 RECOVERY ATTEMPT FAILED WITH PLAIN HTTP 403; NO RERUN**

Parent decisions: D-124 and D-133.

## Purpose

Recover only from the D-132 provider-transport failure. This proposal does **not** change the scientific hypothesis, teacher corpus, market window, features, folds, model, metrics, advancement threshold, sealed periods or broker restrictions.

No Stage 3B market/model result exists yet.

## Frozen scientific scope retained unchanged

- market fence: `2026-06-01T00:00:00Z <= t < 2026-10-09T00:00:00Z`
- teacher: D-116 canonical SHA `8089c9d9d4ade14bf1cd037331d298e787276657a2056daf0bbb2c84325433cd`
- features: 92 GOLD / 155 FULL, SHA `44a73f70a51f3c364ef53c5dc6353443e348e0a86bc9142fa6b8919fbe986104`
- folds: 39 LODO dates, SHA `56a1c301cfebc78373793db10d7099aab9391b33e1470c869b714261ba677ec5`
- eight market series only
- D-120 bounded June1 cold start
- D-121 fail-closed macro policy
- same L2 logistic Task A/Task B, event weighting/pooling, metrics, bootstrap and frozen advancement rule
- 2022–2025, Oct9–Nov30, December shadow and 2027 remain forbidden
- no broker/order action

## Proposed transport-only change

Replace the frozen Dukascopy transport:
- from `dukascopy-node 1.50.0`
- to **`dukascopy-node 1.51.1`**

Reason: upstream 1.51.1 was released after the D-124 transport pin and includes export-widget header / 403-handling changes relevant to the WAF/zero-byte failure class documented in issues #261/#264.

The recovery implementation must:
1. pin 1.51.1 exactly;
2. record transport/debug diagnostics sufficient to distinguish WAF 202/403 from valid empty market data, without logging credentials/private licence material;
3. fail closed on 0-byte output, HTTP challenge/failure, out-of-fence rows or budget overflow;
4. not source-shop or change provider;
5. not inspect model outcomes until all eight authorized market inputs pass integrity;
6. delete raw provider payloads before compact artifact upload;
7. allow exactly **one new recovery attempt**, with no rerun.

## Proposed one-job recovery sequence

Inside one newly authorized attempt:
1. exact runtime and all current no-provider tests;
2. transport sanity request using 1.51.1 **inside the same D-124 date fence** and same authorized XAUUSD BID source;
3. if the sanity request is valid, continue the same job to the full bounded eight-series download/build/benchmark;
4. if sanity fails, stop the attempt and record transport diagnostics; do not retry with another client/provider.

The sanity request is part of the one recovery attempt, not an extra attempt.

## D-134 owner decision

The owner explicitly authorized **one transport-recovery attempt** under this proposal using pinned `dukascopy-node 1.51.1`, with all D-124 scientific scope unchanged. No licence paperwork is requested; the existing owner-attested Dukascopy permission remains accepted.

Execution remains provider-disabled until the exact D-134 authorization commit SHA is admitted into the recovery guard, 1.51.1 diagnostics are implemented, and the no-provider exact-runtime regression passes. No further owner approval is required after those prerequisites; no rerun is authorized.


## D-137 closure

The D-134-authorized one recovery attempt was consumed by D-136. Pinned `dukascopy-node 1.51.1` requested the fixed XAUUSD BID Jun1→Jun2 sanity endpoint and received a plain HTTP 403 with `WAF token: no`. The library correctly did not treat a plain 403 as a WAF challenge. No file was saved, the full eight-series acquisition did not start, and no model was fitted.

This recovery proposal is therefore **closed/consumed**. It is not permission for another attempt. Any future access strategy must be separately proposed and authorized.
