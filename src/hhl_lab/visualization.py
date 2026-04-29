"""Figure generation for the HHL project."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from qiskit.visualization import circuit_drawer

from .analysis import PrecisionSweepPoint, summarize_spectrum
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


def plot_spectral_decomposition(result: SimulationResult) -> plt.Figure:
    figure, axes = plt.subplots(1, 2, figsize=(11.0, 4.5))
    spectrum = summarize_spectrum(result.artifacts.problem)

    basis_positions = np.arange(spectrum.eigenvectors.shape[0])
    width = 0.32
    axes[0].bar(
        basis_positions - width / 2,
        spectrum.eigenvectors[:, 0].real,
        width=width,
        label=r"$|u_1\rangle$",
        color="#1b9e77",
    )
    axes[0].bar(
        basis_positions + width / 2,
        spectrum.eigenvectors[:, 1].real,
        width=width,
        label=r"$|u_2\rangle$",
        color="#d95f02",
    )
    axes[0].set_xticks(basis_positions, [r"$|0\rangle$", r"$|1\rangle$"])
    axes[0].set_ylabel("Component value")
    axes[0].set_title("Eigenvectors of the Hermitian System Matrix")
    axes[0].legend(frameon=False)
    _style_axes(axes[0])

    axes[1].bar(
        [r"$\beta_1$", r"$\beta_2$"],
        np.abs(spectrum.eigenbasis_coefficients),
        color=["#1b9e77", "#d95f02"],
    )
    axes[1].set_ylabel(r"$|\beta_j|$")
    axes[1].set_title(r"Decomposition of $|b\rangle$ in the Eigenbasis")
    _style_axes(axes[1])

    figure.suptitle("Spectral Structure Behind the HHL Transformation", y=1.02, fontsize=13)
    figure.tight_layout()
    return figure


def plot_precision_sweep(points: list[PrecisionSweepPoint]) -> plt.Figure:
    figure, axes = plt.subplots(1, 2, figsize=(11.0, 4.5))
    bits = [point.precision_bits for point in points]
    errors = [point.l2_error for point in points]
    fidelities = [point.fidelity_with_classical for point in points]

    axes[0].plot(bits, errors, marker="o", color="#7570b3", linewidth=2.0)
    axes[0].set_xlabel("Phase register size (bits)")
    axes[0].set_ylabel("Relative L2 error")
    axes[0].set_title("Recovered Solution Error vs Phase Precision")
    _style_axes(axes[0])

    axes[1].plot(bits, fidelities, marker="o", color="#e7298a", linewidth=2.0)
    axes[1].set_xlabel("Phase register size (bits)")
    axes[1].set_ylabel("Fidelity with normalized classical state")
    axes[1].set_ylim(-0.02, 1.02)
    axes[1].set_title("State Fidelity vs Phase Precision")
    _style_axes(axes[1])

    figure.suptitle("Precision Study for Eigenphase Discretization", y=1.02, fontsize=13)
    figure.tight_layout()
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

    from .analysis import precision_sweep

    output_dir = Path(output_dir)
    save_figure(plot_solution_comparison(result), "solution_comparison", output_dir)
    save_figure(plot_statevector_distribution(result), "statevector_distribution", output_dir)
    save_figure(plot_eigenvalue_encoding(result), "eigenvalue_encoding", output_dir)
    save_figure(plot_success_probability(result), "success_probability", output_dir)
    save_figure(plot_spectral_decomposition(result), "spectral_decomposition", output_dir)
    save_figure(plot_precision_sweep(precision_sweep(range(1, 7), result.artifacts.problem)), "precision_sweep", output_dir)
    save_circuit_figures(result, output_dir)
    return sorted(output_dir.glob("*"))
