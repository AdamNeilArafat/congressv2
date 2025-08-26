"""Fetch and parse roll call votes."""
from __future__ import annotations

from typing import Dict, List

from .config import get_settings
from .utils import get_json

API_URL = "https://api.propublica.org/congress/v1"


def fetch_votes(from_date: str) -> List[Dict]:
    """Fetch votes from the ProPublica Congress API since ``from_date``.
    This is a thin wrapper that exercises the request helper.
    """
    settings = get_settings()
    url = f"{API_URL}/votes/{from_date}.json"
    headers = {"X-API-Key": settings.pp_congress_api_key}
    data = get_json(url, headers=headers)
    return data.get("results", [])


def parse_member_positions(vote: Dict) -> Dict[str, str]:
    """Return mapping of member ID to their position on a vote."""
    positions = {}
    for record in vote.get("positions", []):
        positions[record["member_id"]] = record["vote_position"]
    return positions

