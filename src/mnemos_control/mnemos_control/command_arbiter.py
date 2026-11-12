"""Owns final /cmd_vel; it keeps autonomy and human intent observable upstream."""
import json
from time import monotonic

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Bool, String

from .policy import ArbitrationPolicy, Command


class CommandArbiter(Node):
    def __init__(self) -> None:
        super().__init__('mnemos_command_arbiter')
        self.declare_parameter('timeout_seconds', 0.35)
        self.declare_parameter('max_linear_speed', 0.45)
        self.declare_parameter('max_angular_speed', 1.50)
        self.policy = ArbitrationPolicy(self.get_parameter('timeout_seconds').value,
                                        self.get_parameter('max_linear_speed').value,
                                        self.get_parameter('max_angular_speed').value)
        self.output = self.create_publisher(Twist, '/cmd_vel', 10)
        self.status = self.create_publisher(String, '/mnemos/command_arbitration', 10)
        self.create_subscription(Twist, '/cmd_vel_autonomy', self._autonomy, 10)
        self.create_subscription(Twist, '/cmd_vel_human', self._human, 10)
        self.create_subscription(Bool, '/mnemos/human_override', self._override, 10)
        self.create_timer(0.05, self._publish)

    def _autonomy(self, message: Twist) -> None:
        self.policy.set_autonomy(Command(message.linear.x, message.angular.z), monotonic())

    def _human(self, message: Twist) -> None:
        self.policy.set_human(Command(message.linear.x, message.angular.z), monotonic())

    def _override(self, message: Bool) -> None:
        self.policy.set_human_override(message.data)

    def _publish(self) -> None:
        decision = self.policy.decide(monotonic())
        output = Twist()
        output.linear.x, output.angular.z = decision.command.linear, decision.command.angular
        self.output.publish(output)
        self.status.publish(String(data=json.dumps({'source': decision.source.value, 'reason': decision.reason})))


def main() -> None:
    rclpy.init()
    node = CommandArbiter()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
