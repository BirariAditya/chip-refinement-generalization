# Toolchain feasibility and execution plan

Status: design/research only. No installation, training, reproduction, or PPA result is claimed here. The host workspace is Windows; GPU access is confirmed, but GPU model, VRAM, host memory and throughput are unspecified. The six-hour mid-sem deadline is for understanding and a defensible proposal. The execution plan below spans approximately eight weeks.

## Recommended minimum stack

1. The regulator paper's native code/environment, pinned to a recorded commit, for the reference policy and evaluator.
2. The same initial placements and backend for every controlled refiner; use DREAMPlace if that is the paper-compatible path.
3. A common interface for native pass-wise move generation, complete-pass legality, saved feasible incumbents, reward evaluation, undo/reset, and cost logging.
4. Greedy coordinate descent and SA against that interface where faithful; otherwise label strictly legal search as a practical complete-system control, not an isolated policy comparison.
5. OpenROAD/ChiPBench on a small predetermined compatible subset for downstream evidence, after proxy experiments are stable.

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

### Provisional resource tiers

These are scope proposals, not verified hardware requirements:

- **No GPU:** prioritize code inspection, CPU smoke cases, classical controls, and a small native-policy transfer study if feasible. Do not commit to diffusion training. An eight-week full RL training project may require laboratory/cloud access.
- **One accessible GPU:** reserve an initial 10-20 GPU-hour pilot ceiling for installation, throughput measurement, and one short training diagnostic. Allocate a larger fixed cap only after extrapolating measured speed. A working GPU does not establish enough VRAM for every circuit.
- **More compute:** increase independent training seeds and held-out families before expanding architecture complexity. Preserve the same per-test-case budget for all methods.

For illustration only: if four configurations each cost 8 GPU-hours per seed and use three seeds, training alone would cost 96 GPU-hours. This is arithmetic, **not a forecast**; substitute measured hours and include failed/tuning runs. If the total exceeds the available allocation, reduce the number of configurations in the pilot or circuit sizes, then predeclare which final hypotheses remain testable.

## Eight-week plan

| Week | Deliverable | Acceptance gate |
|---|---|---|
| 1 | Read native code, pin environment, build provenance manifest, one legal development placement | dimensions, fixed objects, and independent HPWL check agree |
| 2 | Native refiner smoke run; greedy/SA interface; resource profile | policy and one classical method complete; pass endpoint and interruption checks pass |
| 3 | Training/validation/test family freeze; two-factor/four-configuration pilot | no test-family checkpoint selection; native train-extrema and proposed transfer-reference normalization distinguished |
| 4 | Full training starts; initialization-shift pilots on validation | measured budget fits available resources; main hyperparameters frozen |
| 5 | Complete training seeds and mandatory controls | same start files, evaluator, thread limits, and accounting |
| 6 | Final held-out proxy evaluation; optional preselected routing subset | all failures retained; final test not used to retune |
| 7 | Ablations, family-level analysis, failure cases, optional diffusion comparison | optional work does not displace main evidence |
| 8 | Reproducibility pass, report, final presentation | claims map directly to saved artifacts and source/runtime records |

If the project begins immediately after today's mid-sem, use this as a relative schedule; do not imply the course's actual final date has been confirmed.

## Scope priorities

**Must have:** clean family split, native reference, mixed-start extension, classical controls, common initial artifacts, two budget views, legality, pin HPWL, runtime, ablations, and limitations.

**Should have if the pilot supports it:** downstream global-route validation, three independent training seeds, and the transfer-referenced normalization ablation against the native train-calibrated extrema reference.

**Optional:** matched diffusion integration, detailed-route PPA, an always-legal RL transition ablation, hard-macro-only task variant, uncertainty gating, a new GNN architecture, or test-time adaptation. Each adds a separate source of development and evaluation cost. Power-aware RL is outside the minimum proposal unless actual physical/activity data are available.

## Reproducibility record to save for every run

Save source and dataset revisions, source-file hashes, split/family IDs, environment/container digest, hardware and resource limits, full configuration, all seeds, initial/final placements, checkpoint provenance, training and evaluation durations, objective-call count, feasibility diagnostics, failure status, and raw metric logs. Separate `paper_reported`, `illustrative`, `pilot`, `validation`, and `final_test` results in metadata.

Use an explicit `not_measured` value rather than zero for missing PPA. Keep datasets and large checkpoints outside Git unless redistribution and repository size are appropriate. Provide acquisition instructions and hashes instead.

## Source-backed environment references

- [DREAMPlace official installation/build and benchmark documentation](https://github.com/limbo018/DREAMPlace).
- [Circuit Training environment and platform guidance](https://github.com/google-research/circuit_training).
- [ChiPBench pinned evaluation stack](https://github.com/MIRALab-USTC/ChiPBench).
- [OpenROAD Docker build and verification](https://openroad-flow-scripts.readthedocs.io/en/latest/user/BuildWithDocker.html).
- [OpenROAD end-to-end tutorial](https://openroad-flow-scripts.readthedocs.io/en/latest/tutorials/FlowTutorial.html).

These sources establish available interfaces and installation routes. They do not establish that our host has passed installation or that any particular experiment will fit its resources.
