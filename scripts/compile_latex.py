"""Compile the HHL theory document if pdflatex is available."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
MPLCONFIGDIR = PROJECT_ROOT / ".mplconfig"
MPLCONFIGDIR.mkdir(exist_ok=True)
import os

os.environ.setdefault("MPLCONFIGDIR", str(MPLCONFIGDIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from hhl_lab.latex import theory_pdf_path


def main() -> int:
    pdflatex = shutil.which("pdflatex")
    if pdflatex is None:
        print("pdflatex was not found on PATH. Skipping PDF compilation.", file=sys.stderr)
        print("Install a LaTeX distribution and rerun scripts/compile_latex.py.", file=sys.stderr)
        return 1

    docs_dir = PROJECT_ROOT / "docs"
    tex_path = docs_dir / "theory.tex"
    command = [pdflatex, "-interaction=nonstopmode", tex_path.name]

    for _ in range(2):
        subprocess.run(command, cwd=docs_dir, check=True)

    print(f"Compiled PDF: {theory_pdf_path(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
