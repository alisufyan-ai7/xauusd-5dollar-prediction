# XAU/USD $5 Directional-Move Prediction

Clean-room research project for testing whether XAU/USD contains identifiable market states in which a USD 5 directional target can be predicted before a defined adverse excursion within a fixed time horizon.

## Current status

- Repository initialized from scratch.
- Clean-room context policy established on `main`.
- Active research branch: `research/exp001-foundation`.
- EXP-001 is specification-only at this stage.
- No trading or broker mutation is enabled.

## Initial research question

Can information available at decision time identify XAU/USD states where either:

- BUY: price reaches +$5 before -$3 within 60 minutes; or
- SELL: price reaches -$5 before +$3 within 60 minutes,

at a probability materially above the unconditional baseline and with adequate out-of-sample evidence?

## Research sequence

1. Public-data/provider research and rights review
2. Raw data validation and normalization
3. Exact barrier-label engine
4. Baseline statistics
5. Timestamp-safe feature engine
6. Simple model benchmarks
7. Chronological validation and calibration
8. Frozen final out-of-sample test
9. Forward shadow / Exness demo validation
10. Execution testing
11. Live capability only after separate evidence-based approval

See `PROJECT_CONTEXT_POLICY.md` for the mandatory clean-room rules.
