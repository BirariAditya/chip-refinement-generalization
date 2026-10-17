# Mid-semester LaTeX report

Authors: Aditya Birari (2023A3PS0700P) and Pratyush Mohata (2023A3PS0690P), EEE Department.

The report follows the supplied article template. `main.sty` is copied unchanged. `main.tex` replaces the placeholder content and author fields and uses `references.bib` for topic-specific author-year citations. No slide deck is included.

The current document is a **mid-semester research proposal and progress report**. It focuses on problem understanding, literature, the selected congestion-aware/preference-conditioned refinement direction, a proposed formulation, and a concise preliminary-work summary. It does not present the full project as completed. Conditional PPO training, held-out evaluation, ablations and downstream routing/timing remain future work.

Detailed preliminary records stay outside the report: the original educational RL pilot is under `../prototype/results/`, congestion/preference smoke checks under `../prototype/multiobjective_results/`, and original-code component execution under `../reproduction/`. The report summarizes their status without lengthy benchmark tables, learning curves or engineering logs.

`report_standalone.tex` is the file open in the editor and was revised directly in place. Its compilation was checked with the editor's built-in compiler. `main.tex` contains the synchronized multi-file version. The existing PDF/ZIP under `output/` are the earlier report export; use the current editor preview for the revised text until a new export is requested.

## Compile

With Tectonic, from this directory:

```bash
mkdir output
tectonic --keep-intermediates --outdir output main.tex
```

With a conventional LaTeX installation:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

For Overleaf, upload the report source bundle and select `main.tex` as the main document. The bundle includes `main.sty`, `references.bib`, and the `generated/` LaTeX assets. No shell escape or external figure program is required to compile the saved report.

To regenerate the original numerical assets after a new prototype run, execute `python report/make_report_assets.py` from the repository root. Do not edit generated result values manually. Preserve direct edits in `report_standalone.tex`; the packaging script no longer overwrites the open editor source.

In the earlier extracted source ZIP, report files are at the top level alongside `prototype/`; regenerate assets there with `python make_report_assets.py`. To package a future requested export, first explicitly compile the synchronized multi-file source externally, then run `python report/package_report.py`. The script preserves the editor source.
