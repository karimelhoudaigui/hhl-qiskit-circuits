"""Ancilla-rotation logic for eigenvalue inversion in HHL."""

from __future__ import annotations

from dataclasses import dataclass
from math import asin

from qiskit import QuantumCircuit

from .encoding import bits_to_int, int_to_bits


@dataclass(frozen=True)
class InversionStep:
    """One basis-controlled inversion rule for the phase register."""

    clock_state: str
    eigenvalue: float
    scale: float
    rotation_angle: float


def rotation_angle(eigenvalue: float, scale: float) -> float:
    """Return the Ry angle that yields ancilla amplitude scale / eigenvalue."""

    if scale <= 0:
        raise ValueError("scale must be positive.")
    if abs(scale / eigenvalue) > 1:
        raise ValueError("scale must satisfy |scale / eigenvalue| <= 1.")
    return 2.0 * asin(scale / eigenvalue)


def inversion_schedule(
    eigenvalues: list[float],
    clock_states: list[str],
    scale: float,
) -> list[InversionStep]:
    """Return the basis-state schedule for the inversion ancilla."""

    return [
        InversionStep(
            clock_state=clock_state,
            eigenvalue=eigenvalue,
            scale=scale,
            rotation_angle=rotation_angle(eigenvalue, scale),
        )
        for eigenvalue, clock_state in zip(eigenvalues, clock_states)
    ]


def append_basis_controlled_ry(
    circuit: QuantumCircuit,
    controls: list[int],
    target: int,
    bitstring: str,
    angle: float,
) -> None:
    """Apply a multi-controlled Ry conditioned on a computational basis state."""

    if len(bitstring) != len(controls):
        raise ValueError("bitstring width must match the number of control qubits.")

    zero_controls = [control for control, bit in zip(controls, bitstring) if bit == "0"]
    for qubit in zero_controls:
        circuit.x(qubit)

    circuit.mcry(angle, controls, target, None, mode="noancilla")

    for qubit in zero_controls:
        circuit.x(qubit)


def append_inversion_oracle(
    circuit: QuantumCircuit,
    clock_qubits: list[int],
    ancilla_qubit: int,
    eigenvalues: list[float],
    clock_states: list[str],
    scale: float,
) -> list[InversionStep]:
    """Append the controlled ancilla rotations implementing reciprocal encoding."""

    schedule = inversion_schedule(eigenvalues, clock_states, scale)
    for step in schedule:
        append_basis_controlled_ry(
            circuit=circuit,
            controls=clock_qubits,
            target=ancilla_qubit,
            bitstring=step.clock_state,
            angle=step.rotation_angle,
        )
    return schedule


def encoded_eigenvalue_from_bits(bitstring: str, phases: dict[str, float], evolution_time: float) -> float:
    """Recover an eigenvalue from an encoded phase bitstring."""

    phase = phases[bitstring]
    return (2.0 * 3.141592653589793 * phase) / evolution_time


def all_clock_states(width: int) -> list[str]:
    """Return all binary strings for a clock register width."""

    return [int_to_bits(value, width) for value in range(2**width)]
