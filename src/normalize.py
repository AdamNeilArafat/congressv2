"""Normalization helpers for raw API data."""
from __future__ import annotations

 codex/create-reproducible-pipeline-for-fec-data-analysis-erh252
from datetime import datetime
from typing import Dict, Iterable, List


 codex/create-reproducible-pipeline-for-fec-data-analysis-bn84jr
from datetime import datetime
from typing import Dict, Iterable, List

from datetime import date
from typing import Dict, Iterable, List
from datetime import datetime
 main

 main
from .models import Contribution


def normalize_contributions(records: Iterable[Dict]) -> List[Contribution]:
    """Convert raw contribution dicts to :class:`Contribution` objects."""
    normalized: List[Contribution] = []
    for r in records:
 codex/create-reproducible-pipeline-for-fec-data-analysis-erh252

 codex/create-reproducible-pipeline-for-fec-data-analysis-bn84jr
 main
        date_str = r.get("date")
        parsed_date = (
            datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else None
        )
 codex/create-reproducible-pipeline-for-fec-data-analysis-erh252


        date_val = r.get("date")
        if isinstance(date_val, str):
            date_val = datetime.strptime(date_val, "%Y-%m-%d").date()

 main
 main
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
 codex/create-reproducible-pipeline-for-fec-data-analysis-erh252
                date=parsed_date,

 codex/create-reproducible-pipeline-for-fec-data-analysis-bn84jr
                date=parsed_date,


 main
 main
                cycle=int(r.get("cycle", 0)),
            )
        )
    return normalized

