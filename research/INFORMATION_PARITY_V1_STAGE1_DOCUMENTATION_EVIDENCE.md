# Information Parity V1 — Stage 1 Documentation Evidence

Status: **PROVISIONAL SOURCE-EVIDENCE RECORD — EMPIRICAL PROBES PENDING**

This file records documentation-level evidence collected under the frozen Stage 1 preregistration.

No source is admitted here solely because documentation exists. Final C1-C6 verdicts require the Stage 1 findings record.

## C1 — DXY / broad USD intraday context

### Dukascopy DOLLAR.IDX/USD

Authoritative Dukascopy market documentation lists:

- product: **DOLLAR.IDX/USD**
- description: **US Dollar Index**
- components/meaning: **US Dollar Index Basket**
- quoted as a Dukascopy index CFD.

The pinned `dukascopy-node` instrument registry exposes the corresponding historical identifier:

- `dollaridxusd`
- documented earliest data: **2000-01-01 UTC**

Implication:

This is a strong candidate for a timestamp-aligned USD-index context channel using the same public historical-feed family already used for XAUUSD.

Remaining limitations before admission:

- empirical 2016-2021 M1 coverage/continuity must pass;
- do not claim contractual identity with ICE's licensed DXY calculation unless independently documented;
- use the exact Dukascopy product identity in Stage 2 metadata.

Documentation evidence:
- Dukascopy CFD range-of-markets page, DOLLAR.IDX/USD = US Dollar Index Basket.
- dukascopy-node instrument registry, `dollaridxusd`, earliest 2000-01-01.

## C2 — US Treasury / rate context

### Dukascopy USTBOND.TR/USD

Authoritative Dukascopy documentation identifies:

- product: **USTBOND.TR/USD**
- description: **US government bond**
- component: **US T-Bond**
- traded as a bond CFD.

Dukascopy also applies CFD adjustment mechanics to this continuous product.

The pinned historical downloader exposes:

- `ustbondtrusd`
- documented earliest data: **2000-01-01 UTC**

Scientific implication:

This is **not an exact US 10-year yield series**.

At best it may serve as an intraday long-Treasury price/rates-direction proxy:
- bond-price direction is generally inverse to yield direction;
- its maturity exposure differs from the 10-year yield Badar is observed checking;
- continuous-CFD adjustment mechanics must be treated explicitly.

Therefore `ustbondtrusd` cannot receive a clean "exact 10Y yield" interpretation.

### Other rate candidates

The dukascopy-node registry also exposes **iShares 7-10 Year Treasury Bond ETF** (`iefususd`) with claimed historical availability, but this is an ETF price proxy limited to equity-market trading hours, not a yield series.

A higher-fidelity paid/access-dependent candidate remains CME 10-Year T-Note futures (ZN) from a market-data provider such as Databento.

Stage 1 should prefer an exact intraday yield or 10Y-market proxy when practically reproducible; otherwise a proxy may only be ADMITTED WITH LIMITATION.

## C3 — Scheduled macro-event calendar

### BLS official release schedules

The BLS historical release schedule is directly timestamped.

The 2016 schedule, for example, records:
- Employment Situation releases at **08:30 AM**;
- Consumer Price Index releases at **08:30 AM**;
- JOLTS releases at **10:00 AM**.

This establishes a first-party, timestamp-safe basis for those event families.

### Federal Reserve FOMC

Federal Reserve FOMC archive pages provide:
- meeting dates;
- statement links;
- statement release times.

Historical statement pages explicitly state release time, e.g. **2:00 p.m. EDT/EST**.

This is a first-party basis for FOMC decision/statement timestamps.

### BEA GDP

BEA historical GDP news releases record:
- exact release date;
- release time, typically **8:30 A.M. ET**;
- advance/second/third estimate identity;
- future scheduled dates.

This is a first-party basis for GDP release timestamps and estimate type.

### Department of Labor weekly claims

Department of Labor documentation states the UI Weekly Claims release is normally issued:
- Thursday;
- **8:30 a.m. Eastern**;
with holiday exceptions.

Archived news releases preserve release dates and release-time wording.

### ISM

ISM currently documents:
- Manufacturing PMI: first business day, **10:00 a.m. EST**;
- Services PMI: third business day, **10:00 a.m. EST**.

Historical date exceptions/holiday shifts still require reliable reconstruction or archived release evidence.

### Provisional implication

A **composite first-party macro schedule** appears feasible for several core event families even without a commercial calendar provider.

The final calendar implementation must preserve Eastern-time DST conversion to UTC and exact historical holiday exceptions.

## C4 — Macro actual / forecast / previous / surprise

### Trading Economics point-in-time API

Trading Economics documents a point-in-time economic-calendar endpoint whose stated purpose is to preserve values as they appeared at a historical date before later revisions.

Its documented fields include:
- Date;
- Actual;
- Previous;
- Forecast;
- TEForecast;
- LastUpdate;
- Revised;
- Source;
- Unit;
- Ticker/Symbol.

The documentation includes a concrete 2016 Initial Jobless Claims example with timestamped Actual / Previous / Forecast values.

Scientific implication:

This is a strong candidate for point-in-time surprise-state reconstruction if access/entitlement and historical coverage are practical.

Remaining requirements:
- verify API entitlement for full 2016-2021 history;
- verify timestamp timezone semantics;
- verify forecast/previous fields reflect information available before release for each target family;
- document first-release vs revised-value behavior;
- do not use a current revised database snapshot as if it were point-in-time history.

If those cannot be resolved, Stage 2 should use schedule-only macro context rather than fabricated surprise features.

## C5 — XAUUSD M1 volume semantics

The project already downloads Dukascopy candle volume.

The pinned downloader:
- exposes a `--volumes` option;
- supports volume-unit conversion;
- emits a candle `volume` field;
- reads volume from the Dukascopy candle response.

However, documentation reviewed so far does **not** establish that this is centralized exchange-traded XAUUSD volume.

Therefore the safe interpretation remains:
- **provider volume field / participation proxy**,
not:
- global gold traded volume;
- futures exchange volume;
- complete OTC volume.

Empirical BID/ASK-side behavior is being tested in the fixed Stage 1 probe.

## C6 — XAUUSD tick microstructure

The pinned downloader and existing project validator support tick rows containing:
- timestamp;
- askPrice;
- bidPrice;
- optional askVolume;
- optional bidVolume.

The downloader normalizes source tick ask/bid volume fields separately.

This supports a technical feasibility test for:
- spread dynamics;
- quote-update density;
- provider-side volume-at-quote behavior.

It still does not justify treating those fields as a complete global order book.

## Current provisional state

- C1 DXY: strong candidate; empirical probe required.
- C2 rates: exact 10Y still unresolved; Dukascopy T-Bond is only a proxy candidate.
- C3 macro schedule: first-party composite looks feasible for core event families.
- C4 surprise values: Trading Economics PIT is promising but access/point-in-time details must be verified.
- C5 M1 volume: technically present; economic semantics remain limited/provider-specific.
- C6 tick microstructure: technically supported; empirical practicality probe running.

No final admission verdict is made in this file.
