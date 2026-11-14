"""ROS adapter for memory advice; it publishes an audit record, not /cmd_vel."""
import json
from math import atan2

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32, String

from mnemos_memory.context import scan_signature
from mnemos_memory.model import Episode, EpisodeKind
from mnemos_memory.retrieval import retrieve
from mnemos_memory.store import EpisodeStore
from .advice import advise
from .validation import validate


class MemoryAdvisor(Node):
    def __init__(self) -> None:
        super().__init__('mnemos_memory_advisor')
        self.declare_parameter('database_path', '~/.ros/mnemos_episodes.sqlite3')
        self.declare_parameter('minimum_similarity', 0.55)
        self.declare_parameter('contradiction_threshold', 0.25)
        self.declare_parameter('maximum_age_seconds', 60 * 60 * 24 * 21)
        self.declare_parameter('map_session_id', 'default')
        self.store = EpisodeStore(self.get_parameter('database_path').value)
        self.pose: tuple[float, float, float] | None = None
        self.signature: tuple[float, ...] = ()
        self.cost_publisher = self.create_publisher(Float32, '/mnemos/memory_cost_bias', 10)
        self.audit_publisher = self.create_publisher(String, '/mnemos/memory_advice', 10)
        self.create_subscription(Odometry, '/odom', self._odom, 10)
        self.create_subscription(LaserScan, '/scan', self._scan, 10)
        self.create_timer(0.5, self._advise)

    def _odom(self, message: Odometry) -> None:
        orientation = message.pose.pose.orientation
        yaw = atan2(2 * (orientation.w * orientation.z + orientation.x * orientation.y),
                    1 - 2 * (orientation.y * orientation.y + orientation.z * orientation.z))
        position = message.pose.pose.position
        self.pose = (position.x, position.y, yaw)

    def _scan(self, message: LaserScan) -> None:
        self.signature = scan_signature(message)

    def _advise(self) -> None:
        if self.pose is None or not self.signature:
            self.cost_publisher.publish(Float32(data=0.0))
            return
        current = Episode(EpisodeKind.UNCERTAIN, *self.pose, self.signature,
                         map_session_id=self.get_parameter('map_session_id').value)
        matches = retrieve(self.store.recent(), current, self.get_parameter('minimum_similarity').value, limit=1)
        if not matches:
            self.cost_publisher.publish(Float32(data=0.0))
            return
        episode, similarity = matches[0]
        recommendation = advise(episode, similarity, validate(
            episode, current,
            contradiction_threshold=self.get_parameter('contradiction_threshold').value,
            maximum_age_seconds=self.get_parameter('maximum_age_seconds').value))
        self.cost_publisher.publish(Float32(data=recommendation.cost_bias))
        self.audit_publisher.publish(String(data=json.dumps({
            'episode_id': episode.identifier, 'action': recommendation.action,
            'confidence': recommendation.confidence, 'cost_bias': recommendation.cost_bias,
            'explanation': recommendation.explanation,
        })))


def main() -> None:
    rclpy.init()
    node = MemoryAdvisor()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
