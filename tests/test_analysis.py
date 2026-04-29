import numpy as np

from hhl_lab.analysis import precision_sweep, state_fidelity, summarize_spectrum
from hhl_lab.matrices import default_problem


def test_spectrum_summary_matches_expected_eigenvalues() -> None:
    summary = summarize_spectrum(default_problem())
    assert np.allclose(summary.eigenvalues, np.array([2.0 / 3.0, 4.0 / 3.0]))
    assert np.allclose(np.abs(summary.eigenbasis_coefficients), np.array([1.0, 1.0]) / np.sqrt(2.0))


def test_state_fidelity_is_one_for_identical_states() -> None:
    state = np.array([1.0, 1.0], dtype=complex)
    assert np.isclose(state_fidelity(state, state), 1.0)


def test_precision_sweep_becomes_exact_at_two_bits() -> None:
    points = precision_sweep(range(1, 4), default_problem())
    assert np.isnan(points[0].fidelity_with_classical)
    assert np.isclose(points[1].fidelity_with_classical, 1.0)
    assert points[1].is_exact_encoding is True
