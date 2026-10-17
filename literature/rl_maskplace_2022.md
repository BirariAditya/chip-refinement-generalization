# MaskPlace — why dense rewards alone are not the new contribution

**Reviewed:** 17 October 2026. **Status:** primary paper/author project reviewed; not reproduced.

## Bibliography and evidence

Yao Lai, Yao Mu, Ping Luo. *MaskPlace: Fast Chip Placement via Reinforced Visual Representation Learning*. NeurIPS 2022, volume 35, pp. 24019–24030.

- [Proceedings metadata](https://proceedings.neurips.cc/paper_files/paper/2022/hash/97c8a8eb0e5231d107d0da51b79e09cb-Abstract-Conference.html)
- [Conference paper](https://proceedings.neurips.cc/paper_files/paper/2022/file/97c8a8eb0e5231d107d0da51b79e09cb-Paper-Conference.pdf)
- [Author project](https://laiyao1.me/maskplace/)
- [Official code](https://github.com/laiyao1/maskplace)

## Paper contribution

MaskPlace learns pixel-level representations of chip layouts, places modules sequentially on a high-resolution discrete canvas, and supplies dense wirelength feedback with feasibility masking. Its canvas/mask approach is the architectural ancestor of MaskRegulate. The paper reports wirelength, congestion and density improvements and zero overlaps in its setting. These statements are author-reported results, not results of this project; advertised relative improvements should not be transferred to another benchmark or flow. [Paper](https://proceedings.neurips.cc/paper_files/paper/2022/file/97c8a8eb0e5231d107d0da51b79e09cb-Paper-Conference.pdf).

The author's entry command is `python PPO2.py`; exposed parameters include discount factor, seed, learning rate, benchmark, number of placed modules, batch size and a soft action constraint coefficient. This is useful implementation evidence, but not verification of installation on the present machine. [Author usage instructions](https://laiyao1.me/maskplace/).

## Our explanation and analysis

Imagine placing rectangles on graph paper. A canvas channel tells the policy which regions are occupied; a feasibility channel marks forbidden anchor positions. For each candidate location, a wire channel estimates the change in net bounding boxes. A convolutional model can learn local geometric patterns from these channels without fixing an ordering of graph vertices in its neural input. This is our explanatory interpretation.

The important distinction is **information completeness**, not simply “sparse versus dense.” A from-scratch placer can already have dense feedback. If connected modules have not yet been placed, however, its feedback conditions on only the known part of the geometry. A refiner conditions on an entire existing arrangement and then updates that context as it acts. That makes a cleaner research comparison than suggesting all older RL work only used terminal reward.

Useful baseline questions for our project:

1. Does refinement still outperform constructing from scratch after charging for the initializer?
2. Does a greedy action chosen from the same wire and regularity maps explain most of the improvement?
3. Does a learned policy add value beyond its engineered candidate restriction?
4. Are improvements preserved when macros are held fixed during the common downstream standard-cell stage?

These are proposed experiments; no answers are asserted here.

## Project use and limits

Treat MaskPlace as the **construction baseline**, MaskRegulate as the **refinement baseline**, and a matched-mask greedy method as the **learning-value control**. Keep canvas resolution, macro definition, initialization/restart budget, common evaluator and CPU/GPU reporting consistent.

Reimplementing dense rewards or adding occupancy masks is not a defensible novelty claim. A useful course contribution would identify the conditions under which complete initial context changes generalization, controlling for the initializer and reward maps.

Do not treat its historical performance claims as a current state-of-the-art ranking. A fair new experiment must rerun compatible baselines under one flow. Code availability also does not imply the benchmark package is installed or all dependency licenses have been audited.
