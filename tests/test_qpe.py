import numpy as np
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Statevector

from hhl_lab.matrices import default_problem, evolution_unitary
from hhl_lab.qpe import append_qpe, default_phase_encodings


def test_evolution_unitary_is_unitary() -> None:
    unitary = evolution_unitary(default_problem(), power=1)
    identity = unitary.conj().T @ unitary
    assert np.allclose(identity, np.eye(2))


def test_qpe_encodes_known_eigenphase() -> None:
    problem = default_problem()
    system = QuantumRegister(1, "sys")
    clock = QuantumRegister(2, "clk")
    circuit = QuantumCircuit(system, clock)
    circuit.h(system[0])
    append_qpe(circuit, [1, 2], 0, problem)

    statevector = Statevector.from_instruction(circuit)
    probabilities = np.abs(statevector.data) ** 2

    # The |+> eigenstate should place the clock register on the little-endian string "10".
    assert np.isclose(probabilities[2] + probabilities[3], 1.0)


def test_default_phase_encodings_match_expected_phases() -> None:
    encodings = default_phase_encodings(default_problem())
    assert np.isclose(encodings[0].phase, 0.25)
    assert np.isclose(encodings[1].phase, 0.5)
