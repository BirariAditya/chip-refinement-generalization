# Literature review: Proximal Policy Optimization Algorithms

John Schulman, Filip Wolski, Prafulla Dhariwal, Alec Radford and Oleg Klimov. 2017. [Primary paper](https://arxiv.org/abs/1707.06347). Reviewed 17 October 2026.

## Source-backed contribution

PPO alternates environment sampling with several minibatch optimization epochs on a surrogate policy objective. Its clipped objective restricts incentives for large probability-ratio changes relative to the behavior policy. The paper evaluates online policy-gradient learning on control and Atari tasks. It is foundational algorithmic context, not evidence about chip placement or unseen netlists.

## Interpretation for this project

The policy learns a distribution over mask-permitted grid locations; the critic estimates return. A cost-change reward offers direct local feedback, but discounting can favor improvements arriving earlier in a macro pass. A change in reward normalization can therefore affect optimization stability without changing which physical layout has the best reported objective.

For implementation understanding, inspect the regulator's actual return/advantage code. Do not assume that a PPO implementation uses generalized advantage estimation or a particular normalization scheme because these are common defaults in other libraries.

## Proposed diagnostics

Compare policy entropy, value error, reward ranges, action validity and training/validation performance. A low PPO loss is not evidence of physical quality or OOD generalization. Hold PPO settings fixed in the main factorial so the effect is not confounded with a broad retuning exercise. If the new scaling requires a different learning rate, report both a fixed-hyperparameter comparison and a validation-tuned comparison, with tuning cost included.
