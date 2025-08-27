"""Fetch and parse roll call votes."""
from __future__ import annotations

from typing import Dict, List

from .config import get_settings
from .utils import get_json

API_URL = "https://api.congress.gov/v3"


def fetch_votes(congress: int, session: int, from_date: str) -> List[Dict]:
    """Fetch House roll call votes from Congress.gov.

    The Congress.gov API exposes a beta endpoint for House roll call votes at
    ``/house-vote/{congress}/{session}``.  To mirror the previous behaviour of
    fetching recent votes we allow the caller to supply the congress, session
    number, and a ``from_date`` filter.

    Parameters
    ----------
    congress:
        Congress number for the query, e.g. ``118``.
    session:
        Session number within the congress, ``1`` or ``2``.
    from_date:
        ISO formatted timestamp used to filter results.
    """

    settings = get_settings()
    url = (
        f"{API_URL}/house-vote/{congress}/{session}"
        f"?fromDateTime={from_date}&format=json&limit=250"
    )
    headers = {"X-Api-Key": settings.congress_api_key}
    data = get_json(url, headers=headers)
    # List level responses nest the votes under ``houseRollCallVotes`` ->
    # ``houseRollCallVote``.
    return (
        data.get("houseRollCallVotes", {})
        .get("houseRollCallVote", [])
    )


def fetch_roll_call_vote(congress: int, session: int, roll_call: int) -> Dict:
    """Retrieve a single House roll call vote including member positions.

    Parameters
    ----------
    congress: Congress number for the vote.
    session: Session number within the congress.
    roll_call: Roll call number within the session.
    """

    settings = get_settings()
    url = f"{API_URL}/house-vote/{congress}/{session}/{roll_call}?format=json"
    headers = {"X-Api-Key": settings.congress_api_key}
    data = get_json(url, headers=headers)
    # Member vote details are returned under the ``houseRollCallVoteMemberVotes``
    # key; fall back to ``houseRollCallVote`` if the structure changes.
    return (
        data.get("houseRollCallVoteMemberVotes")
        or data.get("houseRollCallVote")
        or data
    )


def parse_member_positions(vote: Dict) -> Dict[str, str]:
    """Return mapping of member ID to their position on a vote.

    The function supports legacy ``positions`` style records as well as the
    structure returned by the new Congress.gov API which stores member votes in
    a ``results`` container of ``item`` entries with ``bioguideId`` and
    ``voteCast`` keys.
    """

    positions: Dict[str, str] = {}

    # Old style structure used in tests and legacy data.
    for record in vote.get("positions", []):
        positions[record["member_id"]] = record["vote_position"]

    # New API structure.
    results = vote.get("results")
    if isinstance(results, dict):
        items = results.get("item", [])
        # Normalise votes to "Yes"/"No" for downstream consumers.
        normalise = {"Aye": "Yes", "Yea": "Yes", "Nay": "No", "No": "No"}
        for item in items:
            member = item.get("bioguideId")
            cast = item.get("voteCast")
            if member and cast:
                positions[member] = normalise.get(cast, cast)

    return positions

