"""Create episodes at intervention boundaries from explicitly separated command streams."""
from math import atan2, hypot
from time import monotonic

import rclpy
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool, String

from mnemos_memory.model import Episode
from mnemos_memory.context import scan_signature
from mnemos_memory.store import EpisodeStore
from .interpreter import Command, interpret


class InterventionRecorder(Node):
    """Records only a sustained, measurable human/autonomy command disagreement."""
    def __init__(self) -> None:
        super().__init__('mnemos_intervention_recorder')
        self.declare_parameter('database_path', '~/.ros/mnemos_episodes.sqlite3')
        self.declare_parameter('minimum_duration_seconds', 0.4)
        self.declare_parameter('map_session_id', 'default')
        self.declare_parameter('bag_reference', '')
        self.store = EpisodeStore(self.get_parameter('database_path').value)
        self.autonomous = Command(0.0, 0.0)
        self.human = Command(0.0, 0.0)
        self.pose: tuple[float, float, float] | None = None
        self.signature: tuple[float, ...] = ()
        self.nearest_obstacle: float | None = None
        self.human_override = False
        self.started_at: float | None = None
        self.recorded = False
        self.goal: tuple[float, float] | None = None
        self.publisher = self.create_publisher(String, '/mnemos/intervention_events', 10)
        self.create_subscription(Twist, '/cmd_vel_autonomy', self._autonomous, 10)
        self.create_subscription(Twist, '/cmd_vel_human', self._human, 10)
        self.create_subscription(Odometry, '/odom', self._odom, 10)
        self.create_subscription(LaserScan, '/scan', self._scan, 10)
        self.create_subscription(Bool, '/mnemos/human_override', self._override, 10)
        self.create_subscription(PoseStamped, '/goal_pose', self._goal, 10)
        self.create_timer(0.05, self._evaluate)

    def _autonomous(self, message: Twist) -> None:
        self.autonomous = Command(message.linear.x, message.angular.z)

    def _human(self, message: Twist) -> None:
        self.human = Command(message.linear.x, message.angular.z)

    def _odom(self, message: Odometry) -> None:
        q = message.pose.pose.orientation
        yaw = atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
        p = message.pose.pose.position
        self.pose = (p.x, p.y, yaw)

    def _scan(self, message: LaserScan) -> None:
        self.signature = scan_signature(message)
        valid = [value for value in message.ranges if message.range_min <= value <= message.range_max]
        self.nearest_obstacle = min(valid) if valid else None

    def _override(self, message: Bool) -> None:
        self.human_override = message.data

    def _goal(self, message: PoseStamped) -> None:
        self.goal = (message.pose.position.x, message.pose.position.y)

    def _evaluate(self) -> None:
        divergence = hypot(self.human.linear - self.autonomous.linear,
                           self.human.angular - self.autonomous.angular)
        now = monotonic()
        if self.human_override and divergence >= 0.12:
            self.started_at = self.started_at or now
            if self.recorded or self.pose is None or not self.signature:
                return
            duration = now - self.started_at
            result = interpret(self.autonomous, self.human, self.nearest_obstacle, duration,
                               self.get_parameter('minimum_duration_seconds').value)
            if result.confidence <= 0.0:
                return
            episode = Episode(result.kind, *self.pose, self.signature,
                              command_delta_linear=self.human.linear - self.autonomous.linear,
                              command_delta_angular=self.human.angular - self.autonomous.angular,
                              confidence=result.confidence, evidence=result.evidence,
                              goal_x=self.goal[0] if self.goal else None,
                              goal_y=self.goal[1] if self.goal else None,
                              map_session_id=self.get_parameter('map_session_id').value,
                              autonomous_command_linear=self.autonomous.linear,
                              autonomous_command_angular=self.autonomous.angular,
                              human_command_linear=self.human.linear,
                              human_command_angular=self.human.angular,
                              intervention_started_at=self.started_at,
                              intervention_ended_at=now,
                              bag_reference=self.get_parameter('bag_reference').value or None)
            self.store.insert(episode)
            self.recorded = True
            self.publisher.publish(String(data=episode.identifier))
            self.get_logger().info(f'Recorded {result.kind.value} episode {episode.identifier}')
        else:
            self.started_at = None
            self.recorded = False


def main() -> None:
    rclpy.init()
    node = InterventionRecorder()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
