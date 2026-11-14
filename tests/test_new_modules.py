"""Smoke tests for Stage 5-7 scaffolding modules."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [
    str(ROOT / "src/mnemos_memory"),
    str(ROOT / "src/mnemos_reasoning"),
    str(ROOT / "src/mnemos_evaluation"),
]

from mnemos_reasoning.planner_adapter import apply_memory_bias, is_safe_to_apply, combine_costs, PlannerCosts
from mnemos_evaluation.report import full_report
from mnemos_evaluation.ledger import TrialLedger, TrialRecord
from pathlib import Path
import tempfile


def test_planner_adapter():
    assert apply_memory_bias(0.5, 0.2) == 0.7
    assert apply_memory_bias(0.5, 10.0) == 0.85  # capped
    assert is_safe_to_apply(0.2, 0.0) is True
    assert is_safe_to_apply(0.2, 1.0) is False
    c = combine_costs(PlannerCosts(0.1, 0.2, 0.3, 0.4))
    assert c > 0


def test_report():
    with tempfile.TemporaryDirectory() as d:
        ledger = TrialLedger(Path(d) / "t.sqlite3")
        ledger.append(TrialRecord("A", "s", True, 1.0, 1.0, 0, 0))
        r = full_report(ledger, ["A"], ["s"])
        assert "s" in r and "A" in r["s"]


if __name__ == "__main__":
    test_planner_adapter()
    test_report()
    print("OK")