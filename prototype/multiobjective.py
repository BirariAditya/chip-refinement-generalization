"""Initial congestion/Pareto utilities and a greedy control, not conditioned PPO."""
import argparse
import csv
import json
import time
from pathlib import Path

import numpy as np
from placement_rl import Circuit, Environment, initial_layout


def regularity(circuit, positions):
    """Rectangle boundary-distance proxy; not an exact native-mask reproduction."""
    slack = np.array([circuit.width, circuit.height]) - circuit.sizes - positions
    return float(np.minimum(positions, slack).sum())


def rudy_map(circuit, positions, bins=10, minimum_span=0.5):
    """Bin-average bbox routing demand (length/area), with unit demand per net.

    Degenerate bboxes are widened symmetrically then clipped to the canvas.
    This is a declared RUDY-style estimator, not calibrated routing overflow.
    Net importance weights used by HPWL are not physical routing multiplicities.
    """
    pins = circuit.pins(positions)
    axis_x = np.linspace(0, circuit.width, bins + 1)
    axis_y = np.linspace(0, circuit.height, bins + 1)
    density = np.zeros((bins, bins))
    bin_area = circuit.width * circuit.height / bins**2
    for net in circuit.nets:
        lower, upper = pins[net].min(axis=0), pins[net].max(axis=0)
        length = float((upper - lower).sum())
        if length == 0:
            continue
        center = (lower + upper) / 2
        span = np.maximum(upper - lower, minimum_span)
        lower = np.maximum(center - span / 2, [0, 0])
        upper = np.minimum(center + span / 2, [circuit.width, circuit.height])
        area = float(np.prod(upper - lower))
        overlap_x = np.maximum(0, np.minimum(axis_x[1:], upper[0]) - np.maximum(axis_x[:-1], lower[0]))
        overlap_y = np.maximum(0, np.minimum(axis_y[1:], upper[1]) - np.maximum(axis_y[:-1], lower[1]))
        density += (length / area) * np.outer(overlap_x, overlap_y) / bin_area
    return density


def congestion(circuit, positions, top_fraction=0.1):
    demand = rudy_map(circuit, positions).ravel()
    count = max(1, int(np.ceil(top_fraction * len(demand))))
    return float(np.sort(demand)[-count:].mean())


def objectives(circuit, positions):
    # All three objectives are minimized: HPWL, regularity, top-decile demand.
    return np.array([circuit.hpwl(positions), regularity(circuit, positions), congestion(circuit, positions)])


def nondominated(values):
    """Exact minimization dominance; return one representative for duplicates."""
    values = np.asarray(values, dtype=float)
    keep = []
    for i, value in enumerate(values):
        dominated = np.any(np.all(values <= value, axis=1) & np.any(values < value, axis=1))
        duplicate = any(np.array_equal(value, values[j]) for j in keep)
        if not dominated and not duplicate:
            keep.append(i)
    return keep


def greedy(circuit, start, preference):
    env = Environment(circuit, start)
    scale = np.maximum(objectives(circuit, start), [1.0, 1.0, 0.01])
    preference = np.asarray(preference, dtype=float)
    assert np.all(preference >= 0) and np.isclose(preference.sum(), 1)
    initial_cost = float(preference @ (objectives(circuit, start) / scale))
    best, best_cost = start.copy(), initial_cost
    reward_sum = 0.0
    previous = initial_cost
    evaluations = 0
    for t in range(env.horizon):
        macro = t % len(start)
        sites = env.grid[env.legal_mask(macro)]
        candidate_positions = []
        costs = []
        for site in sites:
            candidate = env.positions.copy()
            candidate[macro] = site
            candidate_positions.append(candidate)
            costs.append(float(preference @ (objectives(circuit, candidate) / scale)))
        evaluations += len(sites)
        index = int(np.argmin(costs))
        env.positions = candidate_positions[index]
        reward_sum += previous - costs[index]
        previous = costs[index]
        assert env.is_legal(env.positions)
        if previous < best_cost:
            best, best_cost = env.positions.copy(), previous
    assert np.isclose(reward_sum, initial_cost - previous)
    return objectives(circuit, best), best, evaluations


def verify():
    circuit = Circuit.synthetic(301)
    start = initial_layout(circuit, 8001, "uniform")
    demand = rudy_map(circuit, start)
    pins = circuit.pins(start)
    unweighted_hpwl = sum(np.ptp(pins[net], axis=0).sum() for net in circuit.nets)
    # Every bbox's demand integrates to its length, even after degeneracy handling.
    assert np.isclose(demand.sum() * circuit.width * circuit.height / demand.size, unweighted_hpwl)
    assert np.isfinite(demand).all() and np.all(demand >= 0)
    assert congestion(circuit, start) >= demand.mean()
    assert nondominated([[1, 3], [2, 2], [3, 1], [4, 4], [1, 3]]) == [0, 1, 2]
    assert np.isfinite(objectives(circuit, start)).all()
    horizontal = Circuit.synthetic(301)
    horizontal.nets = [[6, 7]]
    horizontal.weights = np.array([1.0])
    # The fixed terminals form a zero-height, ten-unit horizontal net.
    assert np.isclose(rudy_map(horizontal, start).sum(), 10.0)
    horizontal.nets = [[6, 6]]
    assert np.array_equal(rudy_map(horizontal, start), np.zeros((10, 10)))
    return {"demand_integral_matches_unweighted_hpwl": True, "nonnegative_finite_demand": True,
            "dominance_and_duplicate_check": True, "degenerate_and_zero_length_net_check": True,
            "reward_telescoping_checked_per_rollout": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(Path(__file__).parent / "multiobjective_results"))
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    checks = verify()
    preferences = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (0.5, 0, 0.5), (0.5, 0.5, 0), (1/3, 1/3, 1/3)]
    rows = []
    cases = []
    started = time.perf_counter()
    for seed in (301, 302, 303, 304):
        circuit = Circuit.synthetic(seed)
        for start_seed in (8001, 8002):
            start = initial_layout(circuit, start_seed, "uniform")
            candidates = [objectives(circuit, start)]
            case_rows = []
            for index, preference in enumerate(preferences):
                values, final, evaluations = greedy(circuit, start, preference)
                candidates.append(values)
                case_rows.append({"netlist_seed": seed, "start_seed": start_seed, "preference_index": index,
                                  "w_hpwl": preference[0], "w_regularity": preference[1], "w_congestion": preference[2],
                                  "hpwl": values[0], "regularity": values[1], "top_decile_rudy": values[2],
                                  "objective_evaluations": evaluations, "geometrically_legal": True})
            selected = nondominated(candidates)
            for i, row in enumerate(case_rows):
                row["nondominated_in_sample"] = i + 1 in selected
            rows.extend(case_rows)
            cases.append({"netlist_seed": seed, "start_seed": start_seed, "initial_objectives": candidates[0].tolist(),
                          "sampled_unique_nondominated_count_including_initial": len(selected)})
    with (output / "preference_sweep.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    metadata = {"status": "measured_synthetic_objective_and_greedy_smoke_not_conditioned_PPO",
                "objective_order": ["weighted_center_pin_hpwl", "rectangle_boundary_distance", "top_decile_rudy_demand"],
                "cases": cases, "checks": checks, "seconds": time.perf_counter() - started,
                "limitations": ["no routing capacity, obstacles or layers in RUDY", "no timing information",
                                "no PPO or learned preference conditioning", "no claim of complete Pareto frontier",
                                "six separate greedy runs; not a matched-budget model comparison"]}
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps({"rows": len(rows), "cases": len(cases), "checks": checks, "seconds": metadata["seconds"]}))


if __name__ == "__main__":
    main()
