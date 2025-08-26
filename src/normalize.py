"""Normalization helpers for raw API data."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Iterable, List

from .models import Contribution


def normalize_contributions(records: Iterable[Dict]) -> List[Contribution]:
    """Convert raw contribution dicts to :class:`Contribution` objects."""
    normalized: List[Contribution] = []
    for r in records:
        date_str = r.get("date")
        parsed_date = (
            datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else None
        )
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
                date=parsed_date,
                cycle=int(r.get("cycle", 0)),
            )
        )
    return normalized

