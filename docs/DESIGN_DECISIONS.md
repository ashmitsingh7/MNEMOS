# MNEMOS Design Decisions

## Overview

This document records the key design decisions for the MNEMOS project, their rationale, and any alternatives considered but rejected.

## 1. ROS 2 Distribution: Jazzy Jalisco

**Decision**: Use ROS 2 Jazzy (Python 3.12, rclpy 2).

**Rationale**: The project specification targets Ubuntu 24.04 LTS with ROS 2 Jazzy Jalisco. This is the current stable distribution with Python 3.12 support.

**Alt considered**: ROS 2 Humble (Python 3.8) - too old for Python 3.12 packages; ROS 2 Iron - EOL.

**Status**: Chosen - aligns with project spec.

---

## 2. Simulator: Gazebo Harmonic

**Decision**: Use Gazebo Harmonic with Gazebo Sim 8.

**Rationale**: Project specification targets Gazebo Harmonic. This is the latest Gazebo version compatible with ROS 2 Jazzy.

**Alt considered**: Gazebo Gazebo - older version, less compatible with Jazzy; Ignition Gazebo - different API.

**Status**: Chosen - aligns with project spec.

---

## 3. SLAM Backend: RTAB-Map

**Decision**: Use RTAB-Map as the initial RGB-D SLAM backend; implement educational modules for foundational mathematics independently.

**Rationale**: RTAB-Map is a well-established, production-quality RGB-D SLAM system. The project requires SLAM capability but does not require developing a full SLAM backend from scratch. Educational modules explain the underlying mathematics for transparency.

**Alt considered**: Developing SLAM from scratch - would divert focus from the central research contribution (memory-based navigation); using hector_slam - less capable for RGB-D; using Cartographer - good but RTAB-Map has better Python API access for this project's needs.

**Status**: Chosen - balances capability with focus on research contribution.

---

## 4. Navigation Stack: Nav2

**Decision**: Use Nav2 as the conventional navigation stack; implement a cognitive decision cost layer that integrates with Nav2 rather than replacing it.

**Rationale**: Nav2 is the standard ROS 2 navigation stack. The project requires autonomous navigation capability, and Nav2 provides proven path planning, collision checking, and recovery behaviors. The cognitive layer influences Nav2 through costmap integration without replacing core Nav2 functionality.

**Alt considered**: Replacing Nav2 entirely - too risky, loses safety guarantees; using a custom planner - would need to reimplement all Nav2 features (BTs, costmaps, recovery behaviors).

**Status**: Chosen - provides reliable navigation while allowing cognitive layer integration.

---

## 5. Programming Languages: Python 3 and C++17

**Decision**: Primary implementation in Python 3 for rapid prototyping and ROS 2 integration; C++17 for performance-critical components.

**Rationale**: Python 3 enables rapid development of the cognitive architecture, memory system, and interface. C++17 is used where performance matters (e.g., point cloud processing, real-time control). ROS 2 Python APIs are mature and well-supported.

**Alt considered**: Python only - may have performance limitations for real-time control; C++ only - would significantly slow prototyping and reduce accessibility.

**Status**: Chosen - balances development speed with performance needs.

---

## 6. Episodic Memory Backend: SQLite

**Decision**: Use SQLite as the initial persistence layer for episodic memory; graph representation may be added later.

**Rationale**: SQLite is lightweight, file-based, requires no server process, and supports the structured episode data format. The episode schema is well-defined with explicit types. A graph representation can be added later if justified by retrieval patterns.

**Alt considered**: JSON files - no query capabilities, harder to manage concurrent access; PostgreSQL - too heavy for a single-robot research platform; MongoDB - adds server dependency, overkill for structured episode data.

**Status**: Chosen - lightweight and sufficient for initial implementation.

---

## 7. Memory Similarity Function

**Decision**: Use a weighted combination of geometric, semantic, and behavioural similarity:

```
S(E_i, E_t) = w_g * S_g + w_s * S_s + w_b * S_b
```

With configurable weights starting at w_g = 0.5, w_s = 0.3, w_b = 0.2.

**Rationale**: This decomposition allows incremental improvements - each similarity type can be enhanced independently. The weighted sum provides a single scalar for decision-making while keeping the components inspectable.

**Alt considered**: Single similarity metric - less informative, harder to debug; learned embedding-only approach - black box, harder to explain and debug; graph distance only - doesn't capture all dimensions of episode relevance.

**Status**: Chosen - interpretable and modular.

---

## 8. Memory Validation

**Decision**: Implement a modular validation algorithm that compares previous and current geometric/semantic contexts, checks outcome consistency, verifies age, and produces explicit validity statuses.

**Rationale**: The core research question requires answering "when are previous experiences still valid?". A transparent validation mechanism is essential for testing this question. The modular design allows different validation approaches to be experimentally compared.

**Alt considered**: Simple timeout-based invalidation - too coarse, doesn't distinguish between different types of changes; learned validity classifier - black box, harder to understand why a memory was accepted/rejected; no validation - would violate the research hypothesis.

**Status**: Chosen - essential for the research hypothesis and provides interpretable results.

---

## 9. Cognitive Decision Cost Function

**Decision**: Use a configurable cost function:

```
J(a) = alpha * C_path(a) + beta * C_risk(a) + gamma * C_memory(a) + delta * C_uncertainty(a)
```

With default weights: alpha=1.0, beta=0.5, gamma=0.3, delta=0.2.

**Rationale**: This cost function allows the cognitive layer to influence Nav2's planning without replacing it. Each component can be tuned independently. The cost is added to Nav2's planning pipeline as an additional costmap layer or plugin.

**Alt considered**: Replacing Nav2's cost function entirely - loses safety guarantees; multiplicative combination - harder to tune and debug; only using C_memory - ignores risk and uncertainty, unsafe.

**Status**: Chosen - provides structured influence on Nav2 while maintaining safety.

---

## 10. Intervention Interpretation Engine

**Decision**: Start with a rule-based, transparent baseline; learned classifiers added later if sufficient labelled examples are available.

**Rationale**: The central research question involves interpretation of human interventions. Starting with interpretable rules allows debugging, validation, and gradual learning. Rule-based approaches are also immediately usable with limited data.

**Alt considered**: Learned classifier from the start - would require labelled data that may not be available; latent variable model - more complex than needed for initial implementation.

**Status**: Chosen - transparent baseline that can be enhanced later.

---

## 11. Teleoperation Interface: Python Web Framework

**Decision**: Use a lightweight Python web framework (e.g., Flask or FastAPI) for the teleoperation interface.

**Rationale**: A web interface works across devices (laptop, tablet, phone), is easy to develop iteratively, and integrates naturally with ROS 2 via HTTP endpoints or websockets.

**Alt considered**: ROS 2 GUI frameworks (rtqt_plot, rqt_publisher) - less flexible across devices; native desktop application - harder to deploy across different machines.

**Status**: Chosen - cross-device compatible and easy to develop.

---

## 12. coordinate Frames

**Decision**: Follow TF2 conventions with these key frames:
- `world`: Global/Map frame
- `base_link`: Robot base frame
- `camera_link`: RGB-D camera frame
- `camera_optical_frame`: Optical center of camera
- `odom`: Odometry frame (may differ from base_link via localizer)

**Rationale**: Standard TF2 frames ensure compatibility with ROS 2 tools (RViz2, Nav2) and clear transformation chains.

**Alt considered**: Custom frame names - would break ROS 2 tool compatibility; omitting TF2 - would make coordinate transformations impossible.

**Status**: Chosen - standard and compatible.

---

## 13. Experiment Framework: SQLite + ROS Bags

**Decision**: Record experiments using ROS 2 bags for raw data and SQLite for metric tracking.

**Rationale**: ROS bags capture all topic data for offline analysis. SQLite provides fast metric queries and experiment tracking. Both are lightweight and well-integrated with ROS 2.

**Alt considered**: CSV logs - simpler but lose topic context; InfluxDB - added server dependency; no structured logging - hard to reproduce experiments.

**Status**: Chosen - comprehensive and reproducible.

---

## 14. Development Milestones

**Decision**: Work in 10 defined milestones, each producing a working increment.

**Rationale**: The project specification mandates milestone-based development. This structure prevents attempting too much at once and ensures incremental progress with documentation at each step.

**Alt considered**: Single-phase development - would be overwhelming and risk incomplete features; Kanban without fixed milestones - less predictable for a research project.

**Status**: Chosen - aligns with spec and provides structure.

---

## 15. Documentation Structure

**Decision**: Every package has a README with: purpose, inputs, outputs, ROS topics, ROS services/actions, dependencies, parameters, internal algorithm, failure modes, and test instructions. Architecture diagrams document coordinate frames and system architecture.

**Rationale**: The specification explicitly requires extensive documentation. Documenting each algorithm with "what is implemented, borrowed, custom, experimental" provides clarity for a research platform.

**Alt considered**: Minimal documentation - faster initial development but makes the platform unmaintainable and uninterpretable; no algorithm documentation - violates the spec's explicit requirements.

**Status**: Chosen - aligns with spec and ensures the platform is understandable and extensible.

---

## Quick Reference: Key Design Decision Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| ROS 2 Distro | Jazzy | Project spec target |
| Simulator | Gazebo Harmonic | Project spec target |
| SLAM | RTAB-Map | Production-quality, well-supported |
| Navigation | Nav2 | Standard ROS 2 stack |
| Languages | Python 3 / C++17 | Balance speed and performance |
| Memory Backend | SQLite | Lightweight, file-based |
| Similarity Function | Weighted sum | Interpretable and modular |
| Memory Validation | Modular algorithm | Essential for research hypothesis |
| Cost Function | Weighted sum | Influences Nav2 without replacing it |
| Intervention Interpretation | Rule-based baseline | Transparent, data-efficient |
| Teleop Interface | Python web | Cross-device compatible |
| Coordinate Frames | TF2 standard | ROS 2 tool compatibility |
| Experiment Recording | ROS bags + SQLite | Comprehensive, reproducible |
| Milestones | 10 defined milestones | Structured, incremental progress |
| Package Documentation | Detailed per-spec | Ensures understandability |

---

## Revision History

| Date | Version | Change |
|------|---------|--------|
| 2026-11-06 | 0.1.0 | Initial design decisions document |