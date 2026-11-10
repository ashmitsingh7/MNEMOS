# MNEMOS Glossary

## A

**Ablation Study** — Experiment 5 that compares navigation configurations with different combinations of features: baseline (A), intervention learning (B), intervention learning + episodic memory (C), and all three with memory validation (D).

**Agent** — In the context of reinforcement learning or decision-making, the robot/agent that interacts with the environment and makes navigation decisions.

**Algorithm** — A step-by-step procedure for solving a problem. In MNEMOS, distinguishes between:
- *Implemented*: Code that exists and functions in the platform
- *Borrowed*: Code taken from existing libraries (e.g., RTAB-Map, Nav2)
- *Custom*: Original implementation developed for MNEMOS
- *Experimental*: Algorithms still under evaluation, not yet finalized

**C** — Short label for "Navigation with intervention learning + episodic memory" in ablation study (Experiment 5).

**C_path** — Navigation cost component in the cognitive decision function: base navigation cost for action `a` from Nav2's base_local_planner.

**C_risk** — Physical safety cost component: collision probability of action `a` multiplied by a safety weight.

**C_memory** — Experience-related cost component: 1 - max_similarity * memory_weight, where max_similarity is the highest episodic similarity score for the current state.

**C_uncertainty** — Uncertainty cost component: perception uncertainty for action `a` multiplied by an uncertainty weight.

**Cognitive Decision Engine** — The central module that computes J(a) for each candidate navigation action and selects the optimal one, integrating path costs, risk, memory, and uncertainty.

**Cognitive Navigation Engine** — The integration layer that combines memory with Nav2 using the cost function J(a).

**Collaboration** — Not applicable; this is a single-robot research platform.

## D

**D** — Short label for "Navigation with intervention learning, episodic memory and memory validation" in ablation study (Experiment 5).

**Decision Cost Function** — The function J(a) = alpha * C_path(a) + beta * C_risk(a) + gamma * C_memory(a) + delta * C_uncertainty(a) that evaluates each navigation action.

**Decision Engine** — Synonym for Cognitive Decision Engine.

## E

** episode ** — A structured memory entry containing: unique ID, timestamp, spatial location, robot pose, current navigation goal, local geometric context, semantic context, planned autonomous action, human intervention, difference between autonomous and human commands, resulting trajectory, final outcome, candidate interpretation, confidence score, and memory validity status.

**E_g** — Geometric similarity between two episodes: exp(-||p_i - p_t||^2 / (2 * sigma_g^2)), where ||p_i - p_t|| is the Euclidean distance between episode and current robot pose, and sigma_g is a configurable hyperparameter.

**E_s** — Semantic similarity between two episodes: |intersection(tags_i, tags_t)| / |union(tags_i, tags_t)|, based on sets of semantic labels (objects, location tags).

**E_b** — Behavioural similarity between two episodes: 1 - |Delta_u_i - Delta_u_t| / max_delta, based on velocity command differences, normalized by maximum observed deviation.

**Experiment 1** — Conventional baseline: SLAM + Nav2 navigation only. Measures navigation success, path length, time-to-goal, collision count, navigation failures, and intervention count.

**Experiment 2** — Human intervention learning: Enables intervention capture and interpretation. Measures classification accuracy against human-labelled data, interpretation confidence, repeated intervention frequency, and navigation success.

**Experiment 3** — Episodic memory: Enables contextual memory and retrieval. Measures retrieval precision, retrieval relevance, repeated navigation mistakes, human interventions per task, and navigation success.

**Experiment 4** — Memory validation: Changes the environment between navigation sessions. Measures outdated memory reuse, memory invalidation accuracy, adaptation time, and navigation success after environmental changes.

**Experiment 5** — Ablation study: Compares configurations A through D. Reports results separately for eachConfiguration.

**F** — Not used as a primary glossary term.

## F

**False Positive** — In memory validation: a memory is marked "Valid" but the environment has changed and the memory should not apply.

**False Negative** — In memory validation: a memory is marked "Outdated" or "Contradicted" but the environment is actually the same and the memory would have been helpful.

## G

**Geometric Context** — The spatial arrangement of obstacles, walls, doorways, and other environmental features around the robot at a given time. Serialized as JSON and stored with each episode.

**Gazebo Sim** — The 3D physics simulator (Gazebo Harmonic / Gazebo Sim 8) used in the MNEMOS platform.

**Goal** — The navigation target/orientation specified for the robot to reach. Stored as part of each episode's state.

## H

**Human Intervention** — A corrective action taken by a human operator during teleoperation, overriding the autonomous velocity commands. Recorded as part of each episode with start/end time, autonomous and human commands, and resulting trajectory.

**Human-in-the-Loop** — The overall operating paradigm where a human can intervene at any time during robot navigation.

## I

**Interpretation** — A candidate label for what a human intervention meant, such as: collision avoidance, route preference, passage infeasibility, unexpected obstacle, navigation uncertainty, stopping/waiting preference, or unclassified. Each interpretation has an associated confidence score.

**Interpretation Engine** — The Intervention Interpretation Engine (mnemos_intervention package) that produces candidate interpretations from control deviation and contextual information.

## J

**J(a)** — The cognitive decision cost function: J(a) = alpha * C_path(a) + beta * C_risk(a) + gamma * C_memory(a) + delta * C_uncertainty(a), where `a` is a navigation action.

## K

**Not used** — No primary glossary terms under this letter.

## L

**Learning Classifier** — A machine learning model (e.g., neural network) that could eventually replace or supplement the rule-based interpretation engine. Not implemented in the initial version; added later if sufficient labelled examples are available.

**Localization** — The robot's ability to determine its position within the spatial map. Provided by RTAB-Map in MNEMOS.

## M

**Map** — The spatial representation of the environment built by RTAB-Map (metric) and optionally extended with topological and semantic layers.

**Memory** — Synonym for Episodic Memory.

**Memory Validation** — The process of evaluating whether a retrieved episode is still applicable given the current environment and conditions. Produces explicit validity statuses: Valid, Potentially valid, Outdated, Contradicted, Uncertain.

**Metric Map** — A representation of physical geometry and obstacle locations. One of the four representations in the Spatial World Model.

**Milestone** — A development phase in the MNEMOS workflow. Each milestone produces a working increment with documentation. There are 10 defined milestones (see Development Workflow, Section 19 of the spec).

**Mode A** — Explore: The robot enters an unfamiliar environment and navigates using conventional autonomous navigation.

**Mode B** — Human Control: The operator can take control at any time via the teleoperation interface.

**Mode C** — Experience Formation: After an intervention, MNEMOS constructs a contextual episode.

**Mode D** — Cognitive Autonomous Navigation: When a previously encountered situation occurs, the cognitive architecture retrieves and evaluates relevant episodes to influence navigation.

## N

**Not Used** — No primary glossary terms under this letter.

## O

**Outcome** — The result of a navigation attempt, stored with each episode. Examples: "reached goal", "collision", "timeout", "stalled".

**Outlier** — In similarity calculation: an episode with an unusually high or low similarity score that may unduly influence decisions.

## P

**Potentially Valid** — A memory validity status indicating that most validity checks pass but some uncertainty remains. The memory may or may not apply depending on additional conditions.

## Q

**Not used** — No primary glossary terms under this letter.

## R

**Raw Data** — Unprocessed sensor data (RGB images, depth images, IMU readings, odometry) recorded via ROS 2 bags.

**Recipe** — Not applicable; this is a research platform, not a cooking application.

**RBT** — Not a primary term in this glossary.

**RTAB-Map** — The RGB-D SLAM backend used for visual odometry, mapping, localization, and loop closure.

**S** — Not used as a primary glossary term.

**S_g** — Geometric similarity component of episodic memory similarity function.

**S_s** — Semantic similarity component of episodic memory similarity function.

**S_b** — Behavioural similarity component of episodic memory similarity function.

**Semantic Context** — The meaningful objects and locations in the robot's environment at a given time (e.g., "doorway", "workstation", "corridor", "table", "chair"). Stored as serialized JSON with each episode.

**Semantic Map** — One of the four representations in the Spatial World Model, representing meaningful objects and locations.

**Spatial Relationship** — A relationship between environmental elements, such as: "Doorway connects Room A and Corridor B", "Workstation located in Laboratory A", "Obstacle blocks Corridor C", "Passage has narrow-width property".

**Spatial World Model** — The architectural component (mnemos_world_model package) that maintains multiple representations of the environment: metric, topological, semantic, and spatial relationship representations.

**Specification** — The project specification document ( Sections 1-20) that defines MNEMOS's objectives, architecture, and experimental framework.

## S

** Similarity Function ** — The function S(E_i, E_t) = w_g * S_g + w_s * S_s + w_b * S_b that computes the similarity between two episodes. Weights w_g, w_s, w_b are configurable.

**Simulation** — The Gazebo Harmonic-based robot simulation environment used for development and testing.

**SQLite** — The lightweight, file-based database used for episodic memory persistence.

## T

**TF2** — The coordinate transformation system used throughout ROS 2. Maintains the tree of frames: world, base_link, camera_link, odom, etc.

**Teloporation** — Not a word; see "Teleoperation".

**Teleoperation** — Human control of the robot via the teleoperation interface (Mode B). Also refers to the interface package (mnemos_teleoperation) and the act of controlling the robot.

**Tracker** — Not a primary glossary term.

## U

**Uncertainty** — A measure of how well the robot perceives and understands its current environment. Tracks perception confidence, model uncertainty, and environmental change uncertainty.

**Uncertainty Cost** — C_uncertainty(a) in the decision cost function, representing the cost of acting under high uncertainty.

**Unclassified Intervention** — A human intervention that does not match any of the predefined interpretation categories (collision avoidance, route preference, passage infeasibility, unexpected obstacle, navigation uncertainty, stopping/waiting preference). Interpreted as "unknown" with lower confidence.

## V

**Valid** — A memory validity status indicating that all validity checks pass and the memory can influence navigation decisions.

**Validity Check** — A component of the memory validation algorithm that compares previous and current geometric/semantic contexts, checks outcome consistency, verifies age, and produces a validity status.

**Validity Status** — The explicit status assigned to each episode after validation: Valid, Potentially valid, Outdated, Contradicted, or Uncertain.

**Version** — The current version of the MNEMOS platform, starting at 0.1.0.

## W

**Not used** — No primary glossary terms under this letter.

## X, Y, Z

**Not used** — No primary glossary terms under these letters.

---

## Quick Reference: Key Terms

| Term | Definition |
|------|-----------|
| Episode | Structured memory entry with ID, timestamp, pose, goal, contexts, intervention, outcome |
| S_g | Geometric similarity: exp(-||p_i - p_t||^2 / (2*sigma_g^2)) |
| S_s | Semantic similarity: |intersection/tags_i, tags_t| / |union/tags_i, tags_t|| |
| S_b | Behavioural similarity: 1 - |Delta_u_i - Delta_u_t| / max_delta |
| J(a) | Cognitive decision cost: alpha*C_path + beta*C_risk + gamma*C_memory + delta*C_uncertainty |
| Valid/Outdated/Contradicted | Memory validity statuses after validation algorithm |
| RTAB-Map | RGB-D SLAM backend |
| Nav2 | Standard ROS 2 navigation stack |
| SQLite | Episode persistence backend |
| TF2 | Coordinate transformation system |

---

## Revision History

| Date | Version | Change |
|------|---------|--------|
| 2026-11-06 | 0.1.0 | Initial glossary document |