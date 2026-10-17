# Experimental protocol: congestion-aware preference-conditioned RL refinement

Status: **proposed study; no real-circuit training, placement, routing, or performance result is claimed.** This version follows the user's selected attachment points 4 and 5. It replaces initialization robustness as the main research direction; initializer shift remains an optional evaluation axis. Mid-sem deliverable: researched proposal. Project execution horizon: approximately eight weeks; GPU access is confirmed but hardware/throughput remain unspecified, and timing/router access needs verification.

Full mathematical specification and primary-source discussion: [Approach E](../approaches/E_CONGESTION_PARETO.md).

## 1. Question, contribution, and hypotheses

**Can a preference-conditioned RL regulator generate useful wirelength–regularity–congestion trade-offs on unseen circuit families under a fixed total online budget?**

The proposed contribution is the integration of explicit cheap congestion feedback into refinement, a controllable inference-time preference interface, and rigorous comparison against specialist policies and classical search. [Chang et al. (2022)](https://arxiv.org/abs/2204.06407) already studies flexible multiple-objective chip-placement RL; preference conditioning or Pareto chip placement alone is not new.

- **H1 — reward value:** an explicit hotspot-congestion reward improves the measured HPWL/congestion trade-off relative to the native HPWL/regularity reward.
- **H2 — conditional control:** one conditioned policy offers useful trade-off control, with set quality competitive with fixed-weight specialists under declared total training/online budgets.
- **H3 — practical value:** any benefit survives strong equal-budget SA/greedy and backbone-continuation controls.
- **H4 — proxy validity:** proxy-congestion improvements agree with downstream routed behavior on a prespecified compatible subset. Reversals are a result to analyze, not discard.

Keep H1–H4 separate. Better proxy hypervolume does not establish lower power, better timing, or a complete Pareto front. A well-diagnosed failure of conditioning or proxy validity can still constitute a meaningful course contribution.

## 2. Dataset manifest and leakage-free splits

Before training, record source URLs/revisions/hashes; parent RTL/design lineage and family ID; technology; original/effective floorplan and canvas transforms; object-selection rules; fixed/movable IDs; cell/net/pin counts; units; timing/library/route-data availability; parser and legalizer status.

Split by parent family. Remappings, sub-blocks/variants with common ancestry, augmented layouts, altered floorplans, and initializer seeds inherit the same split. For ChiPBench, conservatively group all Ariane variants, all BlackParrot blocks/variants, and all SweRV variants; audit ancestry elsewhere. Different filenames are not independence. [Official ChiPBench cases](https://github.com/MIRALab-USTC/ChiPBench#dataset) contain such related designs.

Target approximately 6/2/4 independent train/validation/test families only if provenance and compatibility support those counts. Never manufacture the target by splitting siblings. If fewer independent cases exist, predeclare a smaller split or nested family-level cross-validation and narrow uncertainty claims.

Fit any reward floors/scalers, congestion estimator settings, learned preprocessing, and curriculum on training families. Use validation families for checkpoint, hyperparameter, preference-distribution, and stopping selection. Freeze these before final test. The upstream regulator's periodic `benchmark_eval` list must contain validation only while training; never choose a best checkpoint per test design.

Audit pretrained checkpoint provenance. A released policy trained on `superblue1,3,4,5` is not zero-shot on those designs. Timing criticalities measured from a test design's initial layout are available inference-time features only if the complete procedure is frozen and its cost is charged; outcome-driven criticality/reward tuning is prohibited.

## 3. Physical task and feasible endpoint contract

Freeze selected instance IDs, fixed objects/IOs, pin offsets, macro sizes, permitted orientations, halos/blockages, grid, canvas compression, density target, standard-cell backend, and refresh cadence across controlled methods. Check format equivalence rather than mixing ISPD2005, I/O-freed, and MMS variants by name. [DREAMPlace distinguishes these cases](https://github.com/limbo018/DREAMPlace#reference-results-for-macro-placement).

The audited native parser selects the largest `n_macro` instances by area, default 512; these are selected modules, not automatically the physical hard-macro set. Preserve this task for the reproduction reference. A hard-macro-only task is a separately labeled variant, consistently applied to all methods. The [native reader](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/utils/read_superblue.py) is the implementation source.

The native OLD/NEW mask prevents overlap with adjusted modules but may permit temporary overlap with not-yet-adjusted modules. Preserve native pass-wise semantics for reproduction; do not describe every intermediate as fully legal. Independently check complete-pass endpoints against all declared physical constraints. Report legalization repair cost, displacement, and objective change if repair is necessary.

Begin with a checked feasible full placement. Store its artifact, then each complete-pass endpoint that passes checks. At a hard time/objective-call limit, return the **last checked feasible complete-pass endpoint**, or the common feasible start if no pass qualifies. Do not finish an incomplete pass for free, route a partial pass, or score an illegal intermediate as the final candidate. Include checks/repair and unfinished work in the budget. Reserve a checking allowance, or retain the previous incumbent if insufficient time remains.

An always-legal RL mask changes reachable states and is a separate optional ablation. If classical methods cannot share native pass transitions, label them practical feasible-output controls rather than a pure action-selection ablation. Final feasible outputs, task definition, and total resources must still match.

## 4. Objectives, normalization, and policy

Minimum objective vector is `f(s)=(L,R,C)`, all minimized:

- `L`: declared pin-level HPWL, with exact nets/weights and physical units.
- `R`: frozen native regularity definition; retain distinct mask-based training and physical reporting metrics in logs.
- `C`: mean of the highest 10% bin RUDY values, with fixed bin grid, weights, high-fanout filter, and degenerate-box rule.

Use actual directional capacity normalization only when physical routing capacities exist; otherwise label the estimator relative demand density and do not call a value above 1 actual overflow. [DREAMPlace's RUDY implementation](https://github.com/limbo018/DREAMPlace/blob/master/dreamplace/ops/rudy/rudy.py) and [kernel](https://github.com/limbo018/DREAMPlace/blob/master/dreamplace/ops/rudy/src/rudy.cpp) provide an implementation reference, not proof the regulator's bundled version supports the same operator. Validate incremental affected-net updates against full recomputation before timing.

Normalize costs with the shared start: `F_j(s)=f_j(s)/max(f_j(s_0),ε_j)`. Choose positive floors from training only; use the same denominators for every method/preference on that start. Log raw values and floor-trigger rate. Do not fit scales to each method's candidate set or test outcomes. Native train-extrema normalization already exists and is a control, not a new discovery.

Sample `w∈Δ²` once per episode and condition both actor and critic. Begin with a Dirichlet simplex distribution plus explicit vertex/edge sampling. A tiled three-channel preference input or small embedding is sufficient; no GNN rewrite is required. Use a scalar `V(s,w)` first. A vector critic is optional.

For the controlled reward extension, `r_t(w)=wᵀ(F(s_t)-F(s_(t+1)))`. Telescoping equivalence to final scalarized cost requires undiscounted fixed-horizon episodes and consistent terminal repair/fallback accounting. Preserve the native discount/reward setup in the reproduction row; document any changed discounting, clipping, or terminal objective. Do not claim equivalence under arbitrary PPO settings.

## 5. Main experiment and ablations

| Method | Purpose |
|---|---|
| No refinement; backbone continuation | Starting quality and extra optimization controls |
| Native fixed-weight regulator | Faithful published-system reference |
| Fixed-weight congestion-aware regulator | Isolate explicit congestion feedback |
| Preference-conditioned three-objective regulator | Proposed controllable refiner |
| Bank of independent fixed-weight three-objective regulators | Specialist quality/compute control |
| Multi-start SA/greedy preference sweep and archive | Strong non-neural set-generation control |

All controlled objective comparisons use identical start artifacts, cost definitions, accepted endpoint rules, standard-cell updates, and downstream flow. Native reward differences remain explicit in the reproduction row.

Prioritize these ablations: congestion weight zero/nonzero; fixed/conditioned preferences; actor/critic conditioning removed or shuffled; native/start-referenced reward scale; congestion reward-only versus added heatmap observation; mean versus top-tail statistic. Run principal comparisons before expanding the ablation matrix. A small train-style versus held-out-initializer test is secondary; mixed-start training and normalization factorials from the previous proposal are no longer the central four-way study.

## 6. Candidate and compute budgets

Predeclare a 15-weight simplex lattice with denominator 4, or a smaller validation-selected grid if profiling requires it. An optional six off-grid queries assess preference interpolation. Freeze all queries before test.

Per circuit/start, allocate total budget `B` and a common maximum `K` completed candidates. Every method must generate its candidate **set** within that same total cost. Fifteen queries each receiving `B` cost 15B and cannot compete against one B-budget baseline. Report singleton preference-request latency and whole-set cost separately. Multi-start classical baselines receive the same opportunity to return an archive.

Use two complementary views: equal wall time with equal worker/GPU limits, and equal objective-call count with wall time reported. Count preprocessing, inference, congestion updates, masks, standard-cell work, repair/checks, archive selection, failed candidates, and partial passes. Show feasible-endpoint hypervolume and best scalarized cost versus time.

Report all offline training/tuning resources. For specialists, show equal aggregate training resources as the primary practical comparison; equal resources per specialist is a labeled higher-total-compute quality ceiling. Target three training seeds if affordable; use the pilot to freeze a feasible plan. Resource requirements remain unmeasured.

## 7. Pareto evaluation without test-driven selection

Filter final feasible candidate objective vectors for nondominance using a fixed numerical tolerance. Label the output empirical nondominated set; the true Pareto front is unknown. Linear weighted sums may miss unsupported nondominated points of a nonconvex/discrete feasible set. Neither conditioning nor many weights guarantees full coverage.

Primary set metric: minimization hypervolume of normalized costs relative to one fixed worse reference `r`. Proposed transparent reference is `(1.25,1.25,1.25)`, confirmed/frozen on validation; optional sensitivity references 1.10 and 1.50 must also be prespecified. Points outside the dominated reference box contribute no HV; retain/report them and never enlarge the box after seeing test results. Do not clip objective vectors or use per-method axes. [pymoo indicator documentation](https://pymoo.org/misc/indicators.html) uses minimization; check sign conventions if a reward-maximization MORL wrapper is used.

Also report raw component costs, feasible-run rate, unique nondominated count, extreme objective values, per-request held-out-preference cost, and expected best set cost over fixed evaluation weights. Distinguish direct output `wᵀF(s_w)` from set cost `min_(s∈A) wᵀF(s)`; the latter is a descriptive evaluation using a shared charged evaluator, not permission to retune the policy. Do not present IGD to a pooled empirical front as ground-truth Pareto distance.

The generalization unit is independent family, not preference query, training seed, or rollout. Average paired start/seed comparisons within design, then family; report per-family results and equal-family aggregate. Use family-outer hierarchical bootstrap only with sample-size limitations stated. Include preference-collapse evidence, repeated objective vectors, estimator floor events, failures, no-pass-within-budget frequency, and worst-family degradation.

## 8. Downstream congestion/timing validation

Preselect compatible circuit families and queries such as three simplex vertices plus the center before test results. Route the same number of candidates per method under fixed technology, standard-cell placement, CTS/router, and macro-fixed settings. No choosing each method's best-routed candidate without equal charged access.

Measure global-route wirelength and total/max overflow; optional detailed-route completion/DRCs and extracted WNS/TNS. Compare paired proxy versus routed rankings and show reversals. A RUDY front is not a routed-PPA front. Without capacities, libraries, and timing constraints, keep claims at relative congestion/HPWL.

Timing-aware reward is optional: use a criticality-weighted HPWL surrogate from real initial STA weights, or periodic STA at complete passes with charged runtime. Fixed criticalities may become stale; fanout alone is not timing. To retain three objectives, a timing-capable variant explicitly replaces `R` with `T_proxy`; otherwise it is a separate four-objective study. [OpenROAD warns about placement-versus-routed parasitic accuracy](https://openroad.readthedocs.io/en/latest/main/src/rsz/README.html). Report actual timing only at a stated common flow stage. Power needs library/corner/activity assumptions; fixed core dimensions do not establish smaller chip area.

## 9. Eight-week delivery gates

| Weeks | Deliverable and gate |
|---|---|
| 1–2 | Native smoke pipeline; source/split manifest; full/incremental RUDY agreement; checked endpoints and interruption fallback; fixed-weight congestion baseline; measured throughput |
| 3–4 | Condition actor/critic; validation tuning; freeze objectives/scales/query set/reference/budgets/checkpoint rule |
| 5–6 | Training seeds, specialist/search controls, frozen held-out proxy experiment and equal-budget sets |
| 7–8 | Prespecified routing/timing subset if compatible; ablations, failure analysis, reproducibility pass, report and presentation |

If RUDY reward updates or native infrastructure are too costly, retain a smaller checked fixed-weight-plus-conditioned study rather than promise unrun full PPA. Drop optional diffusion, GNN rewriting, four-objective timing, and initializer factorials first. A negative finding needs tuned controls, implementation checks, honest failures, and a precise conclusion such as preference collapse, no gain over specialists, or proxy/routing disagreement.

For today's mid-sem, present the refined question, prior-art boundary, objective/reward equations, policy input change, budget/family split rules, and this schedule. Clearly label all expected outcomes and illustrative diagrams; do not present paper-reported results as ours.
