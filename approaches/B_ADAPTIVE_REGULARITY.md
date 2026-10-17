# Approach B — circuit-conditioned regularity

**Alternative project. Status: proposed; choose this instead of expanding the main project indiscriminately.**

## Question

When does pushing macros toward boundaries help, and when does it lengthen important connections or create edge congestion? Can a circuit-conditioned preference improve the HPWL/congestion tradeoff across unseen circuits?

MaskRegulate incorporates regularity into refinement. EXPlace also encodes engineering expertise, so “adding boundary preference” is not new. The defensible extension is identifying the boundary conditions under which a fixed preference transfers poorly, then adapting its strength with a tightly controlled mechanism. [MaskRegulate](https://proceedings.neurips.cc/paper_files/paper/2024/hash/fe224a60b878e79d5b3d79d7f113f76b-Abstract-Conference.html), [EXPlace](https://openreview.net/forum?id=yqvNwfxRR6)

## Smallest useful method

Condition the policy on a regularity coefficient lambda and train over a fixed range of coefficients on training circuits. Use validation to define either one global coefficient or a deterministic mapping from observable circuit descriptors to the coefficient. Descriptors can include macro-area fraction, aspect-ratio distribution and normalized net connectivity to fixed IO pins.

First use a simple, interpretable selector such as a small set of coefficient bins chosen by validation. A learned meta-controller is optional only if enough independent training circuits exist. Do not fit a complicated selector on four circuit families and call it broad generalization.

Candidate cost `H/H_ref + lambda R/R_ref` remains a proxy. If congestion is added, establish the evaluator first and give every method the same metric. Keep geometry/halos hard constraints rather than soft reward terms that can be traded away.

## Experiments

Compare zero regularity, fixed upstream regularity, validation-tuned global regularity and circuit-conditioned regularity. Use identical starts, masks, budgets and checkpoint rules. Plot per-design HPWL against regularity and a separately measured congestion proxy. Include designs with different IO patterns and macro density; do not manufacture more independent samples by perturbing one netlist.

Required ablations: remove conditioning; remove individual descriptors; hold total training compute constant; compare the selector with a small validation-calibrated constant grid. Test whether the selector changes behavior on unseen circuits or simply chooses one coefficient almost everywhere.

## Interpretation

If the conditional method helps only a particular topology class, report that class and uncertainty. If regularity improves while routed timing worsens, the proxy is misaligned. If the best fixed coefficient performs just as well, a learned selector is unnecessary; the empirical result still identifies the value of simple tuning.

## Feasibility and risks

This approach needs fewer integration layers than diffusion plus RL but risks overlapping closely with expert-conditioned prior work. It also needs enough diverse circuits to justify conditioning. Commit after a pilot finds that the original policy's failures correlate with regularity or boundary bias. It should not be sold as the main contribution before observing that failure.

Six-hour deliverable: a clear motivation, comparison table and falsifiable prediction. Eight-week deliverable: validated selector, Pareto curves and downstream checks on a compatible subset. No existing results in this repository establish the proposed advantage.
