# Baseline SLAM and Navigation Runbook

This runbook covers only the conventional baseline. It does **not** claim that
MNEMOS memory, intervention interpretation, or cognitive cost adaptation are
implemented yet.

## Dependencies

The repository includes the project packages, but the host must also provide
the following Jazzy packages:

```bash
sudo apt-get update
sudo apt-get install -y \
  ros-jazzy-ros-gz-sim ros-jazzy-ros-gz-bridge \
  ros-jazzy-rtabmap-ros ros-jazzy-rtabmap-launch \
  ros-jazzy-nav2-bringup ros-jazzy-navigation2
```

## Build

```bash
cd /home/singh/mnemos-robotics
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Mapping

Start Gazebo Harmonic, the bridge, robot frame publication, and RTAB-Map:

```bash
ros2 launch mnemos_bringup slam.launch.py
```

In a second terminal, source the same overlays and drive conservatively:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/cmd_vel
```

Before interpreting mapping results, confirm input flow and TF:

```bash
ros2 topic echo /mnemos/slam_inputs_ready --once
ros2 topic hz /scan
ros2 topic hz /camera/image
ros2 run tf2_tools view_frames
```

`/mnemos/slam_inputs_ready=true` says that the monitor has seen all expected
inputs; it is not a quality metric and does not prove RTAB-Map localization.

Save a map only after inspecting the occupancy grid in RViz:

```bash
ros2 run nav2_map_server map_saver_cli -f $HOME/mnemos_map
```

## Navigation

Use the saved YAML map, not the image file:

```bash
ros2 launch mnemos_bringup navigation.launch.py map:=$HOME/mnemos_map.yaml
```

Set the initial pose in RViz, then use **Nav2 Goal**. The navigation path
starts AMCL/Nav2 and the same simulation. It is deliberately separate from
online RTAB-Map: combining localization sources without a deliberate
`map -> odom` ownership strategy causes TF conflicts.

## Acceptance criteria

1. `/odom`, `/scan`, camera image/depth/image-info, and `/cmd_vel` bridge in
   the specified directions.
2. RTAB-Map publishes a usable occupancy map while the robot is teleoperated.
3. A saved map can be loaded by Nav2; AMCL owns `map -> odom` in navigation
   mode.
4. The robot reaches at least ten unobstructed goals and rejects or replans
   around newly observed obstacles. Record successes, failures, timing, and
   intervention count before making performance claims.
