"""Foundational context-similarity primitives used by MNEMOS retrieval.

These functions are intentionally dependency-light (standard library only) so
they can be studied, tested, and reused independently of ROS 2.
"""
from __future__ import annotations

import math
from typing import Sequence


def jaccard(left: Sequence[str], right: Sequence[str]) -> float:
    """Set overlap between two tag collections (1.0 when both are empty)."""
    a, b = set(left), set(right)
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def euclidean_distance(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("vectors must have equal length")
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right)))


def gaussian_similarity(left: Sequence[float], right: Sequence[float], scale: float = 1.5) -> float:
    """Gaussian kernel over mean squared error; returns 0 for empty/mismatched."""
    if not left or not right or len(left) != len(right):
        return 0.0
    if scale <= 0:
        return 1.0 if list(left) == list(right) else 0.0
    mse = sum((a - b) ** 2 for a, b in zip(left, right)) / len(left)
    return math.exp(-mse / (2.0 * scale * scale))


def pose_similarity(dx: float, dy: float, sigma: float = 1.25) -> float:
    distance = math.hypot(dx, dy)
    if sigma <= 0:
        return 1.0 if distance == 0.0 else 0.0
    return math.exp(-(distance ** 2) / (2.0 * sigma * sigma))


def behaviour_similarity(delta_linear: float, delta_angular: float,
                        reference_linear: float, reference_angular: float) -> float:
    gap = math.hypot(delta_linear - reference_linear, delta_angular - reference_angular)
    return math.exp(-gap)


def combined_similarity(geometry: float, semantics: float, behaviour: float,
                       weights: tuple[float, float, float] = (0.55, 0.25, 0.20)) -> float:
    w_g, w_s, w_b = weights
    total = w_g * geometry + w_s * semantics + w_b * behaviour
    # Clamp to [0, 1] for interpretability.
    return max(0.0, min(1.0, total))
