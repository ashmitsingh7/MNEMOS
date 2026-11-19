"""Expose whether the minimum live-sensor set needed by MNEMOS is available."""
from dataclasses import dataclass
import signal
import time

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


def fresh_inputs(required, last_seen, now, timeout):
    """Return names with a recent monotonic receipt time."""
    return {name for name in required if now - last_seen.get(name, float('-inf')) <= timeout}


class ReadinessMonitor(Node):
    """Publish fresh-input readiness; freshness uses monotonic wall time, not sim time."""
    def __init__(self) -> None:
        super().__init__('mnemos_slam_readiness_monitor')
        self.inputs = Inputs()
        self.declare_parameter('input_timeout_sec', 2.5)
        self.input_timeout = float(self.get_parameter('input_timeout_sec').value)
        self.last_seen = {}
        self.publisher = self.create_publisher(Bool, '/mnemos/slam_inputs_ready', 1)
        for message_type, topic, field in (
            (LaserScan, '/scan', 'scan'),
            (Image, '/camera/image', 'rgb'), (Image, '/camera/depth_image', 'depth'),
            (CameraInfo, '/camera/camera_info', 'camera_info'),
        ):
            self.create_subscription(message_type, topic, lambda _, name=field: self._seen(name), 10)
        self.create_subscription(Odometry, '/odom', self._odom, 10)
        self.create_timer(1.0, self._publish)

    def _seen(self, field: str) -> None:
        self.last_seen[field] = time.monotonic()

    def _odom(self, message: Odometry) -> None:
        self._seen('odom')

    def _publish(self) -> None:
        now = time.monotonic()
        fresh = fresh_inputs(vars(self.inputs), self.last_seen, now, self.input_timeout)
        for field in vars(self.inputs):
            setattr(self.inputs, field, field in fresh)
        self.publisher.publish(Bool(data=self.inputs.ready))
        if not self.inputs.ready:
            missing = [name for name, value in vars(self.inputs).items() if not value]
            self.get_logger().warn('SLAM input(s) not observed: ' + ', '.join(missing), throttle_duration_sec=10.0)


def main() -> None:
    rclpy.init()
    node = ReadinessMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Launch sends SIGINT to children too. Ignore repeats while tearing down.
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        node.destroy_node()
        rclpy.try_shutdown()
