"""Pure regression tests for readiness timeout behavior."""
import ast
import pathlib
import unittest


SOURCE = pathlib.Path(__file__).resolve().parents[1] / 'src/mnemos_slam/mnemos_slam/readiness_monitor.py'
TREE = ast.parse(SOURCE.read_text())
FUNCTION = next(node for node in TREE.body if isinstance(node, ast.FunctionDef) and node.name == 'fresh_inputs')
NAMESPACE = {}
exec(compile(ast.Module(body=[FUNCTION], type_ignores=[]), str(SOURCE), 'exec'), NAMESPACE)
fresh_inputs = NAMESPACE['fresh_inputs']


class TestFreshInputs(unittest.TestCase):
    def test_missing_and_expired_inputs_are_not_fresh(self):
        names = {'odom', 'scan'}
        self.assertEqual(fresh_inputs(names, {'odom': 10.0}, 12.0, 1.0), set())

    def test_recent_inputs_are_fresh(self):
        names = {'odom', 'scan'}
        self.assertEqual(fresh_inputs(names, {'odom': 10.5, 'scan': 10.9}, 11.0, 1.0), names)


if __name__ == '__main__':
    unittest.main()
