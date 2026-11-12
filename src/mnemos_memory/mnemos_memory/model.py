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
        for field_name in ('scan_signature', 'semantic_tags', 'evidence'):
            record[field_name] = tuple(record[field_name])
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
