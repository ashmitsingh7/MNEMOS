"""Rule-based intervention interpretation primitives for MNEMOS.

These mirror mnemos_intervention.interpreter but are ROS-free and easy to
study or reuse in offline analysis.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Command:
    linear: float
    angular: float


@dataclass(frozen=True)
class Interpretation:
    kind: str
    confidence: float
    evidence: tuple[str, ...]


def interpret(autonomous: Command, human: Command, nearest_obstacle: Optional[float],
              sustained_seconds: float, min_duration: float = 0.40) -> Interpretation:
    linear_delta = human.linear - autonomous.linear
    angular_delta = human.angular - autonomous.angular
    magnitude = math.hypot(linear_delta, angular_delta)
    if sustained_seconds is None or sustained_seconds < min_duration or magnitude < 0.12:
        return Interpretation("uncertain", 0.0, ("Deviation was too brief or too small.",))
    evidence = [f"linear_delta={linear_delta:.2f}", f"angular_delta={angular_delta:.2f}",
                f"duration={sustained_seconds:.2f}s"]
    if nearest_obstacle is not None:
        evidence.append(f"nearest_obstacle={nearest_obstacle:.2f}m")
    if nearest_obstacle is not None and nearest_obstacle < 0.65 and linear_delta < -0.05:
        return Interpretation("avoid", 0.90, tuple(evidence + ["Human reduced forward motion near an obstacle."]))
    if autonomous.linear > 0.10 and abs(human.linear) < 0.03:
        return Interpretation("wait", 0.72, tuple(evidence + ["Human stopped an active autonomous command."]))
    if linear_delta > 0.10 and (nearest_obstacle is None or nearest_obstacle > 0.80):
        return Interpretation("prefer", 0.58, tuple(evidence + ["Human advanced in open space."]))
    if magnitude > 0.30:
        return Interpretation("recovery", 0.52, tuple(evidence + ["Large sustained override; cause is not inferred."]))
    return Interpretation("uncertain", 0.25, tuple(evidence + ["No reliable rule matched."]))
