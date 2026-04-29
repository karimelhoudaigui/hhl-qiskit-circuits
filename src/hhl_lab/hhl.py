"""Circuit construction and solution extraction for the HHL workflow."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Statevector

from .encoding import little_endian_bits, normalize_vector
from .inversion import InversionStep, append_inversion_oracle
from .matrices import HHLProblem, default_problem
from .qpe import append_inverse_qpe, append_qpe, default_phase_encodings


@dataclass(frozen=True)
class HHLConfiguration:
    """Configuration for the small HHL demonstration."""

    num_clock_qubits: int = 2
    inversion_scale: float = 2.0 / 3.0


@dataclass(frozen=True)
class HHLArtifacts:
    """Structured outputs returned alongside the constructed HHL circuit."""

    problem: HHLProblem
    configuration: HHLConfiguration
    circuit: QuantumCircuit
    phase_bitstrings: list[str]
    inversion_steps: list[InversionStep]


def build_hhl_circuit(
    problem: HHLProblem | None = None,
    configuration: HHLConfiguration | None = None,
) -> HHLArtifacts:
    """Build the full HHL circuit for the canonical one-qubit linear system."""

    problem = problem or default_problem()
    configuration = configuration or HHLConfiguration()

    system = QuantumRegister(1, "sys")
    clock = QuantumRegister(configuration.num_clock_qubits, "clk")
    ancilla = QuantumRegister(1, "anc")
    circuit = QuantumCircuit(system, clock, ancilla, name="HHL")

    phase_encodings = default_phase_encodings(problem)
    eigenvalues = [encoding.eigenvalue for encoding in phase_encodings]
    phase_bitstrings = [encoding.clock_state for encoding in phase_encodings]

    append_qpe(
        circuit=circuit,
        clock_qubits=[circuit.find_bit(qubit).index for qubit in clock],
        system_qubit=circuit.find_bit(system[0]).index,
        problem=problem,
    )
    inversion_steps = append_inversion_oracle(
        circuit=circuit,
        clock_qubits=[circuit.find_bit(qubit).index for qubit in clock],
        ancilla_qubit=circuit.find_bit(ancilla[0]).index,
        eigenvalues=eigenvalues,
        clock_states=phase_bitstrings,
        scale=configuration.inversion_scale,
    )
    append_inverse_qpe(
        circuit=circuit,
        clock_qubits=[circuit.find_bit(qubit).index for qubit in clock],
        system_qubit=circuit.find_bit(system[0]).index,
        problem=problem,
    )

    return HHLArtifacts(
        problem=problem,
        configuration=configuration,
        circuit=circuit,
        phase_bitstrings=phase_bitstrings,
        inversion_steps=inversion_steps,
    )


def extract_solution_vector(
    statevector: Statevector,
    system_qubits: list[int],
    clock_qubits: list[int],
    ancilla_qubit: int,
) -> np.ndarray:
    """Extract the postselected system amplitudes from the final HHL statevector."""

    num_qubits = int(np.log2(len(statevector.data)))
    amplitudes = np.zeros(2 ** len(system_qubits), dtype=complex)

    for basis_index, amplitude in enumerate(statevector.data):
        bits = little_endian_bits(basis_index, num_qubits)
        if bits[ancilla_qubit] != 1:
            continue
        if any(bits[qubit] != 0 for qubit in clock_qubits):
            continue

        system_index = 0
        for offset, qubit in enumerate(system_qubits):
            system_index |= bits[qubit] << offset
        amplitudes[system_index] = amplitude

    return amplitudes


def postselected_solution_state(
    statevector: Statevector,
    system_qubits: list[int],
    clock_qubits: list[int],
    ancilla_qubit: int,
) -> np.ndarray:
    """Return the normalized postselected HHL solution state."""

    return normalize_vector(
        extract_solution_vector(
            statevector=statevector,
            system_qubits=system_qubits,
            clock_qubits=clock_qubits,
            ancilla_qubit=ancilla_qubit,
        )
    )
