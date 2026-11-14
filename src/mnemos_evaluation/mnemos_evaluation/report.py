"""Reproducible report generation from the MNEMOS trial ledger."""
from __future__ import annotations

from typing import Iterable

from .ledger import TrialLedger


def configuration_report(ledger: TrialLedger, configurations: Iterable[str],
                         scenario: str) -> dict[str, dict]:
    report: dict[str, dict] = {}
    for configuration in configurations:
        report[configuration] = ledger.summary(configuration, scenario)
    return report


def full_report(ledger: TrialLedger, configurations: Iterable[str],
                scenarios: Iterable[str]) -> dict[str, dict[str, dict]]:
    return {scenario: configuration_report(ledger, configurations, scenario)
            for scenario in scenarios}
