# ChiPFormer — transfer and adaptation must be measured separately

**Reviewed:** 17 October 2026. **Status:** proceedings, paper and official README reviewed; no training run.

## Bibliography and primary sources

Yao Lai, Jinxin Liu, Zhentao Tang, Bin Wang, Jianye Hao, Ping Luo. *ChiPFormer: Transferable Chip Placement via Offline Decision Transformer*. ICML 2023, PMLR 202, pp. 18346–18364.

- [Proceedings record](https://proceedings.mlr.press/v202/lai23c.html)
- [Paper](https://proceedings.mlr.press/v202/lai23c/lai23c.pdf)
- [Official code](https://github.com/laiyao1/ChiPFormer)
- [Author-deposited record](https://arxiv.org/abs/2306.14744)

## Verified contribution

ChiPFormer formulates placement using offline RL and a decision transformer. It learns a transferable policy from previously collected placements, then supports fine-tuning on unseen circuits. The paper evaluates 32 circuits and reports approximately tenfold runtime reduction against its selected contemporary comparisons. These are paper-specific claims; they are not a universal runtime guarantee or evidence that target-circuit fine-tuning is zero-shot inference. [Proceedings abstract and paper](https://proceedings.mlr.press/v202/lai23c.html).

The official repository describes pretraining with `run_dt_place.py`, adaptation with `odt.py --benchmark=adaptec1`, and optional VGAE circuit feature extraction using `graph_train.py`/`graph_eval.py`. It provides offline data links for 12 designs, a small adaptec1 example and a 2026 environment recommendation using Python 3.9, PyTorch 1.10.1 and CUDA 11.3. Its test benchmarks include ISPD05 and ICCAD04; those are not ICCAD2015 superblue files. [Official implementation instructions](https://github.com/laiyao1/ChiPFormer).

## Our conceptual explanation

Online RL improves a policy by repeatedly interacting with the placement environment. Offline sequence modeling can instead start with stored trajectories: observations, prior actions and desired returns provide a sequence context for predicting the next action. This trades expensive new rollouts for dependence on the coverage and quality of historical data. This explanation is our interpretation of the methodological contrast, not a new algorithm.

Transfer evaluation has three different questions:

| Regime | What is permitted on a held-out design? | What must be charged? |
|---|---|---|
| Zero-shot | Frozen policy, fixed inference rule | Initialization, inference and common evaluator |
| Search without policy updates | Multiple candidate rollouts and common selection rule | Every rollout and every scoring call |
| Few-shot adaptation | Bounded target-design updates | All update time and target evaluator interactions |

Do not mix these rows when comparing an RL refiner, diffusion placer and offline transformer. A method that receives 300 target rollouts has a different information and compute budget from a single frozen-policy pass.

## Our project implications

1. The motivation “RL generalizes poorly” requires a qualified statement: it concerns particular algorithms, data distributions and adaptation budgets, not a theorem excluding transfer.
2. If diffusion consumes pretrained placement datasets, account for data generation just as one would for the offline transformer.
3. If an encoder learns from all benchmark graphs, declare that transductive exposure. A strict inductive claim should train representation parameters on training designs only.
4. Exact circuit identities must be split before creating perturbed layouts or trajectories; variants of one netlist must stay together.
5. If included experimentally, use the same macro selection and full-placement evaluator. Otherwise keep ChiPFormer as conceptual context, without publishing incomparable numerical rankings.

## Feasibility and limitations

Running the entire offline pipeline adds data preparation, graph libraries and adaptation code to the project. For a mid-semester milestone, understanding the transfer protocol is more valuable than starting three partially working stacks. Prioritize MaskRegulate and its matched greedy control first; add ChiPFormer only if a common evaluator and comparable data are available.

The README was inspected, but no license conclusion is made here because the complete dependency/data licensing chain was not audited. No reproduction, installation success or numerical result is claimed.
