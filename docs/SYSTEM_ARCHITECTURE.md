# MNEMOS Mathematical Foundations

## Camera Geometry and Depth Projection

### Pinhole Camera Model

The RGB-D camera follows the pinhole camera model:

```
x = (u - cx) * z / fx
y = (v - cy) * z / fy
z = depth_value
```

Where:
- (u, v) = pixel coordinates
- (x, y, z) = camera coordinates
- fx, fy = focal lengths in pixels
- cx, cy = principal point coordinates

### Depth-to-Point-Cloud Conversion

For each pixel (u, v) with depth z:

```
p_camera = R * T * [x, y, z, 1]^T
```

Where R and T are the camera-to-world transformation matrix components.

### Transformation Mathematics

#### TF2 Coordinate Frames

All sensor data is transformed into a common frame:

```
T_world_camera = T_base_link_base * T_camera_base_link
```

Where:
- T_base_link_base: Transformation from base_link to base_frame
- T_camera_base_link: Transformation from camera to base_link

#### Rotation Composition

```
R_total = R_z * R_y * R_x  (Euler angle composition)
```

Or using quaternions:

```
q_total = q_w * q_z * q_y * q_x
```

### Object Detection Geometry

#### Bounding Box Transformation

Detected bounding boxes in the camera frame are transformed to the world frame:

```
x_min_world = min(x_min_camera_transformed)
x_max_world = max(x_max_camera_transformed)
y_min_world = min(y_min_camera_transformed)
y_max_world = max(y_max_camera_transformed)
```

#### Ground Plane Removal

Points with z < threshold are removed (assuming flat ground plane):

```
if point.z < z_ground_threshold: discard
```

## SLAM Mathematics (RTAB-Map)

### Visual Odometry

```
// Notation: ^ denotes estimated, ~ denotes ground truth
odom_error = T_estimated - T_ground_truth
```

Feature-based visual odometry estimates relative pose between consecutive frames using:

1. Feature detection (e.g., ORB, SIFT)
2. Feature matching (e.g., brute-force, FLANN)
3. Essential matrix estimation
4. PnP (Perspective-n-Point) pose estimation
5. Refinement (bundle adjustment)

### Feature Detection

```
detect_features(image) -> keypoints, descriptors
```

### Feature Matching

```
matches = match_descriptors(descriptors1, descriptors2)
essential_mat, mask = find_essential_mat(points1, points2, K)
R, t = recoverPose(essential_mat, points1, points2, K)
```

### PnP (Perspective-n-Point)

Given N 3D-2D point correspondences:

```
// Solve for rotation R and translation t that minimize:
min_R,t sum_i || p_i^world * R + t - p_i^image ||^2
```

Using methods such as EPnP, P3P, or direct linear transform.

### Triangulation

Given two camera views of a 3D point:

```
// DLT (Direct Linear Transform) approach:
A = [x1' * x1, y1' * x1, x1, 0; ...]  // 2x4 per view
P = null(A)  // 4x4 matrix, take last column as triangulated point
```

## Intervention Interpretation

### Control Deviation

```
Delta_u = u_human - u_autonomous
```

Where u is the velocity command (linear and angular).

### Candidate Interpretations (Rule-Based)

Based on Delta_u and contextual information:

| Interpretation | Condition |
|---------------|-----------|
| Collision avoidance | ||robot_pos|| approaching ||obstacle|| |
| Route preference | Delta_u has positive forward component |
| Passage infeasibility | Robot stuck or near-obstacle |
| Unexpected obstacle | New obstacle not in previous map |
| Navigation uncertainty | High uncertainty in perception |
| Stopping/waiting preference | Human commands zero velocity |
| Unclassified | None of the above |

## Episodic Memory Similarity

```
S(E_i, E_t) = w_g * S_g + w_s * S_s + w_b * S_b

S_g = geometric similarity = exp(-||p_i - p_t||^2 / (2 * sigma_g^2))
S_s = semantic similarity = |intersection(tags_i, tags_t)| / |union(tags_i, tags_t)|
S_b = behavioural similarity = 1 - |Delta_u_i - Delta_u_t| / max_delta

Where:
  - ||p_i - p_t|| = Euclidean distance between episode and current robot pose
  - sigma_g = geometric hyperparameter (configurable)
  - tags = set of semantic labels (objects, location tags)
  - Delta_u = velocity command difference
  - max_delta = maximum observed deviation (normalization)
```

Weights w_g, w_s, w_b are configurable and must be documented.

## Memory Validation

### Validity Check Components

For each retrieved episode E_i, validate against current state:

1. **Geometric consistency**: Has the environment geometry changed? Compare obstacle configurations.
2. **Semantic consistency**: Have semantic labels changed? (e.g., passage was blocked, now clear)
3. **Outcome consistency**: Does the previous navigation outcome still hold?
4. **Age check**: How old is the episode? (old episodes may be outdated)
5. **Confidence threshold**: Is the stored confidence above minimum threshold?

### Validity Statuses

- **Valid**: All checks pass, memory applies
- **Potentially valid**: Most checks pass, but some uncertainty remains
- **Outdated**: Environment has changed significantly (e.g., passage cleared)
- **Contradicted**: Current state directly contradicts memory (e.g., memory says "blocked", now clear)
- **Uncertain**: Insufficient data to determine validity

### Validation Algorithm

```
validate_episode(E_i, current_state):
  scores = {}
  
  # Geometric check
  geometric_score = compare_obstacle_config(
    E_i.geometric_context, current_state.obstacles)
  scores['geometric'] = geometric_score
  
  # Semantic check
  semantic_score = compare_semantic_context(
    E_i.semantic_context, current_state.semantic_labels)
  scores['semantic'] = semantic_score
  
  # Outcome check
  outcome_score = check_outcome_consistency(
    E_i.navigation_outcome, current_state.navigation_result)
  scores['outcome'] = outcome_score
  
  # Age check
  age_score = 1.0 if E_i.age < max_age else decay(E_i.age)
  scores['age'] = age_score
  
  # Aggregate validity
  overall_validity = aggregate_validity(scores)
  
  return overall_validity, scores
```

## Cognitive Decision Cost Function

```
J(a) = alpha * C_path(a) + beta * C_risk(a) + gamma * C_memory(a) + delta * C_uncertainty(a)

Where each cost component:

C_path(a) = base navigation cost for action a (from Nav2 base_local_planner)
C_risk(a) = physical safety cost = collision_probability(a) * safety_weight
C_memory(a) = experience-related cost = 1 - max_similarity * memory_weight
  where max_similarity = max over retrieved episodes of S(E_i, current_state)
C_uncertainty(a) = uncertainty cost = perception_uncertainty(a) * uncertainty_weight

Default configurable weights:
  alpha = 1.0  (normalize so sum = 1 or as configured)
  beta = 0.5
  gamma = 0.3 (tunable, depends on memory reliability)
  delta = 0.2
```

All weights are configurable via ROS 2 parameters and must be documented.

## Episode Serialization

Episodes are stored in SQLite with the following schema:

```sql
CREATE TABLE episodes (
  id INTEGER PRIMARY KEY,
  timestamp REAL NOT NULL,
  robot_pose_x REAL,
  robot_pose_y REAL,
  robot_pose_theta REAL,
  goal_x REAL,
  goal_y REAL,
  local_geometric_context TEXT,  -- JSON-serialized
  semantic_context TEXT,         -- JSON-serialized
  planned_action TEXT,           -- JSON-serialized
  human_intervention TEXT,       -- JSON-serialized
  command_difference TEXT,       -- JSON-serialized
  resulting_trajectory TEXT,     -- JSON-serialized
  final_outcome TEXT,            -- JSON-serialized
  candidate_interpretation TEXT,
  confidence_score REAL,
  validity_status TEXT,
  episode_age REAL
);
```

All fields are explicit with documented types and meaning.