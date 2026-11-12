# MNEMOS — Memory-Driven Navigation through Experience and Spatial Reasoning

## Project Overview

MNEMOS is a simulation-first mobile robotics research platform that learns from human teleoperation interventions, converts those interventions into contextual episodic memories, retrieves relevant experiences during future navigation, and adapts its decisions based on whether previous experiences remain valid.

**Primary Objective:** Develop a navigation architecture combining spatial understanding, intervention interpretation, contextual episodic memory, and memory validation to reduce repeated navigation mistakes and unnecessary human interventions.

## Key Behaviors

### Mode A — Explore
- Receive RGB-D camera data, IMU, and wheel odometry
- Estimate position and build spatial maps
- Recognize objects and environmental structures
- Navigate using conventional autonomous navigation

### Mode B — Human Control
- Interface displays camera feed, position, local/global maps, planned and actual trajectories
- Records robot pose, autonomous and human velocity commands, obstacle configuration
- Human control safely overrides autonomous velocity commands

### Mode C — Experience Formation
- Construct contextual episodes after interventions
- Episodes contain: unique ID, timestamp, spatial location, robot pose, navigation goal, geometric/semantic context, planned action, human intervention, command differences, resulting trajectory, outcome, candidate interpretation, confidence score, validity status

### Mode D — Cognitive Autonomous Navigation
- Identify current context and retrieve relevant episodes
- Calculate similarity between current and previous situations
- Check whether previous experiences are still valid
- Modify navigation costs or candidate actions when justified
- Never blindly follow previously recorded routes
- Current perception and collision-safety constraints take precedence over historical memory

## Repository Structure

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

See `docs/INSTALLATION.md` for installation instructions and `docs/TROUBLESHOOTING.md` for common issues.

The runnable Milestone 3–4 baseline (Gazebo Harmonic simulation, RTAB-Map
mapping, and Nav2 navigation) is documented in
[`docs/BASELINE_RUNBOOK.md`](docs/BASELINE_RUNBOOK.md). The cognitive modules
described above remain future work; the baseline is intentionally conventional
so later experiments have an auditable comparison point.

The novel MNEMOS layer is specified in
[`docs/COGNITIVE_ARCHITECTURE.md`](docs/COGNITIVE_ARCHITECTURE.md). It records
human corrections as validated, explainable episodic evidence and emits only
bounded navigation-cost advice; it never blindly replays a prior route.

[`docs/EXPERIMENTATION.md`](docs/EXPERIMENTATION.md) and the versioned
ablation protocol define how the hypothesis is tested without hiding failed
trials or safety regressions.

For the initial execution instructions, see the `Initial Execution Instructions` section of the project specification (Section 20), which outlines stepping through environment inspection, repository creation, robot simulation, baseline SLAM/navigation, and reporting.

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
