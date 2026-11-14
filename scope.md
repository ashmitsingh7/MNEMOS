# MNEMOS Project Scope and Action Plan

## Purpose

MNEMOS investigates whether a mobile robot can learn from human navigation
corrections, retrieve relevant past episodes, and recognize when changed
conditions make those episodes unsafe or unhelpful. This document defines the
next implementation sequence and the evidence required to advance between
stages.

The operating principle is that current sensing, collision handling, and
explicit human control take priority over historical memory. Every memory
influence must be bounded, attributable to an episode, and possible to reject.

## Current state

Implemented ROS 2 packages cover Gazebo simulation, robot description,
bringup, SLAM input readiness, command arbitration, intervention capture,
episodic storage and retrieval, validation/advice, and trial metrics.

Verified in the current environment:

- All nine ROS packages build with `colcon`.
- Gazebo starts and spawns the MNEMOS model.
- Lidar publishes and the SLAM readiness monitor reports all expected inputs.
- `odom -> base_footprint` is broadcast and resolves through TF2.
- The command arbiter, intervention recorder, and memory adviser start
  together; without a fresh command source, the arbiter reports a stop.
- Unit tests cover episode persistence/retrieval, interpretation, memory
  contradiction, bounded advice, command arbitration, and trial accounting.

Still unverified or incomplete:

Still unverified or incomplete:
- Nav2 is not installed system-wide; goal navigation has not been run. (RTAB-Map
  SLAM is now verified via a user-space overlay: Gazebo + RTAB-Map + readiness
  monitor report `slam_inputs_ready: true`.)
- A controlled human command has not yet been traced through the arbiter to
  physical simulated robot motion and a subsequent stop (cognitive nodes start;
  a live trace with simulation is the next step).
- Memory advice is published for inspection but does not influence Nav2.
- Intervention episodes now capture goal, session, command streams, interval,
  outcome, and bag reference; the interpreter is evaluated against a labeled set
  (48/48 tests).
- No experiment results or performance claims exist.

## Sequenced plan

### Stage 1 — Complete the conventional navigation baseline

**Work**

1. Install the ROS 2 Jazzy RTAB-Map and Nav2 packages on a machine with
   administrator authorization.
2. Build the map with the live Gazebo sensor topics and inspect its scale,
   orientation, and obstacle coverage.
3. Launch Nav2 with the saved map and verify AMCL localization, planner and
   controller lifecycle state, and all required TF links.
4. Send a small fixed set of safe goals in the lab and record success,
   failure, path length, elapsed time, and collisions.

**Exit gate**: the robot completes repeatable baseline goals with functioning
obstacle avoidance and no unresolved TF or topic issues. Save launch logs,
maps, seeds, and trial records. If system dependencies cannot be installed,
keep this stage open and continue only with work that does not depend on them.

### Stage 2 — Verify human-priority command control

**Work**

1. Route Nav2 output to `/cmd_vel_autonomy` and final arbiter output to
   `/cmd_vel`.
2. Provide a teleoperation input on `/cmd_vel_human` and an explicit
   `/mnemos/human_override` state.
3. Exercise autonomy, override activation, override release, stale human
   input, stale autonomy input, speed clamping, and emergency zero command.
4. Observe both `/mnemos/command_arbitration` and robot odometry to confirm
   each expected transition.

**Exit gate**: every transition produces the documented source and command;
stale input always stops the robot, and an override never permits autonomous
commands to leak through while active.

### Stage 3 — Make intervention episodes experimentally grounded

**Work**

1. Capture the active goal, map/session identifier, pose, scan context, both
   command streams, intervention interval, and short post-intervention
   outcome.
2. Preserve raw ROS bag references so episode summaries can be audited
   against source data.
3. Define human-readable interpretation labels and collect a small labeled
   set of representative interventions.
4. Measure rule-classifier confusion by class and identify ambiguous cases
   where the right behavior is `uncertain`.

**Exit gate**: episode records round-trip from SQLite, can be traced to a bag
and trial, and interpretation results are reported with a labeled evaluation
set rather than selected anecdotes.

### Stage 4 — Validate contextual memory offline

**Work**

1. Define a context representation using pose-relative geometry, semantic
   labels where available, action delta, and uncertainty.
2. Compare retrieval candidates against human relevance judgments.
3. Test moved obstacles, cleared passages, temporary obstacles, and novel
   nearby geometry.
4. Measure retrieval precision, contradiction detection, false acceptance,
   false rejection, and abstention rates.
5. Calibrate similarity and validation thresholds on a development set, then
   freeze them before held-out trials.

**Exit gate**: held-out changed-context tests show the system rejects
contradicted episodes at the predeclared safety threshold. Report uncertainty
and failure cases.

### Stage 5 — Integrate bounded memory advice with Nav2

**Work**

1. Choose and document an integration point such as a custom costmap layer or
   planner cost adapter.
2. Apply advice only to local route preference; keep obstacle marking,
   clearing, inflation, and collision checks authoritative.
3. Default to zero influence when messages are stale, inputs are missing,
   validation fails, or memory confidence is insufficient.
4. Add runtime diagnostics linking each cost change to its episode,
   validation scores, and final planner decision.
5. Test collision avoidance with memory enabled, disabled, contradicted, and
   disconnected.

**Exit gate**: safety tests demonstrate that memory cannot make occupied or
unsafe space traversable, and node/topic loss returns the system to ordinary
Nav2 behavior.

### Stage 6 — Run controlled experiments

Use the existing A/B/C/D protocol as a starting point and revise it before
data collection if the implemented feature boundaries change. Use matched
simulator seeds and scenarios, randomize run order, preserve all failed runs,
and keep evaluation trials separate from threshold tuning.

Report at minimum:

- navigation success and failure rate;
- collision events;
- intervention count per goal;
- path length and time-to-goal;
- intervention interpretation precision/recall;
- retrieval precision and validation false-accept/false-reject rates;
- stale-memory reuse and contradiction-abstention rates;
- number of trials and confidence intervals.

**Exit gate**: a reproducible report from the trial ledger and raw bags, with
no omitted failures and no unsupported improvement claim.

### Stage 7 — Package the research contribution

1. Freeze code, parameters, environment assets, and experiment protocol.
2. Publish setup instructions and exact commands for reproducing each
   configuration.
3. Document negative results and sensitivity to thresholds, sensor noise,
   and layout changes.
4. State clearly which components are standard ROS/Nav2/Gazebo and which
   components are MNEMOS contributions.

## Engineering rules for each stage

- Implement one stage at a time and record its objective, changes, evidence,
  known failures, and exit-gate status.
- Do not mark a stage complete because its code compiles; use the stage's
  operational acceptance gate.
- Keep memory influence inspectable and bounded. On uncertainty, abstain.
- Do not let learned route preferences suppress live obstacle evidence or
  human override.
- Preserve raw data and failed trials; never manufacture or infer experiment
  results from successful demonstrations alone.

## Immediate next action

Resume Stage 1 by installing RTAB-Map and Nav2 on a host with sudo
authorization. Once installed, run the baseline mapping and navigation gates
before moving to Stage 2's controlled teleoperation experiment.
