"""Lidar scan compression primitives (ROS-free)."""
from __future__ import annotations

from typing import Sequence


def scan_signature(ranges: Sequence[float], range_min: float, range_max: float,
                   sectors: int = 24) -> tuple[float, ...]:
    if not ranges:
        return ()
    sectors = max(1, sectors)
    size = max(1, len(ranges) // sectors)
    signature: list[float] = []
    for index in range(sectors):
        chunk = ranges[index * size:(index + 1) * size]
        values = [v for v in chunk if range_min <= v <= range_max]
        signature.append(min(values) if values else range_max)
    return tuple(signature)
