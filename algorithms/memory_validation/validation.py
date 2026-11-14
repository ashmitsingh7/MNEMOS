"""Foundational memory-validation primitives for MNEMOS.

Validation rejects stale or contradicted evidence before it can influence
navigation. All functions are pure and dependency-light.
"""
from __future__ import annotations

import math
from typing import Sequence


def geometry_score(stored_signature: Sequence[float], current_signature: Sequence[float],
                   scale: float = 1.5) -> float:
    if not stored_signature or not current_signature or len(stored_signature) != len(current_signature):
        return 0.0
    if scale <= 0:
        return 1.0 if list(stored_signature) == list(current_signature) else 0.0
    mse = sum((a - b) ** 2 for a, b in zip(stored_signature, current_signature)) / len(stored_signature)
    return math.exp(-mse / (2.0 * scale * scale))


def semantic_score(stored_tags: Sequence[str], current_tags: Sequence[str]) -> float:
    a, b = set(stored_tags), set(current_tags)
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def age_score(created_at: float, now: float, maximum_age_seconds: float) -> float:
    age_seconds = max(0.0, now - created_at)
    if maximum_age_seconds <= 0:
        return 0.0 if age_seconds > 0 else 1.0
    return math.exp(-age_seconds / maximum_age_seconds)


def validation_score(geometry: float, semantic: float, age: float,
                    weights: tuple[float, float, float] = (0.60, 0.20, 0.20)) -> float:
    w_g, w_s, w_a = weights
    return max(0.0, min(1.0, w_g * geometry + w_s * semantic + w_a * age))


def is_contradicted(geometry: float, threshold: float = 0.25) -> bool:
    return geometry < threshold


def classify(status_inputs: dict) -> str:
    """Return a human-readable validation status string."""
    geometry = status_inputs.get("geometry", 0.0)
    score = status_inputs.get("score", 0.0)
    contradiction_threshold = status_inputs.get("contradiction_threshold", 0.25)
    if geometry < contradiction_threshold:
        return "contradicted"
    if score >= 0.72:
        return "valid"
    if score >= 0.48:
        return "tentative"
    return "outdated"
