# Information Parity V1 — Stage 2 Macro-Calendar Implementation Addendum

Status: **FROZEN BEFORE LIVE MACRO ACQUISITION**

Parent:
`research/INFORMATION_PARITY_V1_STAGE2_SCHEMA_PREREGISTRATION.md`

## Purpose

Resolve the exact public first-party macro-calendar acquisition procedure before the Stage 2 smoke/full build.

No XAUUSD outcome, P&L, or predictive result was used.

## Included V1 macro families

The Stage 2 core scheduled-event calendar will normalize:

- CPI — BLS historical release schedule;
- NFP / Employment Situation — BLS historical release schedule;
- JOLTS — BLS historical release schedule;
- FOMC statement/rate-decision timestamps — Federal Reserve historical FOMC pages and statement pages;
- Initial Jobless Claims — U.S. Department of Labor / ETA official publication schedule;
- GDP national releases — BEA historical GDP news-release archive and release pages.

All source timestamps are normalized from U.S. Eastern local time using `America/New_York`.

## ISM implementation finding

Stage 1 correctly established that ISM documents the normal rule:
- Manufacturing PMI: first business day, 10:00 a.m.;
- Services PMI: third business day, 10:00 a.m.

During Stage 2 implementation review, the first-party public site was also found to state that historical PMI data must be purchased and historical report pages are not reliably available. The current calendar itself documents that ISM-specific holidays can move a release away from the generic first/third-business-day rule.

Therefore Stage 2 V1 will **not fabricate 2016-2021 ISM dates from a generic business-day calendar**.

ISM Manufacturing and Services schedule state are deferred from the V1 normalized calendar unless a reproducible first-party historical date source is found before the first live Stage 2 macro acquisition.

This is a conservative narrowing of C3, not replacement with a third-party calendar.

## DOL claims rule

The official ETA archive states:
- UI Weekly Claims is published Thursday morning at 8:30 a.m. Eastern;
- exception occurs when Thursday falls on a federal holiday.

For V1:
- generate each Thursday 08:30 `America/New_York`;
- if that Thursday is an actual federal holiday, move the release to the preceding Wednesday at 08:30;
- mark `historical_exception_flag=1`;
- preserve the ETA archive URL as source provenance.

This uses the first-party publication rule, not release values.

## BEA GDP

Use BEA's national GDP archive product and follow each matching news-release page.

Only national releases whose title starts with `Gross Domestic Product,` are included.

Release timestamp is parsed from the first-party embargo/release line. No GDP value is ingested.

## Macro readiness definition

For year Y:

`macro_schedule_available=true`

only if all six V1 core families above pass acquisition/normalization checks for Y.

Minimum sanity counts:
- CPI >= 11
- NFP >= 11
- JOLTS >= 11
- FOMC >= 8
- CLAIMS >= 50
- GDP >= 11

Counts are sanity floors, not expected-value tuning.

Family/year counts and acquisition errors must be written to the coverage manifest.

## Prohibited

Stage 2 macro acquisition must not ingest:
- actual release values;
- forecast/consensus;
- previous/revised values;
- surprise calculations;
- third-party economic-calendar timestamps as silent substitutes.

If a first-party family fails, that year remains explicitly incomplete.

## Evidence basis

First-party public documentation establishes:
- BLS yearly historical schedule pages with exact date/time for CPI, Employment Situation and JOLTS;
- Federal Reserve historical FOMC pages linking statement pages whose release time is explicitly stated;
- BEA historical GDP release pages whose embargo lines state the exact release time;
- ETA claims archive stating the Thursday 08:30 Eastern publication rule and federal-holiday exception;
- ISM's current public report calendar stating the first/third-business-day rule and explicit ISM holiday exceptions, while historical PMI material is not reliably available publicly.

## Governance

2016-2021 only for Stage 2 normalized use.

2022-2025 XAUUSD remain sealed.

No profitability model is authorized.
