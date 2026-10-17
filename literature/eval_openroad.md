# OpenROAD/ORFS: what routed metrics can and cannot establish

Reviewed: 17 October 2026. Type: official tool documentation. No installation or routing run claimed.

## Verified source facts

The official [ORFS tutorial](https://openroad-flow-scripts.readthedocs.io/en/latest/tutorials/FlowTutorial.html) describes RTL-to-GDS stages and reporting for area, timing, and power. [Global-routing documentation](https://openroad.readthedocs.io/en/latest/main/src/grt/README.html) provides congestion reporting and distinguishes global-route from detailed-route wirelength. [Endpoint-slack documentation](https://openroad-flow-scripts.readthedocs.io/en/latest/contrib/EndpointSlackTracking.html) warns that timing reports at different flow stages use different parasitic models. [Docker guidance](https://openroad-flow-scripts.readthedocs.io/en/latest/user/BuildWithDocker.html) covers containerized builds and resource allocation.

## Interpretation for our research

The measurement must state the stage. Pin-level HPWL measures the bounding box of each net. A congestion proxy estimates routing demand. Global routing adds physical routing resources and approximate paths. Detailed routing adds further physical constraints and extraction. These measurements answer related but different questions.

Use a hierarchy of claims:

- **Proxy-quality claim:** pin HPWL, density, legality, displacement, and a named congestion estimator.
- **Routability evidence:** global-route overflow and wirelength under a fixed router configuration.
- **Implementation-quality evidence:** detailed-route completion, DRC count, extracted-timing metrics, and area.
- **Conditional power evidence:** reported power with declared library, operating corner, voltage, frequency, and switching activity assumptions.

Do not call these academic flows manufacturing sign-off. Do not infer actual power savings solely from shorter HPWL.

## Fairness requirements

All candidate macro layouts must enter the same downstream stage with macros held consistently fixed. Keep technology files, clock constraints, utilization, standard-cell placement, buffering, CTS, router settings, and CPU count constant. Confirm that a later tool does not move macros and erase the refinement under test.

Report failed routing and timeouts rather than dropping them. If only a subset receives detailed routing, choose that subset before inspecting results and route the same number of preselected candidates for every method.

## Feasible role this semester

Use cheap incremental geometry objectives for RL interaction. Run global routing on fixed checkpoints and a small predetermined case set. Run detailed routing only after the interface works reliably. This design produces useful proxy-versus-routing analysis even if training fails to beat classical search.

No hardware-specific throughput or memory requirements have been established. A one-case pilot must determine the real cost before committing to the full experiment matrix.
