"""Linear-algebra primitives for the fixed HHL problem instance."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.linalg import expm

from .encoding import normalize_vector


@dataclass(frozen=True)
class HHLProblem:
    """Container for the matrix, right-hand side, and simulation time."""

    matrix: np.ndarray
    rhs: np.ndarray
    evolution_time: float

    @property
    def normalized_rhs(self) -> np.ndarray:
        """Return the normalized state-preparation vector."""

        return normalize_vector(self.rhs)

    @property
    def eigenvalues(self) -> np.ndarray:
        """Return the eigenvalues of the Hermitian system matrix."""

        return np.linalg.eigvalsh(self.matrix)

    @property
    def spectral_decomposition(self) -> tuple[np.ndarray, np.ndarray]:
        """Return eigenvalues and orthonormal eigenvectors."""

        return np.linalg.eigh(self.matrix)


def default_problem() -> HHLProblem:
    """Return the canonical 2x2 Hermitian HHL example."""

    matrix = np.array([[1.0, -1.0 / 3.0], [-1.0 / 3.0, 1.0]], dtype=float)
    rhs = np.array([1.0, 0.0], dtype=float)
    evolution_time = 3.0 * np.pi / 4.0
    return HHLProblem(matrix=matrix, rhs=rhs, evolution_time=evolution_time)


def classical_solution(problem: HHLProblem) -> np.ndarray:
    """Solve the linear system classically."""

    return np.linalg.solve(problem.matrix, problem.rhs)


def normalized_classical_solution(problem: HHLProblem) -> np.ndarray:
    """Return the classical solution normalized as a quantum state."""

    return normalize_vector(classical_solution(problem))


def evolution_unitary(problem: HHLProblem, power: int = 1) -> np.ndarray:
    """Return exp(i A t 2^power_factor) for phase estimation."""

    if power < 1:
        raise ValueError("power must be at least 1.")
    return expm(1j * problem.matrix * problem.evolution_time * power)


def phase_from_eigenvalue(eigenvalue: float, evolution_time: float) -> float:
    """Map an eigenvalue to the corresponding phase-estimation fraction."""

    return (eigenvalue * evolution_time) / (2.0 * np.pi)
