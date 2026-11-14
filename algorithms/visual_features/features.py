"""Simple visual feature helpers (ROS-free, no deep learning)."""
from __future__ import annotations

from typing import Sequence


def histogram(values: Sequence[float], bins: int = 8) -> list[int]:
    if not values or bins <= 0:
        return [0] * max(1, bins)
    lo, hi = min(values), max(values)
    if hi == lo:
        result = [0] * bins
        result[0] = len(values)
        return result
    result = [0] * bins
    span = hi - lo
    for v in values:
        idx = min(bins - 1, int((v - lo) / span * bins))
        result[idx] += 1
    return result
