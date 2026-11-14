"""Bounded memory-cost adapter interface for a future Nav2 integration.

This module defines the contract for applying MNEMOS advice to a Nav2 costmap
without granting MNEMOS authority over collision or obstacle layers. It is a
pure-Python interface stub: no ROS or Nav2 runtime is required.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CostPatch:
    """A bounded, attributable cost suggestion for a single cell/region."""
    cost_bias: float
    episode_id: str
    explanation: tuple[str, ...]


class CostmapAdapter(Protocol):
    def apply(self, patch: CostPatch) -> None:
        """Apply a bounded bias; must never lower an occupied cell below its obstacle cost."""
        ...

    def clear(self) -> None:
        """Remove all MNEMOS-applied biases (e.g. on staleness or node loss)."""
        ...


class InMemoryCostmapAdapter:
    """Reference adapter used for offline testing and simulation of the contract."""

    def __init__(self, maximum_absolute_bias: float = 0.35) -> None:
        self.maximum_absolute_bias = maximum_absolute_bias
        self._patches: dict[str, CostPatch] = {}

    def apply(self, patch: CostPatch) -> None:
        if abs(patch.cost_bias) > self.maximum_absolute_bias + 1e-9:
            raise ValueError("cost bias exceeds the configured bound")
        self._patches[patch.episode_id] = patch

    def clear(self) -> None:
        self._patches.clear()

    def patches(self) -> dict[str, CostPatch]:
        return dict(self._patches)
