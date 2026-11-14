"""Planner-cost adapter for applying MNEMOS advice without overriding safety.

This is a pure-Python reference for how a Nav2 planner adapter should consume
`/mnemos/memory_cost_bias`. It never changes obstacle or inflation costs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class PlannerCosts:
    path_cost: float
    risk_cost: float
    memory_cost: float
    uncertainty_cost: float


def combine_costs(costs: PlannerCosts, alpha: float = 1.0, beta: float = 0.5,
                  gamma: float = 0.3, delta: float = 0.2) -> float:
    return (alpha * costs.path_cost + beta * costs.risk_cost +
            gamma * costs.memory_cost + delta * costs.uncertainty_cost)


def apply_memory_bias(base_cost: float, memory_bias: float, cap: float = 0.35) -> float:
    """Apply a bounded memory bias; never allow a negative total cost."""
    bias = max(-cap, min(cap, memory_bias))
    return max(0.0, base_cost + bias)


def is_safe_to_apply(memory_bias: float, obstacle_cost: float, cap: float = 0.35) -> bool:
    """Memory may only adjust cost; it may never make an occupied cell traversable."""
    if obstacle_cost > 0:
        return False
    return abs(memory_bias) <= cap + 1e-9
