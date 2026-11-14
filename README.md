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
| Simulation | Gazebo Harmonic lab/warehouse, differential-drive robot, lidar, RGB-D camera, IMU, ROS–Gazebo bridge |
| ROS packages | Nine installable packages: description, simulation, bringup, SLAM monitor, control, intervention, memory, reasoning, evaluation |
| Baseline interfaces | Configured launch paths for simulation, RTAB-Map SLAM, and Nav2 (live SLAM/Nav2 need their Jazzy packages installed) |
| Command safety | Human-priority arbiter owns `/cmd_vel`, clamps speed, rejects stale commands, fails safe to stop |
| Intervention capture | Explicit sustained human overrides become evidence-backed `avoid`, `wait`, `prefer`, `recovery`, or `uncertain` episodes |
| Episodic memory | SQLite persistence of pose, 24-sector lidar signature, command deltas/streams, confidence, tags, evidence, goal, session id, intervention interval, outcome, bag reference |
| Reasoning | Interpretable retrieval; geometry/semantic/age validation; contradiction-triggered abstention; bounded advice |
| Evaluation | Immutable SQLite trial ledger, matched-seed A/B/C/D ablation protocol, offline retrieval/validation/intervention metrics |
| Hardening | Edge-case guards, schema migration, null-safe APIs, 48 passing tests |

The repository contains **no measured performance claim**. It only provides
the platform and protocol needed to test the hypothesis honestly.

## How the system fits together

```text
Gazebo robot ── lidar / RGB-D / odom ──> ROS bridge ──> RTAB-Map and Nav2
                                                       │ /cmd_vel_autonomy
human teleoperation ───────────────────────────────────┤ /cmd_vel_human
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
collision layer. Nav2 costmap-plugin integration is deliberately deferred
until the conventional runtime stack passes live safety tests.

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

The test suite (48 tests) covers simulator/bridge configuration, package
manifests, SQLite episode round trips and migration, retrieval ranking and
edge cases, contradiction abstention, bounded advice, intervention rules,
command-arbitration safety, trial metrics, and offline evaluation helpers.

## Runtime dependencies and launch paths

The environment has ROS 2 Jazzy, Gazebo Harmonic, `ros_gz_sim`, and
`ros_gz_bridge`. For the full SLAM/navigation stack, install:

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
memory adviser. The recorder needs an explicit `std_msgs/Bool` on
`/mnemos/human_override`; while it is true, stale human input yields a stop.

Useful observability topics:

```bash
ros2 topic echo /mnemos/command_arbitration
ros2 topic echo /mnemos/intervention_events
ros2 topic echo /mnemos/memory_advice
ros2 topic echo /mnemos/memory_cost_bias
ros2 topic echo /mnemos/slam_inputs_ready
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
```

## Project overview

MNEMOS is a simulation-first mobile robotics research platform that learns
from human teleoperation interventions, converts them into contextual
episodic memories, retrieves relevant experiences during future navigation,
and adapts decisions based on whether previous experiences remain valid.

**Primary objective:** develop a navigation architecture combining spatial
understanding, intervention interpretation, contextual episodic memory, and
memory validation to reduce repeated navigation mistakes and unnecessary
human interventions.

## Planned research behaviors

### Mode A — Explore (partially implemented)
- Receive RGB-D, IMU, and wheel odometry; estimate position and build maps;
  recognize objects/structures; navigate conventionally.

### Mode B — Human Control (command path implemented)
- Safe override of autonomous commands; capture robot pose, commands, obstacles.

### Mode C — Experience Formation (compact episode implemented)
- Construct contextual episodes after interventions containing ID, timestamp,
  spatial location, pose, goal, geometric/semantic context, planned action,
  human intervention, command differences/streams, interval, outcome, bag
  reference, candidate interpretation, confidence, validity status.

### Mode D — Cognitive Autonomous Navigation (advisory layer implemented)
- Retrieve relevant episodes, compute similarity, validate against current
  geometry, emit bounded advice. Nav2 costmap integration is roadmap.

## Target research layout

```text
mnemos-robotics/
├── README.md
├── docs/                  # 13 documentation files
├── src/                   # 9 ROS 2 packages (above)
├── algorithms/            # foundational algorithms (scaffolded)
├── experiments/           # ablation protocol + experiment dirs (scaffolded)
├── config/                # parameter configuration (scaffolded)
├── scripts/               # utility scripts (scaffolded)
├── tests/                 # test suites
├── results/               # experiment results (scaffolded)
└── notebooks/             # Jupyter notebooks (scaffolded)
```

## Development philosophy

1. Build a modular, understandable research platform.
2. Prefer established algorithms for foundational capabilities.
3. Original implementations for the central research contribution.
4. Keep perception, SLAM, memory, reasoning, navigation independently testable.
5. Never hide algorithmic complexity behind a black-box API.
6. Avoid unnecessary deep learning.
7. Make all major decisions explainable and inspectable.
8. Record experiments and provide reproducible results.
9. Never claim an improvement without experimental evidence.

## Development workflow

Work in milestones. For each: explain objective, inspect files, propose
architecture, implement smallest working version, build, test, run simulation,
document, explain, identify remaining problems. Maintain a development log.
Never silently skip failed tests; never claim a feature is only a placeholder.

## Staged plan and status

### Stage 1 — Complete conventional navigation baseline
Install RTAB-Map/Nav2, build map, localize, send safe goals, record metrics.
**Status:** blocked on system packages (no sudo).

### Stage 2 — Verify human-priority command control
Autonomy/override/stale/clamping/emergency transitions with odometry checks.
**Status:** code and tests complete; live trace pending.

### Stage 3 — Make intervention episodes experimentally grounded
Capture goal, map/session id, pose, scan, both command streams, intervention
interval, post-intervention outcome, bag reference. **Status:** implemented.

### Stage 4 — Validate contextual memory offline
Context representation, retrieval vs. human relevance, moved/cleared/temporary
obstacles, novel geometry, precision/contradiction/false-accept/false-reject/
abstention metrics, threshold calibration. **Status:** helpers and hardening in
place.

### Stage 5 — Integrate bounded memory advice with Nav2
Custom costmap/planner adapter; obstacle/collision checks authoritative;
default zero influence on stale/missing/failed/low-confidence; diagnostics.
**Status:** deferred until baseline safety tests.

### Stage 6 — Run controlled experiments
Matched-seed A/B/C/D protocol; preserve failures; confidence intervals.
**Status:** protocol defined; data collection pending.

### Stage 7 — Package the research contribution
Freeze code/params/assets/protocol; docs; negative results; contribution
boundary. **Status:** pending.

## Getting started

Start with **Build and verification** above. For runtime details, use the
[baseline runbook](docs/BASELINE_RUNBOOK.md); for episode, validation, and
safety semantics, use the [cognitive architecture](docs/COGNITIVE_ARCHITECTURE.md).
The [experiment guide](docs/EXPERIMENTATION.md) and
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