"""Minimal example using the public package API."""

from hhl_lab import run_hhl_statevector


result = run_hhl_statevector()
print("Normalized classical solution:", result.normalized_classical_solution)
print("Normalized HHL solution:", result.normalized_hhl_solution)
print("Success probability:", result.success_probability)
