# Sources and provenance

Research checked 17 October 2026. Official proceedings identify venue/year; full papers support methods/results; pinned code supports implementation observations; official tool documentation supports interfaces and metric definitions. The reviews explicitly label inference and proposed work. No secondary blog is used as evidence for a technical claim.

## Anchor primary sources

- [MaskRegulate proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/hash/fe224a60b878e79d5b3d79d7f113f76b-Abstract-Conference.html), [paper](https://arxiv.org/html/2412.07167v1), [code](https://github.com/lamda-bbo/macro-regulator).
- [ChipDiffusion proceedings](https://proceedings.mlr.press/v267/lee25y.html), [paper](https://arxiv.org/html/2407.12282v3), [code](https://github.com/vint-1/chipdiffusion).
- [IncreMacro author-hosted paper](https://yibolin.com/publications/papers/PLACE_ISPD2024_Pu.pdf).
- [EXPlace OpenReview](https://openreview.net/forum?id=yqvNwfxRR6), [code](https://github.com/lamda-bbo/EXPlace). Full accepted-paper access was limited; do not infer unverified split details.
- [FlowPlace paper](https://arxiv.org/abs/2604.23658), [code](https://github.com/lamda-bbo/flowplace).
- [PPO paper](https://arxiv.org/abs/1707.06347).
- [DACDMP indexed primary location](https://past.date-conference.com/proceedings-archive/2026/DATA/163.pdf). Direct retrieval returned 404; review limited to indexed primary abstract and author publication listing.

Additional foundational papers and precise links are recorded in their own literature files. Tool sources: [DREAMPlace](https://github.com/limbo018/DREAMPlace), [MacroPlacement](https://github.com/TILOS-AI-Institute/MacroPlacement), [ChiPBench](https://github.com/MIRALab-USTC/ChiPBench), [OpenROAD](https://openroad.readthedocs.io/en/latest/), [Circuit Training](https://github.com/google-research/circuit_training).

## Recorded implementation revisions

| Repository | Inspected revision | Use |
|---|---|---|
| lamda-bbo/macro-regulator | `fe475473c86121bd09e031b6329f18e2d8b9d5ce` | Mask/state/reward, parser, seeding and checkpoint-path audit |
| vint-1/chipdiffusion | `6973e90ee1afc345b56da486bbf7dc9772ada1a4` | Release/config/evaluation/timing audit |
| lamda-bbo/flowplace | `da4a10fc1a68c66dfa0ec31dd10f75b75e2e5547` | Contemporary release and compatibility context |

Code observations concern those revisions. A future revision can fix an issue. A code-path risk is not proof that the authors used that path in their published evaluation.

## Data and result status

- No real benchmark dataset or checkpoint was downloaded into this repository.
- No external paper's implementation was vendored.
- The split manifest is synthetic and deliberately marked `example`.
- The Python toy is an illustrative objective calculation and greedy move; it is not RL training or a physical-design tool.
- Literature-reported numbers remain explicitly attributed. Proposed budgets/counts are planning choices.
- GPU access is confirmed, but model, VRAM, host memory and measured throughput are unknown.

## Licensing

Original repository material uses MIT. Upstream code, papers, benchmark files, checkpoint weights, tools and solver terms remain separate. The regulator repository has BSD-3-Clause at the inspected revision. License metadata for ChipDiffusion and FlowPlace did not establish a root code license during inspection; do not treat public availability as permission to redistribute. Obtain data and tools through their owners' instructions and keep provenance.
