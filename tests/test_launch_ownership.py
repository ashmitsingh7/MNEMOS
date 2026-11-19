"""Regression checks for single-owner simulation launch composition."""
import ast
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
LAUNCH = ROOT / 'src' / 'mnemos_bringup' / 'launch'


def source(name):
    return (LAUNCH / name).read_text()


class TestLaunchOwnership(unittest.TestCase):
    def test_launch_files_parse(self):
        for path in LAUNCH.glob('*.launch.py'):
            with self.subTest(path=path.name):
                ast.parse(path.read_text())

    def test_slam_attaches_without_starting_simulation_or_readiness(self):
        code = source('slam.launch.py')
        self.assertNotIn('simulation.launch.py', code)
        self.assertNotIn('readiness_monitor', code)

    def test_navigation_is_independent_by_default(self):
        self.assertIn("DeclareLaunchArgument('with_simulation', default_value='false'", source('navigation.launch.py'))

    def test_canonical_simulation_owns_infrastructure_once(self):
        code = source('simulation.launch.py')
        self.assertEqual(code.count("executable='parameter_bridge'"), 1)
        self.assertEqual(code.count("executable='robot_state_publisher'"), 1)
        self.assertEqual(code.count("executable='readiness_monitor'"), 1)

    def test_composite_starts_simulation_once_and_disables_nested_copy(self):
        code = source('full_system.launch.py')
        self.assertEqual(code.count("'launch' / 'simulation.launch.py'"), 1)
        self.assertIn("'with_simulation': 'false'", code)


if __name__ == '__main__':
    unittest.main()
