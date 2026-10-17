# ChiPBench: end-to-end evaluation and related-design leakage

Reviewed: 17 October 2026. Type: official benchmark software and paper abstract. No results reproduced.

## Verified source facts

The official [ChiPBench repository](https://github.com/MIRALab-USTC/ChiPBench) evaluates macro, global, and mixed-size placements through an OpenROAD-based flow. It accepts an input DEF and design configuration and writes metrics. Its 20-design table includes several Ariane variants, BlackParrot blocks/variants, and SweRV variants. It pins OpenROAD and Yosys revisions and offers a Docker image. The [paper](https://arxiv.org/abs/2407.15026) motivates evaluation using final implementation PPA rather than isolated placement proxies.

## Why it matters

A placement is only one stage in chip implementation. Later standard-cell optimization, clock-tree synthesis, buffering, legalization, and routing can preserve, erase, or reverse an apparent early improvement. An experiment can therefore succeed on the reward used by RL while failing on the chip metric that motivated the project.

For our study, ChiPBench is a candidate **downstream validation layer**, not an automatic drop-in training corpus. We must first check instance names, physical dimensions, fixed objects, macro orientations, cell libraries, timing constraints, and the interface of each learned method.

## Leakage analysis: proposed safeguard

Randomly splitting layouts is inadequate when variants share a parent design. A conservative grouping should keep all Ariane cases together; keep all BlackParrot blocks and variants together unless a stronger independence argument is documented; and keep SweRV variants together. Sub-blocks can share architectural structure even when their netlists are not identical.

Treat other families as provisional until provenance is checked. For example, processor names alone do not establish independence: OpenRISC-related designs merit an ancestry audit. Store a documented family map before seeing results. Derivatives, technology remappings, floorplan perturbations, and augmented placements inherit the parent split.

## Proposed use and limits

Start with one routable training/development design and one separate development family to debug conversion. Then reserve complete families for final testing. Select the downstream subset in advance using compatibility and runtime criteria, not whether a method wins.

The number of independent families, not the number of files or stochastic rollouts, controls the strength of a generalization claim. A smaller rigorous family-held-out result is more credible than a larger layout-random split with near duplicates.

## Naming caution

This review concerns **ChiPBench, the placement/PPA benchmark** maintained by MIRALab-USTC. Similarly named LLM chip-design benchmarks are different projects.
