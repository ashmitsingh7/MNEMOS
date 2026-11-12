"""Unit tests for the novel MNEMOS layer; no ROS graph or simulator is required."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src/mnemos_memory'), str(ROOT / 'src/mnemos_intervention'),
                str(ROOT / 'src/mnemos_reasoning')]

from mnemos_memory.model import Episode, EpisodeKind, ValidationStatus
from mnemos_memory.retrieval import compare, retrieve
from mnemos_memory.store import EpisodeStore
from mnemos_intervention.interpreter import Command, interpret
from mnemos_reasoning.advice import advise
from mnemos_reasoning.validation import validate


def episode(kind=EpisodeKind.AVOID, scan=(1.0, 1.2, 1.5), age=100.0, confidence=0.9):
    return Episode(kind, 1.0, 2.0, 0.1, scan, ('corridor',), -0.3, 0.2,
                   confidence, ('unit-test',), created_at=age)


class TestCognitiveCore(unittest.TestCase):
    def test_episode_round_trip_is_lossless(self):
        with tempfile.TemporaryDirectory() as directory:
            store = EpisodeStore(Path(directory) / 'episodes.sqlite3')
            original = episode()
            store.insert(original)
            self.assertEqual(store.recent(), [original])

    def test_context_retrieval_ranks_closest_episode(self):
        current = episode(EpisodeKind.UNCERTAIN, age=200.0)
        close = episode(age=150.0)
        far = Episode(EpisodeKind.AVOID, 8.0, 8.0, 0.0, (7.0, 7.0, 7.0), (), confidence=0.9)
        matches = retrieve([far, close], current, minimum_similarity=0.1)
        self.assertEqual(matches[0][0].identifier, close.identifier)
        self.assertGreater(matches[0][1].total, matches[-1][1].total)

    def test_changed_geometry_contradicts_memory(self):
        stored = episode(scan=(0.3, 0.4, 0.5), age=1000.0)
        current = episode(scan=(7.0, 7.0, 7.0), age=1001.0)
        result = validate(stored, current, now=1001.0)
        self.assertEqual(result.status, ValidationStatus.CONTRADICTED)
        self.assertFalse(result.admissible)

    def test_advice_is_bounded_and_never_acts_on_contradiction(self):
        stored = episode()
        current = episode(EpisodeKind.UNCERTAIN, age=101.0)
        permitted = advise(stored, compare(stored, current), validate(stored, current, now=101.0), 0.20)
        self.assertLessEqual(abs(permitted.cost_bias), 0.20)
        contradicted = advise(stored, compare(stored, current),
                             validate(stored, episode(scan=(9.0, 9.0, 9.0)), now=101.0))
        self.assertEqual(contradicted.action, 'abstain')
        self.assertEqual(contradicted.cost_bias, 0.0)

    def test_interpreter_records_evidence_not_unfounded_certainty(self):
        result = interpret(Command(0.3, 0.0), Command(0.0, 0.1), 0.4, 0.7)
        self.assertEqual(result.kind, EpisodeKind.AVOID)
        self.assertGreater(result.confidence, 0.8)
        self.assertTrue(result.evidence)
        uncertain = interpret(Command(0.0, 0.0), Command(0.03, 0.0), None, 0.1)
        self.assertEqual(uncertain.kind, EpisodeKind.UNCERTAIN)


if __name__ == '__main__':
    unittest.main()
