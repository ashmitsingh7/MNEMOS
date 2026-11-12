from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/mnemos_control'))

from mnemos_control.policy import ArbitrationPolicy, Command, CommandSource


class TestArbitrationPolicy(unittest.TestCase):
    def test_human_override_wins_over_autonomy(self):
        policy = ArbitrationPolicy()
        policy.set_autonomy(Command(0.3, 0.1), 10.0)
        policy.set_human(Command(-0.2, -0.4), 10.0)
        policy.set_human_override(True)
        decision = policy.decide(10.1)
        self.assertEqual(decision.source, CommandSource.HUMAN)
        self.assertEqual(decision.command, Command(-0.2, -0.4))

    def test_stale_override_command_stops_instead_of_falling_back(self):
        policy = ArbitrationPolicy(timeout_seconds=0.2)
        policy.set_autonomy(Command(0.3, 0.0), 10.0)
        policy.set_human(Command(0.1, 0.0), 10.0)
        policy.set_human_override(True)
        decision = policy.decide(10.3)
        self.assertEqual(decision.source, CommandSource.FAILSAFE_STOP)
        self.assertEqual(decision.command, Command())

    def test_stale_autonomy_stops_and_speed_is_clamped(self):
        policy = ArbitrationPolicy(timeout_seconds=0.2, max_linear=0.4, max_angular=1.0)
        policy.set_autonomy(Command(9.0, -9.0), 10.0)
        self.assertEqual(policy.decide(10.1).command, Command(0.4, -1.0))
        self.assertEqual(policy.decide(10.3).source, CommandSource.FAILSAFE_STOP)


if __name__ == '__main__':
    unittest.main()
