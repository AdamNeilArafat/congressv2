"""Utilities for loading voter history records."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import List

from .models import VoterHistory


def parse_voter_history(path: str | Path) -> List[VoterHistory]:
    """Parse voter history CSV into ``VoterHistory`` objects."""
    records: List[VoterHistory] = []
    with Path(path).open() as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            record = VoterHistory(
                voter_id=row["voter_id"],
                election_date=datetime.strptime(row["election_date"], "%Y-%m-%d").date(),
                participated=row["participated"].lower() == "true",
                method=row.get("method") or None,
            )
            records.append(record)
    return records
