# MNEMOS Execution Roadmap - Milestone 3-4

## Phase Objective
Integrate RTAB-Map SLAM and Nav2 navigation stack into the MNEMOS project to demonstrate baseline SLAM + navigation capabilities, establishing the foundation for all subsequent cognitive architecture development.

## ⚠️ Prerequisite: Package Installation

**Action Required** (system administrator or user with sudo access):

```bash
# From the MNEMOS project directory
cd /home/singh/mnemos-robotics

# Install RTAB-Map stack (RGB-D SLAM)
sudo apt-get update
sudo apt-get install -y ros2-jazzy-rtabmap-ros ros2-jazzy-rtabmap

# Install Nav2 navigation stack
sudo apt-get install -y ros2-jazzy-nav2-bringup ros2-jazzy-nav2

# Install additional useful packages
sudo apt-get install -y ros2-jazzy-map-server ros2-jazzy-navigation2
```

**Verify Installation**:
```bash
ros2 launch rtabmap_ocs/rtabmap.launch.py 2>&1 | head -10
ros2 launch nav2_bringup bringup_launch.py 2>&1 | head -10
```

## 📦 Phase 1: RTAB-Map SLAM Integration

### Step 1.1: Launch RTAB-Map with the MNEMOS Robot

**File**: `src/mnemos_bringup/launch/rtabmap_launch.py`

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

    use_sim_time = LaunchConfiguration('use_sim_time')
    world_name = LaunchConfiguration('world_name')

    # Launch arguments
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time', default_value='true',
        description='Use simulation clock')
    
    declare_world = DeclareLaunchArgument(
        'world_name', default_value='lab_environment',
        description='Gazebo world name')

    # Launch Gazebo with selected world
    gazebo_cmd = [
        'gz', 'server',
        os.path.join(mnemos_simulation_dir, 'worlds', f'{world_name}.world')
    ]

    # Spawn the MNEMOS robot (already included in world files, 
    # but launch explicitly for clarity)
    robot_spawn = ExecuteProcess(
        cmd=['gz', 'model', '-s', '-f', 
             os.path.join(mnemos_description_dir, 'mnemos_diff_drive.urdf')],
        output='screen')

    # Launch RTAB-Map with the robot
    rtabmap_launch = ExecuteProcess(
        cmd=['ros2', 'launch', 'rtabmap_ros', 'rtabmap.launch.py',
             '-r', '__ns:=/rtabmap',  # Namespace for clarity
             '-o', os.path.join(os.path.expanduser('~'), 'mnemos_map'),  # Map output dir
        ],
        output='screen')

    # Launch RViz2 with RTAB-Map configuration for visualization
    rviz_cmd = [
        'rviz2',
        '-d', os.path.join(
            get_package_share_directory('rtabmap_rviz'), 'layout.rviz')
    ]

    ld = LaunchDescription()
    ld.add_action(declare_use_sim_time)
    ld.add_action(declare_world)
    ld.add_action(ExecuteProcess(cmd=gazebo_cmd, output='screen'))
    ld.add_action(robot_spawn)
    ld.add_action(rtabmap_launch)
    ld.add_action(rviz_cmd)

    return ld
```

**Expected Output**: 
- Gazebo window opens with lab_environment or warehouse_environment
- MNEMOS differential-drive robot spawns
- RTAB-Map begins SLAM processing
- RViz2 opens with map, pose, and image panels

### Step 1.2: Verify RTAB-Map Output

**Topics to Check**:
```bash
# List all RTAB-Map related topics
ros2 topic list | grep rtabmap

# Expected topics:
# /rtabmap/map - Occupancy grid map
# /rtabmap/odom - RTAB-Map estimated odometry  
# /rtabmap/imu_data - IMU data (if configured)
# /rtabmap/markers - Detected features
# /camera/rgb/image_raw - RGB image (if camera plugin active)
# /camera/depth/image_raw - Depth image (if camera plugin active)
```

**RViz2 Panels to Enable**:
1. **Map** - Shows the SLAM-built occupancy grid
2. **Pose Array** - Shows detected robot poses (markers)
3. **Image** - RGB camera feed (if enabled)
4. **TF** - Coordinate frame tree verification

### Step 1.3: Test Mapping Capability

```bash
# Launch RTAB-Map + robot
ros2 launch mnemos_bringup rtabmap_launch.py

# In another terminal, teleop the robot
ros2 run teleop_twist_keyboard teleop_twist_keyboard
# Use wasd arrows to move the robot around

# Watch the map build in RViz2
rviz2
# Enable the "Map" panel - you should see the map grow as you move

# After some exploration, save the map:
ros2 run nav2_map_saver map_saver_cli -f ~/mnemos_map
# This creates mnemos_map.pkg and mnemos_map.yaml
```

### Step 1.3 Troubleshooting RTAB-Map

**Common Issues**:
- **No map appearing**: Check `/rtabmap/map` topic is publishing, verify RViz2 "Map" panel topic is set correctly
- **Robot not localizing**: Verify `/odom` topic is publishing, check `/tf` tree for proper transforms
- **Poor map quality**: Move robot more varied paths, ensure adequate lighting (in real world), check camera parameters
- **Depth issues**: Verify `/camera/depth/image_raw` is publishing, check `/camera/rgb/image_raw` is also publishing

## Phase 2: Nav2 Navigation Stack Integration

### Step 2.1: Create Navigation Map

After RTAB-Map has built a map (or use the saved map from Step 1.3):

```bash
# If you saved in Step 1.3:
ls ~/mnemos_map.pgm  # Should exist

# Or re-save the current map:
ros2 run nav2_map_saver map_saver_cli -f ~/mnemos_final_map
# Creates: mnemos_final_map.pkg + mnemos_final_map.yaml
```

**Verify the map yaml** has correct parameters:
```yaml
# ~/mnemos_final_map.yaml Example
image: mnemos_final_map.pgm
resolution: 0.050000
origin: [-1.500000, -1.500000, 0.000000]  # x, y, theta
mode: 0
```

### Step 2.2: Launch Nav2 with the MNEMOS Map

**File**: `src/mnemos_bringup/launch/nav2_launch.py`

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
    map_path = LaunchConfiguration('map')

    # Launch arguments
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time', default_value='true',
        description='Use simulation clock')
    
    declare_map = DeclareLaunchArgument(
        'map', default_value=os.path.join(
            '/home/user', 'mnemos_final_map.yaml'),
        description='Full path to map yaml file')

    # Launch Gazebo (if not already running from RTAB-Map step)
    gazebo_cmd = [
        'gz', 'server',
        os.path.join('/home/singh/mnemos-robotics/src/mnemos_simulation/worlds',
                       'lab_environment.world')
    ]

    # Spawn the robot
    robot_spawn = ExecuteProcess(
        cmd=['gz', 'model', '-s', '-f', 
             os.path.join(mnemos_description_dir, 'mnemos_diff_drive.urdf')],
        output='screen')

    # Launch Nav2 bringup
    nav2_launch = ExecuteProcess(
        cmd=['ros2', 'launch', 'nav2_bringup', 'bringup_launch.py',
             '--ros-args', '-r', '__node:=nav2'],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen')

    ld = LaunchDescription()
    ld.add_action(declare_use_sim_time)
    ld.add_action(declare_map)
    ld.add_action(gazebo_cmd)
    ld.add_action(robot_spawn)
    ld.add_action(nav2_launch)

    return ld
```

### Step 2.3: Configure Nav2 Parameters

**File**: `config/nav2_params.yaml`

```yaml
# Global costmap settings
global_costmap:
  global_frame: 'map'
  robot_base_frame: 'base_link'
  update_frequency: 5.0
  publish_frequency: 2.0
  width: 6.0  # meters
  height: 6.0

# Local costmap settings
local_costmap:
  global_frame: 'odom'
  robot_base_frame: 'base_link'
  update_frequency: 10.0
  publish_frequency: 2.0
  width: 3.0  # meters
  height: 3.0

# Robot localization (odometry + IMU fusion)
robot_localization:
  combination_method: '2'
  ros2_parameters:
    publish_rate: 30.0
    odom0: /odom
    odom0_frame: 'odom'
    odom0_child_frame: 'base_link'
    imu0: /imu/data
    imu0_frame: 'imu_link'
    # Tune these for your robot:
    # map_frame: 'map'
    # world_frame: 'odom'
    # TODO: Set correct covariance values for your robot

# Path planner (GridBased = A* search)
planner_server:
  planner_plugin_id: 'GridBased'
  planner_configs:
    inflation_radius: 0.5
    allow_unknown: False

# Backup planner (if primary fails)
planner_server:
  planner_plugin_id: 'PotentialField'
  planner_configs:
    override_preferred_planner: True

# Behavior tree navigator
bt_navigator:
  plugin: 'nav2_behavior_tree.BehaviorTreePlanner'
  bt_xml_file: '/opt/ros/jazzy/share/nav2_bt_navigator/bt_navigator.xml'

# Recovery behaviors
recovery_behavior_node:
  load_behaviors_from_cli: False
  default behaviors:
    - rotate_recovery:
        max_rotational_velocity: 1.0
        min_in_place_rotational_velocity: 0.5
        smoothing_window: 0.5
    - backward_recovery:
        max_ translational_velocity: 0.5
        min_translational_velocity: 0.2
        smoothing_window: 1.0
```

### Step 2.4: Test Navigation Loop

```bash
# Full end-to-end launch
ros2 launch mnemos_bringup nav2_launch.py map:=/home/user/mnemos_final_map.yaml

# In RViz2, enable these panels:
# - Nav2 (goal setting, path tracking status)
# - Global Costmap
# - Local Costmap  
# - TF (coordinate frames)
# - Map (underlying map view)

# Select the "2D Nav Goal" button (toolbar icon, or press 'n')
# Click on a position in the RViz2 map window
# The robot should navigate to the goal while avoiding obstacles

# To set multiple goals:
# 1. Click "Set Pose" (or press '3') to set initial pose if needed
# 2. Click "2D Nav Goal" to set destination
# 3. Robot navigates, recomputes path if obstacles appear
# 4. Repeat for additional goals

# Record a navigation run:
ros2 bag record /tf /odom /cmd_vel /scan /image_raw -o nav_run_001
```

### Step 2.4: Navigation Success Criteria

**Test Protocol**: Set 20 random goals in the RViz2 map

**Measure** (per Experiment 1 spec):
- ✅ **Navigation success rate**: % of goals reached without collision
- ✅ **Path length**: Total meters traveled vs. straight-line distance
- ✅ **Time to goal**: Seconds from goal set to arrival
- ✅ **Collision count**: Should be 0 in configured environment
- ✅ **Navigation failures**: Number of times robot couldn't reach goal
- ✅ **Intervention count**: Human overrides needed (should be 0 in baseline)

**Success Threshold**: >80% goal reach success rate, 0 collisions in 20+ test runs

### Step 2.5: Common Nav2 Issues & Fixes

**"Robot doesn't move"**:
- Check `/tf` tree: map → odom → base_link should all exist and rotate
- Verify `use_sim_time` is true in both launch files and parameter files
- Check `cmd_vel` topic is publishing (echo `/cmd_vel`)
- Verify robot_base_frame in costmaps matches `base_link`

**"Robot rotates in place"**:
- Check `planner_server` inflation_radius is not too large
- Verify local_costmap update_frequency is sufficient
- Check base_local_planner configuration (often `TebLocalPlanner` or `GridBased`)

**"Robot goes-off map"**:
- Check global_costmap width/height covers the entire map
- Verify origin in map.yaml matches robot start position
- Check `global_frame: 'map'` in costmap configs

**"Goal unreachable"**:
- Check local_costmap radius allows robot to actually reach the position
- Verify robot can rotate in place (tuning `rotation_speed` in planner configs)
- Ensure goal position is at least `robot_radius + inflation_radius` inside navigable space

## Phase 3: Integration Test (End-to-End)

### Step 3.1: Full RTAB-Map + Nav2 Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│  TERMINAL 1: Launch RTAB-Map + Gazebo                          │
│  ────────────────────────────────────────────────────────────── │
│  ros2 launch mnemos_bringup rtabmap_launch.py                  │
│  ↓                                                             │
│  Robot spawns, RTAB-Map maps environment                       │
│  ↓                                                             │
│  Teleop robot around environment                               │
│  ↓                                                             │
│  ros2 run nav2_map_saver map_saver_cli -f mnemos_map            │
│  ↓                                                             │
│  SAVE: mnemos_map.pkg + mnemos_map.yaml                        │
│  ────────────────────────────────────────────────────────────── │
│  TERMINAL 2: Launch Nav2 with saved map                        │
│  ────────────────────────────────────────────────────────────── │
│  ros2 launch mnemos_bringup nav2_launch.py map:=/home/user/mnemos_map.yaml │
│  ↓                                                             │
│  RViz2 opens with Nav2 panels active                           │
│  ↓                                                             │
│  Set 2D Nav Goal → robot navigates                             │
│  ↓                                                             │
│  Record: ros2 bag record /tf /odom /cmd_vel                    │
│  ↓                                                             │
│  ANALYZE: nav_run_001.bag metrics                              │
│  ────────────────────────────────────────────────────────────── │
│  TERMINAL 3: (Optional) Cognitive layer testing                │
│  .. (after baseline is working)                                │
│  ────────────────────────────────────────────────────────────── │
└─────────────────────────────────────────────────────────────────┘
```

### Step 3.2: End-to-End Success Checklist

**Before marking Phase 3 Complete**:

- [ ] RTAB-Map builds consistent map in Gazebo environment
- [ ] Nav2 loads the map successfully without errors
- [ ] Robot can navigate to 5+ random goals with 80%+ success
- [ ] No collisions recorded during navigation tests
- [ ] `/tf` tree is valid: map → odom → base_link → imu_link, base_link → camera_link
- [ ] `ros2 bag record` captures all necessary topics without errors
- [ ] Navigation metrics (success rate, path length, time-to-goal) are computable
- [ ] Framework is stable (no crashes after 30+ minute runs)
- [ ] **All results documented** in `docs/EXPERIMENT_RESULTS.md` (or equivalent)

### Step 3.3: Data to Record & Metrics to Compute

**Bag Recording**:
```bash
# Record full navigation run
ros2 bag record /tf /odom /cmd_vel /scan /camera/depth/points /rtabmap/odom -o nav_metrics_001

# After test, analyze metrics:
# 1. Path efficiency = straight_line_distance / total_path_length
#    (1.0 = perfectly efficient, <0.5 = very inefficient)
# 2. Time to goal = from goal set message to arrival
# 3. Success = goal reached within timeout (usually 60-120 seconds)
# 4. Collisions = count of /collision events (should be 0)
# 5. Number of path re-plannings = count of NavFn/PROS topics changing significantly
```

**Spreadsheet Metrics Template**:

| Run | Goal POS (x,y) | Success (Y/N) | Time (s) | Path Len (m) | StraightDist (m) | Efficiency | Collisions |
|-----|----------------|---------------|----------|--------------|------------------|------------|------------|
| 1   | (1.0, 2.0)     | Y             | 15.2     | 4.8          | 2.1              | 0.44       | 0          |
| 2   | (-1.0, -1.0)   | N (timeout)   | 59.8     | -            | -                | -          | 0          |
| ... | ...            | ...           | ...      | ...          | ...              | ...        | ...        |

### Step 3.3: Phase 3 Complete When

**All Criteria Met**:
1. RTAB-Map builds consistent, coherent map of the Gazebo environment
2. Nav2 loads the map and localizes the robot within it
3. Robot navigates to randomly set goals with >80% success rate
4. Zero collisions recorded during navigation test suite (20+ runs)
5. Navigation metrics are computed and recorded
6. All data logged and stored in project documentation
7. Framework is stable (no crashes, memory leaks, or topic failures)
8. **All results documented** and committed to GitHub

## Phase 4: Cognitive Architecture Bridge (Post-Baseline)

Once baseline SLAM + navigation is working (Phase 3 complete), begin incremental additions:

### Step 4.1: Cognitive Cost Function Integration

**File**: `config/nav2_cognitive.yaml` (new file)

```yaml
# Cognitive cost plugin for Nav2 local costmap
local_costmap:
  plugins: ["cognitive_cost"]
  cognitive_cost:
    enable: true
    alpha: 1.0    # Path cost weight (from Nav2 base_local_planner)
    beta: 0.5     # Risk/collision cost weight
    gamma: 0.3    # Memory influence weight (from episodic memory)
    delta: 0.2    # Uncertainty cost weight
    # Each cost function receives the proposed navigation action 'a'
    # and returns a scalar cost value
```

### Step 4.2: Behavior Tree Cognitive Check

**File**: `bt_navigator.xml` (modify existing)

```xml
<!-- After NavigateToPose, add cognitive check -->
<BehaviorTree>
  <Sequence name="Cognitive Nav Sequence">
    <NavigateToPose />
    <CognitiveCostCheck alpha="1.0" beta="0.5" gamma="0.3" delta="0.2" />
    <RecoveryBehaviors />
  </Sequence>
</BehaviorTree>
```

### Step 4.2: Experiment 2 - Intervention Learning

**Setup**: Add teleoperation data capture to the pipeline

**Data to Capture**:
```bash
# Record teleop sessions for later analysis
ros2 bag record /tf /cmd_vel /scan /odom -o teleop_session_001

# Later, analyze:
# - Human vs autonomous velocity patterns
# - Intervention timestamps and durations
# - Spatial regions where interventions frequent
# - Semantic context of frequent intervention regions
```

### Step 4.3: Experiment 3 - Episodic Memory

**Setup**: Integrate memory retrieval into Nav2 cost function

**Memory Retrieval Logic** (pseudocode):
```python
def get_episodic_memory_cost(current_state, nav2_cost_map):
    # 1. Query episodic memory database for similar situations
    # 2. Compute similarity: S = w_g * S_g + w_s * S_s + w_b * S_b
    # 3. Return cost = 1 - max_similarity * memory_weight
    # 4. If memory is "Invalid" or "Outdated", return 0 influence
    pass
```

### Step 4.4: Experiment 4 - Memory Validation

**Setup**: Implement context comparison and outcome consistency checks

**Validation Logic**:
```python
def validate_episode(episode, current_state):
    # 1. Compare geometric context (obstacle config change?)
    # 2. Compare semantic context (tags changed?)
    # 3. Check outcome consistency (did previous Nav succeed?)
    # 4. Check age (is episode too old to be relevant?)
    # 5. Return validity_status: Valid | Potentially valid | Outdated | Contradicted | Uncertain
    pass
```

### Step 4.5: Experiment 5 - Ablation Study

**Configurations to Test**:

| Config | Description |
|--------|-------------|
| **A** | Baseline Nav2 only (no cognitive layers) |
| **B** | Nav2 + intervention learning |
| **C** | Nav2 + intervention learning + episodic memory |
| **D** | Nav2 + intervention learning + episodic memory + memory validation |

**Metrics Collection** (per configuration, 20+ goal tests):
- Navigation success rate
- Path efficiency (straight-line / total distance)
- Average time-to-goal
- Collision count
- Number of memory retrievals per run
- Memory validity hit rate
- Human intervention count (if teleop included)

**Statistical Analysis** (compare A vs B vs C vs D):
- ANOVA or similar test on success rates
- T-tests on time-to-goal comparisons
- Collision count comparison
- Efficiency metric comparison

## 📋 Complete Roadmap Summary

| Phase | Status | Deliverable |
|-------|--------|-------------|
| **Phase 1**: RTAB-Map SLAM | ⏳ Pending packages | Map building, localization, topic verification |
| **Phase 2**: Nav2 Integration | ⏳ Pending packages | Navigation, goal reaching, obstacle avoidance |
| **Phase 3**: End-to-End Test | ⏳ After Phases 1-2 | Metrics collected, success criteria met |
| **Phase 4**: Experiment 1 | ⏳ After Phase 3 | Baseline data collected (conventional Nav2 only) |
| **Phase 5**: Experiments 2-5 | ⏳ After Phase 4 | Full cognitive architecture testing |
| **Phase 6**: Final Documentation | ⏳ After all experiments | Complete results, hypothesis validation/refutation |

## 🎯 Immediate Next Steps (When Packages Available)

1. **Install packages**: `sudo apt install ros2-jazzy-rtabmap-ros ros2-jazzy-nav2-`
2. **Run Phase 1**: `ros2 launch mnemos_bringup rtabmap_launch.py`
3. **Verify**: RTAB-Map builds map, topics are publishing
4. **Run Phase 2**: `ros2 launch mnemos_bringup nav2_launch.py map:=/path/to/map.yaml`
5. **Test**: Navigate robot to goals in RViz2
6. **Record**: Metrics for Experiment 1 baseline
7. **Proceed**: Add cognitive layers, run Experiments 2-5

## 🛡️ Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| RTAB-Map fails to build map | Medium | High | Verified TF tree, proper camera params, adequate robot trajectories |
| Nav2 can't localize | Medium | High | Saved map verified, robot start position within map bounds, `use_sim_time: true` |
| Navigation goal unreachable | Medium | Medium | Goal positions within navigable space, proper planner inflation |
| Cognitive cost breaks Nav2 | Low | Medium | Implement as optional plugin, keep Nav2-only default mode |
| Data loss during bag recording | Low | Medium | Record to stable filesystem, multiple smaller bags vs one large |
| Git conflicts on team work | Low | Low | Frequent commits, pull before working, clear commit messages |

## ✅ Phase Completion Checklist

**Phase 3-4 Complete When**::

- [ ] RTAB-Map builds consistent map (verified in RViz2 Map panel)
- [ ] Nav2 loads map and localizes robot (verified via `/odom` and `/tf`)
- [ ] Robot navigates to 20+ random goals with >80% success rate
- [ ] Zero collisions during navigation test suite
- [ ] All navigation metrics computed and recorded
- [ ] All data stored in project directory `/home/singh/mnemos-robotics/results/`
- [ ] All results committed to GitHub repository
- [ ] Framework stable for 30+ minute continuous runs
- [ ] **Documentation updated** with phase results and metrics

## 📞 Quick Start Commands (When Packages Install)

```bash
# 1. Install packages
sudo apt update && sudo apt install ros2-jazzy-rtabmap-ros ros2-jazzy-nav2-bringup -y

# 2. Build/rebuild project
cd /home/singh/mnemos-robotics
source /opt/ros/jazzy/setup.bash
cd ~/mnemos_ws
colcon build --packages-select mnemos_* --symlink-install
source ~/mnemos_ws/install/setup.bash

# 3. Launch RTAB-Map
ros2 launch mnemos_bringup rtabmap_launch.py

# 4. Launch Nav2 with map
ros2 launch mnemos_bringup nav2_launch.py map:=/home/user/mnemos_map.yaml

# 5. Navigate goals in RViz2, record data, proceed to experiments
```

## 📞 Need Help?

**Common Starting Points**:
- If RTAB-Map won't launch: Check ` gazebo_ros` plugin is installed, verify camera plugin path
- If Nav2 won't localize: Verify map.yaml exists and has correct image path, verify `use_sim_time` is true in all launch files and params
- If robot doesn't move: Check `/cmd_vel` is publishing, verify `base_frame_id` matches URDF, check `use_sim_time` everywhere

**Helpful Commands**:
```bash
# List all running nodes
ros2 node list

# Check topic communication
ros2 topic list
ros2 topic echo /odom

# Check TF tree
ros2 run tf2_ros tf2_echo /map /base_link

# View any error logs
ros2 log view --name nav2
```

---
*This roadmap is ready for execution upon RTAB-Map and Nav2 package installation on the Ubuntu 24.04 system.*