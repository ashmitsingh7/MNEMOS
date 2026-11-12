# MNEMOS Cognitive Architecture

## Contribution boundary

MNEMOS does not replay a human-operated path and it does not replace Nav2
collision checking. It captures a **contextual correction** and may later emit
a bounded, auditable local-cost suggestion only if current evidence supports
that correction. This makes the experimental claim falsifiable: every
influence can be traced to an episode, similarity terms, validation factors,
and a capped cost bias.

```
autonomy command ─┐
                  ├─ Command arbiter ─> /cmd_vel
human command ────┘          │
                             └─ Intervention recorder ──> SQLite episode ledger
odom + lidar ────────────────┘                          ▼
odom + lidar ─────> Context query ─> validate ─> bounded advice ─> Nav2 adapter (future)
                                              └─> audit topic
```

## Episode contract

An episode has an ID, timestamp, pose, 24-sector lidar signature, optional
semantic tags, human/autonomy command delta, evidence strings, interpretation,
and confidence. Raw camera data and full trajectories are deliberately not
stored in this first ledger: ROS bags remain the source of raw experimental
evidence, while the episode database stays small and inspectable.

The present interpreter distinguishes `avoid`, `wait`, `prefer`, `recovery`,
and `uncertain`. Its rules only claim what their inputs support. For example,
the high-confidence `avoid` rule requires a sustained reduction in forward
motion while a lidar return is closer than 0.65 m.

## Retrieval and validation

Similarity combines pose/scan geometry (0.55), semantic-tag overlap (0.25),
and command-behaviour similarity (0.20). Validation recomputes geometry,
semantics, and age scores. A geometry score under 0.25 is a direct
contradiction; memory influence is disabled. Scores below 0.48 are outdated;
scores from 0.48 to 0.72 are tentative and explicitly labelled as such.

## Safety contract

`memory_advisor` never publishes `/cmd_vel`, changes a Nav2 safety threshold,
or takes ownership of TF. It emits `/mnemos/memory_cost_bias` and a JSON audit
record on `/mnemos/memory_advice`. The absolute bias is capped at 0.35 by
default, and it is zero for contradicted, outdated, or context-insufficient
memories. A future Nav2 costmap layer may consume this topic only after an
integration test proves that the existing obstacle and inflation layers still
dominate it.

## Operating it

`mnemos_control` now owns the final `/cmd_vel` topic. The human override
Boolean makes intervention boundaries explicit; while it is active, a stale
human command causes a fail-safe stop rather than a fall-back to autonomy. The
recorder only learns while this override is active. It consumes the inputs
below:

```text
/cmd_vel_autonomy  geometry_msgs/Twist  proposed autonomous command
/cmd_vel_human     geometry_msgs/Twist  current human override command
```

With the navigation stack running, launch the cognitive processes with:

```bash
ros2 launch mnemos_bringup cognitive.launch.py
```

Inspect every decision during a trial:

```bash
ros2 topic echo /mnemos/intervention_events
ros2 topic echo /mnemos/memory_advice
ros2 topic echo /mnemos/memory_cost_bias
```

The current package supplies capture, storage, retrieval, validation, and
advice. It intentionally stops short of installing a Nav2 costmap plugin:
that is a safety-critical integration to implement after live baseline
validation and controlled experiment acceptance tests are in place.
