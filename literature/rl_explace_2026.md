# EXPlace — current prior art on expert guidance and timing feedback

**Reviewed:** 17 October 2026. **Evidence status:** official repository and indexed OpenReview primary-paper excerpts inspected; direct PDF retrieval encountered OpenReview browser verification. Fine-grained experimental claims beyond those excerpts remain unverified.

## Bibliography and primary sources

Chengrui Gao, Yunqi Shi, Ke Xue, Ruo-Tong Chen, Siyuan Xu, Mingxuan Yuan, Chao Qian, Zhi-Hua Zhou. *Expertise Can Be Helpful for Reinforcement Learning-based Macro Placement*. ICLR 2026.

- [OpenReview record](https://openreview.net/forum?id=yqvNwfxRR6)
- [OpenReview PDF](https://openreview.net/pdf?id=yqvNwfxRR6)
- [Indexed conference-paper PDF version](https://openreview.net/pdf/3c5ad9254df0e7614e6eae0c9b6830f04a287f71.pdf)
- [Official implementation](https://github.com/lamda-bbo/EXPlace)

## Verified evidence

Primary-paper excerpts describe four expert components: dataflow, macro grouping, periphery biasing and I/O keepout. They encode engineering guidance for macro placement and combine RL pretraining with timing-driven fine-tuning through direct preference optimization. The comparison includes MaskRegulate. [Conference-paper excerpts](https://openreview.net/pdf/3c5ad9254df0e7614e6eae0c9b6830f04a287f71.pdf).

The official repository identifies the paper as ICLR 2026, exposes a PPO agent and actor/critic, describes ICCAD 2015 and OpenROAD evaluations, and reports its own average timing improvements. The workflow downloads an environment image, benchmarks, DREAMPlace and preprocessed data, builds DREAMPlace, and trains/evaluates named designs. Output files include runtime and evaluation metrics. These are upstream capabilities/claims, not verified runtime or quality measurements from our machine. [Official repository](https://github.com/lamda-bbo/EXPlace).

## Our analysis: what it rules out as a novelty claim

Do not propose any of the following as new without a more specific distinction:

- Adding peripheral-distance guidance to RL.
- Adding dataflow or macro-group information to placement masks.
- Reserving room around I/O ports.
- Using backend timing feedback to improve a placement policy.
- Replacing a proxy-only objective with preference-based timing fine-tuning.

These are already present in closely related published work. A new graph encoder plus extra expert channels might be an implementation variation, but it needs convincing controls and a distinct research question.

## What still makes a good course project

Our recommended distinction is **strict out-of-distribution robustness and budgeted acceptance**, not simply “more expert knowledge.” Evaluate a frozen refiner under unseen netlists, different initializers and utilization changes; pre-register checkpoint selection; measure the fraction of harmful proposals; test whether a bounded-move/validation-calibrated acceptance strategy improves reliability at equal runtime.

EXPlace could become an additional contemporary baseline if its interface, datasets and evaluator can be matched. Otherwise include it in the novelty discussion and explicitly state why a numerical comparison is deferred. “Not run because incompatible or out of budget” is more defensible than copying its reported percentages into the project's comparison table.

## Evidence gaps and follow-up

Before claiming detailed superiority or a zero-shot limitation, obtain the accepted paper directly and verify its train/validation/test definitions, target-design update budget, exact timing stage, checkpoint selection and hardware/runtime accounting. The repository alone does not settle those questions. No license determination is made here; no explicit top-level license was visible in the inspected repository listing.
