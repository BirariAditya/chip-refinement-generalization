# Understanding RL for chip placement

This guide explains the concepts needed to defend the proposed project. Definitions and toy arithmetic are explanatory; they are not real-circuit experimental results.

## 1. Where placement fits

An RTL description expresses digital behavior. Logic synthesis maps it to a netlist of instances and connections. Floorplanning establishes the die/core and major constraints. Placement chooses physical locations; clock-tree synthesis and routing build actual clock and signal connections. Timing, power and physical-rule evaluation happen at specified stages of that flow.

This project addresses **macro placement refinement**. A macro is a comparatively large block such as a memory instance. Standard cells are much smaller logic elements. Choosing locations is different from synthesizing a new circuit topology or changing the macro's internal function. [OpenROAD flow](https://openroad-flow-scripts.readthedocs.io/en/latest/mainREADME.html)

The benchmark's definition of “macro” must be audited. In the released MaskRegulate parser, object selection by area can differ from a strict hard-macro-only inventory. Never compare results from differently selected instances as if they solved the same problem. See [the source audit](../literature/rl_maskregulate_2024.md).

## 2. Why it is difficult

If N macros each have K candidate grid locations, even a crude unconstrained search space has K^N assignments. Overlap and floorplan constraints reduce this number but also make optimization harder. Moving one block changes connections to many others, so independent per-block decisions generally fail to capture the global objective.

A circuit is naturally a **hypergraph**: vertices represent instances or pins, and a hyperedge represents a net joining potentially more than two terminals. Replacing a hyperedge with pairwise edges changes the representation unless its weighting is handled deliberately.

Long wires can add delay and routing demand, but the shortest geometric connection pattern need not be routable. Large blocks can obstruct channels. This creates multiple objectives and constraints rather than one universal scalar score.

## 3. HPWL by hand

For one net with pin coordinates `(x_i,y_i)`, half-perimeter wirelength is

```text
HPWL(net) = max_i(x_i) - min_i(x_i) + max_i(y_i) - min_i(y_i).
```

Total weighted HPWL sums this over nets. It is called half-perimeter because a bounding rectangle's perimeter is twice this expression. It is a fast proxy; it is not a routed path length.

Toy example: one net has pins at `(1,1)`, `(4,2)` and `(3,5)`. HPWL is `(4-1)+(5-1)=7`. Move the second pin to `(3,2)` and HPWL becomes `(3-1)+(5-1)=6`. That net improves by one unit. Other nets incident to the moved macro can worsen, so evaluate the complete declared objective. Moving a macro also moves its pins by their offsets; using centers instead of true pins can change the problem.

“Macro HPWL” omits or aggregates some standard-cell connections. “Global HPWL after standard-cell placement” includes a different object set. Report both with their definitions rather than combining them into one column.

## 4. Congestion, regularity and PPA

Congestion occurs when routing demand exceeds available routing capacity. A RUDY-style estimate spreads net demand across bounding boxes; a global router estimates paths and capacities; detailed routing produces more implementation-specific information. These are different evidence levels.

Regularity is a geometric preference for an organized macro layout. MaskRegulate's boundary-distance formulation prefers smaller distances to boundaries; summing nearest horizontal and vertical boundary distances can favor corners. This preference may leave space for cells, but is a heuristic rather than a law that boundary layouts are always better. [MaskRegulate](https://proceedings.neurips.cc/paper_files/paper/2024/file/fe224a60b878e79d5b3d79d7f113f76b-Paper-Conference.pdf)

PPA means power, performance and area. Performance commonly uses slack: WNS is worst negative slack, and TNS sums negative slack across reported endpoints. Values closer to zero are generally better when negative, under the same constraints. Timing interpretation requires the same clock constraints, library corner, parasitic stage and flow. Power estimates require library and activity assumptions. Die area is fixed in a fixed-floorplan placement task; rearranging fixed-size blocks does not by itself reduce area. [OpenROAD metrics](https://openroad.readthedocs.io/en/latest/main/src/utl/README.html)

## 5. Constructing versus refining

In constructive placement, the agent starts with unplaced macros and chooses one location at a time. An early action is made before later macro positions are known. Some methods densify reward, so it is inaccurate to say every constructive RL method has only a terminal reward.

In refinement, the initial placement already locates the objects. Moving a macro can be evaluated against a fuller layout context. That can improve the information in the state and the usefulness of local reward. It does not guarantee a good final layout: the objective may be imperfect, the initial basin may be poor, and coordinated moves may be required.

MaskRegulate uses OLD and NEW occupancy information during a pass. It can temporarily overlap a macro that has not yet been adjusted. Therefore “refinement” must not be explained as “every intermediate layout is guaranteed legal.” Check complete-pass endpoints and support budget interruption safely. [Implementation review](../literature/rl_maskregulate_2024.md)

## 6. The reinforcement-learning formulation

An MDP consists of states S, actions A, transition dynamics, rewards and a horizon/discount rule. For this project:

| Element | Meaning |
|---|---|
| State | Net/geometry context, OLD/NEW layouts, selected macro, pass phase, action mask and budget context |
| Action | Choose an allowed grid location for the current macro |
| Transition | Update placement, occupancy and relevant cost maps |
| Reward | Declared change in wirelength/regularity proxy, with specified scaling |
| Episode | A prescribed sequence of macro passes or completed finite horizon |
| Policy | A shared neural rule mapping placement state to action probabilities |

For cost J, `r_t=J(P_t)-J(P_(t+1))` rewards improvement. In an undiscounted episode, intermediate terms cancel and total reward equals initial minus final cost. With gamma<1, clipping or additional terms, that equivalence changes. A dense reward is frequent feedback, not a guarantee of objective fidelity.

The mask removes disallowed grid actions before sampling. A masked policy can learn choices within that set. To isolate learning, random, greedy and annealing controls should use the same mask when possible; otherwise a result could be caused by the action representation rather than the learned policy.

## 7. PPO intuition

Proximal Policy Optimization updates a policy using trajectories and an advantage estimate. Advantage asks whether an action performed better than expected for its state. An actor chooses actions; a critic estimates future return. The clipped probability-ratio objective limits the incentive for very large policy changes on the sampled batch:

```text
ratio_t = pi_new(a_t|s_t) / pi_old(a_t|s_t)
L_clip = E[min(ratio_t*A_t, clip(ratio_t,1-eps,1+eps)*A_t)].
```

The critic loss and optional entropy term are additional components. Clipping stabilizes the update heuristic; it does not prove cross-circuit generalization or enforce physical constraints. Those require representation choices, data diversity, explicit masks and evaluation. [Original PPO paper](https://arxiv.org/abs/1707.06347)

## 8. What “generalization” must mean here

There are several distinct settings:

- New placement seed for the same netlist: state/initialization robustness, not unseen-circuit transfer.
- A new floorplan variant of the same parent design: variant transfer, not strong family-disjoint evidence.
- Unseen circuit family with frozen weights: the primary circuit-transfer claim.
- Unseen circuit plus a new initializer: the joint shift investigated in this project.
- Gradient updates to policy weights on the new design: adaptation, reported separately.

A frozen policy may evaluate the test graph and optimize its placement; zero-shot does not mean zero computation. Similarly, diffusion can use gradient-based coordinate guidance while keeping learned weights frozen.

Training circuits determine parameters. Validation circuits determine hyperparameters and checkpoint choice. Test circuits determine the final report only. Selecting the best epoch on test HPWL leaks test information even without training gradients on those circuits.

## 9. Diffusion explained for this task

Training adds noise to known placement coordinates and learns a graph-conditioned denoising model. Inference starts from noisy coordinates and iteratively denoises them. This is coordinate generation, not image generation from a chip photograph. Graph structure, dimensions and pin data help the model infer plausible arrangements. Guidance and legalization improve objective quality and feasibility at inference. [ChipDiffusion](https://proceedings.mlr.press/v267/lee25y.html)

The useful comparison asks whether a learned generator, a learned refiner and classical search offer better quality for an explicit resource budget. They are not interchangeable algorithms with identical input information. A hybrid can exploit global proposal diversity and local refinement, but its extra cost must be compared with extra sampling or stronger search.

## 10. Why the project can fail and still teach something

The original policy may already transfer well; proposed scaling may be redundant. Mixed starts may improve robustness only by spending more compute. Simulated annealing may outperform the learned method at the same runtime. Better HPWL may produce worse routed congestion. Available benchmark “designs” may contain too few independent families.

These are testable outcomes. The contribution comes from a sound formulation, controlled comparison and explanation, not from assuming a favorable conclusion. Read the [proposal](../PROJECT_PROPOSAL.md) for the precise hypotheses and [viva answers](../presentation/VIVA_QA.md) for concise ways to defend them.
