# XAU/USD $5 Directional-Move Prediction

Clean-room research project for testing whether XAU/USD contains identifiable market states in which a USD 5 directional target can be predicted before a defined adverse excursion within a fixed time horizon.

## Current status

- Repository initialized from scratch.
- Clean-room context policy established on `main`.
- Active Stage 3B source-construction branch: `research/information-parity-v1-stage3-preregistration`.
- Latest decision: D-124 final owner authorization for the exact bounded 2026 Stage 3B acquisition/model package. D-088 is partially superseded only for that exception; 2022–2025, quarantine/shadow, Stage4/5 and broker actions remain protected. See `research/PROJECT_CONTINUITY.md` and `research/DECISION_LOG.md`.
- Information Parity V1 Stage 2 is accepted on 2016-2021 TRAIN. Final Stage 3B source teacher: 107 ACT, 143 eligible P3, 39 paired dates; exact dataset/hash in `research/reference/information-parity-v1/stage3b-source-freeze-manifest-v1.json`.
- D-088 chronology gate remains closed. D-118 proposal, D-119 preflight findings, source rights and final-approval checklist are in `research/`; Stage 3B market join, fitting and Stage 4/5 execution are not authorized.
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
- `research/NEW_CHAT_HANDOFF.md` — current chat-to-chat handoff
- `research/NEW_CHAT_PROMPT.md` — ready-to-copy prompt for the next chat
- `research/PROJECT_DOCUMENTATION_PROTOCOL.md` — mandatory post-execution documentation rules
- `research/EXPERT_TRADER_OBSERVATION_MODEL.md` — expert-trader observation architecture

The repository is the durable source of truth. Material decisions should not exist only in chat history.
