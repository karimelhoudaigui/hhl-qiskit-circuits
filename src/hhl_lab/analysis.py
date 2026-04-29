"""Numerical analysis helpers for interpreting the HHL experiment."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .encoding import int_to_bits, normalize_vector
from .matrices import HHLProblem, classical_solution, default_problem, phase_from_eigenvalue


@dataclass(frozen=True)
class SpectralSummary:
    """Spectral decomposition data used throughout the documentation."""

    eigenvalues: np.ndarray
    eigenvectors: np.ndarray
    eigenbasis_coefficients: np.ndarray


@dataclass(frozen=True)
class PrecisionSweepPoint:
    """Approximate HHL recovery obtained from discretized eigenphases."""

    precision_bits: int
    phase_bitstrings: list[str]
    encoded_phases: np.ndarray
    encoded_eigenvalues: np.ndarray
    normalized_solution: np.ndarray
    fidelity_with_classical: float
    l2_error: float
    is_exact_encoding: bool


def summarize_spectrum(problem: HHLProblem | None = None) -> SpectralSummary:
    """Return eigenpairs and the decomposition of |b> in the eigenbasis."""

    problem = problem or default_problem()
    eigenvalues, eigenvectors = problem.spectral_decomposition
    coefficients = eigenvectors.conj().T @ problem.normalized_rhs
    return SpectralSummary(
        eigenvalues=eigenvalues,
        eigenvectors=eigenvectors,
        eigenbasis_coefficients=coefficients,
    )


def state_fidelity(left: np.ndarray, right: np.ndarray) -> float:
    """Return the pure-state fidelity |<left|right>|^2."""

    left_state = normalize_vector(left)
    right_state = normalize_vector(right)
    overlap = np.vdot(left_state, right_state)
    return float(np.abs(overlap) ** 2)


def relative_solution_error(reference: np.ndarray, estimate: np.ndarray) -> float:
    """Return the Euclidean relative error between two vectors."""

    return float(np.linalg.norm(reference - estimate) / np.linalg.norm(reference))


def phase_bitstring(phase: float, precision_bits: int) -> str:
    """Encode a phase fraction onto a fixed-size register by nearest rounding."""

    scaled = int(np.round(phase * (2**precision_bits))) % (2**precision_bits)
    return int_to_bits(scaled, precision_bits)


def encoded_phase_from_bits(bitstring: str) -> float:
    """Recover the discretized phase associated with a binary string."""

    return int(bitstring, 2) / (2 ** len(bitstring))


def precision_sweep(
    precision_bits_range: range,
    problem: HHLProblem | None = None,
    inversion_scale: float = 2.0 / 3.0,
) -> list[PrecisionSweepPoint]:
    """Study how eigenphase discretization affects the recovered HHL direction."""

    problem = problem or default_problem()
    classical = normalize_vector(classical_solution(problem))
    spectrum = summarize_spectrum(problem)
    points: list[PrecisionSweepPoint] = []

    for precision_bits in precision_bits_range:
        phase_bitstrings = [
            phase_bitstring(phase_from_eigenvalue(float(eigenvalue), problem.evolution_time), precision_bits)
            for eigenvalue in spectrum.eigenvalues
        ]
        encoded_phases = np.array(
            [encoded_phase_from_bits(bitstring) for bitstring in phase_bitstrings],
            dtype=float,
        )
        encoded_eigenvalues = (2.0 * np.pi * encoded_phases) / problem.evolution_time

        recovered = np.zeros(problem.matrix.shape[0], dtype=complex)
        is_exact_encoding = np.allclose(encoded_eigenvalues, spectrum.eigenvalues)
        valid = np.all(encoded_eigenvalues > 0.0)

        if valid:
            for index, coefficient in enumerate(spectrum.eigenbasis_coefficients):
                recovered += (
                    coefficient
                    * (inversion_scale / encoded_eigenvalues[index])
                    * spectrum.eigenvectors[:, index]
                )
            normalized_solution = normalize_vector(recovered)
            fidelity = state_fidelity(normalized_solution, classical)
            l2_error = relative_solution_error(classical, normalized_solution)
        else:
            normalized_solution = np.full(problem.matrix.shape[0], np.nan, dtype=complex)
            fidelity = float("nan")
            l2_error = float("nan")

        points.append(
            PrecisionSweepPoint(
                precision_bits=precision_bits,
                phase_bitstrings=phase_bitstrings,
                encoded_phases=encoded_phases,
                encoded_eigenvalues=encoded_eigenvalues,
                normalized_solution=normalized_solution,
                fidelity_with_classical=fidelity,
                l2_error=l2_error,
                is_exact_encoding=is_exact_encoding,
            )
        )

    return points
