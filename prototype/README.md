# Initial synthetic RL implementation

This is a small measured mid-semester scaffold, not a MaskRegulate/PPO reproduction or an industrial EDA tool. It extends the earlier three-block greedy illustration into a trainable environment. Python 3 and NumPy are required.

```bash
python prototype/placement_rl.py --episodes 600
python report/make_report_assets.py
```

The environment contains six fixed-size integer-grid rectangles, two fixed terminals, a central blockage, and seeded weighted hypernets. Every move is geometrically legal; this differs from MaskRegulate's OLD/NEW passwise masks. There are no standard cells, routed wires, timing models, rotation actions, halos or process rules.

The policy is a five-parameter linear softmax over legal candidate features and is trained with REINFORCE, an undiscounted return, and a lagged per-step exponential moving-average baseline. It has no PPO clipping or learned critic. A fixed order visits each macro twice. Candidate features include exact immediate HPWL changes, which are also available to the greedy control. All controllers retain a best feasible incumbent; terminal quality is reported separately.

The eight training netlists use generator seeds101-108, validation201-202, and test301-304. Training seeds17/29/43 each run600episodes. Uniform training/validation starts and uniform/edge-biased test starts use separate recorded seeds. Checkpoints are selected on validation only, before test evaluation. The edge-biased initializer is a synthetic sampler, not a distinct industrial placement algorithm.

`results/runs.csv` stores96 actual evaluation runs:16 circuit/initializer/start cases times six controller instances (identity, random, greedy, and three trained policies). `summary.csv` aggregates seeds/starts within each of four test netlists, then averages equally across netlists. `metadata.json` records hyperparameters, platform, selected weights and training time. `learning_curve.csv` contains validation checkpoint scores; `example_layouts.json` retains one predetermined case for report figures.

These are equal-decision experiments (12 decisions), not equal-objective-call or equal-runtime comparisons. Candidate counts vary by trajectory. Timers measure the decision loop including internal assertions; they exclude environment construction and are diagnostic, not deployment benchmarks. The fixed synthetic topology distribution and small number of graphs cannot establish industrial family-level transfer. The original mixed-start/scaling proposal is now a secondary alternative.

Environment checks verify scalar/vector HPWL agreement for all feasible first-step candidates of a development case, boundary/overlap rejection, transition legality, and undiscounted reward telescoping. Raw artifacts are retained so every reported numeric result can be regenerated.

## Selected congestion/Pareto direction

```bash
python prototype/multiobjective.py
```

`multiobjective.py` implements the initial objective/evaluation components of the selected approach. It computes bin-average RUDY-style demand, mean top-decile demand, rectangle boundary-distance regularity, fixed-start normalization, and exact minimization dominance with duplicate removal. A six-preference greedy sweep over four netlists and two starts saves 48 actual runs in `multiobjective_results/`. This is a control implementation; no learned preference-conditioned PPO policy is claimed.

The smoke checks include finite/nonnegative demand, integrated demand equal to unweighted bbox wirelength, degenerate and zero-length nets, dominance/duplicate handling, and the reward telescoping identity. The map is a geometric demand surrogate with unit net demand, 10-by-10 bins, and a 0.5-unit minimum bbox span. It omits routing resources, layer/pitch data, and macro blockages. The regularity term is a rectangle-aware toy proxy; native reproduction preserves the reference implementation's definition.

Each preference has its own greedy run. These measurements illustrate trade-offs and code operation, without a matched-budget claim or a claim to recover the true Pareto frontier. The separate original-code reproduction is documented in `../reproduction/`.
