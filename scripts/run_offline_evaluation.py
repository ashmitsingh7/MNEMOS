"""Run the MNEMOS offline evaluation helpers and print a compact report.

This script requires no ROS 2 runtime: it exercises the pure-Python core
(memory, intervention, reasoning) and is useful for regression checks.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [
    str(ROOT / "src/mnemos_memory"),
    str(ROOT / "src/mnemos_intervention"),
    str(ROOT / "src/mnemos_reasoning"),
    str(ROOT / "src/mnemos_control"),
    str(ROOT / "src/mnemos_evaluation"),
]

from mnemos_memory.model import Episode, EpisodeKind
from mnemos_memory.retrieval import compare
from mnemos_memory.evaluation import RetrievalCase, evaluate_retrieval
from mnemos_intervention.evaluation import LABELED_INTERVENTIONS, classification_report
from mnemos_reasoning.validation import validate
from mnemos_reasoning.evaluation import ValidationCase, evaluate_validation
from mnemos_reasoning.advice import advise


def main() -> int:
    def make(**kw):
        values = dict(kind=EpisodeKind.AVOID, pose_x=1.0, pose_y=2.0, pose_yaw=0.1,
                      scan_signature=(1.0, 1.2, 1.5), semantic_tags=("corridor",),
                      confidence=0.9)
        values.update(kw)
        return Episode(**values)

    # Retrieval evaluation
    close = make(created_at=100.0)
    far = make(created_at=101.0, pose_x=10.0, scan_signature=(9.0, 9.0, 9.0))
    current = make(created_at=100.0, kind=EpisodeKind.UNCERTAIN)
    retrieval_report = evaluate_retrieval([RetrievalCase([far, close], current,
                                                        {close.identifier}, minimum_similarity=0.1)])
    print("Retrieval:", retrieval_report)

    # Validation evaluation
    same = make(scan_signature=(1.0, 1.0, 1.0), created_at=100.0)
    changed = make(scan_signature=(9.0, 9.0, 9.0), created_at=101.0)
    validation_report = evaluate_validation([
        ValidationCase(same, same, 100.0, True),
        ValidationCase(same, changed, 101.0, False, True),
    ])
    print("Validation:", validation_report)

    # Intervention classification
    report = classification_report(LABELED_INTERVENTIONS)
    print("Intervention accuracy:", report["accuracy"])

    # Advice sanity
    stored = make(created_at=100.0)
    cur = make(created_at=100.0)
    sim = compare(stored, cur)
    val = validate(stored, cur, now=100.0)
    adv = advise(stored, sim, val)
    print("Advice:", adv.action, adv.cost_bias, adv.confidence)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
