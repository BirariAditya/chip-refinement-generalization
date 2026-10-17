# IncreMacro — the non-RL refinement control

**Reviewed:** 17 October 2026. **Status:** primary author-hosted paper reviewed; implementation availability not established.

## Bibliography and sources

Yuan Pu, Tinghuan Chen, Zhuolun He, Chen Bai, Haisheng Zheng, Yibo Lin, Bei Yu. *IncreMacro: Incremental Macro Placement Refinement*. ISPD 2024, pp. 169–176. DOI: 10.1145/3626184.3633321.

- [Author-hosted paper, Yibo Lin](https://yibolin.com/publications/papers/PLACE_ISPD2024_Pu.pdf)
- [Author-hosted paper, Bei Yu](https://www.cse.cuhk.edu.hk/~byu/papers/C205-ISPD2024-IncreMacro.pdf)
- [Publisher DOI](https://doi.org/10.1145/3626184.3633321)

## What the paper contributes

IncreMacro refines an analytical placement while pushing poorly placed macros toward peripheral regions and preserving relative positional relationships. Its repeated workflow combines KD-tree macro diagnosis, gradient-based shifts and constraint-graph linear programming for legalization, then resumes standard-cell placement with macros fixed. It integrates with DREAMPlace/AutoDMP and evaluates RISC-V circuits at 7 nm. Relative to DREAMPlace, the paper reports 6.5% lower routed wirelength and improved WNS/TNS; those are results of its flow, not a directly comparable result against MaskRegulate. The implementation uses PyTorch and Gurobi. [Paper §§2–4](https://yibolin.com/publications/papers/PLACE_ISPD2024_Pu.pdf).

## Our assessment

This paper changes the appropriate null hypothesis. If a refiner improves an analytical placement, the gain could come from a better physical-design objective and legalization routine rather than learning. “Refinement is useful” is therefore insufficient; the stronger question is whether **a learned cross-circuit controller improves the quality/runtime tradeoff beyond a non-learned controller using similar physical information**.

The preservation idea is also relevant to transfer risk. A policy might find shorter macro nets by moving many blocks aggressively, yet disrupt a useful arrangement for standard cells and timing. Bounding displacement or preserving selected relative relations is a plausible safety mechanism. This is a proposed extension, not a claim that IncreMacro already guarantees monotonic improvement of every downstream metric.

## How we would compare it

- Start from exactly the same placement file for learned and non-learned refinement.
- Use the same legal canvas, macro definitions and fixed-macro standard-cell stage.
- Report proposal generation, legalization and common downstream evaluation separately.
- Add displacement and relation-preservation statistics beside wirelength and congestion.
- If Gurobi/code access prevents reproduction, clearly label a simpler greedy/periphery heuristic as an **IncreMacro-inspired control**, never as an exact IncreMacro implementation.

## Novelty boundary

Neither moving macros toward boundaries nor refining a previous placement is new. A defensible student contribution could quantify when learned refinement sacrifices useful initial structure under circuit and initializer shift, and test whether a bounded-move or acceptance rule reduces regressions. That needs measured quality/runtime curves and failure cases, not an unverified claim of universal superiority.
