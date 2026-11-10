# MNEMOS Project Summary

## Initialization Phase (Complete)

### Environment Verified
- **OS**: Ubuntu 24.04.5 LTS (Noble Numbat)
- **Python**: 3.12.3
- **OpenCV**: 4.6.0
- **NumPy**: 1.26.4
- **Gazebo Sim**: 8.15.0 (Harmonic-compatible)
- **ROS 2**: Jazzy Jalisco (rclpy available)

### Repository
- **GitHub**: https://github.com/ashmitsingh7/MNEMOS
- **Commit**: e936d10 - Initial project structure and foundation
- **52 files** across all directories

### Core Deliverables
1. **Robot URDF**: `src/mnemos_robot_description/mnemos_diff_drive.urdf`
   - Differential-drive robot with 6 links, 3 continuous joints
   - RGB-D camera and IMU sensors
   - Validated XML structure

2. **Simulation Worlds**: 
   - `src/mnemos_simulation/worlds/lab_environment.world` - Laboratory with corridors, rooms, furniture
   - `src/mnemos_simulation/warehouse_environment.world` - Warehouse with aisles, storage racks, pallets

3. **Launch Infrastructure**: 
   - `src/mnemos_bringup/launch/robot_spawn.launch.py`

4. **Documentation (10 files)**:
   - `README.md`, `RESEARCH_PROBLEM.md`, `SYSTEM_ARCHITECTURE.md`
   - `DESIGN_DECISIONS.md`, `DECISIONS.md`, `INSTALLATION.md`
   - `TROUBLESHOOTING.md`, `GLOSSARY.md`, `PROJECT_OVERVIEW.md`
   - `ENVIRONMENT_AUDIT.md`

5. **Project Structure**:
   - `algorithms/` (8 subdirectories)
   - `experiments/` (5 experiment directories)
   - `src/mnemos_*` (13 ROS 2 package directories)
   - `config/`, `scripts/`, `tests/`, `results/`, `notebooks/`

### Research Problem
MNEMOS investigates: "Can a mobile robot interpret human navigation interventions, associate them with spatial and semantic context, store them as episodic experiences, and use those experiences to improve future autonomous navigation while recognizing when previously learned experiences are no longer valid?"

### Hypothesis
A navigation architecture combining spatial understanding, intervention interpretation, contextual episodic memory and memory validation can reduce repeated navigation mistakes and unnecessary human interventions.

### Five Experiments Planned
- **Experiment 1**: Conventional baseline (SLAM + Nav2)
- **Experiment 2**: Human intervention learning
- **Experiment 3**: Episodic memory
- **Experiment 4**: Memory validation (environment changes)
- **Experiment 5**: Ablation study (A through D configurations)

### Ready for Next Phase
**Milestone 3-4: Baseline SLAM and Navigation Integration**

When RTAB-Map and Nav2 packages are installed, the following should be implemented:

1. **RTAB-Map SLAM Integration**:
   - Launch RTAB-Map with RGB-D camera
   - Demonstrate mapping and localization
   - Publish pose and map status
   - Verify TF tree includes map/odom frames

2. **Nav2 Navigation Stack Integration**:
   - Launch Nav2 bringup with map server
   - Demonstrate goal-based navigation
   - Test obstacle avoidance
   - Verify BT (Behavior Tree) execution

3. **Integration Test**:
   - Spawn robot in Gazebo with RTAB-Map online
   - Navigate to goal positions
   - Record paths and success rates
   - Document any issues or configurations needed

### Known Limitations (Environment)
- RTAB-Map packages not installed via apt (requires sudo)
- Nav2 packages not installed via apt (requires sudo)
- Full Gazebo + RTAB-Map + Nav2 integration not testable in current environment
- All code and configurations are ready for when packages become available

### Next Steps (When Packages Available)
1. Install: `sudo apt install ros2-jazzy-rtabmap-ros ros2-jazzy-rtabmap ros2-jazzy-nav2-bringup ros2-jazzy-nav2`
2. Launch RTAB-Map with robot in Gazebo
3. Launch Nav2 with map saved from RTAB-Map
4. Conduct navigation experiments
5. Begin Experiment 1 (conventional baseline)
6. Progress through all 5 experiments per specification

### Citation
If using MNEMOS in research, cite:
```
@misc{mnemos-project-2026,
  author = {MNEMOS Contributors},
  title = {MNEMOS: Memory-Driven Navigation through Experience and Spatial Reasoning},
  year = {2026},
  url = {https://github.com/ashmitsingh7/MNEMOS}
}
```