"""Run the full HHL demonstration, print numerical diagnostics, and save figures."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
MPLCONFIGDIR = PROJECT_ROOT / ".mplconfig"
MPLCONFIGDIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPLCONFIGDIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import numpy as np

from hhl_lab.analysis import precision_sweep, summarize_spectrum
from hhl_lab.simulation import run_hhl_statevector
from hhl_lab.visualization import generate_all_figures


def build_parser() -> argparse.ArgumentParser:
    """Return the command-line parser for the HHL demo."""

    parser = argparse.ArgumentParser(
        description="Run the educational HHL statevector demo and export portfolio figures."
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "docs" / "figures"),
        help="Directory used for generated figure assets.",
    )
    parser.add_argument(
        "--precision-max-bits",
        type=int,
        default=6,
        help="Largest phase-register precision included in the discretization study.",
    )
    parser.add_argument(
        "--skip-figures",
        action="store_true",
        help="Do not regenerate figure assets.",
    )
    parser.add_argument(
        "--hide-statevector",
        action="store_true",
        help="Suppress printing the full final statevector.",
    )
    parser.add_argument(
        "--save-json",
        type=str,
        default="",
        help="Optional path to store a JSON summary of the experiment.",
    )
    return parser


def precision_table(max_bits: int) -> list[dict[str, object]]:
    """Return precision-scan metrics in a serializable form."""

    rows: list[dict[str, object]] = []
    for point in precision_sweep(range(1, max_bits + 1)):
        rows.append(
            {
                "bits": point.precision_bits,
                "bitstrings": point.phase_bitstrings,
                "encoded_eigenvalues": [float(value) for value in point.encoded_eigenvalues],
                "fidelity": None if np.isnan(point.fidelity_with_classical) else point.fidelity_with_classical,
                "relative_l2_error": None if np.isnan(point.l2_error) else point.l2_error,
                "exact_encoding": point.is_exact_encoding,
            }
        )
    return rows


def print_precision_table(rows: list[dict[str, object]]) -> None:
    """Pretty-print the precision study to stdout."""

    print("Precision sweep")
    print("bits | encoded states | fidelity | rel. L2 error | exact")
    print("---- | -------------- | -------- | -------------- | -----")
    for row in rows:
        fidelity = "undefined" if row["fidelity"] is None else f"{row['fidelity']:.6f}"
        rel_error = "undefined" if row["relative_l2_error"] is None else f"{row['relative_l2_error']:.6f}"
        print(
            f"{row['bits']:>4} | "
            f"{','.join(row['bitstrings']):<14} | "
            f"{fidelity:<8} | "
            f"{rel_error:<14} | "
            f"{row['exact_encoding']}"
        )


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    result = run_hhl_statevector()
    spectrum = summarize_spectrum(result.artifacts.problem)
    rows = precision_table(args.precision_max_bits)

    if not args.skip_figures:
        generate_all_figures(result, Path(args.output_dir))

    np.set_printoptions(precision=6, suppress=True)
    print("=== HHL Algorithm Demo ===")
    print("Problem matrix A:")
    print(result.artifacts.problem.matrix)
    print()
    print("Right-hand side b:")
    print(result.artifacts.problem.rhs)
    print()
    print("Eigenvalues of A:")
    print(spectrum.eigenvalues)
    print()
    print("Eigenbasis coefficients of |b>:")
    print(spectrum.eigenbasis_coefficients)
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
    print(f"State fidelity with normalized classical solution: {result.fidelity_with_classical:.6f}")
    print(f"Relative L2 error: {result.relative_error:.6e}")
    print()
    if not args.hide_statevector:
        print("Final statevector:")
        print(result.statevector.data)
        print()
    print_precision_table(rows)

    if not args.skip_figures:
        print()
        print(f"Figures saved under: {Path(args.output_dir)}")

    if args.save_json:
        payload = {
            "classical_solution": result.classical_solution.real.tolist(),
            "normalized_classical_solution": result.normalized_classical_solution.real.tolist(),
            "normalized_hhl_solution": result.normalized_hhl_solution.real.tolist(),
            "success_probability": result.success_probability,
            "fidelity_with_classical": result.fidelity_with_classical,
            "relative_error": result.relative_error,
            "precision_sweep": rows,
        }
        output_path = Path(args.save_json)
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"JSON summary written to: {output_path}")


if __name__ == "__main__":
    main()
