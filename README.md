# XAU/USD $5 Directional-Move Prediction

Clean-room research project for testing whether XAU/USD contains identifiable market states in which a USD 5 directional target can be predicted before a defined adverse excursion within a fixed time horizon.

## Current status

- Repository initialized from scratch.
- Clean-room context policy established on `main`.
- Active Stage 3B source-construction branch: `research/information-parity-v1-stage3-preregistration`.
- Latest frozen decision: D-113 / Stage 3B Batch 14 (Sep 30 + Oct 1). See `research/PROJECT_CONTINUITY.md` and `research/DECISION_LOG.md` for authoritative state.
- Information Parity V1 Stage 2 is accepted on 2016-2021 TRAIN; Stage 3B empirical market join and fitting remain blocked by D-088.
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


## Project continuity

For any new chat or contributor continuing this research, start with:

- `research/PROJECT_CONTINUITY.md` — current project state and immediate next work
- `research/DECISION_LOG.md` — material decisions and rationale
- `research/NEW_CHAT_HANDOFF.md` — continuation rules
- `research/EXPERT_TRADER_OBSERVATION_MODEL.md` — expert-trader observation architecture

The repository is the durable source of truth. Material decisions should not exist only in chat history.
