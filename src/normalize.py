"""Normalization helpers for raw API data."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Iterable, List

from .models import Contribution, IndependentExpenditure


def normalize_contributions(records: Iterable[Dict]) -> List[Contribution]:
    """Convert raw contribution dicts to :class:`Contribution` objects."""
    normalized: List[Contribution] = []
    for r in records:
        date_val = r.get("date")
        if isinstance(date_val, str):
            date_val = datetime.strptime(date_val, "%Y-%m-%d").date()
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
                date=date_val,
                cycle=int(r.get("cycle", 0)),
            )
        )
    return normalized


def normalize_independent_expenditures(
    records: Iterable[Dict],
) -> List[IndependentExpenditure]:
    """Convert raw schedule E dicts to :class:`IndependentExpenditure` objects."""
    normalized: List[IndependentExpenditure] = []
    for r in records:
        date_val = r.get("date")
        if isinstance(date_val, str):
            date_val = datetime.strptime(date_val, "%Y-%m-%d").date()
        normalized.append(
            IndependentExpenditure(
                committee_id=r.get("committee_id"),
                candidate_id=r.get("candidate_id"),
                payee=r.get("payee"),
                purpose=r.get("purpose"),
                amount=float(r.get("amount", 0)),
                date=date_val,
                support_oppose=r.get("support_oppose"),
                cycle=int(r.get("cycle", 0)),
            )
        )
    return normalized
