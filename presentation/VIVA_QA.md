# Mid-semester questions and concise answers

## What exactly is the project?

We will test whether a frozen RL refiner improves unseen circuit families, including unfamiliar initial layouts. We propose a controlled robustness extension using varied starting layouts and revised reference scaling, then compare it with the native policy and strong search baselines under fixed compute budgets.

## Hasn't MaskRegulate already shown generalization?

Yes. Its Section 4.3 trains on superblue1/3/4/5 and tests superblue7/10/16/18. Our novelty is not that first experiment. We study joint initializer/circuit shift, isolate a small extension and use an auditable validation/test split and compute-matched controls. [Paper](https://proceedings.neurips.cc/paper_files/paper/2024/file/fe224a60b878e79d5b3d79d7f113f76b-Paper-Conference.pdf)

## What does “regulator” do?

It changes macro positions in an existing placement. The term does not mean resizing macros or regulating circuit voltage. Seeing a complete starting layout can make the effect of a move easier to estimate.

## Why is reward denser?

An action can be evaluated against existing macro positions. Frequent cost changes provide more feedback than a purely terminal score. Constructive methods can also use dense proxies, so dense reward alone is not unique to refinement.

## Are all intermediate states legal?

Not in the released MaskRegulate's passwise OLD/NEW mask. It can overlap macros that have not yet been adjusted. We will reproduce that behavior explicitly, validate complete passes, and return the last verified feasible endpoint if a time budget interrupts the pass. Strict always-legal moves are a different variant.

## Why not replace the model with a GNN?

That would add an architecture confound and implementation work. First isolate whether training distribution and scaling are responsible for transfer. A graph architecture can be future work if the controlled study finds a representation bottleneck.

## Isn't normalization already present?

Yes. Upstream has a fixed spatial grid and train-calibrated reward extrema. The proposed ablation compares the native convention with per-episode or physical-reference scaling. If that adds no value, we will report it. We do not claim to introduce normalization to the baseline for the first time.

## What is the role of PPO?

PPO learns action probabilities using trajectories and an advantage estimate, with a clipped update objective. It is the learning engine. It does not provide a guarantee that the representation transfers or that the physical layout is legal.

## Why does your reward correspond to final quality?

For an undiscounted finite episode, summing cost differences equals initial minus final cost. Discounting, clipping and auxiliary rewards alter that relationship. Even an exact proxy improvement does not guarantee routed timing or power improvement.

## What are your strongest baselines?

Original frozen MaskRegulate, tuned greedy/coordinate search, simulated annealing, and continuation of the initial analytical placer. Identity and random moves are sanity checks. Shared-mask controls isolate policy learning; complete external systems measure deployment competitiveness.

## Why do you need a family split?

Two variants of the same RTL design can share substantial structure. Keeping them in different splits can overstate transfer. All parent-design variants, seeds and augmentations must remain together. If provenance is uncertain, we will narrow the claim to design-disjoint evidence.

## What leakage risk did you find?

The upstream training script saves best checkpoints based on its evaluation set. That set must be validation, not final test. This is a code-path hazard; it does not establish that the paper itself leaked test data. We will seed before model construction and freeze checkpoint selection rules before test runs. [Pinned source](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/src/main.py)

## How is this compared with diffusion fairly?

There are two comparisons: complete generation-plus-refinement pipelines under a common backend and total time budget; and different refiners starting from the identical diffusion layout. We must verify graph, pin, geometry and object equivalence first. We will not compare unrelated paper-table numbers as a direct ranking.

## Does zero-shot mean no optimization?

No. It means no task-specific weight updates under the declared setting. Diffusion guidance and a frozen RL policy can still perform substantial optimization on the new circuit. We time that work.

## Why might mixed starts help?

The policy sees a broader range of states during training and may rely less on one initializer's spatial patterns. But the effect could be explained by extra data/compute, so training budgets and start generation costs must be controlled.

## Will you report power, performance and area?

Only where the benchmark has the required libraries, constraints and compatible flow. The core study reports HPWL, explicitly defined congestion estimates, legality and runtime. On a fixed downstream subset we will attempt routing and timing. Fixed die and macro areas do not yield area reduction simply by rearrangement.

## How many seeds and circuits?

The target is at least three training seeds if the pilot budget supports it, with paired evaluation starts. Circuit/family counts depend on a provenance and compatibility audit; a provisional 6/2/4 split is not an established dataset inventory. Families, not macro moves, are the independent generalization units.

## What if the method loses to simulated annealing?

Then the main result is that the proposed learned extension is not competitive under those budgets. We will identify where transfer fails and whether apparent gains disappear after matching compute. This is useful only with checked implementations, tuned controls and clear limits.

## What have you actually completed?

Literature and code analysis, problem formulation, method alternatives, evaluation and ablation design, a repository and presentation preparation. The supplied scripts explain a toy objective and validate a synthetic split manifest. No real-circuit training or PPA result has been produced in this research pass.

## What is the biggest practical risk?

Old dependencies, large CPU/host-memory requirements, differing benchmark object definitions and incompatible evaluators. GPU access helps training but does not solve parsing, legality, physical-flow data or routing cost. Week 1 measures these before committing to a large run matrix.

## Why is the proposal appropriate for two months?

It reuses the baseline architecture, limits the main change to a measurable robustness extension, and prioritizes controls and analysis. Diffusion integration and full downstream PPA are gated extensions. The project remains complete if the core study produces a well-supported negative result.
