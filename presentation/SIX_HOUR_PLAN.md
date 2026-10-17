# Six-hour mid-semester preparation plan

Deadline context: the user has six hours for the mid-semester part, about two months for the complete project, and access to a GPU of unspecified type. This plan is for research understanding and presentation readiness. Real-circuit training is not a prerequisite for today's proposal.

| Elapsed time | Task | Concrete output |
|---|---|---|
| 0:00–0:45 | Read the topic guide; compute the HPWL toy example | Explain netlist, macro, placement, HPWL and refinement without reading |
| 0:45–1:45 | Read MaskRegulate and ChipDiffusion reviews, then inspect their actual method figures | Explain state/action/reward and coordinate denoising; identify existing generalization evidence |
| 1:45–2:30 | Read proposal and Approach A; skim B/C for alternatives | One-sentence question, hypotheses, novelty boundary and four-way ablation |
| 2:30–3:15 | Read evaluation protocol and code-audit hazards | Explain family splits, checkpoint selection, initializers, matched compute and PPA limits |
| 3:15–4:00 | Review the Markdown research discussion notes | A coherent roughly 12-minute explanation; deck creation deferred by request |
| 4:00–4:40 | Run the toy and manifest example if a Python environment is ready; review output | Clearly labeled illustrative evidence and split-checker behavior |
| 4:40–5:30 | Rehearse with viva questions; open paper sections for answers you cannot explain | Clear answers and a shorter version of the talk |
| 5:30–6:00 | Final rehearsal, check research files and repository links | Markdown notes and cited sources ready for discussion |

## The opening statement

“We will study whether an RL placement-refinement policy can improve unseen circuit families when the initial layout also comes from an unfamiliar method. We will test a small robustness extension against the original policy and classical search using clean splits and equal deployment budgets.”

## What is completed versus planned

Completed research package: literature reviews, source-code audit, scoped problem, proposed extension, ablation and evaluation plan, explanatory scripts and presentation material. No real-circuit baseline, GPU training, routing or PPA results are established by these documents.

If you run anything independently, update the progress record with the exact circuit, software revision, command, seed, metric and artifact. Do not replace a “planned” label with “completed” because a dependency installed successfully. A toy example must keep its “illustrative, not a benchmark” label.

## If the presentation slot is eight minutes

Briefly cover the problem and anchor papers, combine the MDP and proposal explanation, then prioritize the research question, ablation, evaluation and eight-week plan. Keep the code audit and alternative approaches for questions. Do not cut the distinction between paper-reported findings and your own results. A slide deck remains deferred by request.

## Avoid in the six-hour window

Do not spend most of the window compiling an old CUDA stack, training diffusion from scratch, downloading a large benchmark collection, or drawing speculative result charts. Your immediate assessment concerns understanding, formulation, progress and a credible plan. Environment validation belongs in week 1 of the full project unless it is already working.
