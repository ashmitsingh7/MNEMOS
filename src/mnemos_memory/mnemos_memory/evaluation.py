"""Offline retrieval evaluation helpers for MNEMOS episodic memory."""
from dataclasses import dataclass, field
from typing import Iterable

from .model import Episode
from .retrieval import retrieve


@dataclass(frozen=True)
class RetrievalCase:
    """A labeled retrieval query for calibration or held-out evaluation."""
    episodes: list[Episode]
    current: Episode
    relevant: set[str] = field(default_factory=set)
    minimum_similarity: float = 0.55
    limit: int = 5


def evaluate_retrieval(cases: Iterable[RetrievalCase]) -> dict:
    if cases is None:
        cases = []
    cases = list(cases)
    precisions = []
    recalls = []
    reciprocal_ranks = []
    retrieved_counts = []
    for case in cases:
        matches = retrieve(case.episodes, case.current, case.minimum_similarity, case.limit)
        retrieved_ids = [episode.identifier for episode, _ in matches]
        relevant_retrieved = [episode_id for episode_id in retrieved_ids if episode_id in case.relevant]
        precision = len(relevant_retrieved) / len(retrieved_ids) if retrieved_ids else 0.0
        recall = (len(relevant_retrieved) / len(case.relevant)) if case.relevant else 0.0
        reciprocal_rank = 0.0
        for rank, episode_id in enumerate(retrieved_ids, start=1):
            if episode_id in case.relevant:
                reciprocal_rank = 1.0 / rank
                break
        precisions.append(precision)
        recalls.append(recall)
        reciprocal_ranks.append(reciprocal_rank)
        retrieved_counts.append(len(retrieved_ids))
    total = len(cases)
    return {
        'queries': total,
        'mean_precision': sum(precisions) / total if total else 0.0,
        'mean_recall': sum(recalls) / total if total else 0.0,
        'mean_reciprocal_rank': sum(reciprocal_ranks) / total if total else 0.0,
        'mean_retrieved': sum(retrieved_counts) / total if total else 0.0,
    }