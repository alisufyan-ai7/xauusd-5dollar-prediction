# EXP-001 Diagnostic Stage

Purpose: test whether the free public XAU/USD M1 feed is operationally adequate for the initial feasibility experiment before committing to a full historical acquisition range.

## Diagnostic window

Initial larger sample:

- from: 2026-08-01
- to: 2026-09-01
- timeframe: M1
- side: BID
- source: the admitted free public Dukascopy feed

This is a data-quality diagnostic only. It is not a model-training or performance-estimation period.

## Required outputs

The diagnostic runner produces:

- raw file SHA-256;
- labeled file SHA-256;
- row count;
- first/last timestamps;
- gap count;
- total missing minutes between observed bars;
- largest observed gap;
- complete/incomplete 60-minute coverage counts;
- BUY/SELL label distributions;
- BUY/SELL ambiguity percentages;
- a preview of detected gaps.

## Interpretation rules

1. Label success rates from this diagnostic sample are descriptive only.
2. No strategy threshold or model parameter may be selected from this sample.
3. Session/weekend gaps are expected and must remain distinguishable from accidental missing data.
4. Ambiguous M1 samples remain unresolved until a later tick-level adjudication stage if needed.
5. Large unexpected intraday gaps or high ambiguity rates require investigation before full acquisition.
