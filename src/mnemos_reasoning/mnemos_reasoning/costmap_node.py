"""ROS 2 node demonstrating the bounded MNEMOS costmap adapter contract.

This node consumes `/mnemos/memory_cost_bias` and maintains an in-memory
cost patch ledger. It does NOT modify any Nav2 costmap; a real integration
would implement CostmapAdapter against the Nav2 costmap API.
"""
from __future__ import annotations

import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String

from .costmap_adapter import InMemoryCostmapAdapter, CostPatch


class MnemosCostmapNode(Node):
    def __init__(self) -> None:
        super().__init__("mnemos_costmap_adapter")
        self.declare_parameter("maximum_absolute_bias", 0.35)
        self.adapter = InMemoryCostmapAdapter(
            self.get_parameter("maximum_absolute_bias").value)
        self.create_subscription(Float32, "/mnemos/memory_cost_bias", self._bias, 10)
        self.create_subscription(String, "/mnemos/memory_advice", self._advice, 10)
        self.get_logger().info("MNEMOS costmap adapter (reference) started.")

    def _bias(self, message: Float32) -> None:
        self.get_logger().debug(f"Received memory bias: {message.data:.3f}")

    def _advice(self, message: String) -> None:
        try:
            payload = json.loads(message.data)
        except json.JSONDecodeError:
            self.get_logger().warn("Invalid advice payload; ignored.")
            return
        episode_id = payload.get("episode_id")
        if episode_id is None:
            return
        patch = CostPatch(cost_bias=float(payload.get("cost_bias", 0.0)),
                          episode_id=episode_id,
                          explanation=tuple(payload.get("explanation", [])))
        try:
            self.adapter.apply(patch)
        except ValueError as exc:
            self.get_logger().warn(str(exc))

    def main() -> None:
        pass


def main() -> None:
    rclpy.init()
    node = MnemosCostmapNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
