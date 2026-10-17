# MaskRegulate — refinement is already a published transfer setting

**Reviewed:** 17 October 2026. **Evidence status:** paper and official source inspected; no placement experiment executed.

## Bibliography and primary sources

Ke Xue, Ruo-Tong Chen, Xi Lin, Yunqi Shi, Shixiong Kai, Siyuan Xu, Chao Qian. *Reinforcement Learning Policy as Macro Regulator Rather than Macro Placer*. NeurIPS 2024, Advances in Neural Information Processing Systems **37**, pp. 140565–140588. The repository's example BibTeX incorrectly gives volume 38; the proceedings metadata gives 37.

- [Official proceedings record](https://papers.nips.cc/paper_files/paper/2024/hash/fe224a60b878e79d5b3d79d7f113f76b-Abstract-Conference.html)
- [Conference paper including appendices](https://proceedings.neurips.cc/paper_files/paper/2024/file/fe224a60b878e79d5b3d79d7f113f76b-Paper-Conference.pdf)
- [Author-deposited HTML](https://arxiv.org/html/2412.07167v1)
- [Official implementation](https://github.com/lamda-bbo/macro-regulator), inspected commit `fe475473c86121bd09e031b6329f18e2d8b9d5ce`.

## What the paper establishes

MaskRegulate moves one macro per decision using an existing layout, pixel masks, PPO and wirelength/regularity rewards. Its regularity proxy prefers peripheral locations. Main experiments use ICCAD 2015; ISPD 2005 appears in the appendix. Comparators include DREAMPlace, AutoDMP, WireMask-EA and MaskPlace. Global HPWL follows standard-cell placement; downstream results use Cadence Innovus. Five runs support proxy comparisons; a best-HPWL placement is selected for downstream evaluation. The paper changes the ICCAD placement area.

**Generalization is already tested:** train on `superblue1,3,4,5`; evaluate `superblue7,10,16,18`. Table 2 reports global HPWL and regularity, rather than a held-out routed-PPA table. All four favor MaskRegulate over MaskPlace. On `superblue7`, global HPWL is 7.99 versus 10.33, in units of 1e8. This is a published observation, not our result.

The formulation, RegularMask, normalization and reward-weight sensitivity already have ablations. Therefore “train a refiner and test unseen chips” reproduces an existing experiment. [Paper §§3–4; appendices A–B](https://arxiv.org/html/2412.07167v1).

## Implementation-level understanding

The following is a source audit of the specified commit, not a claim that the published experiments necessarily used every current default.

| Component | Actual implementation | Why it matters for this project |
|---|---|---|
| Episode | One ordered pass through selected modules | A pass can change the whole layout; “refinement” does not mean small displacement. |
| Action | Integer index in a 224 × 224 grid, decoded as `(action // grid, action % grid)` | 50,176 candidate sites; macro orientation is not part of this action. |
| Observation | Step index; old/new canvases; current/next regularity, position and wire masks; normalized macro dimensions | Dense spatial masks are already a strong hand-engineered circuit representation. |
| Feasibility | PositionMask excludes boundaries and already-adjusted modules | Unadjusted original locations remain available. Intermediate overlap can occur; do not describe this as preserving legality at every move. |
| Wire reward | Negative change encoded in the current macro's WireMask, using macro/port net coordinates | This is not the final routed wirelength or global standard-cell HPWL. |
| Regularity reward | Negative change of a size-aware peripheral-distance mask | “Regularity” is an engineering preference, not a universally valid congestion theorem. |
| Total reward | Legal-action penalty plus `wire_coeff * wire_reward + (1-wire_coeff) * regular_reward` | Default `wire_coeff=0.7`. The mixed reward is not directly power or timing. |
| Reward scaling | Min/max extrema are collected through training-design calibration trajectories | Extrapolated values are not explicitly clipped; the nominal interval need not hold on shifted designs. |
| Actor | Local mask CNN, global ResNet-based branch, merge; categorical actions; geometric and soft cost masks | A graph encoder extension must beat this substantial input engineering, not an empty baseline. |
| PPO | Discounted episode returns, critic-derived advantage, clipped probability ratio, Adam; deterministic argmax at evaluation | Do not assume generalized advantage estimation merely because PPO is used. |
| Standard-cell evaluation | At the end of evaluation episodes, DREAMPlace runs `n_dmp_eval` times and minimum HPWL is retained | Charge these calls to runtime, and match restart budgets across methods. |

Source links: [environment](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/src/place_env/place_env.py), [state parsing](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/utils/state_parsing.py), [actor](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/src/model/actor.py), [agent](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/src/agent.py), [default configuration](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/config/default.yaml).

### Mathematical interpretation for a student

Our interpretation: let `P_t` contain all current module locations and let `i_t` be the next module. The action substitutes its site, producing `P_(t+1)`. For a fixed netlist, changing that module lets us calculate the change in its incident net bounding boxes immediately. This is more informative than scoring an incomplete arrangement with unknown future locations. It still cannot determine routed timing precisely, because routing, buffering and standard-cell optimization have not happened.

The discounted learning target is approximately

```text
G_t = r_t + gamma*r_(t+1) + ...
advantage_t = G_t - V(state_t)
PPO objective = mean(min(ratio_t*advantage_t,
                         clip(ratio_t, 1-epsilon, 1+epsilon)*advantage_t))
```

For this implementation `gamma=0.95`; long-term choices therefore face both future packing consequences and discounting. A useful course question is whether the learned sequencing benefit beats a greedy controller supplied with exactly the same masks and budget. This is our proposed test, not a finding of the paper.

Our geometric observation: adding the nearest horizontal-boundary distance and nearest vertical-boundary distance favors **corners**. A macro halfway along the left boundary has zero horizontal distance but positive vertical distance. Therefore this particular regularity proxy is more specific than merely “put blocks anywhere near the perimeter.” Investigate whether its preference remains useful when I/O or routing channels occupy corners.

## Reproducibility audit and concrete fixes

1. **Checkpoint selection can use evaluation circuits.** `src/main.py` evaluates every `benchmark_eval` item periodically, saves each circuit's best model and saves an average-best model from those same scores. This is a capability of the code, not proof of misconduct in the paper. For our strict study, use only validation designs in this list during training; run frozen test evaluation separately. Never pick one checkpoint per test design. [Training/evaluation loop](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/src/main.py#L192).
2. **Seeds are initialized too late for full reproducibility.** The environment and `PPOAgent` are constructed before `seed_torch(args.seed)`. Move seeding before constructors and record DREAMPlace randomness too. [Main construction order](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/src/main.py#L101).
3. **The parser is ICCAD-specific.** Argument parsing filters benchmark names to strings containing `superblue`; `ProblemInstance` calls `read_superblue`. ISPD05 Bookshelf files cannot simply be substituted. [Parser](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/src/main.py#L38), [problem interface](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/src/problem_instance.py).
4. **Module definition must be disclosed.** The reader sorts circuit instances by size and takes the first `n_macro` (default 512) as the selected modules. This is not automatically the original hard-macro set of an arbitrary physical-design dataset. Preserve or explicitly replace this selection consistently across baselines. [Reader](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/utils/read_superblue.py#L217).
5. **Geometry is transformed.** `_compress_canvas()` calculates a smaller `place_grid` using cell area and `grid_soft_coeff`. Log original/effective bounds, utilization, units and coordinate mapping. [Canvas compression](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/src/problem_instance.py#L54).
6. **Current defaults differ from paper settings.** Current YAML requests 1,500 episodes; manuscript setup uses 1,000. Do not call unmodified defaults an exact reproduction. Resolve the actual intended config before reporting comparisons. [Configuration](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/config/default.yaml), [paper Appendix A](https://arxiv.org/html/2412.07167v1#A1).
7. **Use the implemented checkpoint spelling.** Current source expects `--check_point_path`; the README parameter table mentions `--checkpoint_path`. The example/test script uses the implemented form. Passing the table's form can miss checkpoint loading. [Loader condition](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/src/main.py#L119).
8. **Reward and reporting regularity differ in detail.** Training uses grid masks, while `compute_regularity()` reports an area-weighted distance to boundaries in transformed physical coordinates. Implement both separately and label them. [Reporting metric](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/utils/comp_res.py#L46).
9. **Dense rollout storage is expensive.** Our static memory calculation: each state contains `3 + 8*224*224 = 401,411` scalar entries. With NumPy float64 and a 5,120-step buffer, state arrays alone approach 15.3 GiB; tensor conversion creates additional storage. This is an estimate from the array shapes and defaults, not a measured peak. Profile a short run first; store compact masks or float32 if a controlled port is needed. Preserve precision consistently across compared methods. [State arrays](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/utils/state_parsing.py), [buffer construction](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/src/agent.py).

## Environment and access feasibility

The official README provides a Docker workflow, requires compiling bundled DREAMPlace, lists Python 3.8.5 and PyTorch 1.7.1, and links benchmark downloads. It supplies a policy trained on `superblue1,3,4,5`; testing it on `superblue1` is an in-training smoke test. Current code uses Linux `cp` shell calls. Native Windows/Python 3.14 should not be assumed compatible; use Linux/WSL2 or a remote Linux machine and a verified CUDA/toolchain combination. The code has a [BSD-3-Clause license](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/LICENSE); benchmark and bundled dependency terms must be tracked independently. [Official README](https://github.com/lamda-bbo/macro-regulator).

## Our critical assessment and defensible research gap

**Strong starting point:** the formulation directly targets the assigned topic, comes with code and includes a clear zero-shot reference experiment.

**Evidence boundary:** a four-design same-suite transfer table cannot establish universal out-of-distribution transfer. Different seeds on one netlist are not new circuits. A mask reward that improves an arrangement need not improve its downstream implementation, and neither HPWL nor peripheral distance is a power measurement.

**Suggested extension:** study whether normalized multi-initializer training and a validation-selected acceptance rule improve the probability of helpful transfer under changed initializers, utilization and circuit family. Add a greedy controller with identical masks. Publish all regression cases, initialization cost and rejected proposals. This can deliver a meaningful negative or positive result without promising a new universal placer.

**Mid-semester position:** present the exact MDP, this source audit, a frozen split, one functioning evaluation path if available, and proposed falsifiable hypotheses. Say “planned” until benchmark results have actually been produced.
