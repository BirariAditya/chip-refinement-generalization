# Congestion-aware, timing-aware, preference-conditioned macro regulation

Checked against primary sources on 17 October 2026. This review supports the selected direction: extend an RL macro **refiner**, optimize more than wirelength, and test transfer to unseen circuits. All methodology below is proposed work; no experimental result is claimed.

## Prior art that must appear in the presentation

### Chang et al. — Flexible Multiple-Objective Reinforcement Learning for Chip Placement

DAC 2022 / arXiv:2204.06407. MOPPO already conditions a placement policy and value function on an inference-time preference vector. Its objectives include HPWL, congestion, and anchor distance. The presented preference sweep mainly trades a **fixed wirelength-plus-congestion blend** against anchor distance. Congestion is obtained from global routing and summarized using top-percentage average congestion, ACE; it is not simply RUDY. Section 5.1 explicitly keeps a single canvas during training: its zero-shot demonstration concerns preferences and should not be cited as proof of held-out-circuit transfer. Superblue10 and Superblue18 are the main rectangular-macro examples. This establishes direct prior art for one-model/many-preferences placement. It does not establish that the proposed preference-conditioned refiner generalizes across unseen circuits or that a three-objective timing-aware regulator works. [Primary paper, Sections 4–5](https://arxiv.org/html/2204.06407v1).

**Novelty boundary:** varying weights or adding a preference vector is an established technique. A defensible contribution is its careful adaptation to **placement refinement**, combined with held-out-circuit experiments, independent congestion/timing objectives, and auditing whether proxy gains survive downstream evaluation. This is a proposed distinction, not a verified first-in-literature claim.

### Spindler and Johannes — RUDY

*Fast and Accurate Routing Demand Estimation for Efficient Routability-driven Placement*, DATE 2007. RUDY stands for Rectangular Uniform wire DensitY. It distributes a net's estimated wire demand over its pin bounding rectangle and is intended as an efficient estimate of routing demand. The original work integrates it into routability-driven placement. Cite it as a **routing-demand estimator**, not as an actual global/detailed-routing measurement or a proof of route feasibility. [Authors' institutional publication record](https://portal.fis.tum.de/en/publications/fast-and-accurate-routing-demand-estimation-for-efficient-routabi/), [IEEE paper identifier](https://ieeexplore.ieee.org/document/4211973).

OpenROAD's implementation obtains technology-dependent wire width/pitch information, accumulates net bounding-box contributions, and includes routing-resource reductions/blockage information. Consequently, a lightweight homemade rectangular heatmap without those details should be called a **RUDY-style demand proxy** unless validated as equivalent to a pinned implementation. [Primary implementation](https://github.com/The-OpenROAD-Project/OpenROAD/blob/master/src/grt/src/Rudy.cpp).

### Timing-aware analytical placement already exists

DREAMPlace 4.0 supports timing-driven placement using momentum-based net weighting and an integrated timing engine. Its DATE 2022 paper is *DREAMPlace 4.0: Timing-driven Global Placement with Momentum-based Net Weighting*, by Peiyu Liao, Siting Liu, Zhitang Chen, Wenlong Lv, Yibo Lin, and Bei Yu. Therefore, emphasizing critical nets is not by itself novel. It is an essential non-learning baseline or objective-construction reference. [Official repository, publications and features](https://github.com/limbo018/DREAMPlace).

OpenROAD's global placer documents both timing-driven and routability-driven modes. Its default routability path uses RUDY, whereas `-routability_use_grt` uses the more expensive routing-based estimate. It also exposes timing-net reweighting controls. These options provide credible baseline configurations, subject to availability in the pinned version actually used. [Official global-placement documentation](https://openroad.readthedocs.io/en/latest/main/src/gpl/README.html).

## Metric boundaries: what each number can establish

The following table is the proposed project's reporting contract, based on the distinctions in the cited tool documentation.

| Quantity | Fast training role | What to claim | What to avoid claiming |
|---|---|---|---|
| HPWL | Geometry-based wirelength objective | Lower bounding-box wirelength estimate | Lower routed wirelength, power, or delay without measurement |
| RUDY/RUDY-style map | Spatial demand feature and congestion reward | Lower estimated routing demand under a stated model | Routed overflow, DRC-free routing, or timing closure |
| Criticality-weighted HPWL | Timing-oriented surrogate | Shorter connections for designated critical nets | Measured WNS/TNS improvement |
| Placement-based STA | Periodic audit | Estimated WNS/TNS at the placement/parasitic stage | Post-route signoff timing |
| Global-route overflow | End-of-episode/subset audit | Routing demand versus capacity in the chosen router | Detailed-routing DRC closure |
| Post-global-route STA | Stronger timing audit | WNS/TNS using global-routing parasitics | Full signoff PPA |

OpenROAD exposes `global_route -congestion_report_file ...`; its router also supports routing layers, macro extensions, and resource-capacity adjustments. These settings affect congestion results and must be fixed between methods. Global routing can be permitted to retain congestion, so a successfully emitted route file does not automatically imply zero overflow. [Official global-routing documentation](https://openroad.readthedocs.io/en/latest/main/src/grt/README.html).

OpenSTA uses Liberty timing models, linked netlists, timing constraints such as SDC, and parasitics such as SPEF; without parasitics, its delay calculation does not model routing wires in the same way. [Official OpenSTA examples](https://github.com/The-OpenROAD-Project/OpenSTA/blob/master/doc/Examples.md). OpenROAD distinguishes `estimate_parasitics -placement` from `estimate_parasitics -global_routing`, the latter requiring global routing first. [Parasitic-estimation documentation](https://openroad.readthedocs.io/en/latest/main/src/est/README.html).

**Project decision:** only use the phrase *timing-aware* for an explicitly stated timing surrogate or actual timing feedback. A degree-based net weight alone is a connectivity heuristic. If real timing inputs are absent, label generated criticalities synthetic and treat timing as a later extension. Do not silently fabricate timing-critical net labels for a benchmark.

## Proposed formulation and scope

This section is original project design, not a source's claimed result.

Let a legal placement be P, circuit metadata be G, and preference vector lambda = (lambda_W, lambda_C, lambda_T), with nonnegative entries summing to one. Define minimized objective vector f(P) = (W(P), C(P), T_proxy(P)). The policy pi(a | P,G,lambda) selects a macro refinement move; it does not construct a whole placement from an empty canvas.

Keep feasibility separate: fixed macros and ports remain fixed; legal moves respect canvas, overlap, halos, and any supported region constraints. Do not let a preference setting buy shorter wirelength by accepting illegal overlap. Specify whether the action directly moves a macro or modifies the original regulator's displacement instruction; implementation must match the starting method rather than describe a different MDP accidentally.

Start with **two objectives**, HPWL and congestion. Add timing only after timing data and a reproducible audit flow exist. For each objective use a fixed positive normalization scale determined from training data or a predeclared initial-placement rule; do not tune scales using held-out outcome distributions. Pass lambda to the actor and critic. Sample lambda per episode and keep it fixed throughout that episode initially.

A dense improvement reward can be lambda dot [normalized f(P_t) - normalized f(P_(t+1))]. With undiscounted finite-horizon return this telescopes to the initial-minus-final scalar objective. With a discount factor below one, it need not optimize exactly the same terminal objective. If policy invariance is claimed, use a correctly specified potential-shaping argument instead of asserting that any delta reward preserves the optimum.

Features can include the current congestion heatmap, nearby macro/pin occupancy, normalized pin connectivity, displacement from the initializer, and available timing criticality. Compare features separately from rewards. A richer reward with no local congestion observation may be hard to learn; a richer observation can help even when the objective stays unchanged. Ablate both.

To keep runtime feasible, compute fast proxies after each move and route only at episode endpoints or on a predeclared subset. Report the amortized cost of proxy computation and audit calls separately. A fixed audit schedule across methods prevents extra routing feedback from becoming an undeclared algorithm advantage.

## Pareto claims: the precise limitation

Das and Dennis show why weighted sums can fail to recover nonconvex parts of a Pareto set and why uniform weights need not produce uniform frontier coverage. [Primary publisher record](https://link.springer.com/article/10.1007/BF01197559).

For this project, sweeping positive linear weights is a practical baseline, not a guarantee of recovering the entire frontier. Example with two minimized objectives: feasible points A=(0,2), B=(1,1.1), C=(2,0). B is nondominated, but a positive weighted sum never prefers B to both A and C. Thus even perfect scalar optimization can miss a valid trade-off point; imperfect RL adds further gaps.

Call the output an **empirical nondominated set**. Filter candidates by feasibility, then remove solutions dominated in the same raw metric space. Plot all evaluated candidates as well as the retained set. A proxy-space frontier and a routing/timing-audited frontier are separate objects; report how many preferred proxy solutions become dominated or infeasible downstream.

Measure hypervolume with one predeclared reference point and objective scaling shared by every method, separately for each circuit. Report per-circuit values before aggregating improvements. Invalid outputs contribute no feasible point. Raw hypervolume values across circuits with different scales are not directly comparable. Include seed variability and the number of unique feasible nondominated points; the latter alone is not a quality measure.

If a stronger frontier approximation becomes necessary, evaluate an epsilon-constraint search (for example, minimize W subject to a congestion budget) against the weighted-sum baseline. This is an optional extension with explicit computational cost, not an automatic novelty claim.

## Evaluation needed to support the contribution

1. Use circuit-level train/validation/test splits. All initial placements, perturbations, preferences, and seeds derived from one circuit remain in that circuit's split.
2. Test both unseen circuits and preference interpolation. These are distinct forms of transfer. Disclose that validating on an unseen weight of a known circuit does not establish circuit generalization.
3. Compare no refinement, wirelength-only regulator, fixed-weight congestion-aware regulator, preference-conditioned regulator, and matched-budget non-learning local search. Where feasible, include timing/routability-driven analytical settings.
4. Compare one conditional model with a bank of fixed-weight specialist policies. State both total training compute and inference compute; shared inference weights do not make training free.
5. Ablate congestion observation, congestion reward, preference conditioning, normalization, and timing proxy. Maintain the same initialization, action horizon, legalizer, and circuit representation.
6. Audit candidate preferences chosen without looking at test outcomes. Include fast-versus-routed congestion rank correlation, proxy-versus-STA timing rank correlation, and cases where the ranking reverses.

**Presentation-ready contribution statement:** “We propose to study whether a preference-conditioned RL macro regulator can transfer wirelength–congestion trade-offs across unseen circuits, and whether its proxy improvements survive routing-based evaluation. Timing is added when genuine timing inputs and a validated STA flow are available.”

This phrasing is honest about existing MORL placement work, the selected refinement scope, and the difference between proposed work and completed experiments.

## Concise bibliography metadata for inline LaTeX

Use these keys with `\bibitem{key}` / `\cite{key}`. URL entries are sufficient when an exact DOI has not been verified; do not invent missing volume/page metadata.

| Key | Verified metadata and primary URL |
|---|---|
| `chang2022moppo` | F.-C. Chang et al., “Flexible Multiple-Objective Reinforcement Learning for Chip Placement,” DAC 2022; arXiv:2204.06407. https://arxiv.org/abs/2204.06407 |
| `spindler2007rudy` | P. Spindler and F. M. Johannes, “Fast and Accurate Routing Demand Estimation for Efficient Routability-driven Placement,” DATE 2007, pp. 1–6. IEEE document 4211973. https://ieeexplore.ieee.org/document/4211973 |
| `liao2022dreamplace4` | P. Liao, S. Liu, Z. Chen, W. Lv, Y. Lin, and B. Yu, “DREAMPlace 4.0: Timing-driven Global Placement with Momentum-based Net Weighting,” DATE 2022. Official publication list: https://github.com/limbo018/DREAMPlace |
| `das1997weightedsum` | I. Das and J. E. Dennis, “A closer look at drawbacks of minimizing weighted sums of objectives for Pareto set generation in multicriteria optimization problems,” Structural Optimization, vol. 14, pp. 63–69, 1997. DOI:10.1007/BF01197559. https://doi.org/10.1007/BF01197559 |
| `openroadgpl` | The OpenROAD Authors, “Global Placement,” software documentation, accessed 17 Oct. 2026. https://openroad.readthedocs.io/en/latest/main/src/gpl/README.html |
| `openroadgrt` | The OpenROAD Authors, “Global Routing,” software documentation, accessed 17 Oct. 2026. https://openroad.readthedocs.io/en/latest/main/src/grt/README.html |
| `openroadest` | The OpenROAD Authors, “Parasitics estimation,” software documentation, accessed 17 Oct. 2026. https://openroad.readthedocs.io/en/latest/main/src/est/README.html |
| `openstaexamples` | The OpenSTA Authors, “Examples,” official software documentation, accessed 17 Oct. 2026. https://github.com/The-OpenROAD-Project/OpenSTA/blob/master/doc/Examples.md |
