# Core literature and formulation review for the mid-semester report

Reviewed 17 October 2026. This is an internal writing aid, not an experimental-results claim. Existing proposal, foundations and approaches A/D were inspected. No files outside this note and the companion bibliography were changed.

## Concise literature comparison suitable for a report table

| Work | Relevant idea | Role in our study | Boundary to state |
|---|---|---|---|
| MaskPlace, NeurIPS 2022 | Constructive pixel-mask RL with dense rewards | Architectural/history baseline | Dense rewards are already established. |
| ChiPFormer, ICML 2023 | Offline decision-transformer transfer and adaptation | Clarifies training-data and adaptation budgets | Target-circuit fine-tuning is not frozen-policy transfer. |
| IncreMacro, ISPD 2024 | Analytical refinement, peripheral guidance and relation-preserving legalization | Non-RL refinement comparator | Refinement and peripheral bias are not new. |
| MaskRegulate, NeurIPS 2024 | PPO refinement of complete initial layouts | Main proposed real-circuit baseline | It already evaluates unseen superblue designs. |
| PPO, 2017 | Clipped policy-ratio update objective | Theory behind the intended baseline | Our initial prototype uses REINFORCE instead. |

Primary metadata: [MaskPlace](https://proceedings.neurips.cc/paper_files/paper/2022/hash/97c8a8eb0e5231d107d0da51b79e09cb-Abstract-Conference.html), [ChiPFormer](https://proceedings.mlr.press/v202/lai23c.html), [IncreMacro](https://www.cse.cuhk.edu.hk/~byu/papers/C205-ISPD2024-IncreMacro.pdf), [MaskRegulate](https://papers.nips.cc/paper_files/paper/2024/hash/fe224a60b878e79d5b3d79d7f113f76b-Abstract-Conference.html), [PPO](https://arxiv.org/abs/1707.06347).

Suggested synthesis in our own words: the project should test when a learned controller adds value to a strong existing placement. The distinguishing experiment is joint circuit/initializer shift with a frozen model, matched classical controls and transparent runtime. The proposed contribution is a controlled robustness extension and analysis; neither an entirely new placement paradigm nor a completed empirical success is claimed.

Include ChipDiffusion in the main table using the other research agent's checked entry. Mention EXPlace/FlowPlace briefly in the novelty paragraph if the report presents current prior art; this core bibliography deliberately covers the five requested foundations plus REINFORCE.

## Citation keys and metadata checks

- `xue2024maskregulate`: official NeurIPS BibTeX confirms **volume 37**, pp. 140565–140588 and DOI 10.52202/079017-4462. Do not copy volume 38 from the upstream README.
- `lai2022maskplace`: official NeurIPS BibTeX confirms volume 35, pp. 24019–24030 and DOI 10.52202/068431-1744.
- `lai2023chipformer`: PMLR's own entry confirms volume 202, pp. 18346–18364. No DOI was invented.
- `pu2024incremacro`: author-hosted paper front matter confirms authors, ISPD 2024 and DOI 10.1145/3626184.3633321; paper page span is 169–176.
- `schulman2017ppo`: arXiv confirms all five authors, including **Prafulla** Dhariwal, title and 2017. Cite as a preprint, not as a NeurIPS conference paper.
- `williams1992reinforce`: optional entry for the prototype; [publisher record](https://doi.org/10.1007/BF00992696) confirms Ronald J. Williams, Machine Learning 8, pp. 229–256 (1992).

Use BibTeX `and` between authors. Protect mixed-capital method names with braces. The entries omit abstracts and unverifiable fields.

## Mathematical and conceptual checks for the report

### 1. State the problem at the correct level

The work chooses physical positions of existing macros. It does not redesign logical functionality, synthesize a new circuit, or optimize macro internal geometry. Full placement includes standard cells; our educational synthetic problem contains only rectangular macros and explicitly declared terminals/nets.

Let `G=(V,E)` be a hypergraph, `P={(x_i,y_i)}` a placement of fixed rectangles, and `p_ik=(x_i+dx_ik,y_i+dy_ik)` the coordinate of a pin. Define weighted HPWL over pins:

```text
H(P) = sum_e w_e [max_(p in e) p_x - min_(p in e) p_x
                 + max_(p in e) p_y - min_(p in e) p_y].
```

If the toy code uses block centers instead of pin offsets, call that an explicit simplification. Weighted pairwise Manhattan distance equals HPWL for a two-terminal net; it is not automatically equivalent for multi-terminal nets.

### 2. HPWL is nonsmooth but convex in unrestricted coordinates

Do not write “HPWL is nonconvex” without qualifying the full constrained problem. Each coordinate range is `max(x)+max(-x)`, which is convex; sums with nonnegative net weights remain convex when pin coordinates are affine in macro translations. Non-overlap constraints make the feasible set nonconvex/discrete. A nonsmooth objective and a nonconvex placement problem are different statements. Some source prose blurs this distinction; use the correct mathematical statement.

### 3. Dense improvement rewards telescope only under declared conditions

For a fixed scalar cost and finite horizon, `r_t=J(P_t)-J(P_(t+1))` gives `sum_t r_t=J(P_0)-J(P_T)` when `gamma=1`. With `gamma<1`, clipping, step penalties or changing normalization, that identity no longer holds. Per-episode scales fixed at P0 are acceptable for this identity; scales recomputed at every step are not the same cost function. Avoid describing a new normalized reward as the upstream exact reward.

### 4. Regularity is a proxy, and its sign matters

Lower peripheral-distance cost is better; “higher regularity score” can invert the intended convention. A sum of nearest horizontal and vertical boundary distances favors corners, not every boundary point equally. It does not measure routed congestion or prove that a peripheral layout has better timing. Fixed-size macros on a fixed die also cannot demonstrate area reduction merely by moving.

### 5. The full environment may be Markov; compact features need not be

A complete state can contain graph, geometry, placement, current macro, pass/order phase and remaining horizon. A vector of candidate cost changes or local neighborhoods can omit information needed for future decisions. Describe it as the policy observation/feature representation; do not claim a proof that it is a sufficient Markov state. Synthetic generalization across random graphs is not evidence of transfer between industrial circuit families.

### 6. Explain masking and empty-action behavior

For legal action set `A(s)`, define masked probabilities by normalizing `exp(logit)` only over that set. The denominator requires a nonempty set. In an always-legal local synthetic environment, include the current position as a no-op and check it is feasible. In original MaskRegulate's passwise OLD/NEW interface, the old position may already be occupied by an adjusted macro; a no-op is not automatically valid. Distinguish these environments explicitly.

### 7. Explain REINFORCE without calling it PPO

A modest masked linear/MLP policy with Monte Carlo returns is a useful initial implementation. Its score-function update can be written as

```text
gradient estimate = sum_t (G_t - b_t) * grad_theta log pi_theta(a_t | o_t),
G_t = sum_(k=t)^(T-1) gamma^(k-t) r_k.
```

The baseline `b_t` should be independent of the sampled current action conditional on the observation; a prior moving-average baseline is simple. For a return objective that explicitly discounts from episode start, give the corresponding `gamma^t` weighting or use `gamma=1` in the prototype so the presentation matches the update. Batch/trajectory centering is a practical variance heuristic and should not be presented as a proof of an unbiased estimator. Detach returns/baseline from the policy gradient where applicable.

PPO adds a ratio between current and behavior-policy probabilities and a clipped surrogate, usually with a critic. It is not implemented simply because a policy-gradient loss is used. Its clipping is an optimization heuristic, not a guarantee of monotonic placement improvement, physical legality or OOD generalization. [Original PPO](https://arxiv.org/abs/1707.06347).

### 8. Bound what acceptance guarantees

Selecting the lower exact scalar proxy cost between a legal proposal and P0 can ensure no worsening of that particular measured scalar, within numerical tolerance. It cannot guarantee non-worsening of every component, routed timing or power. Report raw proposal regressions before rollback as well as final incumbent performance, and offer the same selection privilege to baselines.

### 9. Keep evidence levels separate

In the report, label each result as one of: published result; source-code observation; synthetic pilot measurement; proposed real-circuit experiment. Only include pilot numbers with their actual configuration, random seeds, evaluation graph count, holdout mechanism and generated artifact. Report hardware actually used, not planned GPU hardware. A multi-agent research process is not itself a technical algorithmic contribution.

## Recommended report emphasis

Allocate the largest sections to background/MDP understanding, comparison of prior work, precise hypotheses, and an auditable initial prototype. Include an honest implementation-status table. A compact future-work table can cover real benchmark integration, upstream PPO reproduction, 2×2 scaling/mixed-start ablations, matched-mask greedy/annealing controls and optional diffusion comparison. Keep proposed real-circuit gains and all PPA metrics blank or marked not evaluated until measured.
