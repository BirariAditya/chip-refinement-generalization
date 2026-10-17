# DREAMPlace: the analytical backbone and a necessary baseline

Reviewed: 17 October 2026. Type: primary software documentation; not an executed reproduction.

## Verified source facts

[Official repository](https://github.com/limbo018/DREAMPlace) and [reference macro-placement results](https://github.com/limbo018/DREAMPlace#reference-results-for-macro-placement) describe a CPU/GPU analytical placement system built with deep-learning infrastructure. It is **not an RL policy**. Its macro reference results distinguish the original ISPD2005 setup, an I/O-freed setup, and modified MMS cases. The README warns that results on ostensibly identical benchmarks differ substantially and supplies calibration results. Its 4.1 release includes a two-stage macro-placement flow and improved optimization.

## Conceptual understanding

An analytical placer turns coordinates into continuous optimization variables. A smooth wirelength objective and a density penalty guide iterative updates. A legalizer then handles geometric constraints that smooth optimization does not guarantee. Using PyTorch or a GPU does not, by itself, make an algorithm a trained machine-learning model.

For the proposed project, this is the distinction between the **backbone** that generates or repairs a placement and the **policy** that chooses a useful refinement move. An apparent policy improvement can actually come from running a stronger backbone or giving it more optimization steps.

## What this implies for our experiments

- Give every refiner the same initial placement artifact and the same fixed-macro/IO interpretation.
- Save exact backbone revision, JSON configuration, density target, random seed, and legalizer settings.
- Include a backbone-only continuation baseline with the same extra runtime. This asks whether learning contributes beyond simply optimizing longer.
- Evaluate after the same legalization and standard-cell placement stages. Comparing an illegal low-HPWL candidate against a legal baseline is invalid.
- Treat MMS/ISPD naming as a schema question, not a label match: explicitly compare cell/net/macro counts, fixed objects, die dimensions, pin geometry, and target density before merging datasets.

## Limitations and mid-sem use

DREAMPlace can provide a useful common initializer, but successful compilation and benchmark agreement remain unverified here. Do not promise routed PPA from coordinate-only benchmark files. The mid-sem presentation should explain why a good classical initializer makes refinement scientifically interesting: the policy must learn the remaining difficult decisions rather than rediscover obvious coarse placement structure.

## Reproduction gate

On one small case: load the design, generate an initial placement, legalize it, compute independently checked pin-level HPWL, and save the complete log. Expand only after failures and format assumptions are understood.
