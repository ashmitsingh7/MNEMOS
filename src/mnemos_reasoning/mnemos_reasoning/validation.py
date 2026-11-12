"""Reject stale evidence before it can affect a planning-cost integration."""
from math import exp
from time import time

from mnemos_memory.model import Episode, ValidationResult, ValidationStatus
from mnemos_memory.retrieval import signature_similarity


def validate(episode: Episode, current: Episode, *, now: float | None = None,
             maximum_age_seconds: float = 60 * 60 * 24 * 21,
             contradiction_threshold: float = 0.25) -> ValidationResult:
    """Return explicit validation factors, preferring abstention over reuse."""
    if not current.scan_signature:
        return ValidationResult(ValidationStatus.INSUFFICIENT_CONTEXT, 0.0, 0.0, 0.0, 0.0,
                                ('No current scan signature; memory influence disabled.',))
    geometry = signature_similarity(episode.scan_signature, current.scan_signature)
    old_tags, new_tags = set(episode.semantic_tags), set(current.semantic_tags)
    semantic = 1.0 if not old_tags and not new_tags else len(old_tags & new_tags) / len(old_tags | new_tags)
    age_seconds = max(0.0, (time() if now is None else now) - episode.created_at)
    age = exp(-age_seconds / maximum_age_seconds)
    score = 0.60 * geometry + 0.20 * semantic + 0.20 * age
    reasons = [f'geometry={geometry:.2f}', f'semantics={semantic:.2f}', f'age={age:.2f}']
    if geometry < contradiction_threshold:
        return ValidationResult(ValidationStatus.CONTRADICTED, score, geometry, semantic, age,
                                tuple(reasons + ['Current geometry contradicts the stored episode.']))
    if score >= 0.72:
        return ValidationResult(ValidationStatus.VALID, score, geometry, semantic, age, tuple(reasons))
    if score >= 0.48:
        return ValidationResult(ValidationStatus.TENTATIVE, score, geometry, semantic, age,
                                tuple(reasons + ['Only a bounded, low-confidence influence is permitted.']))
    return ValidationResult(ValidationStatus.OUTDATED, score, geometry, semantic, age,
                            tuple(reasons + ['Evidence is stale or insufficiently similar.']))
