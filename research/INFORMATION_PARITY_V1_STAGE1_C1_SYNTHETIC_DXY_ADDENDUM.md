# Information Parity V1 — Stage 1 C1 Synthetic-DXY Probe Addendum

Status: **FROZEN BEFORE SYNTHETIC-DXY EMPIRICAL PROBE**

Reason for addendum:

Documentation review established that Dukascopy introduced its DOLLAR.IDX/USD CFD in August 2018, so it cannot provide complete 2016-2021 TRAIN coverage even though the third-party downloader registry reports a generic earlier availability date.

This addendum adds a causally reproducible C1 fallback **because of documented coverage**, not because of any XAUUSD outcome.

No profitability data are used.

## Candidate

Construct an ICE-method DXY proxy from synchronized Dukascopy M1 FX closes using the official ICE DXY formula.

Official ICE methodology:

`DXY = 50.14348112 × EURUSD^-0.576 × USDJPY^0.136 × GBPUSD^-0.119 × USDCAD^0.091 × USDSEK^0.042 × USDCHF^0.036`

Constituents/weights:
- EUR 57.60%
- JPY 13.60%
- GBP 11.90%
- CAD 9.10%
- SEK 4.20%
- CHF 3.60%

For this Stage 1 feasibility probe use Dukascopy M1 **BID close** for:
- EURUSD
- USDJPY
- GBPUSD
- USDCAD
- USDSEK
- USDCHF

This produces a provider-specific synthetic index following the ICE published formula.

It must be called **SYNTHETIC_DXY_DUKASCOPY_BID**, not represented as an official ICE market print.

## Fixed sample days

Use the already frozen Stage 1 M1 anchor days:

- 2016-02-01
- 2019-02-04
- 2021-02-01

No new date selection is introduced.

## Required outputs

For each day:
- constituent row counts;
- common synchronized timestamps;
- synthetic DXY row count;
- first/last timestamp;
- missingness;
- synthetic level summary.

For 2019 and 2021, where the Dukascopy DOLLAR.IDX/USD CFD may exist:
- align overlapping M1 timestamps;
- report level correlation;
- report first-difference correlation;
- report normalized tracking error after scaling both series to 100 at first common timestamp.

These diagnostics are source-feasibility checks only.

They must not be related to future XAUUSD returns or P&L.

## Admission interpretation

A successful synthetic construction with complete 2016-2021 constituent availability would satisfy C1 historical coverage more cleanly than relying on the post-2018 Dukascopy DXY CFD alone.

The Stage 1 final verdict must still document:
- that the series is synthetic;
- the source provider for each FX quote;
- side/close semantics;
- any minute-level missingness;
- that official ICE DXY prints may differ from the synthetic value because source FX quotes differ.

## Evidence

ICE FX Indexes Methodology publishes the formula constant and currency weights.

Dukascopy/dukascopy-node provide long historical coverage for all six constituent FX pairs.
