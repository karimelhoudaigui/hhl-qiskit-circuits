import numpy as np

from hhl_lab.matrices import default_problem
from hhl_lab.simulation import run_hhl_statevector


def test_hhl_solution_is_proportional_to_expected_vector() -> None:
    result = run_hhl_statevector()
    expected = np.array([9.0 / 8.0, 3.0 / 8.0], dtype=complex)
    ratio = result.raw_solution_amplitudes[0] / expected[0]
    assert np.allclose(result.raw_solution_amplitudes, ratio * expected)


def test_hhl_matches_normalized_classical_solution() -> None:
    result = run_hhl_statevector(default_problem())
    assert np.allclose(
        result.normalized_hhl_solution,
        result.normalized_classical_solution,
        atol=1e-8,
    )


def test_hhl_success_probability_is_nonzero() -> None:
    result = run_hhl_statevector()
    assert np.isclose(result.success_probability, 0.625)
