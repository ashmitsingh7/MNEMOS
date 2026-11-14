"""Skeleton for the MNEMOS A/B/C/D ablation runner.

This module does NOT fabricate data. It defines the trial matrix and the
contract that every run must record a TrialRecord (including failures).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

CONFIGURATIONS = ("A_baseline", "B_interpretation", "C_episodic_memory", "D_validated_memory")
SCENARIOS = ("familiar_clear", "temporary_blockage", "cleared_passage", "novel_obstacle")


@dataclass(frozen=True)
class TrialSpec:
    configuration: str
    scenario: str
    seed: int


def trial_matrix(seeds: Iterable[int]) -> list[TrialSpec]:
    seeds = list(seeds)
    specs: list[TrialSpec] = []
    for configuration in CONFIGURATIONS:
        for scenario in SCENARIOS:
            for seed in seeds:
                specs.append(TrialSpec(configuration, scenario, seed))
    return specs


def describe() -> str:
    return ("MNEMOS ablation: %d configurations x %d scenarios x N seeds. "
            "Every planned attempt must be recorded, including failures and "
            "collisions. No result is reported without matched seeds." %
            (len(CONFIGURATIONS), len(SCENARIOS)))
