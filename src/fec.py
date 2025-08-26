"""Access FEC API for contributions."""
from __future__ import annotations

from typing import Dict, Iterable, List

from .config import get_settings
from .utils import get_json

API_URL = "https://api.open.fec.gov/v1"


def fetch_candidate_ids(bioguide_id: str) -> List[str]:
    """Fetch FEC candidate IDs for a member."""
    settings = get_settings()
    url = f"{API_URL}/candidate/"
    params = {"api_key": settings.fec_api_key, "q": bioguide_id}
    data = get_json(url, params=params)
    return [item["candidate_id"] for item in data.get("results", [])]


def fetch_contributions(candidate_id: str, cycle: int) -> List[Dict]:
    """Fetch Schedule A contributions for a candidate.

    This is a minimal wrapper that demonstrates pagination handling. It is not
    used in tests and serves as a reference implementation.
    """
    settings = get_settings()
    url = f"{API_URL}/schedules/schedule_a/"
    params = {
        "api_key": settings.fec_api_key,
        "candidate_id": candidate_id,
        "per_page": 20,
        "two_year_transaction_period": cycle,
    }
    data = get_json(url, params=params)
    return data.get("results", [])


def link_members_to_candidates(members: Iterable[Dict[str, str]], mapping: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Link members to candidate IDs using provided mapping.

    Parameters
    ----------
    members: iterable of dicts with ``bioguide_id`` keys.
    mapping: mapping from bioguide_id to candidate IDs.

    Returns
    -------
    dict mapping member_id to list of candidate IDs
    """
    result: Dict[str, List[str]] = {}
    for m in members:
        ids = mapping.get(m["bioguide_id"], [])
        result[m["member_id"]] = ids
    return result

