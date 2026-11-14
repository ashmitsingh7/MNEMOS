"""Small, auditable helpers for evaluating the rule-based intervention interpreter."""
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable

from .interpreter import Command, interpret
from mnemos_memory.model import EpisodeKind


@dataclass(frozen=True)
class LabeledIntervention:
    """A human-labelled example used to audit interpretation rules."""
    autonomous: Command
    human: Command
    nearest_obstacle: float | None
    sustained_seconds: float
    expected: EpisodeKind
    name: str = ''


LABELED_INTERVENTIONS: tuple[LabeledIntervention, ...] = (
    LabeledIntervention(Command(0.5, 0.0), Command(0.0, 0.0), 0.4, 1.0, EpisodeKind.AVOID, 'obstacle reduction'),
    LabeledIntervention(Command(0.5, 0.0), Command(0.0, 0.1), 5.0, 1.0, EpisodeKind.WAIT, 'stop at active command'),
    LabeledIntervention(Command(0.1, 0.0), Command(0.3, 0.0), 5.0, 1.0, EpisodeKind.PREFER, 'advance in open space'),
    LabeledIntervention(Command(0.1, 0.0), Command(0.1, 0.5), 5.0, 1.0, EpisodeKind.RECOVERY, 'large angular override'),
    LabeledIntervention(Command(0.1, 0.0), Command(0.12, 0.0), 5.0, 0.1, EpisodeKind.UNCERTAIN, 'brief deviation'),
    LabeledIntervention(Command(0.1, 0.0), Command(0.11, 0.0), 5.0, 1.0, EpisodeKind.UNCERTAIN, 'small deviation'),
)


def predict(example: LabeledIntervention, min_duration: float = 0.40) -> EpisodeKind:
    return interpret(example.autonomous, example.human, example.nearest_obstacle,
                    example.sustained_seconds, min_duration=min_duration).kind


def confusion_matrix(examples: Iterable[LabeledIntervention] = LABELED_INTERVENTIONS
                    ) -> dict[EpisodeKind, dict[EpisodeKind, int]]:
    if examples is None:
        examples = []
    matrix: dict[EpisodeKind, dict[EpisodeKind, int]] = defaultdict(lambda: defaultdict(int))
    for example in examples:
        matrix[example.expected][predict(example)] += 1
    return {expected: dict(predictions) for expected, predictions in matrix.items()}


def classification_report(examples: Iterable[LabeledIntervention] = LABELED_INTERVENTIONS) -> dict:
    if examples is None:
        examples = []
    examples = list(examples)
    predictions = [predict(example) for example in examples]
    expected = [example.expected for example in examples]
    labels = sorted(set(expected) | set(predictions), key=lambda kind: kind.value)
    correct = sum(1 for left, right in zip(expected, predictions) if left == right)
    per_class = {}
    for label in labels:
        true_positive = sum(1 for e, p in zip(expected, predictions) if e == label and p == label)
        false_positive = sum(1 for e, p in zip(expected, predictions) if e != label and p == label)
        false_negative = sum(1 for e, p in zip(expected, predictions) if e == label and p != label)
        precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
        recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[label.value] = {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'support': sum(1 for value in expected if value == label),
        }
    return {
        'accuracy': correct / len(examples) if examples else 0.0,
        'per_class': per_class,
        'confusion_matrix': confusion_matrix(examples),
    }