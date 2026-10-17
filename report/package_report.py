"""Package the compiled report and create a self-contained LaTeX snapshot."""
from pathlib import Path
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
source = (ROOT / "main.tex").read_text(encoding="utf-8")
style = (ROOT / "main.sty").read_text(encoding="utf-8")
for command in (r"\NeedsTeXFormat{LaTeX2e}", r"\ProcessOptions\relax", r"\endinput"):
    style = style.replace(command, "")
source = source.replace(r"\usepackage{main}", "\\makeatletter\n" + style + "\n\\makeatother")
source = re.sub(r"\\input\{([^}]+)\}", lambda m: (ROOT / (m[1] + ".tex")).read_text(encoding="utf-8"), source)
source = source.replace(r"\bibliographystyle{apalike}", "")
source = source.replace(r"\bibliography{references}", (OUT / "main.bbl").read_text(encoding="utf-8"))
standalone = ROOT / "report_standalone.tex"
standalone.write_text("% Generated snapshot. Edit main.tex and regenerate after compilation.\n" + source, encoding="utf-8")
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
