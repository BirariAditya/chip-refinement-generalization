# Approach C — diffusion proposals with a shared refinement stage

**Stretch extension. Status: proposed; pretrained generator preferred.**

## Research question

After a diffusion model proposes a placement for an unseen circuit, is frozen RL refinement more useful per unit of deployment compute than extra diffusion sampling, greedy moves or simulated annealing?

The scientific question is complementarity between generation and refinement. Combining a generator with an optimizer is a familiar idea; claim a controlled chip-placement comparison and analysis, not the invention of hybrid optimization.

## Why a direct paper-table comparison fails

ChipDiffusion generates a full layout from a circuit graph, while MaskRegulate starts with a complete layout. The papers' benchmark suites and evaluators differ. A lower published HPWL number does not identify a better algorithm unless circuit, pin/net representation, initial information and downstream backend match. [ChipDiffusion](https://proceedings.mlr.press/v267/lee25y.html), [MaskRegulate](https://proceedings.neurips.cc/paper_files/paper/2024/hash/fe224a60b878e79d5b3d79d7f113f76b-Abstract-Conference.html)

## Proposed pipeline

```text
Canonical circuit -> pretrained diffusion -> geometry/legalization check -> P0
P0 -> identity / original RL / robust RL / greedy / annealing -> PT
PT -> common standard-cell backend -> shared metrics
```

Freeze the diffusion checkpoint. Verify model configuration and successful state-dict loading; do not allow a missing/mismatched checkpoint to silently produce an untrained baseline. Record synthetic training provenance and clustering/preprocessing costs. [Official code](https://github.com/vint-1/chipdiffusion)

Before RL sees the layout, verify all macro IDs, dimensions, coordinates, origins, pin offsets, orientations, fixed objects, nets and obstacles survive conversion. Match objective values and geometry after round-trip. Passing a file parser is insufficient. If equivalence cannot be established, report separate within-tool experiments and do not claim a direct head-to-head.

## Two separate comparisons

1. **Common-start refinement:** give every refiner the same diffusion P0. This isolates improvement after generation. Add the same experiment using an analytical P0 to reveal initializer dependence.
2. **Total deployment budget:** compare diffusion alone with more samples, diffusion plus RL, diffusion plus search, and analytical placement plus the same refiners. Include generation, guidance, legalization, evaluation, selection, refinement and backend costs consistently.

When using several diffusion samples, give competing methods an equivalent sample/evaluation budget and report best-of-k selection cost. The validation dataset length is not the number of candidates for one circuit. Instrument actual sample loops and timing rather than interpreting configuration names as experimental semantics.

## Metrics and ablations

Report legal-layout rate, HPWL, congestion estimate and quality versus total time, plus flow-based timing only when compatible. Compare one versus several proposals, the refiner removed, and RL replaced by annealing. Record whether improvements disappear once the baseline gets the extra compute used by refinement.

Analyze whether the refiner produces mostly legalization changes or real objective improvements. Legalization must be a shared, separately timed stage. Keep failed or non-routable outputs in the denominator.

## Current prior art and feasibility gate

FlowPlace is a relevant 2026 comparison using flow matching and hard constraints; it increases the burden of claiming novelty for a faster or more legal generative placer. It can be a contextual literature baseline without becoming another required reproduction. [Paper](https://arxiv.org/abs/2604.23658), [official repository](https://github.com/lamda-bbo/flowplace)

Attempt this extension only after one common circuit passes the cross-tool round-trip, frozen checkpoints run correctly, and one shared evaluator agrees. Budget it after the core refinement study. Training diffusion from scratch would add synthetic-data generation and model-training work without being necessary to answer the proposed refinement question.

If adapters fail, Approach A remains a complete project. An honest compatibility audit is useful supporting work, but it cannot substitute for a claimed head-to-head experiment.
