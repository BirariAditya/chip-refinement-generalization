"""Illustrative, strictly legal greedy move. Not RL or a chip benchmark."""

from itertools import combinations


def hpwl(positions, nets):
    total = 0.0
    for net in nets:
        xs, ys = zip(*(positions[node] for node in net))
        total += max(xs) - min(xs) + max(ys) - min(ys)
    return total


def legal(positions, sizes, die=(10.0, 10.0)):
    # Center pins/coordinates and axis-aligned rectangles; no physical site/halo rules.
    rectangles = {}
    for node, (x, y) in positions.items():
        width, height = sizes[node]
        box = (x - width / 2, y - height / 2, x + width / 2, y + height / 2)
        if box[0] < 0 or box[1] < 0 or box[2] > die[0] or box[3] > die[1]:
            return False
        rectangles[node] = box
    for first, second in combinations(rectangles.values(), 2):
        if first[0] < second[2] and second[0] < first[2] and first[1] < second[3] and second[1] < first[3]:
            return False
    return True


def main():
    initial = {"A": (1.0, 1.0), "B": (8.0, 1.0), "C": (5.0, 5.0)}
    sizes = {node: (1.0, 1.0) for node in initial}
    nets = [("A", "B"), ("B", "C")]
    initial_cost = hpwl(initial, nets)
    assert legal(initial, sizes) and initial_cost == 14.0
    best, best_cost = initial.copy(), initial_cost
    for x in range(1, 10):
        for y in range(1, 10):
            candidate = dict(initial, B=(float(x), float(y)))
            if legal(candidate, sizes):
                cost = hpwl(candidate, nets)
                if cost < best_cost:
                    best, best_cost = candidate, cost
    assert best_cost == 8.0 and legal(best, sizes)
    assert not legal(dict(initial, B=initial["A"]), sizes)
    print("ILLUSTRATIVE TOY ONLY: not RL, not a real circuit, not PPA.")
    print(f"Initial center-pin HPWL: {initial_cost:g}")
    print(f"Greedy legal relocation of B: {initial['B']} -> {best['B']}")
    print(f"Final center-pin HPWL: {best_cost:g}")
    print(f"Undiscounted one-step cost-change reward: {initial_cost - best_cost:g}")
    print("Native MaskRegulate has different passwise legality; this toy does not reproduce it.")


if __name__ == "__main__":
    main()
