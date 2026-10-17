# Literature review: Chip Placement with Diffusion Models

Research checked: 17 October 2026. This is a source review and proposed experimental interpretation, not a reproduction result.

## Identification and verified paper findings

Vint Lee, Minh Nguyen, Leena Elzeiny, Chun Deng, Pieter Abbeel, and John Wawrzynek. ICML 2025; PMLR 267:33499–33514. [Proceedings and bibliographic record](https://proceedings.mlr.press/v267/lee25y.html).

The method learns a conditional placement distribution from synthetic netlist–layout pairs. A denoiser interleaves GNN, attention, and residual MLP blocks; dimensions and pin offsets condition coordinate predictions. Guidance optimizes wirelength and overlap during sampling. Synthetic v1 contains 40,000 circuits averaging 230 vertices; v2 has 5,000 averaging 960. Training uses 3 million steps plus 250,000 fine-tuning steps. Real evaluation uses ICCAD04/IBM and ISPD2005, including macro-only, clustered, and downstream mixed-size settings. Standard cells are clustered into 512 partitions where applicable. Reported metrics include HPWL, legality, RUDY congestion, and runtime; these do not constitute complete signoff PPA. Table 6 reports average mixed-size HPWL of 22.7 versus DREAMPlace's 23.6, in units of 10^6. Tables 13–14 report diffusion averages of 4.39 minutes on IBM and 21.2 on ISPD; bigblue2 takes 122 minutes. Generalization is sensitive to graph size and connectivity scale. These are authors' results, not independently replicated findings. [Full paper, Sections 3–5 and Appendix B](https://arxiv.org/html/2407.12282v3).

## What the released implementation establishes

The official repository provides data generation, training, fine-tuning, evaluation, benchmark conversion, and a link to a [Large+v2 checkpoint folder](https://drive.google.com/drive/folders/16b8RkVwMqcrlV_55JKwgprv-DevZOX8v?usp=sharing). Clustering needs external hMetis/shmetis binaries. W&B is enabled by default and can be disabled with `logger.wandb=False`. A critical README warning is that a checkpoint/configuration mismatch can leave random weights in use: the successful state-dictionary message must be checked. Dataset inputs use PyG graphs and NumPy placements; outputs are coordinate arrays in pickle files. Dataset parsing must still be performed. These are release instructions, not evidence that the baseline executes successfully on this workstation. [Official README](https://github.com/vint-1/chipdiffusion).

The environment pins Python 3.10.4, NumPy 1.23.5, PyTorch 2.2.1, and PyG 2.4.0. It includes Shapely, Hydra, and W&B. This is a reproducibility starting point; CUDA availability and compiled dependencies still require a smoke test. [Environment file](https://github.com/vint-1/chipdiffusion/blob/main/environment.yaml).

The saved macro-only IBM configuration uses 1,000 denoising steps, 20 gradient guidance steps, and 20,000 legalization steps; model size is approximately 6.29 million parameters. Fixed ports use the `is_ports` mask. Therefore, zero-shot refers to learned weights, while substantial circuit-specific optimization can still occur at inference. The saved configuration is an auditable example, not a guarantee that every paper result uses identical settings. [Saved configuration](https://github.com/vint-1/chipdiffusion/blob/main/placements/macro-ibm/config.yaml).

The evaluator iterates `val_set[i]` for `num_output_samples` entries. Consequently, the README's values 18 and 8 should not be read as a best-of-18 or best-of-8 search on every circuit. Also, its `time_elapsed` is measured relative to one start time before the output loop, so it is cumulative across entries. It loads and constructs the model before this loop. Instrument per-circuit phases explicitly for a new runtime study. [Evaluation source](https://github.com/vint-1/chipdiffusion/blob/main/diffusion/eval.py).

The conditional model adds noise, predicts the noise with an MSE objective, and preserves masked objects. Sampling begins from noise while reusing masked input positions. This is coordinate generation conditioned on a graph, rather than image diffusion of a rendered chip picture. [Model implementation](https://github.com/vint-1/chipdiffusion/blob/main/diffusion/models.py).

Repository inspection identified commit `6973e90ee1afc345b56da486bbf7dc9772ada1a4`; GitHub's license metadata was null and no root LICENSE/COPYING appeared in the recursive tree at inspection. Treat license status as unresolved; link to upstream rather than copying its implementation or datasets into the course repository. This is a release observation, not a legal determination. [Repository metadata](https://api.github.com/repos/vint-1/chipdiffusion), [tree](https://api.github.com/repos/vint-1/chipdiffusion/git/trees/main?recursive=1).

## Interpretation for the assigned research question

The following is original critical analysis and proposed methodology.

The useful comparison is between complete pipelines. A refinement policy starts with an existing placement; a generative model ordinarily starts with noise. Comparing their reported final HPWL values without specifying the initialization cost would mix different jobs. Compare:

1. A fixed analytical initializer followed by no refinement, greedy local improvement, or RL refinement.
2. Diffusion initialization followed by the same three choices, if integration succeeds.
3. Full native pipelines under the same wall-clock and hardware accounting.

This supports two different conclusions: whether an RL policy transfers as a refiner, and whether adding that policy improves a practical generative pipeline. Neither conclusion follows from simply ranking separate paper tables.

For all variants, keep movable macros, fixed macros, ports, net weights, pin offsets, canvas bounds, orientation rules, and standard-cell representation identical. Macro-only results answer a narrower question than full mixed-size placement. A smaller macro-only netlist can be easier to optimize while omitting connections that determine eventual routing quality. Run downstream evaluation on a manageable subset before arguing about practical PPA.

Report legality before and after correction. A low wirelength score from an overlapping layout is not an admissible success. If a common legalizer is applied, retain native-pipeline results separately: a shared legalizer improves comparability but changes each method's published pipeline. Report failures and infeasible outputs rather than silently dropping them.

Use a circuit-level test split. Different placements, seeds, perturbations, or clusters of one circuit belong to the same split. The supplied pretrained checkpoint can be a useful external baseline, but it has a different synthetic training history from a newly trained RL refiner. Disclose that asymmetry. A matched synthetic-data experiment is more controlled but more expensive; it is optional rather than a mid-semester dependency.

Zero-shot and adaptation should be different result columns. Frozen-weight inference with gradient guidance is still zero-shot learning in the usual parameter-transfer sense, but is not zero optimization. Per-circuit RL fine-tuning should be counted as adaptation, with its cost reported.

## Questions to answer in the presentation

- Why can all coordinates move jointly while sequential constructive placement can commit early mistakes?
- Why does a generalizable prior still need explicit constraint handling?
- Why does good macro-only HPWL not establish timing, power, or routability?
- What computation is included in each runtime bar?
- Does refinement improve an unseen circuit, or does the initializer explain most of the gain?

## Recommended use in the project

Use ChipDiffusion as a conditional end-semester comparison, after a functioning shared evaluator and RL-refinement transfer experiment exist. A mid-semester deliverable should show understanding of its conditioning, training distribution, inference optimization, and comparison hazards. Do not promise a from-scratch 3-million-step diffusion training run before measuring available compute.
