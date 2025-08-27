from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import yaml

from .config import get_settings
from .utils import get_json

API_URL = "https://api.congress.gov/v3"


def _load_from_repo(path: Path) -> List[Dict]:
    """Load member data from a local clone of unitedstates/congress."""
    data = yaml.safe_load(path.read_text())
    items: List[Dict] = []
    for entry in data:
        ids = entry.get("id", {})
        name = entry.get("name", {})
        terms = entry.get("terms", [])
        term = terms[-1] if terms else {}
        chamber = term.get("type", "")
        chamber = "Senate" if chamber == "sen" else "House" if chamber == "rep" else chamber
        items.append(
            {
                "bioguideId": ids.get("bioguide"),
                "firstName": name.get("first"),
                "lastName": name.get("last"),
                "chamber": chamber,
                "party": term.get("party"),
                "state": term.get("state"),
            }
        )
    return items


def fetch_members(from_date: Optional[str] = None, limit: int = 250) -> List[Dict]:
    """Fetch member metadata from a local repo or Congress.gov."""
    settings = get_settings()
    if settings.congress_data_dir:
        path = Path(settings.congress_data_dir) / "data" / "legislators-current.yaml"
        if path.exists():
            return _load_from_repo(path)
    else:
        local = Path("data") / "legislators-current.yaml"
        if local.exists():
            return _load_from_repo(local)

    headers = {"X-Api-Key": settings.congress_api_key}
    params: Dict[str, Optional[str | int]] = {"format": "json", "limit": limit}
    if from_date:
        params["fromDateTime"] = from_date
    url = f"{API_URL}/member"
    items: List[Dict] = []
    while url:
        data = get_json(url, params=params, headers=headers)
        items.extend(data.get("members", {}).get("member", []))
        url = data.get("pagination", {}).get("next")
        params = None
    return items
