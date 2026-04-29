"""Regenerate all figures used in the README and theory notes."""

from __future__ import annotations

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

from hhl_lab.simulation import run_hhl_statevector
from hhl_lab.visualization import generate_all_figures


def main() -> None:
    result = run_hhl_statevector()
    output_dir = PROJECT_ROOT / "docs" / "figures"
    paths = generate_all_figures(result, output_dir)
    print("Generated figures:")
    for path in paths:
        print(path.relative_to(PROJECT_ROOT))


if __name__ == "__main__":
    main()
