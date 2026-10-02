# Information Parity V1 — Stage 1 C2 Rate-Proxy Probe Addendum

Status: **FROZEN BEFORE EMPIRICAL IEF PROBE**

## Reason

The fixed Stage 1 probe established:

- `ustbondtrusd` is unavailable on the 2016 anchor day;
- it is a US T-Bond CFD rather than the exact US 10-year yield Badar is observed checking;
- later samples contain material intraday gaps.

The source registry identifies a second accessible candidate:
- Dukascopy `iefususd`
- iShares 7-10 Year Treasury Bond ETF.

This addendum freezes one final free/access-existing empirical probe for C2 before deciding whether the rate channel is admitted with limitation or deferred.

This probe is justified by source semantics/coverage, not XAUUSD outcomes.

## Fixed dates

Use the already frozen Stage 1 anchor days only:

- 2016-02-01
- 2019-02-04
- 2021-02-01

No new dates are introduced.

## Data

Download one UTC day of M1 BID data for:
- `iefususd`

No XAUUSD outcome or P&L calculation is permitted.

## Required diagnostics

Reuse `scripts/probe_information_parity_stage1.py m1` and report:

- file bytes;
- row count;
- first/last timestamp;
- M1 alignment;
- gap count/largest gap;
- OHLC sanity;
- volume presence and zero share.

## Interpretation boundary

Even if technically successful, IEF is:

- an ETF price, not a Treasury yield;
- limited to exchange trading hours;
- a 7-10 year Treasury basket rather than the on-the-run 10Y yield;
- directionally inverse to yields in ordinary bond-price terms, but duration/convexity and ETF mechanics differ.

Therefore it can receive at most **ADMITTED WITH LIMITATION** as a market-hours rates-direction proxy.

If it lacks reliable 2016-2021 sample coverage, C2 will be **DEFERRED** from Information Parity V1 rather than triggering further free-provider hunting.

A higher-fidelity authenticated source such as CME 10-Year T-Note futures may be reconsidered in a later separately documented data-source milestone if needed.

## Sealed data

2022-2025 XAUUSD remain untouched.
