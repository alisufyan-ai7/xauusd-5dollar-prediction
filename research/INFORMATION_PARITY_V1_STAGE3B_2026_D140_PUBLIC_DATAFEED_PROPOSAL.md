# D-140 — Stage 3B Credential-Free Dukascopy Public Datafeed Access Proposal

STATUS: PROPOSAL / NO PROVIDER REQUEST AUTHORIZED

Parents: D-124 frozen science, D-137 recovery closure, D-139 no-manual-setup constraint.

Goal: replace only provider transport with a route that requires no AWS account, no Dukascopy account, no credentials/manual setup, and can be executed end-to-end by the assistant while remaining Dukascopy-source historical data.

Proposed source representation: DUKASCOPY_PUBLIC_DATAFEED_DIRECT_M1_V1

Historical route:
https://datafeed.dukascopy.com/datafeed/{SYMBOL}/{YYYY}/{MM0}/{DD}/{SIDE}_candles_min_1.bi5

MM0 is zero-based month. SIDE is BID or ASK. One object represents one UTC date of M1 candles for one instrument/side.

Pinned protocol source:
- upstream repo Leo4815162342/dukascopy-node
- historical implementation v1.46.4
- tag object ce06398059b56a85c2081e5f62f126c2f0e92d5f
- commit 4bb92bcbcd2edf7c7d75783173f1dae40bee7ef4
- src/url-generator/index.ts
- src/decompressor/index.ts
- src/data-normaliser/index.ts
- generated instrument metadata.

Recent 2026 public software/reports still reference this datafeed route, but intermittent timeout/unavailability reports also exist. Availability must therefore be tested exactly once only after authorization; it is not assumed.

Frozen logical series:
1. XAUUSD BID
2. XAUUSD ASK
3. EURUSD BID
4. USDJPY BID
5. GBPUSD BID
6. USDCAD BID
7. USDSEK BID
8. USDCHF BID

Frozen date fence: 2026-06-01T00:00:00Z <= bar_start < 2026-10-09T00:00:00Z. No 2022-2025, Oct9-Nov30 2026, December 2026, or 2027+.

Binary M1 contract:
- 24 bytes per record;
- big-endian >5i1f;
- source fields: seconds from UTC date start, open integer, close integer, low integer, high integer, float volume;
- canonical output: timestamp,open,high,low,close,volume;
- timestamp = UTC date start epoch ms + seconds*1000;
- prices divided by frozen decimal factor;
- strictly increasing timestamps;
- no interpolation, synthetic rows, or arbitrary missing-minute fill.

Frozen decimal factors from v1.46.4 metadata:
- XAUUSD 1000
- EURUSD 100000
- USDJPY 1000
- GBPUSD 100000
- USDCAD 100000
- USDSEK 100000
- USDCHF 100000
No auto-detection or divisor search allowed.

Scientific identity caveat:
This route is not claimed byte-identical to accepted Stage-2 JETTA/JSON M1 because Stage-2 raw payloads were not retained in GitHub. Any scientific result must be labeled DUKASCOPY_PUBLIC_DATAFEED_DIRECT_M1_V1.

All downstream science stays frozen: D-116 teacher, 92 GOLD / 155 FULL allowlists, 39 LODO folds, D-120 bounded cold start, D-121 macro fail closed, synchronization, synthetic DXY formula/staleness, L2 logistic models, event weights/pooling, metrics/bootstrap/thresholds, and no rescue tuning.

Pre-provider sequence:
1. implement deterministic decoder/validator;
2. test against pinned v1.46.4 GitHub fixture files and known expected rows;
3. enforce exact URL/date/symbol/side allowlists;
4. prove sealed-date requests impossible;
5. enforce byte/request caps;
6. run off-CI/no-provider tests.

Only after those pass and a separate owner authorization is recorded:
- sanity phase: exactly eight requests for 2026-06-01 (XAUUSD BID+ASK and six FX BID);
- every response must be HTTP 200, nonzero valid LZMA for the active market date, divisible into 24-byte records, satisfy OHLC/timestamp invariants, and yield at least one M1 row;
- any sanity failure stops the entire attempt; zero retry, no alternate host/VPN/proxy/mirror/provider switching;
- only if all eight sanity objects pass may the exact Jun1-Oct8 daily acquisition proceed.

Proposed caps:
- attempts: 1
- sanity GETs: 8
- full GET opportunities: <=1040
- hard total GET cap including sanity: 1050
- raw bytes: <=350 MiB
- normalized/intermediate: <=750 MiB
- retries after provider failure: 0
- alternate host/source in same attempt: forbidden.

No-user-setup property:
No cloud credential, Dukascopy account, email registration, secret, payment method, browser profile or broker connection is required.

Authorization state:
No request to datafeed.dukascopy.com is authorized until deterministic decoder/fence preflight is committed and passes without provider access, followed by explicit owner authorization for the versioned D-140 attempt. Stage 3B remains NOT TESTED.