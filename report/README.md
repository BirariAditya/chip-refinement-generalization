# Mid-semester LaTeX report

Authors: Aditya Birari (2023A3PS0700P) and Pratyush Mohata (2023A3PS0690P), EEE Department.

The report follows the supplied article template. `main.sty` is copied unchanged. `main.tex` replaces the placeholder content and author fields and uses `references.bib` for topic-specific author-year citations. No slide deck is included.

The report emphasizes problem understanding, literature synthesis, the refinement MDP, the proposed research direction, and an initial synthetic implementation. All numerical pilot tables and figures are generated from the recorded results under `../prototype/results/`. Real-circuit PPO, mixed-start/scaling ablations, diffusion integration, routing and PPA remain future work.

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

To regenerate numerical assets after a new prototype run, execute `python report/make_report_assets.py` from the repository root. Do not edit the generated result values manually. A generated standalone source is provided for the in-app LaTeX preview; edit `main.tex` for the multi-file project and regenerate the standalone after changes.

In the extracted source ZIP, the report files are at the top level alongside `prototype/`; regenerate assets there with `python make_report_assets.py`. The saved assets already suffice to compile the report. In the repository, run `python report/package_report.py` after compilation to rebuild the standalone snapshot and source ZIP.
