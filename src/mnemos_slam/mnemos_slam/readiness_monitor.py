"""Expose whether the minimum live-sensor set needed by MNEMOS is available."""
from dataclasses import dataclass

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, Image, LaserScan
from std_msgs.msg import Bool


@dataclass
class Inputs:
    odom: bool = False
    scan: bool = False
    rgb: bool = False
    depth: bool = False
    camera_info: bool = False

    @property
    def ready(self) -> bool:
        return all((self.odom, self.scan, self.rgb, self.depth, self.camera_info))


class ReadinessMonitor(Node):
    """Publishes ``/mnemos/slam_inputs_ready`` without pretending SLAM is healthy."""
    def __init__(self) -> None:
        super().__init__('mnemos_slam_readiness_monitor')
        self.inputs = Inputs()
        self.publisher = self.create_publisher(Bool, '/mnemos/slam_inputs_ready', 1)
        for message_type, topic, field in (
            (Odometry, '/odom', 'odom'), (LaserScan, '/scan', 'scan'),
            (Image, '/camera/image', 'rgb'), (Image, '/camera/depth_image', 'depth'),
            (CameraInfo, '/camera/camera_info', 'camera_info'),
        ):
            self.create_subscription(message_type, topic, lambda _, name=field: self._seen(name), 10)
        self.create_timer(1.0, self._publish)

    def _seen(self, field: str) -> None:
        setattr(self.inputs, field, True)

    def _publish(self) -> None:
        self.publisher.publish(Bool(data=self.inputs.ready))
        if not self.inputs.ready:
            missing = [name for name, value in vars(self.inputs).items() if not value]
            self.get_logger().warn('SLAM input(s) not observed: ' + ', '.join(missing), throttle_duration_sec=10.0)


def main() -> None:
    rclpy.init()
    node = ReadinessMonitor()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
