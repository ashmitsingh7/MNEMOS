"""Interpretable context similarity; intentionally no opaque learned embedding."""
from dataclasses import dataclass
from math import exp, hypot

from .model import Episode


@dataclass(frozen=True)
class Similarity:
    total: float
    geometry: float
    semantics: float
    behavior: float


def _jaccard(left: tuple[str, ...], right: tuple[str, ...]) -> float:
    a, b = set(left), set(right)
    return 1.0 if not a and not b else len(a & b) / len(a | b)


def signature_similarity(left: tuple[float, ...], right: tuple[float, ...], scale: float = 1.5) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    if scale <= 0:
        return 1.0 if left == right else 0.0
    distance = sum((a - b) ** 2 for a, b in zip(left, right)) / len(left)
    return exp(-distance / (2 * scale * scale))


def compare(episode: Episode, current: Episode, position_sigma: float = 1.25) -> Similarity:
    distance = hypot(episode.pose_x - current.pose_x, episode.pose_y - current.pose_y)
    if position_sigma <= 0:
        position = 1.0 if distance == 0.0 else 0.0
    else:
        position = exp(-(distance ** 2) / (2 * position_sigma * position_sigma))
    scan = signature_similarity(episode.scan_signature, current.scan_signature)
    geometry = 0.45 * position + 0.55 * scan
    semantics = _jaccard(episode.semantic_tags, current.semantic_tags)
    command_gap = hypot(episode.command_delta_linear - current.command_delta_linear,
                        episode.command_delta_angular - current.command_delta_angular)
    behavior = exp(-command_gap)
    return Similarity(total=0.55 * geometry + 0.25 * semantics + 0.20 * behavior,
                      geometry=geometry, semantics=semantics, behavior=behavior)


def retrieve(episodes: list[Episode], current: Episode, minimum_similarity: float = 0.55,
             limit: int = 5) -> list[tuple[Episode, Similarity]]:
    if not episodes or current is None:
        return []
    if limit is None:
        limit = len(episodes)
    if limit <= 0:
        return []
    matches = [(episode, compare(episode, current)) for episode in episodes if episode is not None]
    matches = [match for match in matches if match[1].total >= minimum_similarity]
    matches.sort(key=lambda match: match[1].total, reverse=True)
    return matches[:limit]
