# Information Parity V1 — Stage 1 Source Feasibility Findings

Status: **COMPLETE — SOURCE SET FROZEN FOR STAGE 2 DESIGN**

Frozen preregistration:
`research/INFORMATION_PARITY_V1_STAGE1_SOURCE_FEASIBILITY_PREREGISTRATION.md`

Fixed probe plan:
`research/INFORMATION_PARITY_V1_STAGE1_PROBE_PLAN.md`

Addenda:
- `research/INFORMATION_PARITY_V1_STAGE1_C1_SYNTHETIC_DXY_ADDENDUM.md`
- `research/INFORMATION_PARITY_V1_STAGE1_C2_RATE_PROXY_ADDENDUM.md`

Final accepted probe run:
- workflow: `information-parity-stage1`
- run: **36986414645**
- status: SUCCESS
- head: `7b450032dce18c1ab1f5d89712e88c7ffc947013`
- artifact: `information-parity-stage1-probes`
- artifact id: `11217188926`
- artifact digest: `sha256:27ff2ed0f4d03a6392a479208ad9d2a80bd467d45fe5a2b2d46113aa3d7f8821`

The artifact explicitly records:
- fixed M1 anchor days: 2016-02-01, 2019-02-04, 2021-02-01;
- fixed tick windows: 2016-02-01 14:00-15:00 UTC and 2021-02-01 14:00-15:00 UTC;
- `sealed_xauusd_periods_accessed: []`.

No profitability, target-before-stop analysis, or model fitting was used for source selection.

## Final C1-C6 verdicts

| Channel | Final verdict | Stage 2 meaning |
|---|---|---|
| C1 DXY / broad USD intraday | **ADMITTED WITH LIMITATION** | Use `SYNTHETIC_DXY_DUKASCOPY_BID`, constructed from six Dukascopy M1 BID FX constituents using the published ICE DXY formula. Treat it as a provider-specific synthetic reconstruction, not an official ICE market print. |
| C2 US Treasury / rate intraday | **DEFERRED** | Do not include a rate/yield channel in Information Parity V1. The free/access-existing candidates did not meet the frozen coverage/semantics bar. |
| C3 Scheduled macro-event calendar | **ADMITTED WITH LIMITATION** | Build a timestamp-safe composite calendar from first-party U.S. release archives/schedules. Preserve ET/DST conversion and historical exceptions. |
| C4 Macro actual/forecast/previous/surprise | **DEFERRED** | Do not include historical consensus/surprise features in V1 until point-in-time access/reproducibility is independently established. |
| C5 XAUUSD M1 volume | **ADMITTED WITH LIMITATION** | Use only as a Dukascopy provider participation/volume proxy. Do not describe it as centralized/global gold traded volume. |
| C6 XAUUSD tick microstructure | **ADMITTED WITH LIMITATION** | Historical ticks are technically feasible for targeted windows. Use for spread/quote-intensity/provider-side quote-volume research only; full 2016-2021 tick ingestion is not automatically required. |

## C1 — DXY / broad USD intraday

### Direct Dukascopy DXY CFD

Fixed probe results:

- 2016-02-01: **0 rows**
- 2019-02-04: 1,154 rows
- 2021-02-01: 1,237 rows

This is consistent with documentation showing the direct Dukascopy DOLLAR.IDX/USD product was introduced after the beginning of TRAIN.

Therefore the direct CFD cannot supply complete 2016-2021 parity.

### Synthetic DXY fallback

The preregistered synthetic DXY uses:

`50.14348112 * EURUSD^-0.576 * USDJPY^0.136 * GBPUSD^-0.119 * USDCAD^0.091 * USDSEK^0.042 * USDCHF^0.036`

with Dukascopy M1 BID closes.

Fixed-day synchronized constituent coverage:

- 2016-02-01: **1,417** common M1 timestamps
- 2019-02-04: **1,419**
- 2021-02-01: **1,404**

Where the direct Dukascopy dollar-index CFD also exists:

2019:
- overlap: 1,151 rows
- level Pearson: **0.99845**
- first-difference Pearson: **0.94616**
- mean normalized tracking difference: **+0.00314 index points after rebasing to 100**

2021:
- overlap: 1,224 rows
- level Pearson: **0.99978**
- first-difference Pearson: **0.91796**
- mean normalized tracking difference: **+0.00265 index points after rebasing to 100**

Interpretation:

The synthetic construction is technically suitable for a causal broad-USD context channel across TRAIN.

It must remain explicitly labeled:
`SYNTHETIC_DXY_DUKASCOPY_BID`.

It is not an official ICE DXY market print.

Final verdict:
**ADMITTED WITH LIMITATION**.

## C2 — US Treasury / rate intraday

### Dukascopy US T-Bond CFD

Fixed probe:

2016-02-01:
- **0 rows**

2019-02-04:
- 1,205 rows
- 105 gaps
- largest gap: **61 minutes**

2021-02-01:
- 829 rows
- 247 gaps
- largest gap: **61 minutes**

In addition, this product is a US T-Bond price CFD, not the US 10-year yield Badar is observed checking.

### IEF 7-10 Year Treasury ETF fallback

The final preregistered IEF probe returned:

- 2016-02-01: **0 rows**
- 2019-02-04: **0 rows**
- 2021-02-01: **0 rows**

Under the frozen C2 addendum, this ends the free/access-existing provider search.

Interpretation:

The project does not currently have a sufficiently faithful, reproducible 2016-2021 intraday 10Y/rates channel.

Do not substitute the gapped T-Bond CFD and do not keep source-shopping after this result.

A higher-fidelity authenticated source such as CME 10-Year T-Note futures may be reconsidered only under a later separately documented source milestone if evidence later shows the missing rate channel is important.

Final verdict:
**DEFERRED**.

## C3 — Scheduled macro-event calendar

Documentation review established feasible timestamped first-party historical sources for the core event families:

- BLS historical schedules/releases:
  - Employment Situation / NFP;
  - CPI;
  - JOLTS;
- Federal Reserve:
  - FOMC meeting archive;
  - statement release timestamps;
- BEA:
  - GDP release dates/times and estimate stage;
- Department of Labor:
  - Initial Jobless Claims release dates/times;
- ISM:
  - published release-time rules, with historical holiday/date exceptions requiring explicit handling.

Interpretation:

A composite first-party schedule is feasible and avoids dependence on one opaque commercial calendar.

Stage 2 must:
- normalize Eastern Time with DST correctly;
- preserve exact historical release dates rather than regenerate them from current generic rules when an archive exists;
- encode source/event-family provenance;
- avoid placing post-release values into pre-release timestamps.

Final verdict:
**ADMITTED WITH LIMITATION**.

## C4 — Macro release actual / forecast / previous / surprise

Trading Economics documents a point-in-time economic-calendar API with:
- Actual;
- Previous;
- Forecast;
- Revised;
- Date;
- LastUpdate.

This is promising.

However Stage 1 did not establish:
- guaranteed entitlement/access for the full 2016-2021 history;
- exact point-in-time semantics for all required event families;
- reliable preservation of pre-release consensus versus later database updates/revisions.

Because consensus/surprise is especially vulnerable to hindsight contamination, V1 will not include it merely because an API is documented.

Stage 2 may include schedule/proximity state from C3, but not macro surprise features.

Final verdict:
**DEFERRED**.

## C5 — XAUUSD M1 volume

The fixed XAUUSD BID/ASK M1 samples contained a nonzero provider `volume` field on all three anchor dates.

Paired BID/ASK observations:

2016-02-01:
- 1,380 common rows
- BID mean volume: **0.04754**
- ASK mean volume: **0.05847**
- exact BID/ASK volume equality share: **0.29%**
- BID/ASK volume Pearson: **0.7383**

2019-02-04:
- 1,371 common rows
- BID mean: **0.01700**
- ASK mean: **0.01602**
- equality share: **0.36%**
- Pearson: **0.5850**

2021-02-01:
- 1,380 common rows
- BID mean: **0.08014**
- ASK mean: **0.08331**
- equality share: **0.80%**
- Pearson: **0.5567**

Interpretation:

The field is not merely duplicated side metadata and is technically usable as a causal provider participation measure.

Stage 2 may use:
- relative volume;
- rolling volume regime;
- session-relative volume;
- volume expansion/contraction.

Stage 2 must not claim this is:
- centralized exchange volume;
- complete OTC gold volume;
- direct institutional flow.

Final verdict:
**ADMITTED WITH LIMITATION**.

## C6 — XAUUSD tick microstructure

Fixed one-hour tick windows:

2016-02-01 14:00-15:00 UTC:
- 9,190 rows
- ~153.2 rows per observed minute
- file size: ~438 KB
- median spread: **$0.273**
- no negative spreads
- askVolume present
- bidVolume present
- no nonmonotonic timestamps

2021-02-01 14:00-15:00 UTC:
- 27,097 rows
- ~451.8 rows per observed minute
- file size: ~1.29 MB
- median spread: **$0.440**
- no negative spreads
- askVolume present
- bidVolume present
- no nonmonotonic timestamps

Interpretation:

Historical Dukascopy ticks are technically usable for targeted microstructure studies.

Useful causal candidates include:
- spread distribution;
- quote-update intensity;
- short-horizon spread expansion;
- provider-side quote-volume behavior.

A complete six-year tick download is not required by Stage 2 merely because it is feasible. Stage 2 should use M1 as the default information layer and add targeted tick features only if the schema design has a concrete need.

Final verdict:
**ADMITTED WITH LIMITATION**.

## Stage 1 completion test

The frozen Stage 1 minimum requirements are satisfied:

1. Existing synchronized XAUUSD BID/ASK M1 remains available.
2. M1 provider-volume behavior is sufficiently characterized for limited use.
3. At least one cross-market channel is admitted:
   - C1 synthetic broad-USD/DXY context.
4. A scheduled macro-event calendar is admitted:
   - C3 first-party composite calendar.

C2 rates and C4 surprise values are deferred rather than filled with weak substitutes.

Therefore Stage 2 design may begin.

## Frozen source set for Stage 2 design

Information Parity Layer V1 should be designed around:

- XAUUSD M1 BID/ASK OHLC;
- spread;
- Dukascopy M1 provider volume;
- raw XAUUSD causal sequences and multi-timeframe transforms;
- source-supported structural/session/liquidity context;
- `SYNTHETIC_DXY_DUKASCOPY_BID`;
- first-party scheduled U.S. macro-event calendar;
- optional targeted Dukascopy tick microstructure where specifically justified;
- separate trade/account/risk state.

Explicitly excluded from V1 unless a later preregistration changes the data-source hypothesis before empirical model results:

- intraday US 10Y/rate channel;
- historical macro consensus/surprise;
- full global order flow;
- official ICE DXY prints as a complete TRAIN source;
- full six-year tick-history ingestion by default.

## Scientific interpretation

Stage 1 answered the intended question successfully:

The project can build a substantially richer, causal information environment than the one used in prior price-dominant experiments without opening sealed evaluation periods.

The result is **not** evidence that these new channels are predictive or profitable.

Their incremental value must be tested later under the frozen information-channel ablation stage.

## Next step

Do not train a model yet.

The next action is Stage 2 preregistration:

**freeze the Information Parity Layer V1 schema and timestamp-alignment contract before full TRAIN acquisition/integration.**

That contract should define:
- exact row/decision timestamp semantics;
- raw sequence windows;
- multi-timeframe aggregation rules;
- DXY synthesis/alignment;
- macro-event event-time encoding;
- volume transforms;
- allowed targeted tick-derived fields;
- missingness rules;
- source provenance;
- hash/manifest requirements;
- separation of market state from trade/risk state.

2022-2025 remain sealed.
