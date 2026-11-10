# MNEMOS Detailed Design Decisions

This document provides detailed descriptions of all major design decisions for the MNEMOS project, including the rationale, alternatives considered, and any trade-offs made.

## 1. Robot Platform: Differential-Drive Mobile Robot

### Decision: Differential-drive architecture with caster wheel

**Description:** Created a custom differential-drive mobile robot with two independently driven wheels and a caster wheel for support. The robot has:
- Two front/rear wheels (radius 0.08m, length 0.04m) for propulsion
- One caster wheel (radius 0.03m) for stability
- Cylinder collision geometry for all wheels
- RGB-D camera mounted on the robot base
- IMU for orientation sensing

**Rationale:** 
- Differential-drive is the most common and well-understood robot architecture for ROS 2 Nav2 integration
- The caster wheel provides 3DOF support without complex kinematic chains
- Simple wheel geometry enables straightforward odometry calculations
- Compatible with Gazebo Harmonic's physics engine and ROS 2 control interfaces

**Alternatives considered:**
- *Omni-wheel*: Would allow sideways movement but adds complexity to odometry and control; not necessary for the research goals
- *Ackermann steering*: More realistic for car-like robots but complicates Nav2 configuration; the spec explicitly requests differential-drive
- *Legged robot*: Would require completely different locomotion stack; out of scope for initial platform

**Custom vs borrowed:** Custom implementation (URDF created from scratch) to ensure exact specification compliance and full model inspectability.

---

## 2: Simulation: Gazebo Harmonic Worlds

### Decision: Two distinct indoor environments

**Description:** Created two Gazebo Sim 8 world files:
- **lab_environment.world**: Laboratory setting with corridors, rooms, doorways, furniture (desks, shelf, chair, table)
- **warehouse_environment.world**: Warehouse setting with aisles, storage racks, pallets, outer walls

**Rationale:**
- The spec requires "at least two indoor environments: 1) laboratory, 2) warehouse-like"
- Providing distinct environments enables Experiment 4 (memory validation) where the environment changes between sessions
- Different environments test various scenarios: narrow corridors (lab) vs wide aisles (warehouse), movable vs fixed obstacles

**Alt considered:** Single combined environment - would limit experimental variability and make it harder to test environment-change scenarios.

**Custom vs borrowed:** Custom SDF world files created from scratch. All entities (walls, furniture, obstacles) manually positioned with physically consistent scales.

---

## 3: ROS 2 Distribution: Jazzy Jalisco

### Decision: ROS 2 Jazzy (Python 3.12, ament_cmake)

**Description:** Targeting ROS 2 Jazzy Jalisco on Ubuntu 24.04 LTS as the development distribution.

**Rationale:**
- Ubuntu 24.04 LTS is the project specification's target OS
- ROS 2 Jazzy corresponds to the latest stable release compatible with Python 3.12
- Python 3.12 is the system Python on Ubuntu 24.04, enabling modern package features
- Jazzy provides the latest Nav2, RTAB-Map, and perception stack versions

**Alt considered:** 
- ROS 2 Humble (Python 3.8) - EOL, Python 3.8 reached end-of-life in 2024
- ROS 2 Iron - Older, limited Python 3.5/3.6 support

**Custom vs borrowed:** Standard ROS 2 distribution - not a custom build, using officially released packages.

---

## 4: Simulator: Gazebo Harmonic

### Decision: Gazebo Sim 8 (Harmonic)

**Description:** Using Gazebo Sim 8.15.0 as the physics simulator, compatible with ROS 2 Jazzy.

**Rationale:**
- Project specification explicitly targets "Gazebo Harmonic / Gazebo Sim 8"
- This is the latest Gazebo version compatible with ROS 2 Jazzy
- Stable, well-tested physics engine for differential-drive robot simulation
- Supports RGB-D cameras, IMUs, and collision dynamics natively

**Alt considered:**
- Gazebo Gazebo (older version) - Less compatible with Jazzy
- Ignition Gazebo - Different API, would require significant rewrite

**Custom vs borrowed:** Standard ROS 2/Gazebo packages from Ubuntu repositories.

---

## 5: SLAM Backend: RTAB-Map

### Decision: RTAB-Map as initial RGB-D SLAM backend, with educational modules

**Description:** Using RTAB-Map as the production SLAM backend, while implementing separate educational modules for foundational SLAM mathematics.

**Rationale:**
- RTAB-Map is a well-established, production-quality RGB-D SLAM system
- The project requires SLAM capability but does not require developing a full SLAM backend from scratch
- Educational modules (in docs/SYSTEM_ARCHITECTURE.md) explain the underlying mathematics for transparency
- Using an established backend allows focus on the central research contribution (memory-based navigation)

**Alt considered:**
- Developing SLAM from scratch - Would divert focus from the central research contribution
- Using hector_slam - Less capable for RGB-D data, fewer Python API options
- Using Cartographer - Good RGB-D support but more complex to integrate and less Python-friendly

**Custom vs borrowed:** RTAB-Map is borrowed from existing libraries, but educational modules on camera projection, feature detection, epipolar geometry, PnP, triangulation, visual odometry, bundle adjustment, pose graph optimization, and loop closure are custom implementations for transparency.

---

## 6: Navigation Stack: Nav2

### Decision: Nav2 as conventional navigation stack, with cognitive cost layer integration

**Description:** Using Nav2 as the standard ROS 2 navigation stack, with a cognitive decision cost function that integrates with Nav2 without replacing it.

**Rationale:**
- Nav2 is the standard ROS 2 navigation stack, providing proven path planning, collision checking, and recovery behaviors
- The project requires autonomous navigation capability, and Nav2 provides reliable safety guarantees
- The cognitive layer influences Nav2 through costmap integration rather than replacement
- This approach respects Nav2's behavior trees, costmaps, and recovery behaviors

**Alt considered:**
- Replacing Nav2 entirely - Too risky, loses safety guarantees, would need to reimplement all Nav2 features
- Using a custom planner - Would need to reimplement BTs, costmaps, recovery behaviors, etc.
- Using move_base (old stack) - EOL, lacks modern features

**Custom vs borrowed:** Nav2 is borrowed from existing ROS 2 packages. The cognitive cost function (J(a) = alpha*C_path + beta*C_risk + gamma*C_memory + delta*C_uncertainty) is a custom implementation that integrates with Nav2.

---

## 7: Programming Languages: Python 3 and C++17

### Decision: Python 3 primary, C++17 for performance-critical components

**Description:** Primary implementation in Python 3 for rapid prototyping and ROS 2 integration; C++17 for performance-critical components.

**Rationale:**
- Python 3 enables rapid development of the cognitive architecture, memory system, and interface
- ROS 2 Python APIs (rclpy) are mature and well-supported
- C++17 used where performance matters (point cloud processing, real-time control)
- Balance between development speed and performance needs

**Alt considered:**
- Python only - May have performance limitations for real-time control
- C++ only - Would significantly slow prototyping and reduce accessibility
- Rust - Interesting language but immature ROS 2 integration at the time of writing

**Custom vs borrowed:** Mix of custom code and ROS 2 language bindings. Python code is custom; C++ components leverage ROS 2 client libraries.

---

## 8: Episodic Memory Backend: SQLite

### Decision: SQLite as initial persistence layer, graph representation may be added later

**Description:** Using SQLite as the lightweight, file-based persistence layer for episodic memory. A graph representation may be added where justified by retrieval patterns.

**Rationale:**
- SQLite requires no server process, making it ideal for a single-robot research platform
- Supports the structured episode data format with explicit types
- File-based approach simplifies data sharing and backup
- A graph representation can be added later if retrieval patterns justify it

**Alt considered:**
- JSON files - No query capabilities, harder to manage concurrent access
- PostgreSQL - Too heavy for a single-robot research platform, requires server
- MongoDB - Adds server dependency, overkill for structured episode data

**Custom vs borrowed:** SQLite is a borrowed library (Python sqlite3 module), but the episode schema and data model are custom implementations.

---

## 9: Memory Similarity Function

### Decision: Weighted combination of geometric, semantic, and behavioural similarity

**Description:** Using a weighted sum similarity function: S(E_i, E_t) = w_g * S_g + w_s * S_s + w_b * S_b, where:
- S_g = geometric similarity = exp(-||p_i - p_t||^2 / (2 * sigma_g^2))
- S_s = semantic similarity = |intersection(tags_i, tags_t)| / |union(tags_i, tags_t)|
- S_b = behavioural similarity = 1 - |Delta_u_i - Delta_u_t| / max_delta
- Configurable weights w_g, w_s, w_b starting at 0.5, 0.3, 0.2

**Rationale:**
- Decomposition allows incremental improvements - each similarity type can be enhanced independently
- Weighted sum provides a single scalar for decision-making while keeping components inspectable
- Starting weights are documentable and tunable
- Each component (geometric, semantic, behavioural) addresses a different aspect of "episode relevance"

**Alt considered:**
- Single similarity metric - Less informative, harder to debug when results are unexpected
- Learned embedding-only approach - Black box, harder to explain and debug for a research platform
- Graph distance only - Doesn't capture all dimensions of episode relevance (e.g., semantic change)

**Custom vs borrowed:** The mathematical formulation is custom, but the concepts (Euclidean distance, Jaccard similarity, normalized difference) are standard mathematics. The weighting scheme is a custom design decision.

---

## 10: Memory Validation

### Decision: Modular validation algorithm with explicit validity statuses

**Description:** Implementing a modular validation algorithm that compares previous and current geometric/semantic contexts, checks outcome consistency, verifies age, and produces explicit validity statuses: Valid, Potentially valid, Outdated, Contradicted, Uncertain.

**Rationale:**
- The core research question requires answering "when are previous experiences still valid?"
- A transparent validation mechanism is essential for testing this question
- Modular design allows different validation approaches to be experimentally compared
- Explicit statuses make it clear why a memory was accepted, revised, or rejected

**Alt considered:**
- Simple timeout-based invalidation - Too coarse, doesn't distinguish between different types of environment changes
- Learned validity classifier - Black box, harder to understand why a memory was accepted/rejected (violates the research principle of explainability)
- No validation - Would violate the research hypothesis entirely

**Custom vs borrowed:** The validation algorithm is a custom implementation, though it draws on standard concepts from state estimation and change detection. The five statuses (Valid, Potentially valid, Outdated, Contradicted, Uncertain) are a custom design.

---

## 11: Cognitive Decision Cost Function

### Decision: Configurable weighted cost function influencing Nav2 without replacement

**Description:** Using J(a) = alpha * C_path(a) + beta * C_risk(a) + gamma * C_memory(a) + delta * C_uncertainty(a), where:
- C_path = base navigation cost from Nav2's base_local_planner
- C_risk = physical safety cost = collision_probability * safety_weight
- C_memory = experience-related cost = 1 - max_similarity * memory_weight
- C_uncertainty = perception uncertainty * uncertainty_weight
- Default weights: alpha=1.0, beta=0.5, gamma=0.3, delta=0.2 (configurable)

**Rationale:**
- Allows the cognitive layer to influence Nav2's planning without replacing it
- Each cost component can be tuned independently
- The cost is added to Nav2's planning pipeline as an additional costmap layer or plugin
- Default weights provide a starting point for experimentation, all documentable

**Alt considered:**
- Replacing Nav2's cost function entirely - Loses safety guarantees, would break Nav2's planner pipeline
- Multiplicative combination - Harder to tune and debug; interactions between components are less transparent
- Only using C_memory - Ignores risk and uncertainty, which would be unsafe for a mobile robot

**Custom vs borrowed:** The cost function structure is custom, but each component (C_path, C_risk, etc.) draws on well-known navigation cost concepts. The specific weighting and integration approach is a custom design decision.

---

## 12: Intervention Interpretation Engine

### Decision: Rule-based transparent baseline, learned classifiers added later

**Description:** Starting with a transparent, rule-based inference engine for interpreting human interventions. Learned classifiers (e.g., neural networks) can be added later if sufficient labelled examples are available.

**Rationale:**
- The central research question involves interpretation of human interventions
- Starting with interpretable rules allows debugging, validation, and gradual learning
- Rule-based approaches are immediately usable with limited data
- Later, if sufficient labelled examples are available, a learned classifier can supplement or replace the rule-based system

**Alt considered:**
- Learned classifier from the start - Would require labelled data that may not be available initially; also creates a black box that violates the research principle of explainability
- Latent variable model - More complex than needed for initial implementation

**Custom vs borrowed:** The rule-based inference engine is a custom implementation. The comparison format (Delta_u = u_human - u_autonomous) is a custom formulation, though it draws on standard control theory concepts.

---

## 13: Teleoperation Interface: Python Web Framework

### Decision: Lightweight Python web framework (Flask/FastAPI) for cross-device compatibility

**Description:** Using a lightweight Python web framework for the teleoperation interface, accessible via web browser on any device (laptop, tablet, phone).

**Rationale:**
- A web interface works across devices without platform-specific installation
- Easy to develop iteratively with Python expertise
- Integrates naturally with ROS 2 via HTTP endpoints or websockets
- No need for desktop GUI installation on the operator's machine

**Alt considered:**
- ROS 2 GUI frameworks (rtqt_plot, rqt_publisher) - Less flexible across devices, require Qt on operator's machine
- Native desktop application (Tkinter, PyQt) - Harder to deploy across different machines, platform-specific

**Custom vs borrowed:** The web interface code is custom, using Flask or FastAPI (borrowed Python libraries). The ROS 2 integration (publishing velocity commands, subscribing to sensor data) is custom code.

---

## 14: Coordinate Frames: TF2 Standard

### Decision: Following TF2 conventions with standard frame names

**Description:** Using standard TF2 frames: world, base_link, camera_link, camera_optical_frame, odom (may differ from base_link via localizer).

**Rationale:**
- Standard TF2 frames ensure compatibility with ROS 2 tools (RViz2, Nav2)
- Clear transformation chains (base_link → camera_link → optical_frame, etc.)
- Well-documented conventions make the system inspectable and maintainable

**Alt considered:**
- Custom frame names - Would break ROS 2 tool compatibility, create confusion
- Omitting TF2 - Would make coordinate transformations impossible and break all ROS 2 functionality

**Custom vs borrowed:** Frame names and conventions are standard ROS 2/TF2. The specific transforms between frames are custom implementations.

---

## 15: Experiment Framework: ROS Bags + SQLite

### Decision: ROS 2 bags for raw data recording, SQLite for metric tracking

**Description:** Recording experiments using ROS 2 bags for raw sensor and topic data, and SQLite for metric tracking and experiment configuration.

**Rationale:**
- ROS bags capture all topic data for offline analysis and replay
- SQLite provides fast metric queries and experiment tracking
- Both are lightweight and well-integrated with ROS 2
- Comprehensive recording enables reproducible results (mandatory per spec)

**Alt considered:**
- CSV logs - Simpler but lose topic context and multivariate data structure
- InfluxDB - Adds server dependency, overkill for experiment tracking
- No structured logging - Violates the spec's reproducibility mandate, makes experiments uninterpretable

**Custom vs borrowed:** ROS 2 bag integration is part of the ROS 2 framework. The SQLite schema and metric tracking code are custom implementations.

---

## 16: Development Milestones: 10 Defined Milestones

### Decision: Fixed milestone structure with produces deliverables

### Description: Working in 10 defined milestones, each producing a working increment with documentation.

**Rationale:**
- The spec explicitly mandates milestone-based development ("Work in milestones")
- This structure prevents attempting too much at once and ensures incremental progress
- Each milestone has clear entry and exit criteria
- Documentation is produced at each step, ensuring the platform is always documented

**Alt considered:**
- Single-phase development - Would be overwhelming and risk incomplete features
- Kanban without fixed milestones - Less predictable for a research project with many interdependent components

**Custom vs borrowed:** The milestone structure is a custom project management decision, informed by software engineering best practices for research projects.

---

## 17: Documentation Structure: Per-Spec Requirements

### Decision: Every package has detailed README with specified sections

### Description: Every ROS 2 package contains a README explaining: purpose, inputs, outputs, ROS topics, ROS services/actions, dependencies, parameters, internal algorithm, failure modes, and how to test it. Architecture diagrams document coordinate frames and system architecture.

**Rationale:**
- The spec explicitly requires extensive documentation ("Every package must contain a README explaining...")
- Documenting each algorithm with "what is implemented, borrowed, custom, experimental" provides clarity for a research platform
- Architecture diagrams ensure the system is understandable and extensible

**Alt considered:**
- Minimal documentation - Faster initial development but makes the platform unmaintainable and uninterpretable
- No algorithm documentation - Violates the spec's explicit requirements, makes the platform un-extendable

**Custom vs borrowed:** Documentation requirements are spec-mandated. The actual content is custom-written for each package.

---

## 18: Testing Requirements: Comprehensive Test Suite

### Decision: Unit tests, integration tests, ROS 2 launch tests, simulation tests, and more

### Description: Creating unit tests, integration tests, ROS 2 launch tests where practical, simulation tests, data validation tests, memory persistence tests, intervention recording tests, memory retrieval tests, memory invalidation tests, and navigation regression tests.

**Rationale:**
- The spec explicitly requires comprehensive testing ("Create: unit tests, integration tests, ROS 2 launch tests where practical, simulation tests, data validation tests, memory persistence tests, intervention recording tests, memory retrieval tests, memory invalidation tests, navigation regression tests")
- Every major subsystem should be testable independently
- A successful build must be followed by a functional simulation test
- Testing ensures the platform is functionally correct before claiming features

**Alt considered:**
- Testing only the build - Would not verify functionality, only that code compiles
- No tests at all - Violates the spec's explicit testing requirements, risks undetected bugs

**Custom vs borrowed:** Test structure is custom, though it follows standard ROS 2 testing patterns (launch files, topic verification, etc.) and standard Python testing (unittest, pytest).

---

## 19: Initial Execution Instructions: Step-by-Step Following

### Decision: Following spec's 20-step initial instructions exactly

### Description: Starting with environment inspection, repository creation, robot simulation, baseline SLAM/navigation, and stopping for approval before moving to the next major milestone.

**Rationale:**
- The spec's "Initial Execution Instructions" (Section 20) provides a structured, validated onboarding process
- Following step-by-step ensures no critical setup steps are skipped
- The "stop and report" point before major milestones allows for course correction before significant effort

**Alt considered:**
- Skipping steps - Risked missing critical setup, caused problems later in development
- Implementing everything at once - Overwhelming, risked incomplete features, contradicted the milestone philosophy

**Custom vs borrowed:** The execution workflow is a custom project management decision, informed by the spec's explicit instructions.

---

## 20: Research Hypothesis: Test, Not Established Result

### Decision: Treating the hypothesis as unproven, to be tested through experimentation

### Description: The core research hypothesis ("A navigation architecture combining spatial understanding, intervention interpretation, contextual episodic memory and memory validation can reduce repeated navigation mistakes and unnecessary human interventions in previously encountered situations") is treated as a hypothesis to test, not an established result.

**Rationale:**
- Scientific discipline requires claims to be supported by evidence, not assumed
- The entire MNEMOS platform is designed as a testbed for this hypothesis
- All experiments (1-5) are designed to provide evidence pro or con the hypothesis
- Negative results (hypothesis not supported) are still valid scientific contributions

**Alt considered:**
- Claiming the hypothesis as established without experimental evidence - Pseudoscience, contradicts the research principle of reproducibility
- Only reporting positive results - Publication bias, contradicts the research principle of honest scientific inquiry

**Custom vs borrowed:** This is a fundamental philosophy decision for the project, not a code or architecture decision.

---

## Quick Reference: Decision Summary Table

| # | Decision | Key Choice | Rationale |
|---|----------|-----------|-----------|
| 1 | Robot Platform | Differential-drive + caster | Standard, compatible with Nav2, simple odometry |
| 2 | Simulator | Two indoor worlds (lab + warehouse) | Spec requirement, enables env-change experiments |
| 3 | ROS 2 Distro | Jazzy Jalisco | Python 3.12, latest Nav2/RTAB-Map versions |
| 4 | Simulator Version | Gazebo Sim 8 | Project spec target, compatible with Jazzy |
| 5 | SLAM Backend | RTAB-Map + educational modules | Production-quality, focus on research contribution |
| 6 | Navigation | Nav2 + cognitive cost layer | Standard stack, safety guarantees, integrable layer |
| 7 | Languages | Python 3 / C++17 | Balance speed and performance |
| 8 | Memory Backend | SQLite | Lightweight, file-based, no server needed |
| 9 | Similarity Function | Weighted sum (3 components) | Interpretable, modular, incremental improvement |
| 10 | Memory Validation | Modular algorithm + 5 statuses | Essential for research hypothesis, explains accept/reject |
| 11 | Cost Function | Weighted sum influencing Nav2 | Influences without replacing, maintains safety |
| 12 | Intervention Interpretation | Rule-based baseline | Transparent, data-efficient, enhancable later |
| 13 | Teleop Interface | Python web framework | Cross-device compatible, easy to develop |
| 14 | Coordinate Frames | TF2 standard | ROS 2 tool compatibility, clear transform chains |
| 15 | Experiment Recording | ROS bags + SQLite | Comprehensive, reproducible, lightweight |
| 16 | Milestones | 10 defined milestones | Structured incremental progress, documentation at each step |
| 17 | Package Documentation | Per-spec detailed READMEs | Ensures understandability, extensibility |
| 18 | Testing | Comprehensive test suite | Spec requirement, ensures functional correctness |
| 19 | Execution Instructions | Step-by-step per spec | Prevents skipped steps, enables course correction |
| 20 | Research Hypothesis | Treat as unproven hypothesis | Scientific discipline, all experiments test the hypothesis |

---

## Revision History

| Date | Version | Change |
|------|---------|--------|
| 2026-11-10 | 0.1.0 | Initial decisions document creation |
| 2026-11-10 | 0.1.1 | Added detailed rationales and alternatives for all 20 decisions |