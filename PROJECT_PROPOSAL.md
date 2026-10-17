# Selected project: congestion-aware preference-conditioned RL placement refinement

## Current recommendation: attachment points 4 and 5

Train a MaskRegulate-style **refiner** with an explicit congestion reward and an inference-time preference vector. Given a common initial layout and weights `w=(w_HPWL,w_regularity,w_congestion)`, the frozen actor and critic produce a refined feasible layout. Query a fixed weight set to form an empirical nondominated candidate set. Test on unseen circuit families against fixed-weight specialists and strong search using the same **total** candidate-generation budget.

The core three objectives are pin HPWL, the existing regularity measure, and a precisely specified RUDY hotspot statistic. Normalize each objective using the shared initial layout and training-fixed denominator floors. Use capacities only when genuine physical routing capacities exist; otherwise report relative demand density. Timing-aware reward is optional and requires actual initial STA criticalities or a working periodic STA interface. Better RUDY is not proof of better timing or PPA.

**Novelty boundary:** [Chang et al. (2022)](https://arxiv.org/abs/2204.06407) already proposes flexible multiple-objective chip-placement RL. Our contribution is a tested congestion-aware preference-conditioned **refinement** extension, plus comparison against specialist/search controls, family-disjoint transfer, and proxy/routing validation. We do not claim to invent MORL or recover the true complete Pareto front.

## Current formulation and experimental evidence required

Let `f(s)=(L(s),R(s),C(s))` be nonnegative costs, `F_j(s)=f_j(s)/max(f_j(s_0),epsilon_j)`, and `w` lie on the three-objective simplex. A proposed dense scalar reward is `w^T(F(s_t)-F(s_(t+1)))`. It equals final scalarized improvement only under the stated undiscounted fixed-horizon conditions and correct terminal repair/fallback accounting. Keep a faithful native reference with its existing reward normalization and discounting.

Condition both actor and critic on weights sampled once per episode. A small preference embedding or tiled mask channels suffices; a new GNN is unnecessary. Compare native RL, fixed-weight congestion-aware RL, the conditioned policy, an independently trained specialist bank, no refinement, backbone continuation, and tuned greedy/SA sweeps. Show equal aggregate training resources and equal total online set budgets; separately label a higher-compute specialist ceiling.

Preserve the audited native selected-object definition and pass-wise OLD/NEW semantics. Check complete-pass endpoint legality. At a hard budget interruption return the last checked feasible full endpoint or the shared feasible start. Do not silently substitute an always-legal mask or a different hard-macro set and attribute the result to conditioning.

Evaluate feasibility, individual raw costs, preference-request cost, set hypervolume, runtime, and failures. Freeze normalization, preference queries, family splits, checkpoint selection, and hypervolume reference using training/validation only. A candidate set from 15 preferences must share one total budget; it does not receive 15 times a singleton baseline's budget. Route a small prespecified set of circuits/preferences if compatible, and analyze proxy/routed ranking reversals.

## Current eight-week scope and mid-sem claim

Weeks 1–2 establish the native interface, independent objective/legality checks, and a validated RUDY reward. Weeks 3–4 add conditioned actor/critic and freeze validation choices. Weeks 5–6 complete specialist/search controls and held-out equal-budget evaluation. Weeks 7–8 add focused ablations and optional routing/timing evidence, then prepare the report. GPU access is confirmed; hardware details and throughput still need measurement.

The mid-sem deliverable is a source-grounded formulation and plan. Existing synthetic demonstrations are explicitly toy work, not evidence of real-circuit improvement. Meaningful negative findings include preference collapse, no gain over specialists/search, or proxy improvements that fail routing validation.

Full current specification: [Approach E](approaches/E_CONGESTION_PARETO.md), [experimental protocol](methodology/experimental_protocol.md), and [toolchain feasibility](methodology/toolchain_feasibility.md).

## Historical alternative A: initialization robustness

The earlier initialization-robustness proposal below is retained for traceability. It is **not the selected main direction**. Its mixed-start/normalization factorial is archived; initializer shift may remain a small secondary evaluation for E. The earlier title, hypotheses, and schedule below apply only to alternative A.

<details>
<summary>Archived earlier proposal A — expand for historical reasoning</summary>

## Earlier option: initialization-robust cross-circuit RL refinement

## Archived alternative rationale

Train a single MaskRegulate-style policy to refine existing macro layouts. Evaluate it on circuit families absent from training and validation, and on initial layouts whose generation method was absent from training. Add two small, explainable changes: dimensionless representations/rewards and training with varied legal starting placements. Keep the architecture and action interface close to the baseline so the experiment can identify the cause of any improvement.

The main deliverable is a controlled answer to **when refinement transfers**, supported by a tested extension and a reproducible evaluation harness. Diffusion is a comparator and possible source of starting layouts, not a second large model to train from scratch.

## Why this is a meaningful gap

MaskRegulate already studies generalization. Its Section 4.3 uses training circuits superblue1/3/4/5 and held-out superblue7/10/16/18. Therefore “first cross-circuit refinement” is not a valid contribution. The unresolved question for this course project is whether transfer remains useful when both circuit structure and starting-layout distribution change under a strict evaluation protocol. [MaskRegulate paper](https://proceedings.neurips.cc/paper_files/paper/2024/file/fe224a60b878e79d5b3d79d7f113f76b-Paper-Conference.pdf)

ChipDiffusion provides a different hypothesis: learn placement structure from synthetic circuits, then guide sampling on a new graph. This does not by itself refute refinement-based RL. A generator and a refiner see different initial information, and different preprocessing, backends, and runtime boundaries can dominate comparisons. [ChipDiffusion](https://proceedings.mlr.press/v267/lee25y.html)

Our source audit also identifies experimental hazards: upstream MaskRegulate uses evaluation scores while saving best checkpoints; a test circuit passed to that routine could influence model selection. Use that routine for validation only. This is a code-path risk, **not an accusation that the published results used an invalid split**. Pin and inspect the exact revision. [Upstream main.py](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/src/main.py)

Newer EXPlace and FlowPlace already explore expert priors and stronger generative placement. Our proposal does not claim that expert boundary bias, synthetic-data training, or hard legal constraints are new. Consult the literature reviews for the precise overlap.

## Problem definition

Input: hypergraph G=(V,E), fixed die outline, macro sizes, pins/terminals, obstacles and placement constraints, and legal initial layout P0. Standard cells are handled consistently by a fixed downstream backend when available.

Output: a legal refined layout PT within a wall-clock budget B, measured at completed macro-pass boundaries. The policy parameters are frozen on test circuits. Reading the test netlist and evaluating a candidate's objective is allowed test-time optimization; updating neural weights is adaptation and must be a separately labeled experiment.

The released MaskRegulate uses OLD and NEW occupancy maps: it masks overlap with macros already adjusted in the current pass, so intermediate states can overlap macros not yet adjusted. Reproduce that behavior first; it is not identical to always-legal local relocation. Validate completed passes, and on budget interruption return the last checked feasible pass or the initial feasible layout. A strictly always-legal action interface is a separate variant. Also audit the released largest-512-by-area object selection: it must not silently become a different hard-macro benchmark in a comparison.

Legal means the appropriate bounds, orientation, blockage, overlap, spacing/halo and site rules supported by the benchmark are satisfied. A toy rectangle checker is insufficient for real physical legality.

Let H(P) be explicitly defined HPWL, C(P) a congestion **proxy**, and R(P) a regularity penalty. A proposed diagnostic cost is

```text
J(P;P0) = a H(P)/max(H(P0),eps_H)
        + b C(P)/max(C(P0),eps_C)
        + c R(P)/max(R(P0),eps_R).
```

Coefficients and fallback scales are chosen using training and validation only. Near-zero denominators require preregistered physical or training-set scales; do not let an arbitrary epsilon create huge rewards. First reproduce the upstream objective exactly. Then normalize equivalent terms; adding congestion is a separate optional extension and ablation, not an unnoticed change to the objective.

For finite undiscounted episodes, reward `r_t=J(P_t)-J(P_(t+1))` sums to net cost improvement. With discount gamma<1 it no longer simply telescopes. State this distinction and keep gamma identical across the compared agents. Evaluation reports the individual metrics regardless of the scalar training reward.

State must include OLD/NEW layout information, pass phase, current macro or macro-selection state, action mask, die/net information, and remaining budget if decisions depend on it. The action relocates the selected macro to a grid location allowed by the specified mask. Use the original macro ordering first. A no-op is only admissible when it satisfies the current mask; it cannot be assumed safe in an intermediate overlapping pass. This is a refinement MDP, not an RL controller for changing macro dimensions or logical circuit design.

## Hypotheses

**H1 — joint transfer:** normalization plus mixed starting placements improves the per-design refinement gain on unseen families, particularly under a held-out initializer, versus unmodified MaskRegulate.

**H2 — learned value:** the proposed policy improves quality at equal deployment compute compared with greedy legal moves and tuned simulated annealing. A policy that wins only against doing nothing has weak evidence of learned benefit.

**H3 — proxy validity:** HPWL gains do not necessarily improve routed congestion/timing. On a small flow-compatible subset, measure whether improvements survive downstream evaluation. This is an empirical question, not an assumed benefit.

These are proposed hypotheses. No supporting experimental results have been produced yet.

## Proposed method

1. Establish the upstream baseline with its original cost and masks, pinned environment, explicit seeding before model construction, validation checkpoint selection, and legal export.
2. Audit existing normalization first: upstream already uses a fixed grid and train-calibrated reward extrema. Compare that native convention with proposed per-episode or physical-reference scaling; dimensionless coordinates alone may add nothing. Express any additional dimensions/areas or cost-map magnitudes using explicit scales while preserving relative net information.
3. Train the same policy with a mixture of legal starts generated using different seeds, safe perturbations and, once feasible, distinct analytical initialization procedures. Do not call random perturbations a new initializer family. Use comparable training budgets and count data-generation cost.
4. Test a 2x2 factorial: native/train-calibrated versus proposed transfer-reference scaling × single/mixed starting distribution. If scaling combines inputs and rewards, add one focused split ablation before assigning the effect to either part. Do not describe the native policy as unnormalized.
5. Evaluate a frozen model under fixed objective-evaluation and wall-clock budgets in separate experiments. For passwise methods, use only checked feasible pass endpoints. Deployment rollback is available to all optimizers with its evaluation cost included.

No mandatory GNN rewrite, graph pretraining, online PPA reward, or full ChipDiffusion retraining is required. These would make attribution and the eight-week schedule harder.

## Experimental design

**Splits:** circuit family is the unit of independence. All floorplan, utilization, technology, netlist-size and random-placement variants from the same underlying design stay together. Use an auditable manifest of origin, family and file hashes. Check checkpoint pretraining circuits before calling an evaluation zero-shot. If benchmark provenance is insufficient, report a design-disjoint split with the uncertainty rather than claiming family-disjoint transfer.

**Shift grid:** evaluate unseen circuits with familiar initializers and unseen circuits with a held-out initializer. Separately test size/utilization shifts only if enough independent designs exist. Analyze initial quality because strong starts can leave little improvement headroom.

**Refinement comparison:** identity; random masked moves; greedy coordinate/local search; tuned simulated annealing; frozen original MaskRegulate; proposed variant. Give matched-mask controls the same P0, pass/move interface, endpoint checks, evaluator and deployment budget. Strong classical systems using different legality or neighborhoods are separately labeled deployment controls, not evidence that the policy alone caused a difference.

**Generation comparison:** analytical placement, ChipDiffusion and optionally FlowPlace produce P0 under their own compatible input interfaces. Report complete pipeline quality/time with the same downstream backend. An additional `generator + common refiner` experiment isolates complementarity. Do not put a generator in the common-P0 refinement leaderboard as if it solved the same task.

**Metrics:** macro and global HPWL reported separately; overlap/constraint violations; defined congestion proxy; complete refinement and full-pipeline runtime; downstream routed wirelength, overflow and WNS/TNS when available. Power and area are reported only with the necessary libraries, activity assumptions and flow. Fixed die area and fixed macro area cannot demonstrate area reduction.

**Statistics:** target at least three training seeds and paired initialization/evaluation seeds as budget permits. Average repetitions within each circuit, then summarize across circuits with per-circuit tables and an appropriate paired uncertainty interval. Thousands of macro moves are not thousands of independent circuits. Small benchmark suites support case-study conclusions, not universal guarantees.

**Decision rule:** freeze metrics, tolerance definitions and checkpoint rule before test access. A useful outcome requires feasible layouts and improvement against original RL and the strongest budget-matched search, or a clear diagnosis showing where and why transfer fails. “Statistically significant” is insufficient if effect size or runtime cost is negligible.

## Mid-semester scope: due in six hours

Completed in this research package: paper and code review, scoped problem and hypotheses, alternative approaches, benchmark risks, evaluation specification, and an explanatory toy example. The toy example is not a paper reproduction or proof of generalization.

Present the methodology as a proposal. Show implementation milestones as planned until actual logs exist. Prepare a six-hour sequence in [the preparation plan](presentation/SIX_HOUR_PLAN.md). The immediate goal is a clear defense of the question, the novelty boundary and the planned evidence.

## Eight-week execution plan

| Week | Deliverable | Exit condition |
|---|---|---|
| 1 | Linux/CUDA environment, benchmark inventory, pinned source | One real design parses and objective/legality agree on export/reimport |
| 2 | Original policy and non-RL baselines | One repeatable baseline table on train/validation; no final test tuning |
| 3 | Normalization and mixed-start generation | Consistent legal starts; recorded preprocessing cost; training stability |
| 4 | Factorial training and validation | Select frozen configurations using validation; decide whether diffusion adapter is feasible |
| 5 | Held-out circuit and initializer evaluation | Complete paired runs, error/failure ledger, quality-vs-time curves |
| 6 | Focused ablations and shift analysis | Explain which component helps, and which design features predict failure |
| 7 | Small downstream flow subset; optional diffusion hybrid | Verify proxy gains or document inability/mismatch; avoid full PPA claims without data |
| 8 | Final analysis, reproducibility release, report and end-sem slides | Tagged configurations, raw results, uncertainty, limitations, honest conclusions |

GPU access is confirmed by the user; GPU model, memory, team size and throughput are unknown. Measure environment-step, policy-update and backend-evaluation time before choosing dataset size. A GPU does not eliminate CPU-heavy placement and routing costs. Cap the first real-circuit experiment to a measured pilot and scale only when the estimated run matrix fits.

## How this satisfies the instructor's requirements

| Requirement | Evidence planned |
|---|---|
| Meaningful contribution | Explicit joint circuit/initializer shift study plus controlled robustness extension |
| Clear formulation | Frozen-policy refinement MDP with legal states and finite deployment budgets |
| Theory | Hypergraph placement, dense rewards, scalarization, PPO and generalization distinctions |
| Baselines | Original RL, identity, random, greedy and simulated annealing; separate generative pipeline comparison |
| Ablations | 2x2 design; input/reward split if needed; single versus mixed starts |
| Analysis | Per-design gains, shift sensitivity, runtime, failures and downstream proxy mismatch |
| Limitations | Few independent circuits, upstream environments, provenance, proxy fidelity, PPA access |

The earlier title describes archived alternative A only. The selected mid-sem project is now congestion-aware preference-conditioned refinement. A broader claim such as “RL beats diffusion for chip design” would exceed both task definition and evidence.

</details>
