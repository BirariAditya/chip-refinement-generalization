"""Create LaTeX tables/figures directly from recorded synthetic prototype runs."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = (ROOT / "prototype" / "results") if (ROOT / "prototype" / "results").exists() else (ROOT.parent / "prototype" / "results")
GEN = ROOT / "generated"
GEN.mkdir(exist_ok=True)
rows = list(csv.DictReader((RESULTS / "summary.csv").open(encoding="utf-8")))
metadata = json.loads((RESULTS / "metadata.json").read_text())
examples = json.loads((RESULTS / "example_layouts.json").read_text())
names = {"identity": "No refinement", "random": "Random masked", "greedy": "Greedy", "policy": "Learned policy"}
lines = []
for row in rows:
    init = "Uniform" if row["initializer"] == "uniform" else "Edge-biased"
    lines.append(f"{init} & {names[row['method']]} & {float(row['mean_gain_percent']):.2f} & {float(row['mean_terminal_gain_percent']):.2f} & {100*float(row['harmful_terminal_fraction']):.1f} \\\\")
(GEN / "results_rows.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
table = [r"\begin{tabular}{@{}llrrr@{}}", r"\toprule",
         r"Test starts & Method & Selected gain (\%) & Terminal gain (\%) & Harm (\%)\\",
         r"\midrule"] + lines + [r"\bottomrule", r"\end{tabular}"]
(GEN / "results_table.tex").write_text("\n".join(table) + "\n", encoding="utf-8")

def select(initializer, method):
    return next(r for r in rows if r["initializer"] == initializer and r["method"] == method)

values = {
    "UniformPolicyGain": select("uniform", "policy")["mean_gain_percent"],
    "UniformGreedyGain": select("uniform", "greedy")["mean_gain_percent"],
    "EdgePolicyGain": select("edge_biased", "policy")["mean_gain_percent"],
    "EdgeGreedyGain": select("edge_biased", "greedy")["mean_gain_percent"],
    "TotalTrainingSeconds": sum(r["training_seconds"] for r in metadata["training"]),
}
(GEN / "metrics.tex").write_text("\n".join(f"\\newcommand{{\\{key}}}{{{float(value):.2f}}}" for key, value in values.items()) + "\n")

initial = next(e for e in examples if e["method"] == "identity")
greedy = next(e for e in examples if e["method"] == "greedy")
policy = next(e for e in examples if e["method"] == "policy" and e["policy_seed"] == 17)
parts = []
for label, example in (("Initial", initial), ("Greedy", greedy), ("Learned policy", policy)):
    parts.append(r"\begin{minipage}[t]{0.32\linewidth}\centering")
    parts.append(r"\begin{tikzpicture}[x=0.135in,y=0.135in,font=\scriptsize]")
    parts.append(r"\draw[step=1,gray!18,very thin] (0,0) grid (10,10);")
    parts.append(r"\draw[thick] (0,0) rectangle (10,10);")
    parts.append(r"\filldraw[fill=gray!45,draw=gray] (4,4) rectangle (6,6);")
    parts.append(r"\node[font=\tiny] at (5,5) {blocked};")
    parts.append(r"\fill (0,5) circle (2pt); \fill (10,5) circle (2pt);")
    for i, ((x, y), (w, h)) in enumerate(zip(example["selected_positions"], example["sizes"])):
        parts.append(f"\\filldraw[fill=blue!18,draw=blue!60!black] ({x},{y}) rectangle ({x+w},{y+h});")
        parts.append(f"\\node at ({x+w/2},{y+h/2}) {{{chr(65+i)}}};")
    parts.append(r"\end{tikzpicture}\\")
    parts.append(f"{label}: $H={example['selected_hpwl']:.1f}$")
    parts.append(r"\end{minipage}")
(GEN / "layouts.tex").write_text("\n".join(parts), encoding="utf-8")

curve = list(csv.DictReader((RESULTS / "learning_curve.csv").open()))
plot = [r"\begin{tikzpicture}", r"\begin{axis}[width=0.8\linewidth,height=1.8in,xlabel={Training episode},ylabel={Validation HPWL gain (\%)},xmin=0,xmax=600,ymin=0,ymax=65,grid=major,legend style={font=\scriptsize,at={(1.02,1)},anchor=north west},tick label style={font=\scriptsize},label style={font=\small}]"]
for seed, color in ((17, "blue"), (29, "red!70!black"), (43, "green!50!black")):
    values = [(r["episode"], r["validation_gain"]) for r in curve if int(r["seed"]) == seed]
    coords = " ".join(f"({x},{float(y):.4f})" for x, y in values)
    plot.append(f"\\addplot[color={color},mark=*,mark size=1.1pt] coordinates {{{coords}}};")
    plot.append(f"\\addlegendentry{{Seed {seed}}}")
plot += [r"\end{axis}", r"\end{tikzpicture}"]
(GEN / "learning_curve.tex").write_text("\n".join(plot), encoding="utf-8")
print("Generated results table, numeric macros, layout figure and validation curves from saved runs.")
