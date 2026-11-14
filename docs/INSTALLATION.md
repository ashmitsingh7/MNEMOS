# MNEMOS Installation Guide

## Prerequisites

### OS: Ubuntu 24.04 LTS (Noble Numbat)

Confirmed:
- Ubuntu 24.04.5 LTS (from environment check)
- Python 3.12.3

### ROS 2 Jazzy Installation

If ROS 2 Jazzy is not yet installed, install it:

```bash
# Setup repositories
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository universe

# Add ROS 2 Jazzy repository
sudo sh -c 'echo "deb http://packages.ros.org/ros2/ubuntu noble main" > /etc/apt/sources.list.d/ros2-latest.list'
curl -s https://raw.githubusercontent.com/ros/ros2/jazzy/ros2/release.key | sudo apt-key add -

# Install ROS 2 Jazzy
sudo apt update
sudo apt install -y ros2-jazzy-desktop
```

### Initialize ros2 environment

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

Verify:

```bash
ros2 --version
# Expected output: rclpy 2.XXX.0
```

### Gazebo Harmonic Installation

```bash
# Install Gazebo Harmonic
sudo apt update
sudo apt install -y gz-harmonic

# Verify
gz sim -v
# Expected output: Gazebo Sim 8
```

## Python Dependencies

### Required Packages

```bash
pip3 install numpy opencv-python pyoctomap rtabmap-ros
```

### Optional / Recommended

```bash
pip3 install torch torchvision  # PyTorch for DL components
pip3 install fastapi uvicorn    # Web interface for teleoperation
pip3 install pytest pytest-ros2  # Testing
```

## ROS 2 Packages

### Install Navigation Stack

```bash
sudo apt install -y ros2-jazzy-nav2-bringup ros2-jazzy-nav2 ros2-jazzy-nav2-msgs
```

### Install RTAB-Map Stack

```bash
sudo apt install -y ros2-jazzy-rtabmap-ros ros2-jazzy-rtabmap
```

### Install Slam Toolbox (alternative)

```bash
sudo apt install -y ros2-jazzy-slam-toolbox
```

## Verification

After installation, verify each component:

```bash
# Check ROS 2
ros2 --version

# Check Gazebo
gz sim -v

# Check Python packages
python3 -c "import cv2; print(f'OpenCV {cv2.__version__}')"
python3 -c "import numpy; print(f'NumPy {numpy.__version__}')"
# python3 -c "import torch; print(f'PyTorch {torch.__version__}')"  # if installed
```

## ROS 2 Workspace Setup

```bash
# Create workspace
mkdir -p ~/mnemos_ws/src
cd ~/mnemos_ws/src

# Clone or link mnemos-robotics
ln -s /home/singh/mnemos-robotics mnemos

# Build
cd ~/mnemos_ws
colcon build --packages-select mnemos_*

# Source
source ~/mnemos_ws/install/setup.bash
```

## Simulation Verification

```bash
# Launch Gazebo with robot
ros2 launch mnemos_simulation robot_world.launch.py

# Verify robot spawns
# Check TF tree
ros2 run tf2_ros tf2echo /world /base_link

# Check RViz2
ros2 run rviz2
```

## Perception Setup

```bash
# Install pretrained models or download as needed
# See mnemos_perception package for specifics
```

## Intervention Interface

```bash
# The teleoperation interface runs as a Python web server
# Start it with: python3 mnemos_teleoperation/launch/server.py
# Or: ros2 run mnemos_teleoperation server_node
```

## Evaluation Framework

```bash
# Experiment configs are in config/ directory
# Run experiments via: ros2 run mnemos_evaluation experiment_name
```

## Troubleshooting

Common issues and resolutions:

1. **Gazebo fails to launch**: Verify `gz-harmonic` is installed and Ubuntu 24.04
2. **ROS 2 commands not found**: Source the setup.bash file
3. **RTAB-Map not launching**: Ensure `ros2-jazzy-rtabmap-ros` is installed
4. **Nav2 not loading**: Verify navigation stack packages are installed
5. **TF tree errors**: Check coordinate frame names and transformations
6. **PyTorch import failure**: May need `pip3 install torch` compatible with Python 3.12

## Next Steps After Installation

1. Build the workspace: `colcon build --packages-select mnemos_*`
2. Source the setup: `source ~/mnemos_ws/install/setup.bash`
3. Launch simulation: `ros2 launch mnemos_simulation robot_world.launch.py`
4. Verify robot spawns and sensors publish
5. Run RViz2 visualization
6. Proceed to Milestone 1: Environment and Robot Verification
```

## User-space Nav2/RTAB-Map overlay (no sudo)

On machines where `sudo apt install` is unavailable, Nav2 and RTAB-Map can be
downloaded with `apt-get download` and extracted into a user prefix. This
repository has been validated with such an overlay.

```bash
mkdir -p ~/ros2_nav2/debs ~/ros2_nav2/prefix
cd ~/ros2_nav2/debs
# Download the RTAB-Map + Nav2 package set and transitive system libs, then:
for deb in *.deb; do dpkg -x "$deb" ~/ros2_nav2/prefix; done
```

Source the overlay before building/running MNEMOS:

```bash
export AMENT_PREFIX_PATH=~/ros2_nav2/prefix/opt/ros/jazzy:/opt/ros/jazzy
export LD_LIBRARY_PATH=~/ros2_nav2/prefix/opt/ros/jazzy/lib:~/ros2_nav2/prefix/opt/ros/jazzy/lib/x86_64-linux-gnu:~/ros2_nav2/prefix/usr/lib:~/ros2_nav2/prefix/usr/lib/x86_64-linux-gnu:/opt/ros/jazzy/lib:${LD_LIBRARY_PATH}
source /opt/ros/jazzy/setup.bash
```

Verified working: `ros2 launch mnemos_bringup slam.launch.py` starts Gazebo,
RTAB-Map, and the readiness monitor (reports `slam_inputs_ready: true`).