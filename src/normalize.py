"""Normalization helpers for raw API data."""
from __future__ import annotations

from datetime import date
from typing import Dict, Iterable, List

from .models import Contribution


def normalize_contributions(records: Iterable[Dict]) -> List[Contribution]:
    """Convert raw contribution dicts to :class:`Contribution` objects."""
    normalized: List[Contribution] = []
    for r in records:
        normalized.append(
            Contribution(
                committee_id=r.get("committee_id"),
                recipient_fec_id=r.get("recipient_id"),
                contributor_name=r.get("name"),
                contributor_employer=r.get("employer"),
                contributor_occupation=r.get("occupation"),
                contributor_type=r.get("type"),
                industry=r.get("industry"),
                amount=float(r.get("amount", 0)),
                date=date.fromisoformat(r.get("date")),
                cycle=int(r.get("cycle", 0)),
            )
        )
    return normalized

