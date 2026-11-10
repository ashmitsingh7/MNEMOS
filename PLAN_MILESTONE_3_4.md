# MNEMOS Milestone 3-4 Plan: RTAB-Map SLAM and Nav2 Navigation Integration

## Phase Objective

Integrate RTAB-Map SLAM and Nav2 navigation stack into the MNEMOS project to demonstrate baseline SLAM + navigation capabilities. This milestone establishes the foundation upon which all subsequent cognitive architecture (intervention learning, episodic memory, memory validation) will be built.

## Prerequisites (System Administration Required)

Before beginning this phase, the system administrator must install:

```bash
sudo apt update
sudo apt install -y ros2-jazzy-rtabmap-ros ros2-jazzy-rtabmap
sudo apt install -y ros2-jazzy-nav2-bringup ros2-jazzy-nav2
```

**Dependencies that will be pulled in**:
- `libignition-fuel-tools1`, `libignition-common1`, etc. (Gazebo plugins)
- `ros2-jazzy-nav2-*`, `ros2-jazzy-nav-msgs`, `ros2-jazzy-nav2-msgs`
- `ros2-jazzy-rtabmap-ros`, `ros2-jazzy-rtabmap`, `ros2-jazzy-libvision-aquila` (depth processing)

**Workspaces**:

```bash
# Create ROS 2 workspace if not existing
mkdir -p ~/mnemos_ws/src
cd ~/mnemos_ws/src

# Link or copy MNEMOS repository
ln -s /home/singh/mnemos-robotics mnemos

# Build
cd ~/mnemos_ws
colcon build --packages-select "mnemos_* rtabmap_* nav2_*"
source ~/mnemos_ws/install/setup.bash
```

## Phase 1: RTAB-Map SLAM Integration

### 1.1 Launch RTAB-Map with the Robot

Create `src/mnemos_bringup/launch/rtabmap_launch.py`:

```python
#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    mnemos_description_dir = get_package_share_directory('mnemos_robot_description')
    mnemos_simulation_dir = get_package_share_directory('mnemos_simulation')
    rtabmap_dir = get_package_share_directory('rtabmap_ros')

    use_sim_time = LaunchConfiguration('use_sim_time')
    world_name = LaunchConfiguration('world_name')

    declare_use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time', default_value='true',
        description='Use simulation clock')
    
    declare_world_arg = DeclareLaunchArgument(
        'world_name', default_value='lab_environment',
        description='Name of the world file to load')

    # Launch Gazebo with robot
    gazebo_cmd = [
        'gz', 'server',
        os.path.join(mnemos_simulation_dir, 'worlds', f'{world_name}.world')
    ]

    # Spawn robot (already in the world file, but ensure it's there)
    robot_spawn = ExecuteProcess(
        cmd=['gz', 'model', '-s', '-f', 
             os.path.join(mnemos_description_dir, 'mnemos_diff_drive.urdf')],
        output='screen')

    # Launch RTAB-Map
    rtabmap Launch = ExecuteProcess(
        cmd=['ros2', 'launch', 'rtabmap_ros', 'rtabmap.launch.py',
             '-f', os.path.join(mnemos_description_dir, 'mnemos_diff_drive.urdf'),
             '-o', 'rtabmap',  # Output directory for map/database
             '--ros-args', '-r', '__node:=rtabmap_slam'
        ],
        output='screen')

    # RViz2 with RTAB-Map configuration
    rviz_config = os.path.join(
        get_package_share_directory('rtabmap_rviz'), '配置/layout.rviz')
    rviz_node = ExecuteProcess(
        cmd=['rviz2', '-d', rviz_config],
        output='screen')

    ld = LaunchDescription()
    ld.add_action(declare_use_sim_time_arg)
    ld.add_action(declare_world_arg)
    ld.add_action(ExecuteProcess(cmd=gazebo_cmd, output='screen'))
    ld.add_action(robot_spawn)
    ld.add_action(rtabmap Launch)
    ld.add_action(rviz_node)

    return ld
```

### 1.2 Verify RTAB-Map Output

**Expected topics**:
- `/rtabmap/map` - Occupancy grid map
- `/rtabmap/odom` - RTAB-Map odometry pose
- `/rtabmap/rtabmap/goal` - Navigation goal (if using action)
- `/rtabmap/markers` - Detected features/markers
- `/camera/rgb/image_raw` - RGB image (if camera plugin active)
- `/camera/depth/image_raw` - Depth image (if camera plugin active)

**RViz2 Panels to Enable**:
- Map (OccupancyGrid)
- Pose Array (Markers)
- Image (for camera feed)
- TF (coordinate frame tree)

### 1.3 Test Mapping Loop

```bash
# In one terminal:
ros2 launch mnemos_bringup rtabmap_launch.py

# In another terminal:
ros2 topic echo /rtabmap/odom

# Move robot around with teleop
ros2 run teleop_twist_keyboard teleop_twist_keyboard
# Use: w/a/s/d to move, arrows to rotate

# Watch the map build in RViz2
rviz2
# Enable: Map panel, set Topic: /rtabmap/map
```

## Phase 2: Nav2 Navigation Stack Integration

### 2.1 Create Navigation Map

After RTAB-Map has built a map, save it:

```bash
# In RViz2, or via command line:
ros2 run nav2_map_saver map_saver_cli -f ~/mnemos_map

# This creates:
# ~/mnemos_map.pgm (map image)
# ~/mnemos_map.yaml (map metadata)
```

### 2.2 Create Nav2 Bringup Launch

Create `src/mnemos_bringup/launch/nav2_launch.py`:

```python
#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    mnemos_description_dir = get_package_share_directory('mnemos_robot_description')

    use_sim_time = LaunchConfiguration('use_sim_time')
    map_yaml_path = LaunchConfiguration('map')

    declare_use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time', default_value='true',
        description='Use simulation clock')

    declare_map_arg = DeclareLaunchArgument(
        'map', default_value=os.path.join(
            '/home/user', 'mnemos_map.yaml'),
        description='Full path to map yaml file to load')

    # Launch Gazebo (if not already running)
    gazebo_cmd = [
        'gz', 'server',
        os.path.join('/home/singh/mnemos-robotics/src/mnemos_simulation/worlds',
                       'lab_environment.world')
    ]

    # Launch robot spawn (same as before)
    robot_spawn = ExecuteProcess(...)

    # Launch Nav2 bringup
    nav2_launch = ExecuteProcess(
        cmd=['ros2', 'launch', 'nav2_bringup', 'bringup_launch.py',
             '--ros-args', '-r', '__node:=nav2_server'
        ],
        output='screen')

    ld = LaunchDescription()
    ld.add_action(declare_use_sim_time_arg)
    ld.add_action(declare_map_arg)
    ld.add_action(gazebo_cmd)
    ld.add_action(robot_spawn)
    ld.add_action(nav2_launch)

    return ld
```

### 2.3 Nav2 Parameters to Configure

Create `/home/singh/mnemos-robotics/config/nav2_params.yaml`:

```yaml
global_costmap:
  global_frame: 'map'
  robot_base_frame: 'base_link'
  update_frequency: 5.0
  publish_frequency: 2.0

local_costmap:
  global_frame: 'odom'
  robot_base_frame: 'base_link'
  update_frequency: 10.0
  publish_frequency: 2.0

robot_localization:
  combination_method: '2'
  ros2_parameters:
    publish_rate: 30.0
    odom0: /odom
    odom0_frame: 'odom'
    odom0_child_frame: 'base_link'
    imu0: /imu/data
    imu0_frame: 'imu_link'

planner_server:
  planner_plugin_id: 'GridBased'
  planner_configs:
    grid_size: 0.1
    inflation_radius: 0.5

bt_navigator:
  plugin: 'nav2_behavior_tree.BehaviorTreePlanner'
  bt_xml_file: '/opt/ros/jazzy/share/nav2_bt_navigator/bt_navigator.xml'

planner_server:
  planner_plugin_id: 'GridBased'
  planner_configs:
    allow_unknown: False

recovery_behavior_node:
  load_behaviors_from_cli: False
```

### 2.3 Test Navigation Loop

```bash
# Full navigation launch
ros2 launch mnemos_bringup nav2_launch.py map:=/home/user/mnemos_map.yaml

# In RViz2, enable:
# - Nav2 Panel (shows goal setting, path tracking)
# - Global Costmap
# - Local Costmap
# - TF

# Select "2D Nav Goal" button
# Click on the map to set a goal position
# robot will navigate to the goal while avoiding obstacles
```

## Phase 3: Integration Test

### 3.1 End-to-End Test Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  Start Gazebo + RTAB-Map                                              │
│  ↓                                                                  │
│  Robot spawns, RTAB-Map begins mapping                              │
│  ↓                                                                  │
│  Save map: ros2 run nav2_map_saver map_saver_cli -f mnemos_map   │
│  ↓                                                                  │
│  Start Nav2 with map                                                │
│  ↓                                                                  │
│  Set 2D Nav Goal in RViz2                                          │
│  ↓                                                                  │
│  Robot navigates to goal, avoids obstacles                          │
│  ↓                                                                  │
│  Record: ros2 topic echo /tf, /odom, /cmd_vel                     │
│  ↓                                                                  │
│  Evaluate: Did robot reach goal? Avoid obstacles?                   │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Success Criteria

**Navigation Success**: Robot reaches >80% of set goals without collision
**Mapping Coverage**: RTAB-Map builds consistent map of environment
**Localization**: Robot knows its position within the map
**Obstacle Avoidance**: No collisions with static or dynamic obstacles during 50+ test runs

### 3.3 Data to Record

```bash
# Record full navigation run
ros2 bag record /tf /odom /cmd_vel /scan /camera/depth/points /rtabmap/odom -o nav_run_001

# After test, analyze:
ros2 bag play nav_run_001.db3  # Replay to review

# Metrics to compute:
# - Path length vs. straight-line distance (efficiency)
# - Time to goal
# - Number of path replanning events
# - Collision count (should be 0)
# - Goal reach success rate
```

## Phase 4: Cognitive Architecture Bridge

### 4.1 Connect Cognitive Cost Function to Nav2

The cognitive decision cost function J(a) = alpha*C_path + beta*C_risk + gamma*C_memory + delta*C_uncertainty should influence Nav2's costmap:

```yaml
# In nav2_params.yaml, add cognitive layer costs:
local_costmap:
  plugins: ["cognitive_cost"]
  cognitive_cost:
    enable: true
    alpha: 1.0
    beta: 0.5
    gamma: 0.3
    delta: 0.2
    # Cost functions will be implemented as ROS 2 costmap plugins
```

### 4.2 Behavioral Tree Integration

Modify Nav2 BT to include cognitive layer decisions:

```xml
<!-- In bt_navigator.xml, add cognitive sequence -->
<BehaviorTree>
  <Sequence name="Cognitive Navigation">
    <Sleep time="0.1"/>
    <CheckAction feedback="true" action="/cmd_vel" />
    <NavigateToPose />
    <CognitiveCostCheck alpha="1.0" beta="0.5" gamma="0.3" delta="0.2" />
    <RecoveryBehaviors />
  </Sequence>
</BehaviorTree>
```

### 4.3 Experiment 1: Conventional Baseline

**Setup**: RTAB-Map + Nav2 only (no cognitive memory layers)

**Measurements** (per Experiment 1 spec):
- Navigation success rate
- Path length (meters)
- Time to goal (seconds)
- Collision count
- Navigation failures
- Intervention count (human overrides)

**Test Protocol**:
1. Set 20 random goals in the lab/warehouse environment
2. Record each navigation attempt
3. Compute average success rate, path efficiency, time
4. Compare against baseline without cognitive layers

### 4.3 Experiment Progression Path

Once Experiment 1 is working:

**Experiment 2**: Add intervention learning (teleoperation data capture)
**Experiment 3**: Add episodic memory retrieval and cost integration
**Experiment 4**: Add memory validation algorithm
**Experiment 5**: Full ablation study (A through D configurations)

## Installation Checklist

### ✅ Before Starting Phase 3-4

- [ ] Install RTAB-Map packages: `sudo apt install ros2-jazzy-rtabmap-ros ros2-jazzy-rtabmap`
- [ ] Install Nav2 packages: `sudo apt install ros2-jazzy-nav2-bringup ros2-jazzy-nav2`
- [ ] Verify: `ros2 launch rtabmap_ocs/rtabmap.launch.py` works
- [ ] Verify: `ros2 launch nav2_bringup bringup_launch.py` works
- [ ] Create map and save: `ros2 run nav2_map_saver map_saver_cli -f mnemos_map`
- [ ] Verify: `ros2 launch mnemos_bringup nav2_launch.py map:=/home/user/mnemos_map.yaml` works
- [ ] Verify: Robot can navigate to goals in RViz2 without cognitive layers
- [ ] Backup existing map/database files
- [ ] Document any configuration issues in ENVIRONMENT_AUDIT.md

### ✅ After Successful Integration

- [ ] RTAB-Map builds consistent map in Gazebo environment
- [ ] Nav2 navigates robot to goals without collisions
- [ ] Cognitive cost function framework is integrated (even if default weights)
- [ ] Experiment 1 data collected and recorded
- [ ] Framework ready for Experiments 2-5 incremental additions
- [ ] All results documented in docs/EXPERIMENT_RESULTS.md (or equivalent)

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| RTAB-Map fails to launch | Medium | High | Verify Gazebo plugins, check TF tree, review known issues |
| Nav2 fails to localize | Medium | High | Ensure map is saved, verify robot localization, check odometry |
| Cognitive cost integration breaks Nav2 | Low | Medium | Implement as optional plugin, default to Nav2-only mode |
| Memory invalidation bugs | Low | Medium | Test in sandbox, revert to safe mode if issues arise |
| Git repository conflicts | Low | Low | Pull before making changes, commit frequently |

## Success Definition

**Phase 3-4 Complete When**:
1. RTAB-Map builds consistent map of Gazebo environment
2. Nav2 navigates robot to randomly set goals with >80% success rate
3. No collisions recorded during 50+ test navigation runs
4. All data logged and measurable metrics computed
5. Framework ready for incremental cognitive architecture additions
6. Results documented and commit to GitHub

## Next Steps After Phase 3-4

Once baseline SLAM + navigation is working:

1. **Experiment 2**: Implement teleoperation data capture and intervention learning
2. **Experiment 3**: Implement episodic memory retrieval and integration into Nav2 cost function
3. **Experiment 4**: Implement memory validation algorithm (context comparison, outcome consistency)
4. **Experiment 5**: Full ablation study (A through D configurations)
5. **Documentation**: Record all results in docs/EXPERIMENT_RESULTS.md
6. **Thesis/Report**: Write up findings and hypothesis validation

---
*This plan is ready for execution upon RTAB-Map and Nav2 package installation.*