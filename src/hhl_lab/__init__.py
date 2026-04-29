"""HHL educational toolkit built around a 2x2 Hermitian linear system."""

from .analysis import precision_sweep, state_fidelity, summarize_spectrum
from .hhl import HHLArtifacts, HHLConfiguration, build_hhl_circuit, extract_solution_vector
from .matrices import HHLProblem, classical_solution, default_problem
from .simulation import run_hhl_statevector

__all__ = [
    "HHLArtifacts",
    "HHLConfiguration",
    "HHLProblem",
    "build_hhl_circuit",
    "classical_solution",
    "default_problem",
    "extract_solution_vector",
    "precision_sweep",
    "run_hhl_statevector",
    "state_fidelity",
    "summarize_spectrum",
]
