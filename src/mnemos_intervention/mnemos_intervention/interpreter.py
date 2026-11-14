"""Rule-based interpretation: grounded claims and evidence rather than guessed intent."""
from dataclasses import dataclass
from math import hypot

from mnemos_memory.model import EpisodeKind


@dataclass(frozen=True)
class Command:
    linear: float
    angular: float


@dataclass(frozen=True)
class Interpretation:
    kind: EpisodeKind
    confidence: float
    evidence: tuple[str, ...]


def interpret(autonomous: Command, human: Command, nearest_obstacle: float | None,
              sustained_seconds: float, min_duration: float = 0.40) -> Interpretation:
    """Conservative rules; unclear corrections remain explicitly uncertain."""
    linear_delta = human.linear - autonomous.linear
    angular_delta = human.angular - autonomous.angular
    magnitude = hypot(linear_delta, angular_delta)
    if sustained_seconds is None or sustained_seconds < min_duration or magnitude < 0.12:
        return Interpretation(EpisodeKind.UNCERTAIN, 0.0, ('Deviation was too brief or too small.',))
    evidence = [f'linear_delta={linear_delta:.2f}', f'angular_delta={angular_delta:.2f}',
                f'duration={sustained_seconds:.2f}s']
    if nearest_obstacle is not None:
        evidence.append(f'nearest_obstacle={nearest_obstacle:.2f}m')
    if nearest_obstacle is not None and nearest_obstacle < 0.65 and linear_delta < -0.05:
        return Interpretation(EpisodeKind.AVOID, 0.90, tuple(evidence + ['Human reduced forward motion near an obstacle.']))
    if autonomous.linear > 0.10 and abs(human.linear) < 0.03:
        return Interpretation(EpisodeKind.WAIT, 0.72, tuple(evidence + ['Human stopped an active autonomous command.']))
    if linear_delta > 0.10 and (nearest_obstacle is None or nearest_obstacle > 0.80):
        return Interpretation(EpisodeKind.PREFER, 0.58, tuple(evidence + ['Human advanced in open space.']))
    if magnitude > 0.30:
        return Interpretation(EpisodeKind.RECOVERY, 0.52, tuple(evidence + ['Large sustained override; cause is not inferred.']))
    return Interpretation(EpisodeKind.UNCERTAIN, 0.25, tuple(evidence + ['No reliable rule matched.']))
