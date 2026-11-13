"""Additional edge-case coverage for the MNEMOS pure-Python core."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [
    str(ROOT / 'src/mnemos_memory'),
    str(ROOT / 'src/mnemos_intervention'),
    str(ROOT / 'src/mnemos_reasoning'),
    str(ROOT / 'src/mnemos_control'),
    str(ROOT / 'src/mnemos_evaluation'),
]

from mnemos_memory.model import Episode, EpisodeKind, ValidationStatus
from mnemos_memory.retrieval import compare, retrieve, signature_similarity
from mnemos_memory.store import EpisodeStore
from mnemos_memory.evaluation import RetrievalCase, evaluate_retrieval
from mnemos_intervention.interpreter import Command, interpret
from mnemos_intervention.evaluation import (LABELED_INTERVENTIONS, classification_report,
                                           confusion_matrix, predict)
from mnemos_reasoning.advice import advise
from mnemos_reasoning.validation import validate
from mnemos_reasoning.evaluation import ValidationCase, evaluate_validation
from mnemos_control.policy import ArbitrationPolicy, Command as PolicyCommand, CommandSource
from mnemos_evaluation.ledger import TrialLedger, TrialRecord

try:
    from sensor_msgs.msg import LaserScan
    from mnemos_memory.context import scan_signature
    ROS_AVAILABLE = True
except Exception:  # pragma: no cover - optional in minimal environments
    ROS_AVAILABLE = False


def make_episode(**overrides):
    values = dict(
        kind=EpisodeKind.AVOID,
        pose_x=1.0,
        pose_y=2.0,
        pose_yaw=0.1,
        scan_signature=(1.0, 1.2, 1.5),
        semantic_tags=('corridor',),
        command_delta_linear=-0.3,
        command_delta_angular=0.2,
        confidence=0.9,
        evidence=('unit-test',),
    )
    values.update(overrides)
    return Episode(**values)


class TestModelAndRetrieval(unittest.TestCase):
    def test_signature_similarity_empty_or_mismatched(self):
        self.assertEqual(signature_similarity((), (1.0,)), 0.0)
        self.assertEqual(signature_similarity((1.0, 2.0), (1.0,)), 0.0)
        self.assertEqual(signature_similarity((1.0, 2.0), (1.0, 2.0)), 1.0)

    def test_signature_similarity_scale_guard(self):
        self.assertEqual(signature_similarity((1.0, 2.0), (1.0, 2.0), scale=0.0), 1.0)

    def test_retrieve_respects_limit_and_threshold(self):
        current = make_episode(kind=EpisodeKind.UNCERTAIN, scan_signature=(1.0, 1.2, 1.5))
        episodes = [
            make_episode(created_at=100.0),
            make_episode(created_at=101.0, pose_x=10.0, scan_signature=(9.0, 9.0, 9.0)),
        ]
        matches = retrieve(episodes, current, minimum_similarity=0.1, limit=1)
        self.assertEqual(len(matches), 1)
        self.assertGreaterEqual(matches[0][1].total, 0.1)

    def test_retrieve_empty_input(self):
        current = make_episode()
        self.assertEqual(retrieve([], current), [])

    def test_compare_behavior_identical_commands(self):
        episode = make_episode()
        similarity = compare(episode, episode)
        self.assertEqual(similarity.behavior, 1.0)
        self.assertGreaterEqual(similarity.total, 0.0)
        self.assertLessEqual(similarity.total, 1.0)


class TestStore(unittest.TestCase):
    def test_recent_limit_none_and_ordering(self):
        with tempfile.TemporaryDirectory() as directory:
            store = EpisodeStore(Path(directory) / 'episodes.sqlite3')
            first = make_episode(created_at=1.0, evidence=('first',))
            second = make_episode(created_at=2.0, evidence=('second',))
            store.insert(first)
            store.insert(second)
            records = store.recent(limit=None)
            self.assertEqual(len(records), 2)
            self.assertEqual(records[0].created_at, 2.0)
            self.assertEqual(records[1].created_at, 1.0)

    def test_recent_limit_zero(self):
        with tempfile.TemporaryDirectory() as directory:
            store = EpisodeStore(Path(directory) / 'episodes.sqlite3')
            store.insert(make_episode())
            self.assertEqual(store.recent(limit=0), [])


class TestInterpreter(unittest.TestCase):
    def test_avoid_branch(self):
        result = interpret(Command(0.5, 0.0), Command(0.0, 0.0), 0.4, 1.0)
        self.assertEqual(result.kind, EpisodeKind.AVOID)
        self.assertGreater(result.confidence, 0.8)

    def test_wait_branch(self):
        result = interpret(Command(0.5, 0.0), Command(0.0, 0.1), 5.0, 1.0)
        self.assertEqual(result.kind, EpisodeKind.WAIT)

    def test_prefer_branch(self):
        result = interpret(Command(0.1, 0.0), Command(0.3, 0.0), 5.0, 1.0)
        self.assertEqual(result.kind, EpisodeKind.PREFER)

    def test_recovery_branch(self):
        result = interpret(Command(0.1, 0.0), Command(0.1, 0.5), 5.0, 1.0)
        self.assertEqual(result.kind, EpisodeKind.RECOVERY)

    def test_uncertain_branches(self):
        self.assertEqual(interpret(Command(0.1, 0.0), Command(0.12, 0.0), 5.0, 1.0).kind, EpisodeKind.UNCERTAIN)
        self.assertEqual(interpret(Command(0.1, 0.0), Command(0.1, 0.0), 5.0, 0.1).kind, EpisodeKind.UNCERTAIN)

    def test_boundary_magnitude(self):
        result = interpret(Command(0.0, 0.0), Command(0.12, 0.0), None, 0.5)
        self.assertIsNotNone(result)


class TestValidationAndAdvice(unittest.TestCase):
    def test_insufficient_context(self):
        stored = make_episode()
        current = make_episode(scan_signature=())
        result = validate(stored, current, now=101.0)
        self.assertEqual(result.status, ValidationStatus.INSUFFICIENT_CONTEXT)
        self.assertFalse(result.admissible)

    def test_contradicted(self):
        stored = make_episode(scan_signature=(0.3, 0.4, 0.5), created_at=1000.0)
        current = make_episode(scan_signature=(7.0, 7.0, 7.0), created_at=1001.0)
        result = validate(stored, current, now=1001.0)
        self.assertEqual(result.status, ValidationStatus.CONTRADICTED)
        self.assertFalse(result.admissible)

    def test_valid(self):
        stored = make_episode(created_at=100.0)
        current = make_episode(created_at=100.0)
        result = validate(stored, current, now=100.0)
        self.assertEqual(result.status, ValidationStatus.VALID)
        self.assertTrue(result.admissible)

    def test_advice_cap(self):
        stored = make_episode(confidence=10.0)
        current = make_episode(created_at=100.0)
        similarity = compare(stored, current)
        validation = validate(stored, current, now=100.0)
        advice = advise(stored, similarity, validation, maximum_absolute_bias=0.20)
        self.assertLessEqual(abs(advice.cost_bias), 0.20)

    def test_advice_abstains_on_contradiction(self):
        stored = make_episode()
        current = make_episode(scan_signature=(9.0, 9.0, 9.0))
        similarity = compare(stored, current)
        validation = validate(stored, current, now=101.0)
        advice = advise(stored, similarity, validation)
        self.assertEqual(advice.action, 'abstain')
        self.assertEqual(advice.cost_bias, 0.0)

    def test_advice_uncertain_zero_bias(self):
        stored = make_episode(kind=EpisodeKind.UNCERTAIN)
        current = make_episode()
        similarity = compare(stored, current)
        validation = validate(stored, current, now=100.0)
        advice = advise(stored, similarity, validation)
        self.assertEqual(advice.cost_bias, 0.0)


class TestPolicy(unittest.TestCase):
    def test_override_wins(self):
        policy = ArbitrationPolicy()
        policy.set_autonomy(PolicyCommand(0.3, 0.1), 10.0)
        policy.set_human(PolicyCommand(-0.2, -0.4), 10.0)
        policy.set_human_override(True)
        decision = policy.decide(10.1)
        self.assertEqual(decision.source, CommandSource.HUMAN)
        self.assertEqual(decision.command, PolicyCommand(-0.2, -0.4))

    def test_stale_override_stops(self):
        policy = ArbitrationPolicy(timeout_seconds=0.2)
        policy.set_autonomy(PolicyCommand(0.3, 0.0), 10.0)
        policy.set_human(PolicyCommand(0.1, 0.0), 10.0)
        policy.set_human_override(True)
        decision = policy.decide(10.3)
        self.assertEqual(decision.source, CommandSource.FAILSAFE_STOP)
        self.assertEqual(decision.command, PolicyCommand())

    def test_stale_autonomy_stops_and_clamps(self):
        policy = ArbitrationPolicy(timeout_seconds=0.2, max_linear=0.4, max_angular=1.0)
        policy.set_autonomy(PolicyCommand(9.0, -9.0), 10.0)
        self.assertEqual(policy.decide(10.1).command, PolicyCommand(0.4, -1.0))
        self.assertEqual(policy.decide(10.3).source, CommandSource.FAILSAFE_STOP)

    def test_no_fresh_source_stops(self):
        policy = ArbitrationPolicy()
        decision = policy.decide(1.0)
        self.assertEqual(decision.source, CommandSource.FAILSAFE_STOP)


class TestLedger(unittest.TestCase):
    def test_summary_multiple_configurations(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = TrialLedger(Path(directory) / 'trials.sqlite3')
            ledger.append(TrialRecord('A', 'scenario', True, 10.0, 4.0, 0, 0))
            ledger.append(TrialRecord('B', 'scenario', False, 20.0, 3.0, 1, 2))
            summary_a = ledger.summary('A', 'scenario')
            summary_b = ledger.summary('B', 'scenario')
            self.assertEqual(summary_a['trials'], 1)
            self.assertEqual(summary_b['trials'], 1)
            self.assertEqual(summary_b['total_collision_events'], 2)

    def test_empty_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = TrialLedger(Path(directory) / 'trials.sqlite3')
            summary = ledger.summary('missing', 'missing')
            self.assertEqual(summary['trials'], 0)


if ROS_AVAILABLE:
    class TestContext(unittest.TestCase):
        def test_scan_signature_empty(self):
            scan = LaserScan(ranges=[], range_min=0.1, range_max=10.0)
            self.assertEqual(scan_signature(scan), ())

        def test_scan_signature_sector_count(self):
            scan = LaserScan(ranges=[1.0] * 360, range_min=0.1, range_max=10.0)
            self.assertEqual(len(scan_signature(scan)), 24)

        def test_scan_signature_invalid_values_use_range_max(self):
            scan = LaserScan(ranges=[0.0] * 360, range_min=0.1, range_max=10.0)
            self.assertTrue(all(value == 10.0 for value in scan_signature(scan)))

        def test_scan_signature_sector_guard(self):
            scan = LaserScan(ranges=[1.0] * 10, range_min=0.1, range_max=10.0)
            self.assertEqual(len(scan_signature(scan, sectors=0)), 1)


class TestInterpretationEvaluation(unittest.TestCase):
    def test_labeled_set_covers_all_classes(self):
        expected = {item.expected for item in LABELED_INTERVENTIONS}
        self.assertEqual(expected, {EpisodeKind.AVOID, EpisodeKind.WAIT, EpisodeKind.PREFER,
                                    EpisodeKind.RECOVERY, EpisodeKind.UNCERTAIN})

    def test_confusion_matrix_diagonal_for_labeled_set(self):
        for example in LABELED_INTERVENTIONS:
            self.assertEqual(predict(example), example.expected)

    def test_classification_report_accuracy(self):
        report = classification_report(LABELED_INTERVENTIONS)
        self.assertEqual(report['accuracy'], 1.0)
        self.assertIn('avoid', report['per_class'])


class TestValidationEvaluation(unittest.TestCase):
    def test_evaluate_validation_metrics(self):
        stored = make_episode(scan_signature=(1.0, 1.0, 1.0), created_at=100.0)
        current_same = make_episode(scan_signature=(1.0, 1.0, 1.0), created_at=100.0)
        current_changed = make_episode(scan_signature=(9.0, 9.0, 9.0), created_at=101.0)
        cases = [
            ValidationCase(stored, current_same, 100.0, True),
            ValidationCase(stored, current_changed, 101.0, False, True),
        ]
        report = evaluate_validation(cases)
        self.assertEqual(report['trials'], 2)
        self.assertEqual(report['false_positive'], 0)
        self.assertEqual(report['false_negative'], 0)
        self.assertEqual(report['contradiction_detection_rate'], 1.0)


class TestRetrievalEvaluation(unittest.TestCase):
    def test_evaluate_retrieval(self):
        close = make_episode(created_at=100.0)
        far = make_episode(created_at=101.0, pose_x=10.0, scan_signature=(9.0, 9.0, 9.0))
        current = make_episode(created_at=100.0, kind=EpisodeKind.UNCERTAIN)
        case = RetrievalCase([far, close], current, {close.identifier}, minimum_similarity=0.1)
        report = evaluate_retrieval([case])
        self.assertEqual(report['queries'], 1)
        self.assertGreater(report['mean_precision'], 0.0)
        self.assertEqual(report['mean_reciprocal_rank'], 1.0)


if __name__ == '__main__':
    unittest.main()