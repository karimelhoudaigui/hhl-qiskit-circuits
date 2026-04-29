"""Statevector simulation helpers for the HHL project."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from qiskit.quantum_info import Statevector

from .hhl import HHLArtifacts, HHLConfiguration, build_hhl_circuit, extract_solution_vector
from .matrices import (
    HHLProblem,
    classical_solution,
    default_problem,
    normalized_classical_solution,
)


@dataclass(frozen=True)
class SimulationResult:
    """Collected outputs from the HHL statevector experiment."""

    artifacts: HHLArtifacts
    statevector: Statevector
    raw_solution_amplitudes: np.ndarray
    normalized_hhl_solution: np.ndarray
    classical_solution: np.ndarray
    normalized_classical_solution: np.ndarray
    success_probability: float


def run_hhl_statevector(
    problem: HHLProblem | None = None,
    configuration: HHLConfiguration | None = None,
) -> SimulationResult:
    """Build and simulate the HHL circuit, then recover the postselected solution."""

    problem = problem or default_problem()
    configuration = configuration or HHLConfiguration()
    artifacts = build_hhl_circuit(problem=problem, configuration=configuration)
    statevector = Statevector.from_instruction(artifacts.circuit)

    system_qubits = [artifacts.circuit.find_bit(artifacts.circuit.qregs[0][0]).index]
    clock_qubits = [artifacts.circuit.find_bit(qubit).index for qubit in artifacts.circuit.qregs[1]]
    ancilla_qubit = artifacts.circuit.find_bit(artifacts.circuit.qregs[2][0]).index

    raw_solution = extract_solution_vector(
        statevector=statevector,
        system_qubits=system_qubits,
        clock_qubits=clock_qubits,
        ancilla_qubit=ancilla_qubit,
    )
    success_probability = float(np.sum(np.abs(raw_solution) ** 2))
    normalized_hhl = raw_solution / np.sqrt(success_probability)

    return SimulationResult(
        artifacts=artifacts,
        statevector=statevector,
        raw_solution_amplitudes=raw_solution,
        normalized_hhl_solution=normalized_hhl,
        classical_solution=classical_solution(problem),
        normalized_classical_solution=normalized_classical_solution(problem),
        success_probability=success_probability,
    )
