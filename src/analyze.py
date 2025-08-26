"""Alignment analysis between funding and votes."""
from __future__ import annotations

import math
from typing import Dict, Iterable, List

from .models import AlignmentEvent


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def compute_alignment_score(net_industry: float, matches_interest: bool) -> float:
    """Compute alignment score given net industry funding and vote alignment."""
    score = sigmoid(math.log(1 + net_industry))
    return score if matches_interest else 0.0


def analyze_events(records: Iterable[Dict]) -> List[AlignmentEvent]:
    """Create :class:`AlignmentEvent` objects from simple records.

    ``records`` should contain ``member_id``, ``vote_id``, ``net_industry`` and
    ``matches_interest`` keys.
    """
    events: List[AlignmentEvent] = []
    for r in records:
        score = compute_alignment_score(r["net_industry"], r["matches_interest"])
        events.append(
            AlignmentEvent(
                member_id=r["member_id"],
                vote_id=r["vote_id"],
                alignment_score=score,
                rationale=r.get("rationale"),
                drivers=r.get("drivers"),
            )
        )
    return events

