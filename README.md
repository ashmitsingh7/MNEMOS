# MNEMOS — Memory-Driven Navigation through Experience and Spatial Reasoning

MNEMOS is an implementation-first ROS 2 Jazzy research platform for
**validated episodic navigation**. It learns compact, explainable evidence
from explicit human corrections, retrieves it in similar lidar/pose contexts,
and refuses to use it when current geometry contradicts the memory.

It does not replay human trajectories or replace Nav2 safety systems. Nav2
remains responsible for planning, collision checking, and recovery. MNEMOS
adds an auditable advisory layer whose only current output is a bounded
navigation-cost suggestion and its explanation.

## Implementation status

| Component | What ships now |
| --- | --- |
| Simulation | Gazebo Harmonic lab, differential-drive robot, lidar, RGB-D camera, IMU, and ROS–Gazebo topic bridge |
| ROS packages | Nine installable packages: description, simulation, bringup, SLAM monitor, control, intervention, memory, reasoning, and evaluation |
| Baseline interfaces | Configured launch paths for simulation, RTAB-Map SLAM, and Nav2; live SLAM/Nav2 needs their Jazzy packages installed |
| Command safety | A human-priority arbiter owns `/cmd_vel`, clamps speed, rejects stale commands, and fails safe to a stop |
| Intervention capture | Explicit, sustained human overrides become evidence-backed `avoid`, `wait`, `prefer`, `recovery`, or `uncertain` episodes |
| Episodic memory | SQLite persistence for pose, 24-sector lidar signature, command delta, confidence, semantic tags, and evidence |
| Reasoning | Interpretable retrieval; geometry/semantic/age validation; contradiction-triggered abstention; bounded advice |
| Evaluation | Immutable SQLite trial ledger and a matched-seed A/B/C/D ablation protocol |

The repository contains **no measured performance claim**. It only provides
the platform and protocol needed to test the hypothesis honestly.

## How the implemented system fits together

```text
Gazebo robot ── lidar / RGB-D / odom ──> ROS bridge ──> RTAB-Map and Nav2
                                                       │ /cmd_vel_autonomy
human teleoperation ──────────────────────────────────┤ /cmd_vel_human
                                                       ▼
                          /mnemos/human_override ─> command arbiter ─> /cmd_vel
                                                               │
                    pose + scan + separate command streams ───┘
                                                               ▼
                         intervention recorder ─> SQLite episode ledger
                                                               │
                                     retrieval + validation + bounded advice
                                                               ▼
                      /mnemos/memory_cost_bias and /mnemos/memory_advice
```

The memory adviser never writes `/cmd_vel`, takes TF ownership, or bypasses a
collision layer. A Nav2 costmap-plugin integration is deliberately deferred
until the conventional runtime stack has passed live safety tests.

## Build and verification

```bash
cd /home/singh/mnemos-robotics
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash

python3 -m unittest discover -s tests -v
gz sdf -k src/mnemos_simulation/worlds/lab.sdf
gz sdf -k src/mnemos_simulation/worlds/mnemos_robot.sdf
```

The test suite covers the simulator/bridge configuration, package manifests,
SQLite episode round trips, retrieval ranking, contradiction abstention,
bounded advice, intervention rules, command-arbitration safety, and trial
metrics.

## Runtime dependencies and launch paths

The existing development environment has ROS 2 Jazzy, Gazebo Harmonic,
`ros_gz_sim`, and `ros_gz_bridge`. To run the complete SLAM/navigation stack,
install:

```bash
sudo apt-get update
sudo apt-get install -y \
  ros-jazzy-rtabmap-ros ros-jazzy-rtabmap-launch \
  ros-jazzy-nav2-bringup ros-jazzy-navigation2
```

Then use the source overlay and launch one operating mode:

```bash
ros2 launch mnemos_bringup simulation.launch.py
ros2 launch mnemos_bringup slam.launch.py
ros2 launch mnemos_bringup navigation.launch.py map:=$HOME/mnemos_map.yaml
ros2 launch mnemos_bringup cognitive.launch.py
```

`cognitive.launch.py` runs the command arbiter, intervention recorder, and
memory adviser. The recorder needs an explicit `std_msgs/Bool` message on
`/mnemos/human_override`; while it is true, stale human input yields a stop,
not a surprise return to autonomous motion.

Useful observability topics:

```bash
ros2 topic echo /mnemos/command_arbitration
ros2 topic echo /mnemos/intervention_events
ros2 topic echo /mnemos/memory_advice
ros2 topic echo /mnemos/memory_cost_bias
```

## Implementation map

```text
src/
├── mnemos_robot_description/  # URDF and RViz configuration
├── mnemos_simulation/         # Gazebo Harmonic world and robot SDF
├── mnemos_bringup/            # simulation, SLAM, navigation, cognitive launches
├── mnemos_slam/               # input-readiness monitor
├── mnemos_control/            # human-priority final-command policy
├── mnemos_intervention/       # override interpretation and episode recording
├── mnemos_memory/             # episode model, SQLite storage, similarity retrieval
├── mnemos_reasoning/          # validation and bounded advisory output
└── mnemos_evaluation/         # reproducible trial ledger

docs/
├── BASELINE_RUNBOOK.md
├── COGNITIVE_ARCHITECTURE.md
└── EXPERIMENTATION.md

experiments/protocols/mnemos_ablation.yaml
```

Read [the baseline runbook](docs/BASELINE_RUNBOOK.md), [the cognitive
architecture](docs/COGNITIVE_ARCHITECTURE.md), and [the experiment guide](docs/EXPERIMENTATION.md)
for contracts, acceptance criteria, and limitations.

## Project Overview

MNEMOS is a simulation-first mobile robotics research platform that learns from human teleoperation interventions, converts those interventions into contextual episodic memories, retrieves relevant experiences during future navigation, and adapts its decisions based on whether previous experiences remain valid.

**Primary Objective:** Develop a navigation architecture combining spatial understanding, intervention interpretation, contextual episodic memory, and memory validation to reduce repeated navigation mistakes and unnecessary human interventions.

## Planned research behaviors

### Mode A — Explore (partially implemented)
- Receive RGB-D camera data, IMU, and wheel odometry
- Estimate position and build spatial maps
- Recognize objects and environmental structures
- Navigate using conventional autonomous navigation

### Mode B — Human Control (command path implemented; interface is roadmap)
- Interface displays camera feed, position, local/global maps, planned and actual trajectories
- Records robot pose, autonomous and human velocity commands, obstacle configuration
- Human control safely overrides autonomous velocity commands

### Mode C — Experience Formation (compact episode implemented)
- Construct contextual episodes after interventions
- Episodes contain: unique ID, timestamp, spatial location, robot pose, navigation goal, geometric/semantic context, planned action, human intervention, command differences, resulting trajectory, outcome, candidate interpretation, confidence score, validity status

### Mode D — Cognitive Autonomous Navigation (advisory layer implemented; Nav2 costmap integration is roadmap)
- Identify current context and retrieve relevant episodes
- Calculate similarity between current and previous situations
- Check whether previous experiences are still valid
- Modify navigation costs or candidate actions when justified
- Never blindly follow previously recorded routes
- Current perception and collision-safety constraints take precedence over historical memory

## Target research layout

The following is the broader planned research layout. Directories and modules
not shown in the **Implementation map** above are roadmap items, not claims of
completed functionality.

```
mnemos-robotics/
├── README.md                          # This file
├── LICENSE
├── CONTRIBUTING.md
├── .gitignore
├── docs/                              # Documentation directory
│   ├── PROJECT_OVERVIEW.md
│   ├── RESEARCH_PROBLEM.md
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── MATHEMATICAL_FOUNDATIONS.md
│   ├── DESIGN_DECISIONS.md
│   ├── EXPERIMENT_PROTOCOL.md
│   ├── EXPERIMENT_RESULTS.md
│   ├── INSTALLATION.md
│   ├── TROUBLESHOOTING.md
│   └── GLOSSARY.md
├── src/                               # ROS 2 packages
│   ├── mnemos_interfaces/             # Custom ROS 2 messages and services
│   ├── mnemos_robot_description/      # Robot URDF/XACRO models
│   ├── mnemos_simulation/             # Gazebo Harmonic models and worlds
│   ├── mnemos_bringup/                # Launch files and configuration
│   ├── mnemos_perception/             # Perception pipeline packages
│   ├── mnemos_slam/                   # RTAB-Map integration and educational modules
│   ├── mnemos_world_model/            # Metric, topological, semantic, spatial relationship representations
│   ├── mnemos_teleoperation/          # Teleoperation interface
│   ├── mnemos_intervention/           # Intervention interpretation engine
│   ├── mnemos_memory/                 # Episodic memory engine
│   ├── mnemos_reasoning/              # Cognitive reasoning and validation
│   ├── mnemos_navigation/             # Cognitive navigation engine integrating with Nav2
│   └── mnemos_evaluation/             # Experiment framework and metrics
├── algorithms/                        # Foundational algorithms
│   ├── camera_geometry/
│   ├── point_cloud_processing/
│   ├── visual_features/
│   ├── state_estimation/
│   ├── intervention_analysis/
│   ├── memory_retrieval/
│   ├── memory_validation/
│   └── decision_costs/
├── experiments/                       # Experiment definitions and results
│   ├── exp01_baseline/
│   ├── exp02_intervention_learning/
│   ├── exp03_episodic_memory/
│   ├── exp04_memory_validation/
│   └── exp05_ablation/
├── config/                            # Parameter configuration
├── scripts/                           # Utility scripts
├── tests/                             # Test suites
└── results/                           # Experiment results
└── notebooks/                         # Jupyter notebooks
```

## Development Philosophy

1. Build a modular and understandable research platform.
2. Prefer established algorithms for foundational capabilities.
3. Develop original implementations for the central research contribution.
4. Keep perception, SLAM, memory, reasoning, and navigation independently testable.
5. Never hide algorithmic complexity behind a black-box API.
6. Avoid unnecessary deep learning models.
7. Do not train large neural networks without a clear research requirement.
8. Make all major decisions explainable and inspectable.
9. Record experiments and provide reproducible results.
10. Never claim an improvement without experimental evidence.

## Development Workflow

Work in milestones. For each milestone:
1. Explain the objective
2. Inspect existing files
3. Propose the architecture
4. Implement the smallest working version
5. Build the affected packages
6. Run tests
7. Run the relevant simulation
8. Document results
9. Explain the implementation
10. Identify remaining problems

Maintain a development log. Never silently skip failed tests. Never claim a feature is implemented when it is only represented by a placeholder.

## Getting Started

Start with **Build and verification** above. For runtime details, use the
[baseline runbook](docs/BASELINE_RUNBOOK.md); for episode, validation, and
safety semantics, use the [cognitive architecture](docs/COGNITIVE_ARCHITECTURE.md).
The [experiment guide](docs/EXPERIMENTATION.md) and versioned
[ablation protocol](experiments/protocols/mnemos_ablation.yaml) define the
evidence required to evaluate the project without hiding failures or safety
regressions.

## Citation

If you use MNEMOS in your research, please cite:

```
@misc{mnemos-robotics2026,
  author = {MNEMOS Contributors},
  title = {MNEMOS: Memory-Driven Navigation through Experience and Spatial Reasoning},
  year = {2026},
  doi = {10.5281/zenodo.1234567}
}
```
