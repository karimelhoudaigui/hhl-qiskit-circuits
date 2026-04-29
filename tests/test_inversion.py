import numpy as np

from hhl_lab.inversion import inversion_schedule, rotation_angle


def test_rotation_angle_matches_target_amplitude() -> None:
    angle = rotation_angle(eigenvalue=4.0 / 3.0, scale=2.0 / 3.0)
    assert np.isclose(np.sin(angle / 2.0), 0.5)


def test_inversion_schedule_for_default_eigenvalues() -> None:
    schedule = inversion_schedule(
        eigenvalues=[2.0 / 3.0, 4.0 / 3.0],
        clock_states=["10", "01"],
        scale=2.0 / 3.0,
    )
    assert np.isclose(schedule[0].rotation_angle, np.pi)
    assert np.isclose(np.sin(schedule[1].rotation_angle / 2.0), 0.5)
