# Research analysis and choice of project direction

Research checked 17 October 2026. This synthesis combines the separate literature/code reviews with original analysis. It proposes experiments; it does not report new placement results. The scope is a mid-semester research defense due within six hours, followed by approximately eight weeks of GPU-supported work. No deck is being created.

**Current selection:** [E — congestion-aware preference-conditioned refinement](approaches/E_CONGESTION_PARETO.md), following the user's attachment points 4 and 5. The earlier initialization-robustness proposal A is retained as an archived alternative; it is not the current research spine. Historical transfer analysis below remains useful for evaluating E.

## 1. The most useful question

The broad brief asks whether RL refinement generalizes to unseen circuits. The selected project sharpens this to:

> Can one preference-conditioned RL regulator generate useful HPWL–regularity–congestion trade-offs on unseen circuit families, compared with specialists and search under a fixed total candidate-generation budget?

This asks about controllable, useful refinement rather than only executing a model on a new graph. A conditioned policy can ignore weights, produce duplicate layouts, need more compute than a specialist, or optimize RUDY while worsening actual routing. These are empirical failure modes the project must measure.

The selected contribution is a cheap explicit congestion reward plus preference-conditioned refinement and controlled evaluation. It is an extension of established ideas. [Chang et al. (2022)](https://arxiv.org/abs/2204.06407) already proposes flexible MORL for chip placement; preference conditioning or a Pareto interface alone cannot be claimed novel. The earlier joint circuit/initializer-shift question is retained as an optional secondary test.

## 2. What the literature already establishes

| Work | Established idea or evidence | What it does not establish for our project |
|---|---|---|
| [MaskPlace](literature/rl_maskplace_2022.md) | Pixel masks, dense feedback and constrained constructive placement | Refinement does not uniquely own dense reward or masking |
| [ChiPFormer](literature/rl_chipformer_2023.md) | Offline sequence-model transfer and target-task improvement | A frozen refiner's compute-matched initializer robustness |
| [MaskRegulate](literature/rl_maskregulate_2024.md) | Existing-layout RL, regularity and cross-chip evaluation | Universal transfer across initializer/family shifts, budgets and downstream flows |
| [Flexible MORL chip placement, Chang et al. 2022](https://arxiv.org/abs/2204.06407) | Inference-time variable objective weights in one pretrained placement model | That preference conditioning alone is a new contribution; our test concerns congestion-aware refinement and controlled evaluation |
| [IncreMacro](literature/rl_incremacro_2024.md) | Non-RL incremental physical refinement and relation preservation | That learning is necessary for useful refinement |
| [ChipDiffusion](literature/diffusion_chipdiffusion_icml2025.md) | Synthetic-data conditional coordinate generation and zero-shot real-circuit placement | A controlled comparison against frozen MaskRegulate refinement on common inputs |
| [EXPlace](literature/rl_explace_2026.md) | Expert-informed placement and timing feedback | That adding another expert mask would be a distinct contribution |
| [FlowPlace](literature/diffusion_flowplace_dac2026.md) | Flow-matching placement and explicit constraint handling | That faster generative placement alone answers learned-refinement value |
| [DREAMPlace](literature/eval_dreamplace.md) | Strong analytical backbone and benchmark variants | That every file variant represents the same task |
| [MacroPlacement/SA](literature/eval_macroplacement_sa.md) | Need for strong classical baselines and careful evaluation | That winning against identity or weak random search is sufficient |
| [ChiPBench](literature/eval_chipbench.md) and [OpenROAD](literature/eval_openroad.md) | Downstream evaluation interfaces and design data | That HPWL-only files automatically support PPA claims |

The associated source links and evidence boundaries are in each standalone review. Published percentages belong to the authors' exact flows; they should not be copied into a new “our methods” ranking.

## 3. Why refinement might transfer—and why it might not

**Reason to expect transfer:** complete starting-layout context makes the local consequences of a macro adjustment more observable. Mask-based cost features can encode geometric relationships without assigning a separate learned parameter to every circuit identity. A shared controller might reuse useful placement behavior.

**Structural shift:** new graphs can change net fanout, macro size distribution and the relationship between macros and IOs. A policy can act on the same tensor dimensions while encountering a very different decision problem.

**Initializer shift:** the same netlist may be placed by another algorithm that creates different macro ordering, spacing and optimization basins. A policy trained on one characteristic layout can learn that initializer's errors rather than transferable improvement rules.

**Quality shift:** poor starts offer abundant easy gains; excellent starts may require temporary proxy degradation or coordinated moves. Report absolute starting quality and improvement headroom. Do not infer robust performance from large percentage gains on deliberately degraded starts alone.

**Reward shift:** train-calibrated extrema may scale unseen costs poorly. Per-episode reference scaling may help, but it can also hide useful size information or magnify tiny denominators. This is a falsifiable mechanism, not an assumed improvement.

**Objective shift:** macro-pin HPWL, full standard-cell HPWL, congestion and timing are different functions. A policy can generalize its training proxy while harming practical implementation.

**Compute shift:** a pass that fits on a small circuit may exceed the entire runtime budget on a large one. Because the native mask permits intermediate overlap, incomplete passes cannot automatically be scored as feasible final layouts. A method that completes no pass within budget must be reported as such.

## 4. The selected direction and historical alternatives

| Direction | Main contribution | Feasibility in eight weeks | Main risk | Recommendation |
|---|---|---|---|---|
| [E: Congestion-aware Pareto refinement](approaches/E_CONGESTION_PARETO.md) | Explicit RUDY hotspot feedback plus preference-conditioned refinement and matched-budget set evaluation | Reasonable after native/RUDY pilot; optional timing requires physical data | Existing MORL prior art, proxy gaming, preference collapse, candidate-set compute inflation | **Selected main project** |
| [A: Robust transfer](approaches/A_ROBUST_TRANSFER.md) | Joint circuit/initializer shift study; mixed-start training and transfer-referenced scaling | Reuses architecture and native masks | Incremental method; strength depends on rigorous analysis and search controls | Archived earlier main alternative; limited initializer shift can evaluate E |
| [B: Adaptive regularity](approaches/B_ADAPTIVE_REGULARITY.md) | Identify and adapt when geometric boundary preference helps | Reasonable if a pilot shows a consistent regularity failure | Expert priors and conditioning overlap with existing work; few families may underfit the question | Alternative if mechanism is supported |
| [C: Diffusion + RL](approaches/C_DIFFUSION_RL_HYBRID.md) | Quantify generator/refiner complementarity at equal total cost | Integration dependent; pretrained models reduce training work | Mismatched object definitions, formats, legalizers and hidden inference optimization | Stretch comparison |
| [D: Budgeted reliable refinement](approaches/D_BUDGETED_RELIABLE_REFINEMENT.md) | Predict whether another completed pass is worth its cost and limit harmful intervention | Moderate after core rollout logs exist | Naive acceptance/stopping is already classical; learned gate must beat simple heuristics | Technical extension if core completes early |

These are not five required implementations. E is the current research spine. Preserve A–D as alternatives or staged follow-ups, not additional core requirements. Do not add diffusion training, GNN rewriting, and four-objective timing before the main controls and family-held-out study are complete.

## 5. The selected project's technical contribution

### Contribution 1: explicit congestion feedback with a defined estimator

Augment the existing wirelength/regularity regulator with a RUDY hotspot cost. Define bins, directional demand, capacities if available, net filtering/weights, degeneracy handling, and the top-tail aggregation. Normalize using the shared initial layout with training-fixed denominator floors. Validate full versus incremental affected-net updates. A relative demand estimator without physical capacities is not measured routing overflow.

### Contribution 2: inference-time preference control

Condition actor and critic on a simplex preference vector sampled once per episode. Preserve the core mask architecture and native pass semantics. Compare fixed-weight congestion-aware training with the conditioned policy and a bank of independently trained specialists. The test is whether a shared model offers useful trade-offs efficiently, not whether it can display different weight labels.

The original already normalizes rewards. A start-referenced scale is a labeled ablation, not the invention of normalization. Likewise, preference conditioning has direct chip-placement prior art. The expected contribution is the concrete refinement integration and evidence; do not inflate it into a new MORL algorithm.

### Contribution 3: evaluate candidate sets under fair resources

Use a predeclared preference query set and the same total runtime/candidate cap for conditioned RL, specialist banks, and scalarized SA/greedy sweeps. Compute empirical nondominance and fixed-reference hypervolume with identical normalized axes. Report individual objectives, feasibility, request latency, whole-set time, and preference collapse. Fifteen preference queries must not receive fifteen times a baseline's online budget. Report offline training cost separately.

Weighted sums can miss unsupported nondominated solutions of a nonconvex/discrete front; a finite policy-generated set is an approximation, not the true Pareto front. Check family-level uncertainty and worst-family behavior. Keep checkpoint and reference-point selection validation-only.

### Contribution 4: check the proxy on a small physical-flow subset

Freeze a compatible circuit/preference subset before evaluating downstream outcomes. Test whether the RUDY/HPWL rankings survive global or detailed routing and report reversals. Timing reward is optional: use genuine STA-derived criticality weights or periodic timed analysis, not fanout relabeled as timing. A timing-capable three-objective variant explicitly replaces regularity with the timing surrogate. This is not a promised complete PPA optimization system.

## 6. The exact minimum convincing experiment

1. A verified development circuit passes parser, geometry, object-selection, objective and complete-pass export checks.
2. A circuit-family manifest separates training, validation and final test; no test-driven checkpoint choice.
3. Native RL, fixed-weight congestion-aware RL, conditioned RL, and specialist policies use declared comparable aggregate training resources; label higher-total-compute specialist ceilings.
4. Each held-out circuit/start is shared by no-refinement, backbone continuation, SA/greedy sweeps, and learned variants, with matched final feasibility rules.
5. Equal total set-generation time and equal objective-evaluation budgets are separate views. Record complete-pass counts, unfinished work, and feasible incumbents.
6. Hypervolume uses frozen common objective scales/reference; queries/checkpoints are fixed before test. Every result includes failures, raw logs, seeds, and actual independent-family uncertainty.
7. At least one conclusion explains behavior: for example, added congestion reward reduces hotspots but worsens routing; the conditioned policy collapses to one layout; or specialists/search match its front at equal resources.

This is substantially more than a basic implementation even without designing a new neural architecture. Its credibility depends on execution and disciplined interpretation.

## 7. What would change the recommendation?

- **Upstream stack is intractable by week 2:** narrow to a reproducible native-policy audit and a small compatible benchmark rather than adding another model stack. Discuss the adjusted empirical scope with the instructor.
- **RUDY updates dominate runtime:** implement checked incremental affected-net updates or narrow the case set; do not omit estimator cost from timing.
- **Conditioned policy ignores preferences:** diagnose sampling, scales, actor/critic conditioning, and objective conflict using validation. A specialist comparison and honest collapse result are preferable to test-driven tuning.
- **A diffusion output can be round-tripped exactly by week 4:** add C as an initializer and pipeline comparison, using a verified frozen checkpoint.
- **Regularity correlates consistently with failures across validation families:** use this as analysis; consider B later, after E's fixed-weight and conditioned controls are complete.
- **Too few independent families exist:** use transparently limited design-disjoint studies or nested family cross-validation. Do not disguise augmentation as independent evidence.

## 8. What to say in the mid-semester discussion

Use the title **“Congestion-Aware Preference-Conditioned RL for Placement Refinement.”** State that MaskRegulate already studies cross-chip refinement and Chang et al. already studies flexible MORL placement. The project extends a refiner with explicit congestion feedback and preference control, then tests whether its trade-offs are useful under strict resources and unseen families. Present hypotheses, not forecast results.

Show the refinement MDP, objective normalization, RUDY concept, preference-conditioned actor/critic, and specialist/search comparison. Explain empirical nondominance, why weighted sums may miss parts of a front, and why set generation needs a total budget. Be able to describe temporary overlap, checkpoint selection, benchmark module definitions, and proxy-versus-PPA limits.

The six-hour goal is a clear technical defense. The eight-week goal is measured evidence with enough controls that a negative result is still informative.
