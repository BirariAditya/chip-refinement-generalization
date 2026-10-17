# Approach D — budgeted reliable refinement

**Optional technical extension after Approach A. Status: proposed, without experimental results.**

## Research question

Can a lightweight decision rule predict whether another full macro-adjustment pass is worth its latency on an unseen circuit and starting layout?

This targets a practical deployment issue: the native passwise mask can produce intermediate overlap, so a partial pass may not supply a new feasible output. A budget-aware system must decide at meaningful completed endpoints, including the option to keep the original feasible placement. [Native environment](https://github.com/lamda-bbo/macro-regulator/blob/fe475473c86121bd09e031b6329f18e2d8b9d5ce/src/place_env/place_env.py)

## Minimal implementation

Reuse training/validation rollouts from the core study. At completed feasible pass k, log normalized current cost, recent cost change, macro displacement, macro-area fraction, pass duration and remaining budget. Train a small regression or classification model on training families to predict the utility of one additional pass, such as expected proxy gain minus a fixed latency price. Select thresholds and latency price using validation only.

At test, freeze both refiner and gate. The gate chooses continue/stop; it never changes macro sizes or uses test routing results to tune weights. If the predicted pass cannot fit within remaining budget, stop. Keep the last independently checked feasible incumbent; charge descriptor computation, gate inference, endpoint evaluation and rollback to the budget.

Start with a heuristic gate before a learned one. If a threshold on recent improvement works equally well, a learned gate is unnecessary.

## Important distinction: acceptance is not a novel guarantee

Selecting the better of P0 and a feasible proposal under an exactly evaluated scalar proxy gives non-worsening **selection for that proxy**, up to numerical tolerance. It does not prove lower routed congestion, power or delay. Give identity/rollback and common evaluation to every optimizer. A proposal that loses before rollback remains a harmful proposal in the analysis; rollback should not erase that diagnostic.

Avoid the word “safe” as a physical guarantee. This project concerns empirical reliability, budget management and proxy-level selection. Quantified uncertainty from a few circuits is not a universal OOD certificate.

## Controls and ablations

- Fixed number of passes, chosen using validation.
- Fixed time budget with last-feasible-incumbent output.
- Stop after a fixed number of non-improving passes.
- Stop when recent improvement per second falls below a validation threshold.
- Learned gate with the same passwise refiner.
- Learned gate without recent gain, without circuit descriptors and without timing features.

Use identical candidate trajectories for an offline diagnostic where possible, then run the selected online system with actual overhead. A clairvoyant best stop point from the whole test trajectory is only an oracle upper bound, never a deployable baseline. Report regret relative to that oracle separately from comparisons against practical methods.

## Evidence needed

Quality at matched total time, time to a fixed target gain, feasible pass completion, fraction stopped with useful improvement remaining and fraction of avoided harmful passes. A gate that saves time by producing weaker placements is a tradeoff, not an unqualified win. Plot Pareto outcomes instead of reducing everything to a single latency price.

## Novelty and scope risk

Stopping rules and learned algorithm control are established. Dynamic Algorithm Configuration for Global Placement (DATE 2026) already uses RL to control DREAMPlace's learning rate; its indexed primary abstract establishes related algorithm-control prior art, although full-PDF retrieval failed during this review. [Primary conference source](https://past.date-conference.com/proceedings-archive/2026/DATA/163.pdf)

Our proposed distinction is endpoint-aware learned stopping for a frozen refiner under circuit/initializer shift. A targeted prior-art search must still precede any first-ever claim. This extension is feasible only after the core system produces enough real rollout logs. It should not displace strong classical baselines or the clean held-out experiment.
