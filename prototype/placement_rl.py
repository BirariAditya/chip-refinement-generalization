"""Small synthetic placement/REINFORCE scaffold; not MaskRegulate or real EDA."""
import argparse
import csv
import json
import platform
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class Circuit:
    seed: int
    sizes: np.ndarray
    nets: list
    weights: np.ndarray
    width: int = 10
    height: int = 10

    @classmethod
    def synthetic(cls, seed):
        rng = np.random.default_rng(seed)
        sizes = np.array([[1, 1], [2, 1], [1, 2], [1, 1], [2, 1], [1, 2]], dtype=float)
        rng.shuffle(sizes)
        # Six macro nodes and two fixed port nodes; independent seeded netlists.
        nets = [rng.choice(8, size=int(rng.integers(2, 4)), replace=False).tolist() for _ in range(10)]
        for node in range(6):
            if not any(node in net for net in nets):
                nets.append([node, 6 + node % 2])
        return cls(seed, sizes, nets, rng.integers(1, 3, size=len(nets)).astype(float))

    def pins(self, positions):
        return np.vstack([positions + self.sizes / 2, [[0, 5], [10, 5]]])

    def hpwl(self, positions):
        pins = self.pins(positions)
        return float(sum(w * np.ptp(pins[net], axis=0).sum() for w, net in zip(self.weights, self.nets)))


class Environment:
    """Every step preserves rectangle legality; this differs from native pass masks."""
    def __init__(self, circuit, initial, passes=2):
        self.circuit = circuit
        self.positions = np.array(initial, dtype=float).copy()
        self.initial = self.positions.copy()
        self.reference = circuit.hpwl(self.positions)
        self.cost = self.reference
        self.horizon = passes * len(self.positions)
        self.step_index = 0
        self.grid = np.array([(x, y) for x in range(10) for y in range(10)], dtype=float)
        self.objective_evaluations = 0
        assert self.is_legal(self.positions)

    def legal_mask(self, macro, positions=None):
        pos = self.positions if positions is None else positions
        size = self.circuit.sizes[macro]
        upper = self.grid + size
        valid = (upper[:, 0] <= 10) & (upper[:, 1] <= 10)
        for other, p in enumerate(pos):
            if other == macro or np.isnan(p).any():
                continue
            other_upper = p + self.circuit.sizes[other]
            overlap = np.all(self.grid < other_upper, axis=1) & np.all(upper > p, axis=1)
            valid &= ~overlap
        # A fixed central blockage, identical across all synthetic designs.
        valid &= ~(np.all(self.grid < [6, 6], axis=1) & np.all(upper > [4, 4], axis=1))
        return valid

    def is_legal(self, positions):
        for i, p in enumerate(positions):
            if np.isnan(p).any() or np.any(p < 0) or np.any(p + self.circuit.sizes[i] > [10, 10]):
                return False
            match = np.all(self.grid == p, axis=1)
            if not np.any(match & self.legal_mask(i, positions)):
                return False
        return True

    def candidates(self):
        i = self.step_index % len(self.positions)
        sites = self.grid[self.legal_mask(i)]
        pins = self.circuit.pins(self.positions)
        costs = np.zeros(len(sites))
        for weight, net in zip(self.circuit.weights, self.circuit.nets):
            if i not in net:
                costs += weight * np.ptp(pins[net], axis=0).sum()
            else:
                other = [node for node in net if node != i]
                lower, upper = pins[other].min(axis=0), pins[other].max(axis=0)
                moving = sites + self.circuit.sizes[i] / 2
                costs += weight * (np.maximum(upper, moving) - np.minimum(lower, moving)).sum(axis=1)
        self.objective_evaluations += len(sites)
        gain = (self.cost - costs) / max(self.reference, 1.0)
        distance = np.abs(sites - self.positions[i]).sum(axis=1) / 20.0
        centers = sites + self.circuit.sizes[i] / 2
        boundary = np.minimum(centers, 10 - centers).sum(axis=1) / 10.0
        remaining = 1 - self.step_index / self.horizon
        features = np.column_stack([10 * gain, -distance, -boundary, 10 * gain * remaining, -(distance ** 2)])
        return sites, costs, features

    def step(self, site, cost):
        reward = (self.cost - float(cost)) / max(self.reference, 1.0)
        self.positions[self.step_index % len(self.positions)] = site
        self.cost = float(cost)
        self.step_index += 1
        return reward


def initial_layout(circuit, seed, initializer):
    rng = np.random.default_rng(seed)
    env = object.__new__(Environment)
    env.circuit = circuit
    env.grid = np.array([(x, y) for x in range(10) for y in range(10)], dtype=float)
    env.positions = np.full((6, 2), np.nan)
    for i in range(6):
        sites = env.grid[env.legal_mask(i)]
        if initializer == "uniform":
            index = rng.integers(len(sites))
        elif initializer == "edge_biased":
            centers = sites + circuit.sizes[i] / 2
            proximity = np.minimum(centers, 10 - centers).min(axis=1)
            probability = np.exp(-2.0 * proximity)
            index = rng.choice(len(sites), p=probability / probability.sum())
        else:
            raise ValueError(initializer)
        env.positions[i] = sites[index]
    return env.positions.copy()


def probabilities(features, theta):
    logits = features @ theta
    logits -= logits.max()
    p = np.exp(logits)
    return p / p.sum()


def rollout(circuit, start, method, theta=None, seed=0, train=False):
    rng = np.random.default_rng(seed)
    env = Environment(circuit, start)
    history, rewards, scores = [env.cost], [], []
    best_cost, best = env.cost, env.positions.copy()
    start_time = time.perf_counter()
    if method != "identity":
        for _ in range(env.horizon):
            sites, costs, features = env.candidates()
            if method == "random":
                action = int(rng.integers(len(sites)))
            elif method == "greedy":
                action = int(np.argmin(costs))
            elif method == "policy":
                p = probabilities(features, theta)
                action = int(rng.choice(len(sites), p=p)) if train else int(np.argmax(p))
                scores.append(features[action] - p @ features)
            else:
                raise ValueError(method)
            rewards.append(env.step(sites[action], costs[action]))
            assert env.is_legal(env.positions)
            history.append(env.cost)
            if env.cost < best_cost:
                best_cost, best = env.cost, env.positions.copy()
    elapsed = time.perf_counter() - start_time
    return {"initial_hpwl": env.reference, "terminal_hpwl": env.cost,
            "selected_hpwl": best_cost, "gain_percent": 100 * (env.reference - best_cost) / env.reference,
            "terminal_gain_percent": 100 * (env.reference - env.cost) / env.reference,
            "legal": env.is_legal(best), "objective_evaluations": env.objective_evaluations,
            "seconds": elapsed, "history": history, "initial_positions": start.tolist(),
            "selected_positions": best.tolist()}, np.array(rewards), np.array(scores)


def validation_score(theta, circuits):
    return float(np.mean([rollout(c, initial_layout(c, 7000 + j, "uniform"), "policy", theta)[0]["gain_percent"]
                          for c in circuits for j in range(2)]))


def train_policy(seed, episodes, train_circuits, validation):
    rng = np.random.default_rng(seed)
    theta = rng.normal(0, 0.01, 5)
    baseline = np.zeros(12)
    batch = np.zeros(5)
    best_score = validation_score(theta, validation)
    best_theta, chosen_episode = theta.copy(), 0
    log = [{"seed": seed, "episode": 0, "validation_gain": best_score}]
    begin = time.perf_counter()
    for episode in range(1, episodes + 1):
        circuit = train_circuits[int(rng.integers(len(train_circuits)))]
        start = initial_layout(circuit, int(rng.integers(1_000_000)), "uniform")
        _, rewards, score = rollout(circuit, start, "policy", theta, int(rng.integers(1_000_000)), True)
        returns = np.cumsum(rewards[::-1])[::-1]  # gamma=1; undiscounted finite horizon.
        batch += ((returns - baseline)[:, None] * score).sum(axis=0)
        baseline = 0.95 * baseline + 0.05 * returns
        if episode % 10 == 0:
            gradient = batch / 10
            norm = np.linalg.norm(gradient)
            theta += 0.12 * gradient / max(1.0, norm / 5.0)
            batch[:] = 0
        if episode % 100 == 0 or episode == episodes:
            value = validation_score(theta, validation)
            log.append({"seed": seed, "episode": episode, "validation_gain": value})
            if value > best_score:
                best_score, best_theta, chosen_episode = value, theta.copy(), episode
    return best_theta, log, {"seed": seed, "training_seconds": time.perf_counter() - begin,
                             "selected_episode": chosen_episode, "validation_gain": best_score,
                             "theta": best_theta.tolist(), "episodes": episodes}


def verify_environment():
    circuit = Circuit.synthetic(101)
    env = Environment(circuit, initial_layout(circuit, 1, "uniform"))
    sites, costs, _ = env.candidates()
    for site, cost in zip(sites, costs):
        candidate = env.positions.copy(); candidate[0] = site
        assert np.isclose(cost, circuit.hpwl(candidate))
        assert env.is_legal(candidate)
    duplicate = env.positions.copy(); duplicate[1] = duplicate[0]
    assert not env.is_legal(duplicate)
    outside = env.positions.copy(); outside[0] = [-1, 0]
    assert not env.is_legal(outside)
    result, reward, _ = rollout(circuit, env.positions, "random", seed=3)
    assert np.isclose(reward.sum(), (result["initial_hpwl"] - result["terminal_hpwl"]) / result["initial_hpwl"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=600)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "results")
    args = parser.parse_args()
    verify_environment()
    args.output.mkdir(parents=True, exist_ok=True)
    splits = {"train": list(range(101, 109)), "validation": [201, 202], "test": [301, 302, 303, 304]}
    train = [Circuit.synthetic(seed) for seed in splits["train"]]
    validation = [Circuit.synthetic(seed) for seed in splits["validation"]]
    policy_records, logs, training = [], [], []
    for seed in (17, 29, 43):
        theta, log, info = train_policy(seed, args.episodes, train, validation)
        policy_records.append((seed, theta)); logs.extend(log); training.append(info)
        print(f"seed={seed} selected_episode={info['selected_episode']} validation_gain={info['validation_gain']:.3f}%", flush=True)
    # Only now evaluate final test designs. No checkpoint selected using test results.
    rows, examples = [], []
    for initializer in ("uniform", "edge_biased"):
        for circuit_seed in splits["test"]:
            circuit = Circuit.synthetic(circuit_seed)
            for start_seed in (8001, 8002):
                start = initial_layout(circuit, start_seed, initializer)
                methods = [(m, None, 0) for m in ("identity", "random", "greedy")]
                methods += [("policy", theta, seed) for seed, theta in policy_records]
                for method, theta, policy_seed in methods:
                    result, _, _ = rollout(circuit, start, method, theta, start_seed)
                    if initializer == "edge_biased" and circuit_seed == 301 and start_seed == 8001:
                        examples.append({"method": method, "policy_seed": policy_seed, "sizes": circuit.sizes.tolist(),
                                         "nets": circuit.nets, **result})
                    rows.append({"circuit": circuit_seed, "initializer": initializer, "start_seed": start_seed,
                                 "method": method, "policy_seed": policy_seed,
                                 **{k: v for k, v in result.items() if k not in ("history", "initial_positions", "selected_positions")}})
    summary = []
    for initializer in ("uniform", "edge_biased"):
        for method in ("identity", "random", "greedy", "policy"):
            selected = [r for r in rows if r["initializer"] == initializer and r["method"] == method]
            by_circuit = [np.mean([r["gain_percent"] for r in selected if r["circuit"] == c]) for c in splits["test"]]
            summary.append({"initializer": initializer, "method": method, "runs": len(selected),
                            "independent_synthetic_circuits": 4, "mean_gain_percent": float(np.mean(by_circuit)),
                            "min_circuit_gain_percent": float(np.min(by_circuit)),
                            "mean_terminal_gain_percent": float(np.mean([r["terminal_gain_percent"] for r in selected])),
                            "harmful_terminal_fraction": float(np.mean([r["terminal_gain_percent"] < -1e-8 for r in selected])),
                            "legal_fraction": float(np.mean([r["legal"] for r in selected])),
                            "mean_objective_evaluations": float(np.mean([r["objective_evaluations"] for r in selected])),
                            "mean_seconds": float(np.mean([r["seconds"] for r in selected]))})
    for filename, content in (("runs.csv", rows), ("summary.csv", summary), ("learning_curve.csv", logs)):
        with (args.output / filename).open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=list(content[0])); writer.writeheader(); writer.writerows(content)
    metadata = {"status": "measured_synthetic_prototype_not_real_circuit_evidence", "splits": splits,
                "train_initializer": "uniform", "test_initializers": ["uniform", "edge_biased"],
                "algorithm": "linear masked REINFORCE, gamma=1, lagged per-step EMA baseline",
                "candidate_features": ["10*normalized_HPWL_gain", "negative_displacement", "negative_boundary_distance", "gain_times_remaining_horizon", "negative_squared_displacement"],
                "checkpoint_rule": "highest_uniform_validation_gain; earliest_tie", "passes": 2,
                "selection_rule": "best_feasible_incumbent_including_initial_for_all_methods",
                "budget_rule": "12_decisions_not_equal_objective_calls_or_wall_time",
                "python": platform.python_version(), "numpy": np.__version__, "platform": platform.platform(),
                "training": training, "environment_checks": "passed"}
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (args.output / "example_layouts.json").write_text(json.dumps(examples, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
