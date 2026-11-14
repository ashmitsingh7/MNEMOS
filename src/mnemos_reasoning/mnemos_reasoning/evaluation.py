"""Offline evaluation helpers for MNEMOS memory validation."""
from dataclasses import dataclass
from typing import Iterable

from mnemos_memory.model import Episode, ValidationResult, ValidationStatus
from .validation import validate


@dataclass(frozen=True)
class ValidationCase:
    """A labeled stored/current pair for calibration or held-out testing."""
    stored: Episode
    current: Episode
    now: float
    expected_admissible: bool
    expected_contradicted: bool = False


def evaluate_validation(cases: Iterable[ValidationCase]) -> dict:
    if cases is None:
        cases = []
    cases = list(cases)
    true_positive = false_positive = true_negative = false_negative = 0
    expected_contradictions = detected_contradictions = 0
    inadmissible = 0
    for case in cases:
        result = validate(case.stored, case.current, now=case.now)
        if case.expected_admissible:
            if result.admissible:
                true_positive += 1
            else:
                false_negative += 1
        else:
            if result.admissible:
                false_positive += 1
            else:
                true_negative += 1
        if case.expected_contradicted:
            expected_contradictions += 1
            if result.status == ValidationStatus.CONTRADICTED:
                detected_contradictions += 1
        if not result.admissible:
            inadmissible += 1
    total = len(cases)
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    return {
        'trials': total,
        'true_positive': true_positive,
        'false_positive': false_positive,
        'true_negative': true_negative,
        'false_negative': false_negative,
        'precision': precision,
        'recall': recall,
        'false_accept_rate': false_positive / total if total else 0.0,
        'false_reject_rate': false_negative / total if total else 0.0,
        'contradiction_detection_rate': (detected_contradictions / expected_contradictions
                                        if expected_contradictions else 1.0),
        'abstention_rate': inadmissible / total if total else 0.0,
    }