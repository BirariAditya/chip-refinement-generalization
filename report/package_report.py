"""Package an externally compiled multi-file report; preserve open editor edits.

The current report_standalone.tex is edited directly. This script never replaces it.
Compile main.tex externally only when explicitly desired before running packaging.
"""
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
standalone = ROOT / "report_standalone.tex"
assert standalone.is_file(), "The directly edited standalone report must exist."
pdf = OUT / "Midsem_RL_Chip_Placement_Report.pdf"
shutil.copyfile(OUT / "main.pdf", pdf)
archive = OUT / "Midsem_RL_Chip_Placement_Source.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
    for name in ("main.tex", "main.sty", "references.bib", "report_standalone.tex", "make_report_assets.py", "README.md"):
        bundle.write(ROOT / name, name)
    for path in sorted((ROOT / "generated").glob("*.tex")):
        bundle.write(path, path.relative_to(ROOT))
    for path in sorted((ROOT.parent / "prototype").rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            bundle.write(path, path.relative_to(ROOT.parent))
with zipfile.ZipFile(archive) as bundle:
    assert bundle.testzip() is None
    assert "main.tex" in bundle.namelist()
print(pdf)
print(archive)
print(standalone)
