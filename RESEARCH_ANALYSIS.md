# Research analysis and choice of project direction

Research checked 17 October 2026. This synthesis combines the separate literature/code reviews with original analysis. It proposes experiments; it does not report new placement results. The scope is a mid-semester research defense due within six hours, followed by approximately eight weeks of GPU-supported work. No deck is being created.

## 1. The most useful question

The broad brief asks whether RL refinement generalizes to unseen circuits. The sharper project question is:

> When does a frozen placement-refinement policy produce useful improvement on an unseen circuit, and how much does that depend on the starting layout and available deployment compute?

This asks about **conditional usefulness**, not just whether a trained model can execute on a new graph. A refiner might technically transfer but make an already strong layout worse, need more time than search, or optimize a proxy that disagrees with routing.

The recommended project tests those possibilities and evaluates a modest robustness extension. It avoids spending the semester merely reproducing the original train/test table or making a difficult cross-tool comparison whose numbers cannot be interpreted.

## 2. What the literature already establishes

| Work | Established idea or evidence | What it does not establish for our project |
|---|---|---|
| [MaskPlace](literature/rl_maskplace_2022.md) | Pixel masks, dense feedback and constrained constructive placement | Refinement does not uniquely own dense reward or masking |
| [ChiPFormer](literature/rl_chipformer_2023.md) | Offline sequence-model transfer and target-task improvement | A frozen refiner's compute-matched initializer robustness |
| [MaskRegulate](literature/rl_maskregulate_2024.md) | Existing-layout RL, regularity and cross-chip evaluation | Universal transfer across initializer/family shifts, budgets and downstream flows |
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

## 4. The four plausible project directions

| Direction | Main contribution | Feasibility in eight weeks | Main risk | Recommendation |
|---|---|---|---|---|
| [A: Robust transfer](approaches/A_ROBUST_TRANSFER.md) | Joint circuit/initializer shift study; mixed-start training and transfer-referenced scaling | Best relative fit: reuses architecture and native masks | Incremental method; strength depends on rigorous analysis and search controls | **Core project** |
| [B: Adaptive regularity](approaches/B_ADAPTIVE_REGULARITY.md) | Identify and adapt when geometric boundary preference helps | Reasonable if a pilot shows a consistent regularity failure | Expert priors and conditioning overlap with existing work; few families may underfit the question | Alternative if mechanism is supported |
| [C: Diffusion + RL](approaches/C_DIFFUSION_RL_HYBRID.md) | Quantify generator/refiner complementarity at equal total cost | Integration dependent; pretrained models reduce training work | Mismatched object definitions, formats, legalizers and hidden inference optimization | Stretch comparison |
| [D: Budgeted reliable refinement](approaches/D_BUDGETED_RELIABLE_REFINEMENT.md) | Predict whether another completed pass is worth its cost and limit harmful intervention | Moderate after core rollout logs exist | Naive acceptance/stopping is already classical; learned gate must beat simple heuristics | Technical extension if core completes early |

These are not four required implementations. Choose A as the research spine; choose at most one of C or D as an end-semester extension. B becomes attractive if the initial failure analysis specifically implicates boundary bias. The final recommendation is based on integration effort and interpretability, not an asserted guarantee of publication novelty.

## 5. The recommended project's technical contribution

### Contribution 1: evaluate the joint shift correctly

Create a design-family and initializer matrix with all netlist relatives confined to one split. Separate validation from final tests and audit pretrained provenance. Measure the frozen native policy under familiar and unfamiliar initializer algorithms, then separately vary initializer quality. This distinguishes graph transfer from starting-state dependence.

### Contribution 2: a controlled robustness intervention

Keep the baseline architecture and passwise interface. Train on a mixture of legal starting states; compare native train-extrema scaling with a proposed initial-layout or physical-reference scaling. This is an explicit small extension. The existing fixed-grid and normalized features are not newly invented.

The factorial design asks whether start diversity, scaling, their interaction, or neither explains the effect. If initial representation auditing shows no meaningful scaling change is needed, narrow the central intervention to mixed-start training and spend the saved compute on stronger controls and held-out families. Do not retain a redundant component merely to make the method sound more complex.

### Contribution 3: measure improvement reliability and cost

Alongside mean HPWL, measure worst-family degradation, harmful-refinement fraction, feasible completion rate, displacement and quality versus time. Compare shared-mask greedy/SA controls, then separately evaluate strong practical optimizers with their native transitions. If a policy sees a wire-cost map, classical controls deserve that same information when isolating learning.

### Contribution 4: check the proxy on a small physical-flow subset

Freeze a compatible subset before evaluating downstream outcomes. Test whether proxy rankings survive routing/timing. This is an evidence check, not a promised complete PPA optimization system. The project can be complete with restricted routing evidence and a transparent limitation if the core evaluation is strong.

## 6. The exact minimum convincing experiment

1. A verified development circuit passes parser, geometry, object-selection, objective and complete-pass export checks.
2. A circuit-family manifest separates training, validation and final test; no test-driven checkpoint choice.
3. Original RL, mixed-start RL, proposed reference scaling, and the combined variant use comparable training budgets. If a component is redundant, explain and reduce scope before final tests.
4. Each held-out circuit/start is shared by identity, random masked actions, greedy, SA and learned variants. Add analytical-backbone continuation as a deployment baseline.
5. Equal deployment time and equal objective-evaluation budgets are separate result views. Record full pass counts and feasible incumbents.
6. Every result includes failures, metrics definitions, raw logs, seeds and uncertainty across actual independent families.
7. At least one conclusion is an explanatory analysis: for example, mixed starts help only on weak starts; scaling helps only at large size shift; or SA removes the learned method's apparent advantage.

This is substantially more than a basic implementation even without designing a new neural architecture. Its credibility depends on execution and disciplined interpretation.

## 7. What would change the recommendation?

- **Upstream stack is intractable by week 2:** narrow to a reproducible native-policy audit and a small compatible benchmark rather than adding another model stack. Discuss the adjusted empirical scope with the instructor.
- **Mixed starts give no validation benefit:** do not tune on test. Investigate whether stronger starts, mask shortcuts or normalization saturation explain it; consider D only if pass cost varies enough to support a stopping question.
- **A diffusion output can be round-tripped exactly by week 4:** add C as an initializer and pipeline comparison, using a verified frozen checkpoint.
- **Regularity correlates consistently with failures across validation families:** consider B with an interpretable selector and fixed-coefficient controls.
- **Too few independent families exist:** use transparently limited design-disjoint studies or nested family cross-validation. Do not disguise augmentation as independent evidence.

## 8. What to say in the mid-semester discussion

Use the title **“Initialization-Robust Cross-Circuit RL Refinement under Fixed Compute Budgets.”** State that existing work motivates the mechanism and already demonstrates initial cross-chip evidence. Your contribution is a stricter conditional generalization question, a small testable extension and a controlled evaluation. Present hypotheses, not forecast results.

Show the refinement MDP, one HPWL calculation, the four-way ablation and the split/budget design. Explain why diffusion is a comparison setting rather than a simple replacement baseline. Be able to describe temporary overlap, checkpoint selection, benchmark module definitions and the difference between proxies and PPA.

The six-hour goal is a clear technical defense. The eight-week goal is measured evidence with enough controls that a negative result is still informative.
