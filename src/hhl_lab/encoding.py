"""State-preparation and bitstring helper utilities."""

from __future__ import annotations

from typing import Iterable

import numpy as np


def normalize_vector(vector: Iterable[complex]) -> np.ndarray:
    """Return a normalized complex vector."""

    array = np.asarray(list(vector), dtype=complex)
    norm = np.linalg.norm(array)
    if np.isclose(norm, 0.0):
        raise ValueError("Cannot normalize the zero vector.")
    return array / norm


def bits_to_int(bits: str) -> int:
    """Convert a binary string into an integer."""

    return int(bits, 2)


def int_to_bits(value: int, width: int) -> str:
    """Convert an integer into a zero-padded binary string."""

    if value < 0:
        raise ValueError("Only non-negative integers are supported.")
    return format(value, f"0{width}b")


def little_endian_bits(index: int, width: int) -> list[int]:
    """Return the little-endian bit decomposition of a basis index."""

    return [(index >> position) & 1 for position in range(width)]
