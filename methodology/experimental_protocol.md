# Experimental protocol: initialization-robust cross-circuit RL refinement

Status: **proposed study; no training, placement, routing, or performance results have been produced by this research pass.** Mid-sem deadline: six hours. Full-project horizon: approximately eight weeks. GPU access is confirmed; GPU model, memory and measured throughput remain unknown.

## 1. The research question and the intended contribution

**Can an RL macro-placement refiner trained on several circuit families improve unseen families reliably when the initial placement algorithm or quality changes, under the same online compute budget as classical search?**

The proposed contribution is a controlled study plus a modest training extension: compare the native **train-calibrated extrema normalization** with a **transfer-referenced normalization**, and train with a mixture of initial-placement qualities. The original already normalizes reward; adding normalization in general is not a novel contribution. The factorial evaluation separates normalization-reference choice from start diversity. It does not require replacing the published policy with a new GNN.

The central claim to test is initialization robustness, not a general claim that RL beats all placers or generalizes to arbitrary chips. If the extension does not improve held-out performance, a leakage-audited, compute-matched diagnosis of where and why it fails is still a potentially meaningful course contribution.

### Hypotheses, fixed before final testing

- **H1:** Training on mixed initial layouts reduces degradation when the initializer changes at test time, compared with training on a single initializer.
- **H2:** A transfer-referenced reward normalization improves transfer across circuit sizes or starting qualities, compared with the native training-extrema reference. Coordinate/action conventions remain fixed in this experiment.
- **H3:** Any improvement survives comparison against bounded coordinate descent, SA, and a backbone-only continuation at matched online runtime; distinguish matched transition semantics from practical complete-system comparisons.
- **H4, exploratory:** Proxy improvements have imperfect agreement with downstream routing quality; characterize failures rather than assuming agreement.

Report H1-H4 separately. Passing H1 while failing H3 supports robustness improvement, not superiority over classical search.

## 2. Dataset manifest and leakage control

Build the manifest before training. Each row must contain source URL, revision/hash, file hash, root RTL/design lineage, family ID, technology, floorplan, fixed/movable object rules, macro count, cell/net count, units, available timing/library/route data, parser status, and legalizer compatibility.

**Split by parent design family.** All technology mappings, variants, augmented layouts, altered floorplans, and different initializer seeds of one parent must remain in the same split. Avoid preprocessing all designs together: fitted scalers, learned clustering, curriculum thresholds, and reward calibration use training data only.

For ChiPBench, conservatively group Ariane variants together, BlackParrot blocks/variants together, and SweRV variants together. Audit ancestry of other designs rather than inferring independence from filenames. See the [official case list](https://github.com/MIRALab-USTC/ChiPBench#dataset). For ISPD/MMS, audit provenance and related variants separately; synthetic transformations are not new independent circuits.

**Target, not established inventory:** approximately 6 training / 2 validation / 4 test independent families if the manifest supports it. Do not force these counts by treating sibling variants as independent. If fewer families are compatible, report the actual count and use a smaller prespecified split or family-level cross-validation; describe the resulting uncertainty. A leave-one-family-out analysis is useful when feasible, but its tuning must remain nested within the remaining families.

Validation families select hyperparameters, reward weights, episode count, and checkpoints. Final test families never select the best epoch, initializer, temperature, move radius, or downstream candidate. In particular, do not reuse an upstream script's periodic test evaluation as a model-selection signal. Checkpoint using validation only.

Two distinct transfer claims require two labels:

1. **Unseen-family transfer:** hold out the circuit family while keeping the experiment schema and technology consistent.
2. **Cross-domain transfer:** change benchmark schema, technology, or routing stack as well. This adds confounders and is optional.

## 3. Freeze the physical optimization problem

Within each experiment, freeze die/core dimensions, macro sizes and allowed orientations, pin offsets, IO locations, blockages, halos, grid resolution, density target, and which instances are fixed. Export a common instance-ID map. Record the same legalizer, standard-cell placer, and downstream flow versions for every method.

**Selected objects are part of the task definition.** The audited native reader sorts instances by area and chooses the largest `n_macro` (default 512). These selected modules are not automatically the physical hard-macro set. Preserve the selection for the reproduction track, record every selected instance ID/type, and describe the study as selected-module refinement where appropriate. A hard-macro-only experiment is a separately declared task variant applied consistently to all methods. Likewise, record native canvas compression and coordinate transforms rather than silently reverting them. See the [audited reader](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/utils/read_superblue.py) and [problem instance](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/src/problem_instance.py).

First verify format equivalence with counts and coordinate/pin checks. An original ISPD2005 case, an I/O-freed variant, and a modified MMS case are not interchangeable; [DREAMPlace documents these distinctions](https://github.com/limbo018/DREAMPlace#reference-results-for-macro-placement).

**Pass-wise versus always-legal transitions:** the native OLD/NEW occupancy logic masks previously adjusted modules but can overlap modules not yet adjusted. Therefore an intermediate native state must not be described as a fully legal placement. Preserve native pass-wise transition semantics for the reproduction track. At the end of every complete pass, check full geometry against the declared selected/nonselected objects, bounds, blockages, and constraints; do not infer legality from the policy mask alone. If legalizer repair is required, report its distance, time, pre/post-repair cost, and failure rate.

Initialize evaluation from a checked feasible full placement and keep a saved feasible incumbent. At a hard time/evaluation limit, return the **last checked feasible complete-pass endpoint**, or the shared initial feasible placement if no pass endpoint qualifies. Never score an interrupted, partially adjusted native pass as the final answer. Include complete-pass checking, repair, and all discarded/unfinished work in the online budget; reserve a fixed checking allowance or return the prior incumbent when insufficient budget remains. Apply the same incumbent/fallback contract to controlled methods. Show endpoint-quality-versus-time as a step function and report the fraction of budgets that complete no pass.

A strictly always-legal mask is an optional additional ablation, not a silent reproduction fix. It changes the reachable intermediate states and exploration problem. Keep its results separate from the native semantics. For complete-system baselines with different transition semantics, compare final feasible outputs and total cost, and do not claim that this isolates policy learning alone.

## 4. Factorial training experiment

Train four configurations using identical networks, training-step budgets, validation rules, and as many independent training seeds as affordable (target three; five only if the pilot supports it).

| ID | Feature/reward convention | Training initial placements | Purpose |
|---|---|---|---|
| A | Native train-calibrated extrema reference | Single initializer/quality | Reproduction-oriented reference |
| B | Proposed transfer-referenced normalization | Single initializer/quality | Isolate normalization-reference choice |
| C | Native train-calibrated extrema reference | Mixture | Isolate start diversity |
| D | Proposed transfer-referenced normalization | Mixture | Combined proposed method |

**Normalization-reference specification:** the audit found that the native method collects min/max reward extrema using calibration trajectories on training designs; its shifted-design normalized values need not stay within the nominal range. Preserve this reference in A/C and log extrapolation. In B/D, test a dimensionless reward component such as wirelength change divided by that episode's initial HPWL, with an explicit positive floor and the same underlying cost components/weights. An episode's initial HPWL is available inference-time context, not test-outcome fitting. Calibrate any additional constants on training families only and use validation to freeze the exact formula. Keep native observation, action, geometry, regularity, discounting, and clipping conventions unchanged in the four-way experiment, except for the declared reward-reference change. Any later `x/W`, action-radius, congestion-objective, or regularity-definition modification requires its own ablation. The native source is [place_env.py](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/src/place_env/place_env.py).

**Start mixture:** use legal layouts from a fixed backbone at prespecified optimization checkpoints, plus bounded legal perturbations of converged starts. Include a second initializer only after its interface passes. Freeze mixture probabilities using validation. A perturbed layout is an augmentation, not an independent design. Do not generate the mixture by selecting layouts that the proposed policy happens to improve most.

For a cost `C(s)` to minimize, a simple dense reward is `r_t = C(s_t) - C(s_(t+1))`, with explicit normalization and legality handling. This telescopes to net cost reduction only for an undiscounted fixed-horizon return without extra terms. If the original RL uses discounting, variable episode lengths, clipping, or auxiliary penalties, explain the changed objective rather than claiming exact equivalence. Keep the original algorithm for the reference; document every modification.

## 5. Test matrix and controls

Evaluate on unseen families with (i) the training-style initializer, (ii) a held-out initializer or held-out quality regime, and (iii) prespecified perturbation magnitudes. Share the exact initial artifact for each circuit/initializer/seed across methods. Separate initializer **quality shift** from initializer **algorithm shift** in figures.

Mandatory controls:

- No refinement: measures whether an intervention improves its own starting point.
- Backbone continuation: spend the same additional runtime optimizing the initial analytical placement.
- Random action selection using the native pass-wise masks and complete-pass incumbent contract.
- Greedy or bounded coordinate descent with the same candidate neighborhood and pass semantics where possible.
- Shared-transition SA, if it can use the same pass-wise interface, with temperature and move settings selected on validation only.
- Original/native RL refiner and the four configurations of the two-factor experiment above.

Useful stronger controls if compatible: upstream TILOS SA and the ICML 2025 diffusion model. [MacroPlacement's current assessments](https://github.com/TILOS-AI-Institute/MacroPlacement) make strong search baselines especially important. Label shared-action implementations separately from published complete systems.

If greedy/SA cannot be expressed faithfully with native pass-wise transitions, include their strictly legal implementations as **practical feasible-output controls**, explicitly disclose the transition mismatch, and do not call them a pure action-selection ablation. A separate always-legal RL ablation can share their action interface if resources permit. All tracks use the same starting physical problem and fully checked final outputs. Report native pass count and selected-object count alongside objective-call budgets.

The diffusion comparison is conditional on code/data compatibility and available budget. Use two views where possible: its complete placement pipeline versus complete RL pipeline, and its output followed by the same refiners. The first measures practical quality/cost; the second tests refinement benefit. Do not describe a diffusion constructor and an RL refiner as identical tasks. Never tune a checkpoint on final test circuits. If no clean integration is possible, document the barrier and compare reported claims qualitatively without mixing published numbers into our experimental table.

## 6. Budget accounting

Report **two complementary matching schemes**:

1. Equal online wall time on the same machine and thread/GPU limits, including preprocessing, policy inference, mask generation, objective calls, legalization, backend updates, and candidate selection.
2. Equal number of candidate objective evaluations, while also reporting wall time. One search sweep may inspect many alternatives; one RL action is not inherently equal compute.

Training and hyperparameter-search cost are reported separately, including all failed runs and seeds. State initializer cost, online refinement cost, final downstream evaluation cost, and total pipeline cost. Show quality-versus-time curves and area under a prespecified time range; do not report only the best final point. A pretrained policy may amortize training over many future designs; report a break-even estimate only from measured costs, not speculation.

Provisional test budgets: 30 / 120 / 600 seconds per circuit-start, revised once using development pilots and then frozen before test. These are planning choices, not achieved runtime. Restrict CPU threads equally. Warm up GPU kernels consistently and log hardware, clock/power policy where available, software, precision, and peak memory.

Budget fairness includes pass completion: no method may finish an incomplete pass for free after its deadline. Check and store feasible endpoints during the timed run; if the current pass is unfinished at the deadline, return the prior saved endpoint without post-deadline refinement. The same rule applies to objective-call limits. Report evaluation trajectories at feasible endpoints rather than misleading smooth curves through infeasible states.

## 7. Metrics and claim boundaries

| Measurement | Definition/report | Legitimate claim |
|---|---|---|
| Legality | overlaps, out-of-bound area, halo/blockage/orientation violations; feasible-run fraction | Geometric feasibility |
| Pin HPWL | sum of per-net pin bounding-box half-perimeters; net filtering/weights declared | Wirelength proxy |
| Congestion proxy | exact estimator, bin/capacity settings, units, aggregation | Proxy congestion only |
| Global routing | total/max overflow, global-route wirelength, routing completion | Routing-resource evidence |
| Detailed routing | routed wirelength, DRC count, completion, extracted WNS/TNS | Implementation evidence on selected designs |
| Area | core area and final cell area separately | Placement area is fixed if the floorplan is fixed |
| Power | leakage/internal/switching, library/corner/activity/frequency declared | Conditional tool-estimated power |
| Cost | online and total time, objective calls, CPU/GPU time, peak memory | Efficiency under named resources |

OpenROAD [distinguishes global and detailed wirelength](https://openroad.readthedocs.io/en/latest/main/src/grt/README.html); compare at the same flow stage. Power requires an appropriate activity model and physical data. HPWL-only ISPD files do not establish power, timing, or manufacturable PPA. Smaller HPWL does not prove lower power. A fixed-size floorplan cannot demonstrate reduced chip area unless a separate area optimization experiment is performed.

For method `m` on a common start, report `100*(HPWL_m - HPWL_start)/HPWL_start`; negative is better. Alongside this, compare against the strongest matched baseline. Do not silently drop failed/illegal runs or average only successes. Present feasibility and quality separately; any scalar failure penalty must be fixed in advance and accompanied by sensitivity analysis.

## 8. Statistics and visual analysis

The primary generalization unit is the **independent circuit family**. Multiple initial placements, test rollouts, and training seeds characterize variability within a family; they do not create more independent unseen circuits.

Average paired start/seed comparisons within a design, then average related designs within a family, and aggregate equally across families. Provide per-family tables, median/mean normalized improvements, worst-case degradation, feasible-run rate, win/tie/loss counts, and runtime curves. If reporting uncertainty, use a hierarchical bootstrap with families as the outer resampling unit and disclose the small family count. Treat intervals as descriptive when only a few families exist; avoid overinterpreting p-values.

Include failure examples: layouts, move trajectories, congestion heatmaps where available, and cost curves. Analyze associations with macro count, occupied area fraction, connectivity, and starting quality as exploratory findings, not causal proof. Test whether proxy rankings agree with routed rankings using paired plots/rank correlation on the fixed downstream subset, with uncertainty and sample size stated.

## 9. Six-hour mid-sem deliverable

The honest deliverable today is a source-grounded understanding, narrowed question, comparison matrix, manifest schema, four-way ablation design, budget plan, and eight-week schedule. Show any locally verified artifact only with its actual evidence. Do not label paper-reported numbers as our results or imply that a proposed experiment has run.

A useful presentation can still show the complete decision chain: placement problem → refinement MDP → why generalization can fail → initializer confound → proposed factorial extension → matched controls → evaluation/risks. Include one clearly labeled illustrative toy move if available, not a fabricated benchmark outcome.

## 10. Stop/go criteria and valid negative results

By the end of week 2, require a functioning native refiner on one development circuit, a common evaluation/legality interface, one working classical control, and measured throughput. If these fail, narrow to a transparent cross-initialization audit with the available system and small cases; obtain instructor agreement to the reduced empirical scope.

By week 4, require family-manifest audit and a pilot ablation. Drop optional diffusion or full PPA integration before sacrificing strong controls and clean test separation. A valid final negative result can establish that improvements vanish under matched compute, do not survive initializer shift, or do not transfer from HPWL to routing. It must include checked implementations, tuned baselines, adequate diagnostics, and precise claim limits.
