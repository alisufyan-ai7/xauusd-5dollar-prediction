# D-148 — Stage 3B Dukascopy FREESERV Chart JSON3 Access Strategy

**STATUS: PREREGISTERED CANDIDATE / SOURCE-ONLY RESEARCH / NO PROVIDER MARKET REQUEST AUTHORIZED**

Parents: D-124 frozen Stage 3B science, D-139 no-manual-setup constraint, D-147 closure of the consumed D-144/D-140 direct-datafeed attempt.

## 1. Why a different transport is required

D-136 consumed the pinned dukascopy-node/JETTA recovery on a plain HTTP 403. D-146 consumed the D-140 direct-datafeed attempt when the first XAUUSD BID June 1 sanity connection to `datafeed.dukascopy.com` was reset by the peer during TLS before any HTTP response.

The current upstream `Leo4815162342/dukascopy-node` `master` is identical to the pinned 1.51.1 release commit `068bf57b67e3cae3f5c952653ef20157d3852699`; there is no later upstream transport commit to justify another retry. The official Historical Data Export widget is also reported unavailable in current upstream issue discussion.

Therefore D-148 investigates a genuinely different Dukascopy-native public transport used by the embeddable chart API, not a retry, header mutation, proxy, VPN, alternate mirror, or source switch.

## 2. Candidate source representation

Proposed representation name:

`DUKASCOPY_FREESERV_CHART_JSON3_M1_V1`

Endpoint family:

`https://freeserv.dukascopy.com/2.0/index.php?path=chart/json3`

This is the public chart JSONP transport used by the current public `Eghosa-Osayande/dukascopy` DataFeedV1 implementation and by Dukascopy's embeddable chart surface.

Pinned public implementation identity:
- repository: `Eghosa-Osayande/dukascopy`
- branch head inspected: `2e48b12cb3f5d81426a08886e9427af81d10f002` (2026-11-17)
- DataFeedV1 blob: `47738a147d42c71312329d76e766afe658f8d575`
- compatibility implementation blob: `765850e2c6569e7fa9dcc6f55c6beffd3df37da7`
- compatibility instrument registry blob: `16493bd886629fb2fd99b56205e2b6d0300fb436`
- 2026-10-28 generated instrument metadata blob: `689b457f9beda4a52c62c255df3594f341030def`

The current public package release corresponding to this repository is `dukascopy-python 7.0.0`, released 2026-11-17.

## 3. Frozen request semantics from source inspection

For M1 candles:
- `path=chart/json3`
- `splits=true`
- `stocks=true`
- `time_direction=N`
- `interval=1MIN`
- `offer_side=B` for BID
- `offer_side=A` for ASK
- `last_update=<UTC epoch milliseconds>`
- optional `limit`, with the inspected public implementation documenting a maximum of 30,000 rows
- JSONP callback name is caller-generated and the payload is decoded as a list of rows.

Candle row interpretation in the pinned implementation:
1. timestamp in epoch milliseconds;
2. open;
3. high;
4. low;
5. close;
6. volume.

The implementation advances forward from the last returned timestamp and removes a repeated cursor row on later pages.

D-148 does not inherit the upstream retry defaults. Any future project client must be **zero-retry after provider/transport failure** unless a later owner authorization explicitly says otherwise.

## 4. Frozen instruments and scientific scope

Logical series remain exactly the D-124/D-140 eight:
1. XAU/USD BID
2. XAU/USD ASK
3. EUR/USD BID
4. USD/JPY BID
5. GBP/USD BID
6. USD/CAD BID
7. USD/SEK BID
8. USD/CHF BID

All seven slash-form instrument identifiers are present in the pinned compatibility registry.

Frozen half-open market fence remains:
`2026-06-01T00:00:00Z <= bar_timestamp < 2026-10-09T00:00:00Z`.

No 2022-2025, no 2026-10-09 through 2026-11-30, no December shadow, and no 2027+ access.

All downstream science remains unchanged:
- D-116 teacher and source hashes;
- 92 GOLD / 155 FULL feature allowlists;
- 39 LODO folds;
- D-120 bounded cold start;
- D-121 macro fail-closed behavior;
- same synchronization / synthetic-DXY semantics;
- same L2 logistic tasks and preprocessing;
- same event weighting/pooling;
- same bootstrap, metrics and advancement thresholds;
- no rescue tuning;
- no broker/order mutation.

## 5. Representation caveat

`DUKASCOPY_FREESERV_CHART_JSON3_M1_V1` is a **new source representation**.

It is not claimed byte-identical to:
- accepted Stage-2 JETTA/JSON M1;
- D-140 direct `.bi5` M1;
- any previously downloaded raw provider snapshot.

A future result must carry the D-148 representation name and must not silently claim Stage-2 byte parity.

Before execution, timestamp/bar-start semantics, strict monotonicity, OHLC invariants, volume non-negativity, and source-range behavior must fail closed in deterministic code and then in the separately authorized sanity phase.

## 6. Proposed bounded transport design

No provider request is authorized by this document.

For a future separately authorized attempt, the proposed structure is:

### Sanity phase
- exactly 8 requests, one per logical series;
- cursor fixed at 2026-06-01T00:00:00Z;
- `interval=1MIN`;
- small fixed `limit` sufficient to prove JSONP, row shape, side, instrument and timestamp decoding;
- every sanity response must be valid HTTP/JSONP, non-empty, monotone, within the authorized fence and satisfy OHLC/volume invariants;
- any failure stops the attempt;
- zero retry.

### Full phase
- cursor begins at the frozen start independently for each logical series;
- `limit=30000`;
- forward-only pagination;
- repeated cursor row may be removed exactly once on a subsequent page;
- every accepted timestamp must satisfy the half-open D-124 fence before persistence;
- stop each series when the first returned timestamp reaches/exceeds the end fence;
- unexpected cursor non-advancement, malformed JSONP, malformed rows, side/instrument mutation, HTTP/transport failure, or budget exceedance stops the attempt.

The theoretical maximum number of M1 calendar slots in the 130-day fence is 187,200 per series. At a 30,000-row page size, seven full pages per series are sufficient if the endpoint fills pages as requested; because page-fill behavior is not guaranteed by source inspection alone, the execution request ceiling must be separately frozen before authorization rather than inferred from this theoretical value.

The existing 350 MiB raw and 750 MiB normalized/intermediate ceilings remain upper governance bounds unless a later preregistration explicitly lowers them.

## 7. Required no-provider work before owner authorization

Owner-independent work may now:
1. implement a standard-library JSONP parser and exact query builder;
2. pin the host, path, request parameters, seven instruments and eight logical sides;
3. enforce the D-124 half-open date fence before dispatch and after decode;
4. implement monotone forward cursor paging with duplicate-cursor handling and non-advancement failure;
5. enforce zero retry and a conservative request/byte budget;
6. write synthetic/mock response fixtures covering BID/ASK, malformed JSONP, malformed rows, duplicate cursors, out-of-range timestamps and cap failures;
7. run local deterministic tests without network;
8. if local tests pass, run one narrowly scoped exact-CPython-3.12.14 **no-provider** compatibility workflow.

None of those steps may contact `chart/json3` for market data.

## 8. Authorization boundary

D-144 is consumed and cannot authorize D-148.

Only after the deterministic no-provider implementation is committed and accepted may the owner be asked for a **new explicit one-attempt D-148 authorization**. That later authorization must freeze the exact sanity limit, full request ceiling, byte ceilings and no-rerun rule.

No AWS account, Dukascopy login, credential, secret, payment method, browser profile or owner-operated infrastructure is expected by this candidate route.

Current scientific state remains:

**STAGE 3B = NOT TESTED.**
