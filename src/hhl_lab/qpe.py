"""Quantum phase estimation helpers for the HHL circuit."""

from __future__ import annotations

from dataclasses import dataclass

from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT, UnitaryGate

from .matrices import HHLProblem, evolution_unitary, phase_from_eigenvalue


@dataclass(frozen=True)
class PhaseEncoding:
    """Known phase-encoding information for the canonical HHL instance."""

    eigenvalue: float
    phase: float
    clock_state: str


def default_phase_encodings(problem: HHLProblem) -> list[PhaseEncoding]:
    """Return the two exact clock-register encodings used in this project.

    The bitstrings follow the local control-qubit order used by Qiskit, so they
    are expressed in little-endian register order.
    """

    encodings: list[PhaseEncoding] = []
    for eigenvalue, clock_state in zip(problem.eigenvalues, ["10", "01"]):
        encodings.append(
            PhaseEncoding(
                eigenvalue=float(eigenvalue),
                phase=phase_from_eigenvalue(float(eigenvalue), problem.evolution_time),
                clock_state=clock_state,
            )
        )
    return encodings


def append_qpe(
    circuit: QuantumCircuit,
    clock_qubits: list[int],
    system_qubit: int,
    problem: HHLProblem,
) -> None:
    """Append a two-qubit phase estimation block for U = exp(iAt)."""

    for qubit in clock_qubits:
        circuit.h(qubit)

    for offset, clock_qubit in enumerate(clock_qubits):
        power = 2 ** (len(clock_qubits) - 1 - offset)
        gate = UnitaryGate(evolution_unitary(problem, power=power), label=f"U^{power}")
        circuit.append(gate.control(1), [clock_qubit, system_qubit])

    circuit.append(QFT(len(clock_qubits), inverse=True, do_swaps=False).to_gate(label="QFT†"), clock_qubits)


def append_inverse_qpe(
    circuit: QuantumCircuit,
    clock_qubits: list[int],
    system_qubit: int,
    problem: HHLProblem,
) -> None:
    """Append the inverse of the phase-estimation block."""

    qpe_block = QuantumCircuit(len(clock_qubits) + 1, name="QPE")
    local_clock = list(range(len(clock_qubits)))
    local_system = len(clock_qubits)
    append_qpe(qpe_block, local_clock, local_system, problem)
    circuit.append(qpe_block.inverse().to_gate(label="QPE†"), [*clock_qubits, system_qubit])
