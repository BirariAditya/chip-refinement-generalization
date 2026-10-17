# Literature context: Dynamic Algorithm Configuration for Global Placement

Chen Lu, Ke Xue, Ruo-Tong Chen, Yunqi Shi, Siyuan Xu, Mingxuan Yuan, Chao Qian and Zhi-Hua Zhou. DATE 2026. Research checked 17 October 2026.

**Evidence limitation:** an indexed primary conference-PDF abstract was inspected. Direct retrieval subsequently returned 404. This is a contextual review of that abstract, not a full-paper or code audit. [Primary conference PDF location](https://past.date-conference.com/proceedings-archive/2026/DATA/163.pdf), [author publication list](https://www.lamda.nju.edu.cn/xuek/).

## Verified abstract-level idea

DACDMP applies RL to dynamically control DREAMPlace's learning rate rather than using only a static tuned configuration. The abstract also describes increasing optimization steps in Lagrangian subproblems and reports comparison with DREAMPlace, AutoDMP and Xplace. The timing/wirelength results are authors' claims; they have not been replicated here.

## Our interpretation

RL for algorithm control is already relevant prior art. A proposal to choose a placement optimization parameter or stopping time cannot claim novelty merely because it places RL “above” a conventional solver. It must identify a specific missing problem and show controls against simple dynamic heuristics.

Approach D targets a narrower setting: deciding whether another completed pass of an already trained refiner is worthwhile under unseen circuit/initializer distributions. That is a proposed distinction, not proof of novelty. Full-paper access and a targeted stopping-policy search remain necessary before making a publication claim.

## What must be verified later

Exact state/action/reward definitions, training designs, target-design adaptation, compute matching and code availability. No assumption about these details is used in the core Approach A protocol.
