"""Camera geometry helpers (ROS-free)."""
from __future__ import annotations

import math
from typing import Tuple


def pixel_to_ray(px: float, py: float, fx: float, fy: float,
                 cx: float, cy: float) -> Tuple[float, float, float]:
    return ((px - cx) / fx, (py - cy) / fy, 1.0)


def depth_to_point(px: float, py: float, depth: float, fx: float, fy: float,
                   cx: float, cy: float) -> Tuple[float, float, float]:
    x = (px - cx) * depth / fx
    y = (py - cy) * depth / fy
    return (x, y, depth)
