# MacroPlacement and simulated annealing: why strong search controls matter

Reviewed: 17 October 2026. Type: official benchmark repository and implementation documentation. No experiments executed.

## Verified source facts

[TILOS MacroPlacement](https://github.com/TILOS-AI-Institute/MacroPlacement) supplies public designs, evaluation flows, format translators, and baseline implementations. Its December 2025/January 2026 updates report further Circuit Training comparisons and favorable simulated annealing results; these are the repository authors' reported findings, not universal proof that RL cannot work. The [SA implementation documentation](https://github.com/TILOS-AI-Institute/MacroPlacement/blob/main/CodeElements/SimulatedAnnealing/README.md) describes swap, shift, mirror, move, and shuffle actions, probabilistic acceptance of worsening moves, and standard-cell re-placement during search.

## Core idea in plain language

Greedy search accepts only immediate improvements, so it can become trapped. Simulated annealing sometimes accepts a worse layout while the temperature is high, then becomes more selective. RL could improve on this by learning which moves are worth trying from structural information about the circuit. The relevant scientific question is therefore whether **learned move selection beats well-tuned search under the same information and computation budget**.

## Project implications

SA is a mandatory serious baseline for the proposed contribution. A weak random-move comparison alone cannot establish value. Two controls answer different questions:

1. **Shared-action SA:** same legal moves, reward evaluator, and initial layout as the learned policy. This isolates move selection and acceptance strategy.
2. **Upstream SA implementation:** preserves a stronger published system, subject to compatibility. This measures practical competitiveness but may differ in its move set, evaluator, and threading.

If the upstream system cannot be integrated, report that limitation and include a transparent, tuned shared-action implementation. Do not label a restricted student implementation as a complete reproduction of TILOS SA.

## Important interpretation limits

Different macro placers may optimize different proxy costs and run different downstream flows. Favorable HPWL does not automatically imply better timing. Likewise, wall time depends on worker count. A multi-start method using many CPU cores cannot be described as compute-matched to a single-thread run merely because both finish after ten minutes.

## Mid-sem explanation and deliverable

Show a tiny legal placement where one worsening move enables a later improvement. Explain SA acceptance as `min(1, exp(-(C_new-C_old)/T))` for a cost to minimize. Then state the RL hypothesis precisely: structural context may make exploration more efficient across unseen circuits. This is a testable hypothesis, not an assumed advantage.

Proposed reproduction gate: validate a move's legality, cost update, undo operation, and seed behavior before timing a full SA sweep.
