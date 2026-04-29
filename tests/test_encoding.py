import numpy as np

from hhl_lab.encoding import bits_to_int, int_to_bits, little_endian_bits, normalize_vector


def test_bitstring_round_trip() -> None:
    assert bits_to_int("10") == 2
    assert int_to_bits(2, 2) == "10"


def test_little_endian_bits() -> None:
    assert little_endian_bits(5, 3) == [1, 0, 1]


def test_normalize_vector() -> None:
    normalized = normalize_vector([3.0, 4.0])
    assert np.isclose(normalized[0], 0.6)
    assert np.isclose(normalized[1], 0.8)
