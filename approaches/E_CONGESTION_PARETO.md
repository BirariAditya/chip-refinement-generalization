# Selected direction E: congestion-aware, preference-conditioned placement refinement

Status: proposed research direction, selected from attachment points 4 and 5. No policy trained or placement result measured. This supersedes initialization robustness as the central contribution; initializer shifts remain an evaluation axis.

## 1. Project claim and novelty boundary

**Research question:** Can a single preference-conditioned RL regulator refine an existing placement into useful wirelength–regularity–congestion trade-offs on unseen circuit families, at a fixed total inference budget?

The proposed contribution combines a cheap explicit congestion reward with a preference-conditioned **refinement** policy, then tests its usefulness using strong matched-budget controls and downstream proxy validation. It does not claim to invent MORL, RUDY, preference conditioning, Pareto optimization, or their first application to chip placement.

Direct prior art is [Chang et al., Flexible Multiple-Objective Reinforcement Learning for Chip Placement (2022)](https://arxiv.org/abs/2204.06407), which already proposes one model with inference-time variable objective weights. [Yang, Sun and Narasimhan (NeurIPS 2019)](https://papers.neurips.cc/paper/9605-a-generalized-algorithm-for-multi-objective-reinforcement-learning-and-policy-adaptation.pdf) establishes a general preference-conditioned MORL setting with linear preferences. Our semester project is an application/extension and evaluation, not a new MORL algorithm. Related modern methods may already use congestion/timing; the final report must narrow novelty to the actual implemented comparison.

## 2. Three objectives and hard constraints

For a complete layout `s`, minimize `f(s) = (L(s), R(s), C(s))`:

- `L`: pin-level HPWL using declared nets/pin offsets/net weights. Record selected-module and post-standard-cell HPWL separately.
- `R`: the regulator's existing regularity measure, with the exact implementation/units frozen. The training-mask and physical reporting versions are not interchangeable. Retain both in logs and designate one explicitly for the controlled reward.
- `C`: a declared RUDY-based hotspot statistic over the same net/pin representation and fixed bin grid.

Full endpoint legality is a **hard acceptance constraint**, not a fourth preference objective. A sufficiently large wirelength reward must never make an overlapping final placement admissible. Preserve native OLD/NEW pass semantics for the reference: intermediate states may overlap not-yet-adjusted modules. Check complete-pass endpoints independently and return only the last checked feasible endpoint, with the shared feasible start as fallback at a budget interruption.

The native parser selects the largest `n_macro` instances by area (default 512), not necessarily all physical hard macros. Keep this selected-object task for reproduction and make a hard-macro-only variant explicit if added. Do not silently change canvas compression, fixed objects, standard-cell refresh cadence, regularity, or routing constraints while attributing improvement to the new reward.

## 3. Precise congestion estimator

RUDY distributes estimated wire demand over each net's pin bounding box; [Spindler and Johannes (DATE 2007)](https://portal.fis.tum.de/de/publications/fast-and-accurate-routing-demand-estimation-for-efficient-routabi/) is the original source. A practical **proposed variant**, specified rather than claimed identical to every RUDY implementation, is:

For net `n`, form pin box `B_n` of width `w_n` and height `h_n`. Handle zero or very narrow boxes by expanding symmetrically to at least `δ_x, δ_y` (e.g. fixed bin width/height), clipping/redistributing at die edges while preserving positive extent. Store that convention. Set `a_n` to a fixed net/pin-count weight (initially 1). For bin `b`,

`D_b^H = Σ_n a_n |B_n ∩ b| / (|b| h_n)` and

`D_b^V = Σ_n a_n |B_n ∩ b| / (|b| w_n)`.

Demand densities have units of wirelength/area. If routing-capacity densities `K_b^H,K_b^V` exist, define

`u_b = max(D_b^H/K_b^H, D_b^V/K_b^V)`.

If capacities are unavailable, report `d_b = max(D_b^H,D_b^V)` as **relative demand density**, normalized by the episode's common start statistic; do not call `d_b>1` physical overflow. Do not invent capacity values and then claim router congestion. Macro blockage corrections require actual layer-aware routing information and form an optional estimator refinement.

Let `q = max(1,ceil(0.10 * number_of_bins))`. Define `C(s)` as the mean of the largest `q` values of `u_b` (capacity-aware) or `d_b` (relative-density track). This top-tail statistic penalizes hotspots that mean demand can conceal. Freeze grid, tail fraction, high-fanout filtering, fixed-net inclusion, degenerate-box handling, and net weights on training/validation. Report mean, maximum, and top-tail statistics separately.

[DREAMPlace's official RUDY wrapper](https://github.com/limbo018/DREAMPlace/blob/master/dreamplace/ops/rudy/rudy.py) divides horizontal/vertical demand maps by bin area and directional capacities, then takes their maximum. Its [CPU kernel](https://github.com/limbo018/DREAMPlace/blob/master/dreamplace/ops/rudy/src/rudy.cpp) has net-degree weighting and a specific zero-size tolerance. If reusing this operator, preserve and document its exact convention rather than asserting equivalence to our minimum-box variant. Inspect the bundled regulator version; the current upstream operator is not proof it is already available in that environment.

**Efficient updates:** maintain per-net bounding boxes and per-bin contributions. A move changes only nets incident to the moved module, so subtract old affected-net maps and add new maps. Validate the incremental output against a full recomputation. Avoid materializing a full RUDY-delta map for every one of the 224×224 candidate positions initially: compute chosen-action reward first and supply the current congestion heatmap as optional observation. Reward-only versus heatmap additions are separate ablations. Standard-cell positions remain frozen during a pass and refresh on a fixed shared schedule; record the resulting proxy lag.

## 4. Normalization and vector reward

For common initial layout `s_0`, define

`F_j(s) = f_j(s) / max(f_j(s_0), ε_j)`, for `j ∈ {L,R,C}`.

All quantities are nonnegative costs. Choose physical-unit floors `ε_j` from training only, specify them, and reuse each start's denominators across all methods and preferences. An inference-time initial measurement is permissible context; fitting scales to final test trajectories is not. Log raw objectives as well as normalized ones, and do not clip objective values for Pareto evaluation. Near-zero initial regularity/congestion must not create unstable divisions. Do not min–max each method's candidate set: that can change comparisons and makes weights meaningless.

The original regulator already uses training-calibrated extrema; the proposal is a reference change, not the first use of normalization. Include native normalization as a control. A shared vector-reward definition for the controlled study is

`r_t_vec = F(s_t) - F(s_(t+1))`, `r_t(w)=wᵀ r_t_vec`.

For a fixed horizon and `γ=1`, this telescopes to `wᵀ(F(s_0)-F(s_T))`. This equivalence does not automatically hold with the native discount factor, reward clipping, early termination, or unaccounted repair. Preserve the native algorithm as the reference; label any changed reward/discounting as a controlled extension. Include final repair/fallback in the terminal objective. Terminal scalarized cost with properly specified shaping is an alternative if fixed undiscounted training is unstable; do not quietly switch objectives.

## 5. Preference-conditioned PPO

Sample `w=(w_L,w_R,w_C)` on the simplex, `w_j≥0`, `Σw_j=1`, once per episode. Keep it fixed throughout that episode. Start with `Dirichlet(1,1,1)` mixed with explicitly sampled simplex vertices and edges so extremes are not neglected. Tune mixture frequency on validation only.

Condition **both actor and critic** on `w`. A minimal modification tiles the three weights as constant image channels for mask fusion, or concatenates a small weight embedding into the policy/value features. Use a scalar conditioned critic `V(s,w)` first; a three-head vector critic is optional and should be ablated. This preserves the core architecture and avoids an unnecessary GNN rewrite. A policy that receives random preference labels but ignores them is a useful collapse control.

At inference, freeze all parameters and query a predeclared preference set. A tractable proposal is the 15 simplex lattice weights with denominator 4: `(i/4,j/4,k/4)` where `i+j+k=4`. Add six predeclared off-grid weights to test interpolation only if affordable; distinguish interpolation in preference space from transfer to unseen circuits. These counts are a plan, not measured throughput.

## 6. What the resulting Pareto set means

Layout `a` dominates `b` if all three costs are no worse and at least one is strictly better. Deduplicate objective vectors under a fixed numerical tolerance, remove infeasible candidates, and nondominated-filter the remaining set. Call it the **empirical nondominated set** or approximate front. It is not the true or complete Pareto front.

Positive weighted sums recover only supported efficient solutions in general; nonconvex/discrete fronts can contain unsupported Pareto points that no linear weight selects. Zero preference components can yield dominated ties unless nondominated filtering is applied. Neural optimization adds further approximation error. For a simple example, minimizing costs `(0,2),(1.1,1.1),(2,0)` makes the middle point nondominated but never strictly optimal for a nonnegative weighted sum. Thus changing weights does not guarantee complete front coverage.

An optional follow-up is augmented Chebyshev scalarization or epsilon-constraint search, after the linear baseline works. These do not guarantee coverage with a finite neural training budget either. Do not add a nonlinear scalarization directly to one-step rewards and assume it equals scalarization of the final return; specify an episode-level objective or an augmented state.

## 7. Timing: useful extension with honest labels

Timing is not part of the minimum three-objective front because it needs additional data and evaluation cost. If Liberty/SDC and a working STA interface are available, evaluate WNS/TNS and violated-endpoint counts on a prespecified subset. Compare at the same physical-flow stage.

A cheap **timing surrogate** can use `T_proxy(s)=Σ_n c_n^0 HPWL_n(s)`, where criticalities `c_n^0` come from the initial layout's timing analysis and remain fixed during an episode. Select a criticality mapping using training/validation only; do not infer criticality from fanout and call it timing. Frozen weights can become stale after large moves. Refreshing STA every `k` complete passes is an optional distinct configuration, with analysis time charged. [OpenROAD documents that placement-based parasitics do not accurately predict routed parasitics](https://openroad.readthedocs.io/en/latest/main/src/rsz/README.html).

To keep three objectives in a timing-capable variant, explicitly replace regularity with this surrogate: `(L,C,T_proxy)`, while reporting regularity diagnostically. A four-objective `(L,R,C,T)` study is beyond the minimum scope. Neither criticality-weighted HPWL nor better RUDY alone proves better timing or PPA.

## 8. Experimental comparisons and budgets

Mandatory comparisons:

1. No refinement and backbone continuation.
2. Native fixed-weight regulator.
3. Fixed-weight congestion-aware regulator: isolates the new reward from conditioning.
4. One preference-conditioned three-objective regulator.
5. A bank of independently trained fixed-weight three-objective regulators.
6. Multi-start SA/greedy scalarization sweep on the same objective definition; use an archive to nondominated-filter candidates.

Compare the policy bank in two explicitly labeled views: equal aggregate training resources (practical efficiency) and equal resources per specialist (quality ceiling, higher total training cost). The latter cannot be described as training-compute-matched. For final candidate generation, impose the same **total** budget `B` and maximum number of completed candidates `K` per circuit/start. Querying 15 weights for `B` each gives a 15B method; it must not compete against one baseline run of `B`. Report per-request single-preference latency and full-set generation cost separately. Count precomputation, proxy updates, legalizer, rejected candidates, and standard-cell refreshes.

Minimum ablations are: congestion weight zero versus nonzero; fixed versus conditioned preference; conditioning removed/shuffled; native versus start-referenced reward scaling; reward-only congestion versus added heatmap; and mean versus top-tail congestion aggregation. Run main comparisons before expanding this list. Hold initialization fixed for attribution, then test a smaller cross-initializer shift as an additional generalization analysis.

## 9. Metrics that avoid a misleading Pareto claim

Primary set-quality metric: minimization hypervolume `HV(A;r)=volume(∪_(z∈A,z≤r) [z_1,r_1]×[z_2,r_2]×[z_3,r_3])`. Use common normalized objective axes and a reference point frozen **before test outcomes**. One transparent default is `r=(1.25,1.25,1.25)` in start-referenced coordinates; choose/confirm on validation. Points outside the box contribute no hypervolume: retain them in tables, report their count, and do not enlarge `r` after test. Predeclare sensitivity references (e.g. 1.10 and 1.50) if useful. These numerical choices are protocol choices, not physical thresholds. [pymoo's official indicator documentation](https://pymoo.org/misc/indicators.html) supports direct minimization-oriented HV; MORL libraries may instead expect reward maximization, so check sign conventions.

Also report per-family component costs, feasibility rate, nondominated count, extremes, equal-budget hypervolume versus time, and held-out preference loss `mean_w wᵀF(s_w)`. Distinguish the **direct request loss** for the candidate generated under `w` from **set utility** `mean_w min_(s∈A) wᵀF(s)`. The latter is a legitimate descriptive set metric if all methods receive the same full vector evaluator and charged candidate budget; it is not permission to tune a policy on test.

The true Pareto front is unknown. Do not report IGD to a pooled set as distance to ground truth. If an empirical pooled reference is shown, label it explicitly and use it only for post-hoc descriptive analysis. Family-level paired comparisons and hierarchical uncertainty remain necessary; seeds/preferences are not new unseen circuits.

For routed validation, preselect circuit families and preference queries (e.g. three vertices plus center) using compatibility/runtime criteria. Route the same query budget for every method. Keep macro placement, standard-cell backend, CTS/router configuration, and technology fixed. Report proxy/routed ranking agreement and reversals. A proxy front is not a routed-PPA front.

## 10. Feasibility and failure contribution

Weeks 1–2: native reproduction interface, RUDY full/incremental check, feasible-endpoint contract, common fixed-weight congestion-aware baseline. Weeks 3–4: conditioned actor/critic and validation-only preference/normalization tuning. Weeks 5–6: specialist bank, SA controls, frozen held-out families and equal-budget candidate sets. Weeks 7–8: optional routing/timing subset, ablations, preference-collapse/proxy-gap analysis, report.

GPU access is confirmed, but its model, memory, and throughput remain unspecified; routing/STA compatibility needs verification. The minimum meaningful result is a checked congestion-aware refiner plus a controlled conditioned-versus-specialist/search comparison. Useful negative results include preference collapse, no benefit over a fixed-weight bank, proxy gaming, or routed congestion ranking reversals. The mid-sem deliverable is this formulation and experimental plan, not unperformed experiments.
