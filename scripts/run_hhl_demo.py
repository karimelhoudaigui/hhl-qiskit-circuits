"""Run the full HHL demonstration and save the project figures."""

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

import numpy as np

from hhl_lab.simulation import run_hhl_statevector
from hhl_lab.visualization import generate_all_figures


def main() -> None:
    result = run_hhl_statevector()
    figure_dir = PROJECT_ROOT / "docs" / "figures"
    generate_all_figures(result, figure_dir)

    np.set_printoptions(precision=6, suppress=True)

    print("=== HHL Algorithm Demo ===")
    print("Final statevector:")
    print(result.statevector.data)
    print()
    print("Classical solution A^-1 b:")
    print(result.classical_solution)
    print()
    print("Normalized classical solution:")
    print(result.normalized_classical_solution)
    print()
    print("Raw postselected HHL amplitudes:")
    print(result.raw_solution_amplitudes)
    print()
    print("Normalized HHL solution:")
    print(result.normalized_hhl_solution)
    print()
    print(f"Postselection success probability: {result.success_probability:.6f}")
    print(f"Figures saved under: {figure_dir}")


if __name__ == "__main__":
    main()
