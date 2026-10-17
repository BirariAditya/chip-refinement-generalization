# Contextual literature review: FlowPlace — Flow Matching for Chip Placement

Research checked: 17 October 2026. This later work matters when stating what is new in the proposed project.

## Identification and paper claims

Peng Xie, Ke Xue, Yunqi Shi, Ruo-Tong Chen, Chengrui Gao, Siyuan Xu, Chenjian Ding, Mingxuan Yuan, and Chao Qian. DAC 2026; DOI [10.1145/3770743.3804343](https://doi.org/10.1145/3770743.3804343). The arXiv v2 is dated 1 June 2026. FlowPlace combines boundary-aware, mask-guided synthetic placement data, a graph-conditioned flow-matching model, and hard constraint projection during sampling. Its velocity network alternates GATv2 and self-attention; it uses 20–50 Euler sampling steps instead of ChipDiffusion's 1,000 denoising steps. Authors report zero overlaps, improved placement/PPA metrics, and 10–50 times faster sampling on ICCAD2015 and OpenROAD benchmarks. Compared methods include DREAMPlace 4.1, MaskPlace, EfficientPlace, and ChipDiffusion. The paper evaluates routed wirelength, routing overflow, WNS, and TNS on ICCAD2015. These are author claims in their evaluation configuration; sampling speedup does not by itself establish equal end-to-end speedup or a universal PPA advantage. [Primary paper](https://arxiv.org/html/2604.23658v2), [version record](https://arxiv.org/abs/2604.23658).

## Release feasibility

The official README exposes synthetic-data generation, training, and evaluation scripts, with downloadable pretrained weights, dataset, benchmark cache, and generated DEF files. DREAMPlace is used for standard-cell placement. ICCAD2015 PPA evaluation relies on a commercial EarlyGlobalRoute flow, and the authors explicitly cannot share those evaluation scripts. OpenROAD evaluation has a released flow and Python interface. Therefore, the public OpenROAD path is the more reproducible candidate for a student PPA extension, subject to successful installation and the actual data terms. [Official code and evaluation instructions](https://github.com/lamda-bbo/flowplace).

Release v1.0.0 lists `mask.61.tar.gz` (about 387 MB), pretrained archive `mask.61.train_mask_flowplace_uniform.61.tar.gz` (about 56 MB), `benchmark_cache.tar.gz`, `flowplace_DEFS.tar.gz`, `OpenROAD-flow-scripts.tar.gz`, and `tech.lef`. These assets were enumerated, not downloaded or executed. Availability is not an assertion of complete reproducibility. [Release assets](https://github.com/lamda-bbo/flowplace/releases/tag/v1.0.0).

Repository HEAD inspected: `da4a10fc1a68c66dfa0ec31dd10f75b75e2e5547`. GitHub returned null license metadata. Do not infer an open-source license from a publicly visible repository. Keep upstream assets outside the course repository pending their applicable terms. [Repository metadata](https://api.github.com/repos/lamda-bbo/flowplace).

## Implications for novelty — original analysis

Boundary bias, synthetic training, stronger legality, and faster generative sampling already have direct contemporary prior art. A proposal framed only as adding these features would need a narrower distinction and additional literature checking.

The stronger course contribution remains a controlled study of **transferable refinement**: does a frozen RL policy improve genuinely unseen circuits, how does its effect depend on the initializer, and when does extra learned refinement outperform equally budgeted non-learning search?

FlowPlace makes initializer dependence more interesting. A learned refiner may behave well on analytical placements but fail on samples from a generative model because overlap patterns, macro boundary preferences, and netlength distributions differ. Initializer-family transfer can be a separate held-out condition. Do not train on FlowPlace outputs for a circuit later declared unseen, and distinguish circuit transfer from initializer transfer.

For a feasible semester project, do not make reproducing FlowPlace, ChipDiffusion, and a new RL algorithm all mandatory. Use this paper to delimit novelty now. Add its pretrained pipeline only if the main experiment is stable and its outputs can be converted into the shared placement representation. A documented failed integration with a precise reason is preferable to labeling an unexecuted baseline as evaluated.

## Useful instructor discussion

Propose that the main contribution be an initializer-aware, circuit-held-out RL-refinement study with explicit legal-move handling and normalized graph/spatial features. Ask whether a generative baseline is required for end-semester, or whether a rigorous analytical/local-search comparison plus a well-scoped generative extension is sufficient. This question concerns project scope; it does not replace implementation of the core study.
