"""Domain model deliberately independent of ROS messages and Nav2 internals."""
from dataclasses import asdict, dataclass, field
from enum import Enum
from time import time
from typing import Any
from uuid import uuid4


class EpisodeKind(str, Enum):
    AVOID = 'avoid'
    PREFER = 'prefer'
    WAIT = 'wait'
    RECOVERY = 'recovery'
    UNCERTAIN = 'uncertain'


class ValidationStatus(str, Enum):
    VALID = 'valid'
    TENTATIVE = 'tentative'
    OUTDATED = 'outdated'
    CONTRADICTED = 'contradicted'
    INSUFFICIENT_CONTEXT = 'insufficient_context'


@dataclass(frozen=True)
class Episode:
    """A compact observation, never a recorded trajectory to blindly replay."""
    kind: EpisodeKind
    pose_x: float
    pose_y: float
    pose_yaw: float
    scan_signature: tuple[float, ...]
    semantic_tags: tuple[str, ...] = ()
    command_delta_linear: float = 0.0
    command_delta_angular: float = 0.0
    confidence: float = 0.0
    evidence: tuple[str, ...] = ()
    goal_x: float | None = None
    goal_y: float | None = None
    map_session_id: str | None = None
    autonomous_command_linear: float = 0.0
    autonomous_command_angular: float = 0.0
    human_command_linear: float = 0.0
    human_command_angular: float = 0.0
    intervention_started_at: float | None = None
    intervention_ended_at: float | None = None
    outcome: str | None = None
    bag_reference: str | None = None
    created_at: float = field(default_factory=time)
    identifier: str = field(default_factory=lambda: str(uuid4()))

    def to_record(self) -> dict[str, Any]:
        record = asdict(self)
        record['kind'] = self.kind.value
        return record

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> 'Episode':
        record = dict(record)
        record['kind'] = EpisodeKind(record['kind'])
        import json as _json
        for field_name in ('scan_signature', 'semantic_tags', 'evidence'):
            value = record.get(field_name)
            if isinstance(value, str):
                try:
                    value = _json.loads(value)
                except (ValueError, TypeError):
                    value = (value,)
            record[field_name] = tuple(value) if value is not None else ()
        # Backward-compatible defaults for records created before Stage 3 fields.
        defaults = {
            'map_session_id': None,
            'autonomous_command_linear': 0.0,
            'autonomous_command_angular': 0.0,
            'human_command_linear': 0.0,
            'human_command_angular': 0.0,
            'intervention_started_at': None,
            'intervention_ended_at': None,
            'outcome': None,
            'bag_reference': None,
            'goal_x': None,
            'goal_y': None,
        }
        for key, value in defaults.items():
            if record.get(key) is None and key in ('autonomous_command_linear', 'autonomous_command_angular',
                                                   'human_command_linear', 'human_command_angular'):
                record[key] = value
            else:
                record.setdefault(key, value)
        return cls(**record)


@dataclass(frozen=True)
class ValidationResult:
    status: ValidationStatus
    score: float
    geometry_score: float
    semantic_score: float
    age_score: float
    explanation: tuple[str, ...]

    @property
    def admissible(self) -> bool:
        return self.status in (ValidationStatus.VALID, ValidationStatus.TENTATIVE)
