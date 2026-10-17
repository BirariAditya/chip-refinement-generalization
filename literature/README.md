# Literature review index

Fourteen individual Markdown reviews were prepared from primary papers, official repositories and tool documentation. Paper findings, code observations, original interpretation and unverified details are distinguished inside each file. Research date: 17 October 2026. No review represents a local reproduction.

## Required reading order

1. [MaskRegulate, NeurIPS 2024](rl_maskregulate_2024.md) — the anchor method, existing transfer experiment, exact masks/rewards and code hazards.
2. [ChipDiffusion, ICML 2025](diffusion_chipdiffusion_icml2025.md) — conditional denoising, synthetic data, evaluation and deployment costs.
3. [IncreMacro, ISPD 2024](rl_incremacro_2024.md) — why non-RL refinement is a necessary control.
4. [MacroPlacement and strong SA evaluation](eval_macroplacement_sa.md) — fair classical comparison.
5. [DREAMPlace](eval_dreamplace.md), [ChiPBench](eval_chipbench.md), [OpenROAD](eval_openroad.md) — task/evaluator compatibility and PPA boundaries.

## Complete list

| Review | Role in the project | Evidence boundary |
|---|---|---|
| [PPO, 2017](foundation_ppo_2017.md) | Underlying learning method | Not placement evidence |
| [MaskPlace, 2022](rl_maskplace_2022.md) | Dense masks and constructive RL context | Not a refinement method |
| [ChiPFormer, 2023](rl_chipformer_2023.md) | Offline learning and transfer context | Distinguish transfer from target-task adaptation |
| [MaskRegulate, 2024](rl_maskregulate_2024.md) | Anchor refiner and pinned source audit | Published flow and current code defaults can differ |
| [IncreMacro, 2024](rl_incremacro_2024.md) | Non-RL refinement precedent | Exact implementation availability not established |
| [ChipDiffusion, 2025](diffusion_chipdiffusion_icml2025.md) | Generator comparison | Different benchmark/interface; not a controlled refiner head-to-head |
| [EXPlace, 2026](rl_explace_2026.md) | Expert priors/timing novelty boundary | Accepted-PDF direct access limited; source excerpts/repository separated |
| [FlowPlace, 2026](diffusion_flowplace_dac2026.md) | Newer generative placement context | Not locally run; full commercial flow not reproduced |
| [DACDMP, 2026](context_dacdmp_date2026.md) | Algorithm-control prior art for optional stopping extension | Indexed abstract only; direct PDF returned 404 |
| [DREAMPlace](eval_dreamplace.md) | Analytical backbone and formats | Tool documentation, not new measured results |
| [MacroPlacement/SA](eval_macroplacement_sa.md) | Strong search and evaluation context | Source-reported claims require their exact benchmark setup |
| [ChiPBench](eval_chipbench.md) | Downstream benchmark and family grouping | Provenance still needs case-level audit |
| [OpenROAD](eval_openroad.md) | Flow stages, congestion and timing metrics | Available tools do not imply data or installation compatibility |
| [Circuit Training](eval_circuit_training.md) | Alternative RL framework/platform context | Optional reference stack, not a second required implementation |

The prefixes are organizational only: `rl_incremacro` reviews a non-RL paper. See [research synthesis](../RESEARCH_ANALYSIS.md) for conclusions and [source provenance](../SOURCES.md) for source hierarchy and pinned code versions.
