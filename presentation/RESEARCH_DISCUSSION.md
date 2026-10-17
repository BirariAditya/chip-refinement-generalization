# Mid-semester research discussion notes

This is a Markdown discussion outline, not a slide deck. Suggested length: roughly 10–12 minutes, adapted to the course slot. No empirical performance result is claimed.

## 1. State the research question

“Can a frozen RL placement-refinement policy improve an unseen circuit when the initial layout also comes from an unfamiliar method, at a competitive compute budget?”

Explain that the project changes physical macro positions, not the circuit's logical function. Mention the two-month experimental horizon and that the immediate submission is research framing.

## 2. Explain the physical-design problem

Define netlist, macro, standard cell, floorplan and placement. Show the HPWL formula using the toy example in the topic guide. Explain overlap, fixed pins and routing channels. Clarify why optimizing HPWL alone cannot establish PPA.

## 3. Explain refinement versus construction

A constructive policy chooses positions before all future locations are known. A refiner starts with existing positions and can evaluate changes in a fuller context. Constructive policies can also have dense rewards. Native refinement may make large moves and temporary overlaps; it is not necessarily small always-legal nudging.

## 4. Explain the two anchor papers

MaskRegulate: learn a grid-location policy from placement masks, wire rewards and regularity; it already reports held-out-chip evaluation. ChipDiffusion: generate coordinates conditioned on a graph using synthetic training, denoising, guidance and legalization. Their different task inputs prevent a simple paper-table ranking. See the two full literature reviews for sources.

## 5. Identify the gap

“We need to know whether gains persist when circuit family and initializer both change, after matching time and search information.”

Distinguish circuit shift, initializer-algorithm shift and initializer-quality shift. Describe why same-netlist seeds are not unseen circuits. State that broad first-ever generalization is not a claim of this project.

## 6. Describe the MDP

State: OLD/NEW placement masks, current macro, net/geometry features and pass/budget context. Action: allowed grid location. Transition: move macro and update masks. Reward: declared cost change with documented scaling. Endpoint: independently checked completed pass. The policy is frozen at test.

If asked about theory, explain the PPO ratio and clipped objective, and why discounted cost differences do not simply equal final cost improvement.

## 7. Present the proposed intervention

Start with the original implementation and its existing normalization. Compare native train-calibrated references with transfer-referenced scaling; train using single versus mixed legal starts. Hold architecture and action interface fixed. If scaling is redundant, drop that component and strengthen the controlled robustness study.

## 8. Describe evidence and baselines

Use a four-way factorial, shared initial files, validation-only model selection and family-disjoint tests when provenance permits. Compare original RL, greedy/SA, random masked actions, identity and analytical-backbone continuation. Separate equal runtime from equal objective-call studies. Count complete feasible passes, failures and rollback cost.

## 9. Explain diffusion's role

It is an optional initializer and a complete pipeline comparison. Verify graph/pin/object equivalence and common downstream evaluation. Compare diffusion plus RL against diffusion plus search and extra diffusion sampling at equal total cost. Integration is a week-4 gate, not today's result.

## 10. Explain planned analysis

Per-family HPWL change, harmful-refinement rate, feasible-run fraction, cost/time curves, displacement and the dependence on initial quality. On a compatible subset, compare proxy rankings with routing/timing. Report missing metrics as unmeasured, not zero.

## 11. Report actual progress honestly

Completed: primary-source reviews, code-level risk audit, project alternatives, recommended formulation, experimental protocol and research repository. Explanatory scripts are toy/bookkeeping tools. No real-circuit baseline execution, training or PPA result has been established here.

## 12. End with the execution decision

Weeks 1–2 establish a functioning native path and strong control; weeks 3–4 implement and validate the intervention; weeks 5–6 run frozen tests; weeks 7–8 analyze and document. Keep Approach A as the core. Add one extension only if the gates pass. The result may be positive or negative, but must be controlled and explained.

Use [viva answers](VIVA_QA.md) for preparation and [the full proposal](../PROJECT_PROPOSAL.md) for equations and experimental detail.
