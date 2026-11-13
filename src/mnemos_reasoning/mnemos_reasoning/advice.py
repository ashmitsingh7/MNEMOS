"""Convert admitted memories into explainable, bounded *advice*, never velocity commands."""
from dataclasses import dataclass

from mnemos_memory.model import Episode, EpisodeKind, ValidationResult
from mnemos_memory.retrieval import Similarity


@dataclass(frozen=True)
class CognitiveAdvice:
    cost_bias: float
    confidence: float
    action: str
    explanation: tuple[str, ...]


def advise(episode: Episode, similarity: Similarity, validation: ValidationResult,
           maximum_absolute_bias: float = 0.35) -> CognitiveAdvice:
    """Apply a cap so perception/collision constraints always dominate memory."""
    if not validation.admissible:
        return CognitiveAdvice(0.0, 0.0, 'abstain', validation.explanation)
    confidence = min(1.0, episode.confidence * similarity.total * validation.score)
    direction = 1.0 if episode.kind in (EpisodeKind.AVOID, EpisodeKind.RECOVERY) else -1.0
    if episode.kind == EpisodeKind.UNCERTAIN:
        direction = 0.0
    bias = direction * min(maximum_absolute_bias, maximum_absolute_bias * confidence)
    action = 'raise_local_cost' if bias > 0 else ('lower_local_cost' if bias < 0 else 'abstain')
    explanation = (*validation.explanation, f'similarity={similarity.total:.2f}',
                   f'kind={episode.kind.value}', f'bounded_bias={bias:.3f}')
    return CognitiveAdvice(bias, confidence, action, explanation)
