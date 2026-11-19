"""Verify readiness monitor shutdown is idempotent after an interrupt."""
import ast
import pathlib
import unittest


SOURCE = pathlib.Path(__file__).resolve().parents[1] / 'src/mnemos_slam/mnemos_slam/readiness_monitor.py'
TREE = ast.parse(SOURCE.read_text())
FUNCTION = next(node for node in TREE.body if isinstance(node, ast.FunctionDef) and node.name == 'main')


class TestReadinessShutdown(unittest.TestCase):
    def test_interrupt_masks_repeat_and_uses_try_shutdown(self):
        events = []

        class FakeNode:
            def destroy_node(self):
                events.append('destroy')

        class FakeRclpy:
            @staticmethod
            def init():
                events.append('init')

            @staticmethod
            def spin(_node):
                events.append('spin')
                raise KeyboardInterrupt

            @staticmethod
            def try_shutdown():
                events.append('shutdown')

        class FakeSignal:
            SIGINT = 'SIGINT'
            SIG_IGN = 'SIG_IGN'

            @staticmethod
            def signal(sig, handler):
                events.append((sig, handler))

        namespace = {
            'rclpy': FakeRclpy,
            'ReadinessMonitor': FakeNode,
            'signal': FakeSignal,
        }
        exec(compile(ast.Module(body=[FUNCTION], type_ignores=[]), str(SOURCE), 'exec'), namespace)
        namespace['main']()

        self.assertEqual(events, [
            'init', 'spin', ('SIGINT', 'SIG_IGN'), 'destroy', 'shutdown',
        ])


if __name__ == '__main__':
    unittest.main()
