# Information Parity V1 — Stage 2 Corrected Bounded Smoke Findings

Status: **ACCEPTED**

Accepted run:
- workflow: `information-parity-stage2`
- run: **37231837219**
- head: `e2aaaaa829a76be6cd10e35f9dac85e3b7c6b343`
- conclusion: **SUCCESS**
- artifact: `information-parity-stage2-smoke`
- artifact ID: `11314132575`
- artifact digest: `sha256:05d7955f11834eb668d191b2cbf5dcf64ff0b4bbedec646c2e42fd2079cfe59e`

This smoke was executed after the D-074 D1 fix and the D-076 static-review corrections.

## Scope

Market window:
- 2016-02-01 through 2016-02-06
- XAUUSD BID/ASK M1
- six BID FX constituents for synthetic DXY
- normalized 2016 first-party macro schedule

Governance:
- TRAIN-only
- sealed XAUUSD periods accessed: none
- no future-return/P&L labels
- no model training

## Build counts

- synchronized XAUUSD M1: **6,840**
- M3: **2,280**
- M5: **1,368**
- M15: **456**
- M30: **228**
- H1: **114**
- H4: **25**
- D1: **5**
- W1: **1**
- structural state: **6,840**
- macro event state: **6,840**
- decision index: **6,840**
- trade/risk template: **6,840**
- synthetic DXY M1: **7,008**
- admitted macro schedule rows: **108**

The corrected D1/W1 path is now non-empty in the same bounded market window that previously produced zero rows under the D-074 bug.

## Coverage

- DXY available share: **1.0**
- macro schedule available share: **1.0**
- feature-ready market share: **0.8252923976608187**
- XAUUSD BID flat-fill rows: **0**
- XAUUSD ASK flat-fill rows: **0**

## Integrity

All reported checks passed, with no warnings:

- D1 <- H1 hierarchy
- W1 <- D1 hierarchy
- M1 decision-time semantics
- annual scope
- nonnegative spreads
- DXY backward as-of alignment
- macro outcome-field exclusion
- macro state alignment
- macro timezone alignment
- previous-day backward as-of state
- structural alignment
- structural causality
- structural signed-distance arithmetic
- neutral trade/risk state
- availability checks for M3/M5/M15/M30/H1/H4/D1/W1
- sealed-period guard

Macro 2016 coverage in the accepted smoke:
- CLAIMS 52
- CPI 12
- FOMC 8
- GDP 12
- JOLTS 12
- NFP 12
- parser/acquisition errors: none

## Interpretation

This run closes the uncertainty created by D-074.

The Stage 2 implementation now has:
1. a deterministic local logic pass;
2. an exact-runtime deterministic preflight pass;
3. a corrected real-provider bounded smoke pass with non-empty D1/W1 and independently validated previous-day state.

This is sufficient to move to the **full 2016-2021 Stage 2 TRAIN information-layer build**.

It is not evidence about trading profitability and does not authorize model selection or access to 2022-2025.
