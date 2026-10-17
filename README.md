# Congestion-aware preference-conditioned RL placement refinement

**Selected project (attachment points 4 and 5):** Congestion-Aware Preference-Conditioned RL for Placement Refinement.

**Question:** Can one preference-conditioned regulator refine existing placements into useful HPWL–regularity–congestion trade-offs on unseen circuit families, compared with specialist policies and search under the same total candidate-generation budget?

This repository contains a researched mid-semester proposal, individual literature reviews, five separately documented project approaches, an experimental protocol, and initial executable experiments. Completed work includes the original toy REINFORCE pilot, 48 new toy preference-sweep control runs, and local execution checks of the released MaskRegulate checkpoint. [Native reproduction records](reproduction/README.md) distinguish actual original-code component execution from the full DREAMPlace/routing pipeline. No real-circuit training or routed PPA improvement is claimed. No slide deck has been created. Research checked 17 October 2026.

Start with [selected Approach E](approaches/E_CONGESTION_PARETO.md). The earlier initialization-robustness project is retained as **archived alternative A**, with initializer shift available as a secondary test. Timing-aware reward is an optional data-dependent extension; the core three objectives are HPWL, existing regularity, and a specified RUDY congestion proxy. [Chang et al. (2022)](https://arxiv.org/abs/2204.06407) already studies flexible MORL chip placement, so the contribution is a controlled congestion-aware refinement extension and evaluation, not the first use of preference conditioning.

## Start here

**Current revised report:** [LaTeX source edited in place](report/report_standalone.tex) · [Report status/build notes](report/README.md). The [existing PDF](report/output/Midsem_RL_Chip_Placement_Report.pdf) is an **earlier export** and does not reflect the current selected-direction revision; no separate updated PDF export was requested. The repository also includes a [measured synthetic REINFORCE prototype](prototype/README.md) with four held-out toy netlists. It is an initial toy implementation, not a real-circuit or PPO reproduction and not evidence for the proposed three-objective conditioned policy.

1. [Thorough research analysis and direction comparison](RESEARCH_ANALYSIS.md)
2. [Project recommendation and research gap](PROJECT_PROPOSAL.md)
3. [Topic explained from first principles](foundations/TOPIC_EXPLAINED.md)
4. [Mid-semester research discussion notes](presentation/RESEARCH_DISCUSSION.md)
5. [Six-hour preparation plan](presentation/SIX_HOUR_PLAN.md)
6. [Questions and defensible answers](presentation/VIVA_QA.md)
7. [Literature index and evidence map](literature/README.md)
8. [Evaluation protocol](methodology/experimental_protocol.md) and [toolchain feasibility](methodology/toolchain_feasibility.md)

## Approaches

| Direction | Contribution to test | Role |
|---|---|---|
| [E: congestion-aware Pareto refinement](approaches/E_CONGESTION_PARETO.md) | Explicit RUDY hotspot reward and a preference-conditioned regulator, compared with specialists/search and validated against routing where feasible | **Selected main project** |
| [A: robust cross-circuit refinement](approaches/A_ROBUST_TRANSFER.md) | Normalization-reference and varied-start training, tested with family-disjoint circuits and fixed budgets | Archived earlier main alternative; initializer shift is a secondary test |
| [B: adaptive regularity](approaches/B_ADAPTIVE_REGULARITY.md) | Condition boundary preference on circuit context instead of imposing one bias everywhere | Alternative if the main failure is boundary bias |
| [C: diffusion plus RL](approaches/C_DIFFUSION_RL_HYBRID.md) | Determine whether RL improves diffusion proposals more efficiently than search or extra sampling | Stretch extension after adapters work |
| [D: budgeted reliable refinement](approaches/D_BUDGETED_RELIABLE_REFINEMENT.md) | Predict when another complete refinement pass is worth its cost | Optional extension after core rollout logs exist |

The directions are alternatives; implementing all five is not required. E is the current selection. RUDY, MORL, preference conditioning, normalization, multi-start training, stopping rules, and generator/optimizer combinations are established ideas. The proposed contribution is a narrowly scoped refinement extension and a controlled generalization/proxy-validation study; no first-ever novelty claim is made.

## What the literature changes about the brief

- MaskRegulate already reports cross-circuit transfer. An unseen-circuit experiment alone repeats an existing question. [Paper](https://proceedings.neurips.cc/paper_files/paper/2024/hash/fe224a60b878e79d5b3d79d7f113f76b-Abstract-Conference.html)
- ChipDiffusion is a full placement generator trained on synthetic data. Its zero-shot setting and refinement are different tasks. Compare complete pipelines separately from refiners sharing the same initial layout. [Paper](https://proceedings.mlr.press/v267/lee25y.html)
- Current prior art includes EXPlace (ICLR 2026) and FlowPlace (DAC 2026); read the corresponding reviews before making novelty claims.
- HPWL, regularity, and fast congestion estimates are proxies. A PPA claim needs a compatible physical-design flow with constraints and libraries.

## Repository use

Documentation is usable immediately. The small Python scripts use only the standard library; they illustrate the objective and guard experimental bookkeeping. They are **not an implementation of MaskRegulate or an EDA placer**.

```bash
python scripts/toy_refinement_demo.py
python scripts/validate_manifest.py configs/split_manifest.example.json
python scripts/validate_manifest.py configs/split_manifest.example.json --require-real
```

The first two commands should pass. The third must reject the deliberately synthetic manifest. Replace it with audited real design families before running a generalization experiment. See [experiment configuration](configs/experiment_plan.json), [results policy](results/README.md), and [source provenance](SOURCES.md).

Original documentation and starter scripts are licensed under MIT. Referenced papers, upstream code, datasets, checkpoints, and tool licenses remain with their owners; no third-party benchmark or model is redistributed here.
