"""Bounded decision-cost helpers for MNEMOS.

Memory influence is capped so perception and collision constraints always
dominate. These primitives mirror the reasoning layer's advice logic.
"""
from __future__ import annotations

from typing import Iterable


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def path_cost(distance_to_goal: float, path_length: float) -> float:
    if path_length <= 0:
        return 1.0
    efficiency = distance_to_goal / path_length
    return clamp(1.0 - efficiency, 0.0, 1.0)


def risk_cost(nearest_obstacle: float | None, safety_margin: float = 0.65) -> float:
    if nearest_obstacle is None:
        return 0.0
    if nearest_obstacle <= 0:
        return 1.0
    if nearest_obstacle >= safety_margin:
        return 0.0
    return clamp(1.0 - (nearest_obstacle / safety_margin), 0.0, 1.0)


def memory_cost(kind: str, confidence: float, similarity: float, validation_score: float,
                maximum_absolute_bias: float = 0.35) -> float:
    if kind not in ("avoid", "recovery", "prefer", "wait"):
        return 0.0
    confidence = clamp(confidence, 0.0, 1.0)
    combined = confidence * similarity * validation_score
    combined = clamp(combined, 0.0, 1.0)
    direction = 1.0 if kind in ("avoid", "recovery") else -1.0
    if kind == "uncertain":
        direction = 0.0
    bias = direction * min(maximum_absolute_bias, maximum_absolute_bias * combined)
    return clamp(bias, -maximum_absolute_bias, maximum_absolute_bias)


def total_cost(alpha: float, beta: float, gamma: float, delta: float,
               path: float, risk: float, memory: float, uncertainty: float) -> float:
    return alpha * path + beta * risk + gamma * memory + delta * uncertainty


def is_admissible(bias: float, maximum_absolute_bias: float = 0.35) -> bool:
    return abs(bias) <= maximum_absolute_bias + 1e-9
