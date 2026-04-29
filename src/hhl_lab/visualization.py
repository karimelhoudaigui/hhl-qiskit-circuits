"""Figure generation for the HHL project."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from qiskit.visualization import circuit_drawer

from .simulation import SimulationResult


FIGURE_SIZE = (7.5, 4.5)


def _style_axes(axis: plt.Axes) -> None:
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.grid(alpha=0.25, linestyle="--", linewidth=0.8)


def save_figure(figure: plt.Figure, stem: str, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_dir / f"{stem}.png", dpi=220, bbox_inches="tight")
    figure.savefig(output_dir / f"{stem}.svg", bbox_inches="tight")
    plt.close(figure)


def plot_solution_comparison(result: SimulationResult) -> plt.Figure:
    figure, axis = plt.subplots(figsize=FIGURE_SIZE)
    labels = [r"$x_0$", r"$x_1$"]
    x_positions = np.arange(2)
    width = 0.35

    axis.bar(
        x_positions - width / 2,
        result.normalized_classical_solution.real,
        width=width,
        label="Classical (normalized)",
        color="#1b9e77",
    )
    axis.bar(
        x_positions + width / 2,
        result.normalized_hhl_solution.real,
        width=width,
        label="HHL (postselected)",
        color="#d95f02",
    )
    axis.set_xticks(x_positions, labels)
    axis.set_ylabel("Amplitude")
    axis.set_title("Normalized Classical Solution vs Postselected HHL State")
    axis.legend(frameon=False)
    _style_axes(axis)
    return figure


def plot_statevector_distribution(result: SimulationResult) -> plt.Figure:
    figure, axis = plt.subplots(figsize=(9.5, 4.5))
    probabilities = np.abs(result.statevector.data) ** 2
    basis_labels = [format(index, "04b") for index in range(len(probabilities))]
    axis.bar(basis_labels, probabilities, color="#7570b3")
    axis.set_xlabel("Basis state |sys clk anc⟩ in Qiskit index order")
    axis.set_ylabel("Probability")
    axis.set_title("Final HHL Statevector Probability Distribution")
    axis.tick_params(axis="x", labelrotation=45)
    _style_axes(axis)
    return figure


def plot_eigenvalue_encoding(result: SimulationResult) -> plt.Figure:
    figure, axis = plt.subplots(figsize=FIGURE_SIZE)
    eigenvalues = [step.eigenvalue for step in result.artifacts.inversion_steps]
    encoded_states = [step.clock_state for step in result.artifacts.inversion_steps]
    axis.scatter(eigenvalues, range(len(eigenvalues)), s=180, color="#e7298a")
    for idx, (eigenvalue, clock_state) in enumerate(zip(eigenvalues, encoded_states)):
        axis.text(eigenvalue + 0.02, idx, f"{clock_state}", va="center")
    axis.set_xlabel("Eigenvalue")
    axis.set_yticks(range(len(eigenvalues)), [r"$|u_1\rangle$", r"$|u_2\rangle$"])
    axis.set_title("Two-Qubit Phase Register Encoding of Eigenvalues")
    _style_axes(axis)
    return figure


def plot_success_probability(result: SimulationResult) -> plt.Figure:
    figure, axis = plt.subplots(figsize=(5.0, 4.5))
    axis.bar(["postselect anc=1"], [result.success_probability], color="#66a61e")
    axis.set_ylim(0.0, 1.0)
    axis.set_ylabel("Probability")
    axis.set_title("Success Probability of the Inversion Ancilla")
    _style_axes(axis)
    return figure


def save_circuit_figures(result: SimulationResult, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    full_circuit = circuit_drawer(result.artifacts.circuit, output="mpl", fold=-1)
    full_circuit.savefig(output_dir / "circuit_hhl.svg", bbox_inches="tight")
    full_circuit.savefig(output_dir / "circuit_hhl.png", dpi=220, bbox_inches="tight")
    plt.close(full_circuit)

    inversion_only = result.artifacts.circuit.copy_empty_like()
    for instruction in result.artifacts.circuit.data:
        if "ry" in instruction.operation.name or instruction.operation.name == "x":
            inversion_only.append(instruction.operation, instruction.qubits, instruction.clbits)

    inversion_figure = circuit_drawer(inversion_only, output="mpl", fold=-1)
    inversion_figure.savefig(output_dir / "inversion_oracle.svg", bbox_inches="tight")
    inversion_figure.savefig(output_dir / "inversion_oracle.png", dpi=220, bbox_inches="tight")
    plt.close(inversion_figure)


def generate_all_figures(result: SimulationResult, output_dir: str | Path) -> list[Path]:
    """Generate and save all project figures."""

    output_dir = Path(output_dir)
    save_figure(plot_solution_comparison(result), "solution_comparison", output_dir)
    save_figure(plot_statevector_distribution(result), "statevector_distribution", output_dir)
    save_figure(plot_eigenvalue_encoding(result), "eigenvalue_encoding", output_dir)
    save_figure(plot_success_probability(result), "success_probability", output_dir)
    save_circuit_figures(result, output_dir)
    return sorted(output_dir.glob("*"))
