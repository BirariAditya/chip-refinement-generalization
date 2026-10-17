# Toolchain feasibility and execution plan

**Selected direction E:** congestion-aware preference-conditioned refinement, following attachment points 4 and 5. The minimum stack now adds a checked RUDY reward, preference inputs to actor and critic, specialist/search candidate-set controls, and frozen-reference Pareto evaluation. The prior mixed-start/normalization factorial belongs to archived alternative A. See the [selected approach](../approaches/E_CONGESTION_PARETO.md) and [current protocol](experimental_protocol.md).

Status: proposed full-project plan with an initial local execution track. The Windows PC has 32 GB RAM and Intel Arc graphics; the user confirmed that GPU access is on another machine, whose model and access details remain unspecified. An isolated Python 3.8.20 / CPU PyTorch 1.7.1 environment now loads and executes the released checkpoint. See [reproduction records](../reproduction/README.md) for actual component tests, original entry-point failures, and backend build diagnostics. These checks do not establish full paper reproduction or routed PPA. The execution plan below spans approximately eight weeks.

## Recommended minimum stack

1. The regulator paper's native code/environment, pinned to a recorded commit, for the reference policy and evaluator.
2. The same initial placements and backend for every controlled refiner; use DREAMPlace if that is the paper-compatible path.
3. A common interface for native pass-wise move generation, complete-pass legality, saved feasible incumbents, reward evaluation, undo/reset, and cost logging.
4. Greedy coordinate descent and SA against that interface where faithful; otherwise label strictly legal search as a practical complete-system control, not an isolated policy comparison.
5. A checked RUDY estimator with full/incremental comparison, explicit bins/weights/degenerate-box handling, and genuine routing capacities only when available.
6. A minimal actor/critic preference embedding or tiled channels; shared initial-reference scales; fixed-weight specialist bank and SA/greedy preference sweep.
7. A minimization-oriented nondominance/HV evaluator with frozen scales/reference and a single total online budget for the complete candidate set.
8. OpenROAD/ChiPBench on a small predetermined compatible circuit/preference subset for downstream congestion evidence, after proxy experiments are stable. Timing-aware rewards require an additional working STA/data interface.

Circuit Training is useful reference material but is not a mandatory second RL stack. Its [documentation](https://github.com/google-research/circuit_training) explicitly requires Linux and recommends Docker. Prefer a Linux lab server, or a WSL2/container environment if available and verified. Do not assume native Windows compilation or GPU passthrough works. No system-level installation has been performed by this review.

The [ChiPBench installation instructions](https://github.com/MIRALab-USTC/ChiPBench#dependencies) pin OpenROAD `8396d08669f418279c89b5bbd4d7e3f5204d3288` and Yosys `4d581a97d6f0f3e545bcdaa9462b4276fab99fa3`, and offer `tuzj/chipbench:v1.0`. Verify those pins against the chosen checkout and record the resolved image digest. Do not mix a pinned benchmark flow with the latest upstream tool merely because the latter installs more easily.

## Interface compatibility checklist

Before promising a comparison, verify all of the following with a development case:

| Boundary | Evidence required | Typical failure |
|---|---|---|
| Netlist to parser | consistent object/net/pin counts and stable IDs | dropped nets or remapped macros |
| Object selection | area-ranked native largest-512 selection recorded with instance types | confusing selected modules with hard macros |
| Coordinates | units, origin, pin offsets, orientation transforms | impressive but incorrect HPWL |
| Fixed objects | IOs, blockages, fixed macros preserved | solving an easier problem |
| Pass/mask semantics | OLD/NEW states and full-pass endpoint checked explicitly | partial pass called always-legal |
| Budget interruption | timed feasible-incumbent checkpoint and common fallback | reporting an incomplete or post-deadline layout |
| Legalizer | endpoint violations and deterministic repair log, before/after cost | repair dominates the method |
| Reward normalization | native train-extrema vs proposed transfer reference documented | claiming normalization itself is new |
| Congestion estimator | full/incremental agreement; units/capacities/bin/tail rules fixed | calling relative density actual routing overflow |
| Preference conditioning | actor and critic receive the same episode-fixed simplex vector | ignoring preferences or conditioning only one component |
| Set evaluator | common minimization axes, frozen HV reference, deduplication tolerance | sign errors or test-driven reference expansion |
| Candidate budget | total cost for all queries, specialist/search archives matched | 15-weight method receiving 15 times baseline time |
| Standard cells | same placement/update schedule across methods | backbone causes the gain |
| RL checkpoint | correct architecture, feature schema, training provenance | unusable or leaked weights |
| Diffusion checkpoint | input representation and train-family audit | held-out circuit seen during pretraining |
| Placement to DEF | instance IDs/orientations/units round-trip | downstream tool ignores or misreads layout |
| DEF to routed flow | fixed macro locations verified after every relevant stage | later optimization erases intervention |
| Metrics parser | units, stage, failed runs, and missing values explicit | silent success-only averages |

Record benchmark transformations. Format translation cannot manufacture missing Liberty timing models, routing layers, or switching activity. A proxy-only dataset must remain proxy-only unless a documented physical implementation is supplied.

The native implementation's mask can allow temporary overlaps with not-yet-adjusted modules. Keep this pass-wise behavior for faithful reproduction and validate complete-pass endpoints independently. Reserve time for endpoint checking/repair, and stop at the previous checked feasible endpoint if a budget expires mid-pass. A strictly always-legal mask changes the task and needs a separate labeled ablation. The native object selection, canvas transformation, reward regularity, and observation/action conventions must also remain fixed unless a declared experiment changes them; see the [source audit](../literature/rl_maskregulate_2024.md).

## Pilot measurements before any scale commitment

Run a tiny smoke case and then one realistic development design. Measure parser/reset time, a native move and its reward time, inference latency, candidates per second, a complete adjustment pass, complete-pass legality checking/repair, a full episode, standard-cell update cost, and peak host/GPU memory. Check budget interruption deliberately: the returned layout must equal a saved checked feasible endpoint or the common feasible start. Separately measure one global-route and one full-route run if the design supports them.

For an approximate training budget:

`training wall time ≈ number of transitions / measured effective transitions per second + optimizer/checkpoint overhead`.

Effective throughput must include any repeated backend calls and data collection. A fast neural forward pass does not guarantee fast RL interaction. Profile CPU bottlenecks before buying more GPU time.

Profile chosen-action RUDY updates before attempting all-grid candidate congestion maps. The latter can multiply cost by the action-grid size. Charge congestion maps, preference-query repeats, legality checks, standard-cell refreshes, and nondominated archive work to online runtime. A GPU-compatible operator in current upstream DREAMPlace is not evidence that the regulator's older bundled environment builds it unchanged.

### Provisional resource tiers

These are scope proposals, not verified hardware requirements:

- **No GPU:** prioritize code inspection, CPU smoke cases, classical controls, and a small native-policy transfer study if feasible. Do not commit to diffusion training. An eight-week full RL training project may require laboratory/cloud access.
- **One accessible GPU:** reserve an initial 10-20 GPU-hour pilot ceiling for installation, throughput measurement, and one short training diagnostic. Allocate a larger fixed cap only after extrapolating measured speed. A working GPU does not establish enough VRAM for every circuit.
- **More compute:** increase independent training seeds and held-out families before expanding architecture complexity. Preserve the same per-test-case budget for all methods.

For illustration only: one conditioned policy costing 8 GPU-hours per seed across three seeds costs 24 GPU-hours, whereas 15 specialists receiving that same per-policy allocation cost 360 GPU-hours. These are arithmetic examples, **not forecasts**. Use an equal aggregate allocation as the practical comparison and label equal-per-specialist training as a higher-total-compute ceiling. Measure all actual costs and include failed/tuning runs. Reduce the preference grid, circuit size, or optional variants if the run matrix does not fit.

## Eight-week plan

| Week | Deliverable | Acceptance gate |
|---|---|---|
| 1 | Read native code, pin environment, build provenance manifest, one legal development placement | dimensions, fixed objects, and independent HPWL check agree |
| 2 | Native refiner, RUDY reward, greedy/SA interface; resource profile | full/incremental estimator agreement; endpoint and interruption checks pass |
| 3 | Family split freeze; actor/critic preference inputs; fixed-weight congestion-aware pilot | no test checkpoint selection; preference dependence and scales checked |
| 4 | Conditioned training and validation; specialist/search pilot | freeze queries/HV reference/normalization/budgets; measured matrix fits resources |
| 5 | Training seeds and specialist/search controls | same initial artifacts, total set budgets, evaluator, and resource limits |
| 6 | Final held-out empirical-front evaluation | all failures retained; common HV axes/reference; final test not used to retune |
| 7 | Focused ablations, preference-collapse analysis, preselected routing/timing subset if feasible | optional work does not displace main evidence |
| 8 | Reproducibility pass, report, final presentation | claims map directly to saved artifacts and source/runtime records |

If the project begins immediately after today's mid-sem, use this as a relative schedule; do not imply the course's actual final date has been confirmed.

## Scope priorities

**Must have:** clean family split; native reference; fixed-weight congestion-aware and preference-conditioned refiners; specialist/search controls; common starts/objectives; total candidate-set budget accounting; checked feasibility; HPWL/regularity/RUDY metrics; frozen-reference empirical-front evaluation; ablations and limitations.

**Should have if the pilot supports it:** downstream global-route validation, three training seeds, conditioning/reward-only/heatmap ablations, and start-reference versus native train-extrema scaling.

**Optional:** a timing-surrogate variant with actual STA-derived criticalities; periodic STA; detailed-route PPA; a small initializer-shift test; matched diffusion integration; an always-legal RL ablation; or a hard-macro-only task variant. The earlier mixed-start/four-configuration robustness study remains archived alternative A, not a second main project. Four-objective training, a new GNN, and test-time adaptation are outside the minimum scope. Power-aware RL requires appropriate physical/activity data.

## Reproducibility record to save for every run

Save source/dataset revisions and hashes, split/family IDs, environment digest, hardware/resources, full configuration, seeds, initial/final placements, checkpoint provenance, durations/call counts, feasibility diagnostics, failures, and raw logs. Also save per-episode preferences, query set, objective denominators/floors, full RUDY configuration, candidate vectors, archive tolerance, HV reference, and total set-generation budgets. Separate `paper_reported`, `illustrative`, `pilot`, `validation`, and `final_test` results in metadata.

Use an explicit `not_measured` value rather than zero for missing PPA. Keep datasets and large checkpoints outside Git unless redistribution and repository size are appropriate. Provide acquisition instructions and hashes instead.

## Source-backed environment references

- [DREAMPlace official installation/build and benchmark documentation](https://github.com/limbo018/DREAMPlace).
- [Circuit Training environment and platform guidance](https://github.com/google-research/circuit_training).
- [ChiPBench pinned evaluation stack](https://github.com/MIRALab-USTC/ChiPBench).
- [OpenROAD Docker build and verification](https://openroad-flow-scripts.readthedocs.io/en/latest/user/BuildWithDocker.html).
- [OpenROAD end-to-end tutorial](https://openroad-flow-scripts.readthedocs.io/en/latest/tutorials/FlowTutorial.html).

These sources establish available interfaces and installation routes. They do not establish that our host has passed installation or that any particular experiment will fit its resources.
