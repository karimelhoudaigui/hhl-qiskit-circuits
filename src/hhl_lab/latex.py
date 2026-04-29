"""Helpers for documenting the HHL experiment in LaTeX."""

from __future__ import annotations

from pathlib import Path

from .simulation import SimulationResult


def build_results_snippet(result: SimulationResult) -> str:
    """Return a compact LaTeX snippet summarizing the numerical results."""

    classical = result.classical_solution
    hhl = result.normalized_hhl_solution
    return rf"""
\[
x = A^{{-1}}b =
\begin{{bmatrix}}
{classical[0]:.6f} \\
{classical[1]:.6f}
\end{{bmatrix}},
\qquad
\lvert x \rangle_{{\mathrm{{HHL}}}} =
\begin{{bmatrix}}
{hhl[0].real:.6f} \\
{hhl[1].real:.6f}
\end{{bmatrix}}.
\]
"""


def theory_pdf_path(project_root: str | Path) -> Path:
    """Return the expected PDF output path."""

    return Path(project_root) / "docs" / "theory.pdf"
