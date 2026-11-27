# D-138 — Stage 3B Provider-Access Strategy Proposal: Official Dukascopy Requester-Pays S3

**STATUS: PREREGISTERED BUT OPERATIONALLY INFEASIBLE UNDER D-139 — NO S3 ACCESS**

Parent decisions: D-124, D-133, D-134, D-137.

## Why a new access strategy is necessary

D-136 proved that the current Dukascopy JETTA/export transport is not merely suffering an old-client parsing bug:
- pinned `dukascopy-node 1.51.1`;
- exact supported headers/browser surface installed;
- fixed XAUUSD BID sanity endpoint;
- direct **HTTP 403**;
- `WAF token: no`;
- no file saved.

The current upstream `dukascopy-node` repository still reports **1.51.1** as its package version. There is no newer published package version to preregister as another transport retry.

Issue #264 also contains a 2026-11-27 report that the Dukascopy historical-data widget itself is down. This is supporting operational context only; D-136's direct HTTP 403 remains the project evidence.

## Official Dukascopy alternative

Dukascopy's current official Wiki documents a separate Historical Price Data distribution path:
- S3 bucket: `cfg-public-proper-wallaby`
- AWS region: `eu-west-1`
- policy: **Requester Pays**
- authenticated AWS credentials required
- daily `.bi5` tick objects
- current path convention: `SYMBOL/YEAR/MM0/DD_ticks.bi5`
- current daily record format: 20-byte big-endian `>IIIff`
  - milliseconds since UTC day start
  - ask integer price
  - bid integer price
  - ask float volume
  - bid float volume
- missing daily object means no recorded ticks for that day, not an empty-file error.

Source: https://wiki.dukascopy.com/en/development/data-export/

This is the **same provider** but a materially different access/data representation. It is not authorized by D-124 or D-134.

## Recommended route — S3 tick reconstruction

Proposed source identity:

`DUKASCOPY_S3_TICK_RECONSTRUCTED_M1_V1`

This route intentionally does **not** claim raw-bar identity with the accepted Stage-2 JETTA M1 files. The accepted Stage-2 run retained only compact manifests/hashes, not the original M1 payload, so exact bar-by-bar parity cannot now be independently demonstrated from repository artifacts.

Because no Stage-3B model has ever been fitted, this representation change can still be preregistered before any model result exists.

### Seven underlying S3 instruments

A single tick object contains both ask and bid, so seven underlying prefixes produce the frozen eight Stage-3B series:

1. `XAUUSD` -> XAUUSD BID + ASK
2. `EURUSD` -> EURUSD BID
3. `USDJPY` -> USDJPY BID
4. `GBPUSD` -> GBPUSD BID
5. `USDCAD` -> USDCAD BID
6. `USDSEK` -> USDSEK BID
7. `USDCHF` -> USDCHF BID

The first paid/discovery action must confirm these exact prefixes exist in the official bucket. If any required prefix is absent, **stop the attempt**. No provider/source fallback is allowed inside the same attempt.

## Frozen price-scale metadata

Pinned Dukascopy metadata source:
- repository: `Leo4815162342/dukascopy-node`
- source commit: `068bf57b67e3cae3f5c952653ef20157d3852699`
- file: `src/utils/instrument-meta-data/generated/raw-meta-data-2026-07-13.json`

Frozen metadata:

| Instrument | Dukascopy code | priceScale | pipValue | group |
|---|---|---:|---:|---|
| XAU/USD | XAU-USD | 3 | 0.01 | FX_METAL |
| EUR/USD | EUR-USD | 5 | 0.0001 | FX_MAJOR |
| USD/JPY | USD-JPY | 3 | 0.01 | FX_MAJOR |
| GBP/USD | GBP-USD | 5 | 0.0001 | FX_MAJOR |
| USD/CAD | USD-CAD | 5 | 0.0001 | FX_MAJOR |
| USD/SEK | USD-SEK | 5 | 0.0001 | FX_CROSS |
| USD/CHF | USD-CHF | 5 | 0.0001 | FX_MAJOR |

Decoder rule:
`point_value = 10 ** priceScale`.

Thus:
- XAUUSD: 1,000
- USDJPY: 1,000
- EURUSD/GBPUSD/USDCAD/USDSEK/USDCHF: 100,000.

If observed S3 values fail deterministic scale/plausibility/integrity checks, stop; do not try alternate divisors.

## Deterministic tick -> M1 rule

For each UTC minute and each side independently:
- timestamp = UTC minute start in epoch milliseconds;
- open = first source tick price in that minute;
- high = maximum source tick price;
- low = minimum source tick price;
- close = last source tick price;
- volume = sum of that side's tick volumes;
- source record order is preserved for equal-millisecond ticks;
- no tick deduplication;
- no interpolation or synthetic minute insertion.

Output schema remains the existing six-column provider-M1 schema:
`timestamp,open,high,low,close,volume`.

The existing Stage-3B synchronization, synthetic-DXY, bounded information-layer, teacher join, GOLD/FULL features, folds, models, metrics, bootstrap and advancement rule remain unchanged downstream.

## Access sequence — exactly one future S3 attempt

The proposed **single** S3 attempt contains the following ordered phases.

### Phase 1 — authenticated low-cost discovery

Using Requester Pays:
1. one top-level delimiter LIST;
2. confirm all seven required prefixes;
3. list only the relevant monthly prefixes:
   - 2026 months June through October;
4. enumerate only objects falling in
   `2026-06-01 <= date < 2026-10-09`;
5. compute exact listed object count and declared total bytes **before GET**.

Fail closed if:
- any required prefix is absent;
- path/layout is not the documented daily `.bi5` form;
- listed target bytes exceed **350 MiB**;
- request plan would exceed the caps below.

### Phase 2 — fixed seven-instrument one-day sanity

Download only **2026-06-01** objects for the seven prefixes that exist.

For each:
- LZMA decode succeeds;
- decompressed byte length divisible by 20;
- tick timestamps are inside the UTC date;
- prices are positive and ask >= bid;
- price scaling uses only frozen `priceScale`;
- minute aggregation produces valid OHLC;
- no NaN/Inf;
- exact file/object identity recorded.

If any required active-market sanity object is absent or invalid, stop the attempt.

### Phase 3 — bounded 2026 acquisition

Only if Phase 2 passes:
- fetch the listed daily objects for Jun1 through Oct8 inclusive;
- no recursive full-prefix scan;
- no dates outside the frozen window;
- no extra instruments;
- missing objects are recorded as no-tick dates per official Dukascopy documentation;
- raw downloaded bytes remain <= **350 MiB**.

Then:
- derive seven bid M1 streams plus XAUUSD ask M1;
- validate the existing eight-series provider contract;
- delete raw `.bi5` after identities/reconstruction are frozen;
- normalized cap remains <= **750 MiB**.

### Phase 4 — unchanged Stage 3B benchmark

Only if all provider/integrity checks pass:
- build bounded D-120 information state;
- macro remains D-121 fail-closed;
- join only D-116 eligible teacher events;
- run only frozen GOLD/FULL L2 logistic 39-date LODO benchmark;
- no tuning/rescue/source switching.

## Request, transfer and cost caps

There are 130 calendar dates in the frozen Jun1→Oct9 half-open interval.

Hard technical ceilings for the attempt:
- underlying instruments: **7**
- target-day object opportunities: **<= 910**
- S3 LIST operations: **<= 50**
- S3 GET operations: **<= 1,000**
- downloaded raw bytes: **<= 350 MiB**
- normalized bytes: **<= 750 MiB**
- requester-pays owner budget: **USD 1.00 maximum**
- attempts: **1**
- rerun: **forbidden**

The official Dukascopy guide currently gives requester-pays examples that are far below USD 1 for this scale, but the **USD 1.00 limit is a governance ceiling, not a price guarantee**.

## AWS credential boundary

Do **not** paste AWS keys into ChatGPT, GitHub files, issues, workflow logs or command arguments.

Preferred authentication:
- a temporary/least-privilege AWS IAM role assumed by GitHub Actions via OIDC;
- trust restricted to this repository and active research branch;
- role allowed only the read/list operations needed for the seven approved prefixes;
- no write/delete permissions.

If OIDC is unavailable, any temporary AWS credentials must be configured directly in GitHub Actions secrets outside chat and removed after the attempt.

The GitHub connector available to this project cannot be treated as an AWS credential store.

## Alternative not recommended as first choice — authenticated JForex API

Dukascopy also officially documents historical data through JForex `IHistory`; historical data returned in DEMO is documented as LIVE historical data.

Potential advantage:
- native M1 bars, closer to the old JETTA-minute representation.

Reasons not selected as the primary D-138 recommendation:
- requires a Dukascopy authenticated account/session;
- API surface is trading-capable even if our code would be read-only;
- creates a larger credential/governance boundary than read-only S3;
- less convenient raw-file auditability.

JForex remains a separately authorizable alternative, not a fallback inside the S3 attempt.

## Scientific caveat

S3-derived M1 is a newly preregistered representation. It preserves provider, timestamps, BID/ASK source information and the frozen downstream feature/model protocol, but it must **not** be described as byte-identical to Stage-2 JETTA M1.

Any later Stage-3B result must be reported as:
`DUKASCOPY_S3_TICK_RECONSTRUCTED_M1_V1`.

## Authorization required before any S3 operation

No S3 LIST, HEAD or GET may occur from this proposal alone.

The owner must separately:
1. authorize the one Requester-Pays S3 attempt and USD 1.00 ceiling;
2. accept the preregistered S3 tick-reconstructed M1 representation;
3. configure the required AWS authentication outside chat.

Only then may implementation/exact-runtime preflight proceed. No S3 access should occur merely to test credentials before that authorization.


## D-139 operational disposition

The owner will not configure AWS or other external credentials/infrastructure, and execution must be assistant-operated end-to-end. Because Requester-Pays S3 inherently requires an AWS identity unavailable to current project tools, D-138 is not executable under D-139. Do not ask the owner to configure AWS and do not attempt S3 access.
