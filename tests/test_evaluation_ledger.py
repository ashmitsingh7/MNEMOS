from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/mnemos_evaluation'))

from mnemos_evaluation.ledger import TrialLedger, TrialRecord


class TestTrialLedger(unittest.TestCase):
    def test_summary_counts_failures_and_collisions(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = TrialLedger(Path(directory) / 'trials.sqlite3')
            ledger.append(TrialRecord('A_baseline', 'familiar_clear', True, 10.0, 4.0, 0, 0))
            ledger.append(TrialRecord('A_baseline', 'familiar_clear', False, 20.0, 3.0, 1, 2))
            summary = ledger.summary('A_baseline', 'familiar_clear')
            self.assertEqual(summary['trials'], 2)
            self.assertEqual(summary['success_rate'], 0.5)
            self.assertEqual(summary['total_collision_events'], 2)
            self.assertEqual(summary['mean_interventions'], 0.5)


if __name__ == '__main__':
    unittest.main()
