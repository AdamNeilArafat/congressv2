from __future__ import annotations

from typing import Dict, List, Optional

from .config import get_settings
from .utils import get_json

API_URL = "https://api.congress.gov/v3"


def fetch_records(from_date: Optional[str] = None, limit: int = 250) -> List[Dict]:
    """Fetch Congressional Record entries from Congress.gov."""
    settings = get_settings()
    headers = {"X-Api-Key": settings.congress_api_key}
    params: Dict[str, Optional[str | int]] = {"format": "json", "limit": limit}
    if from_date:
        params["fromDateTime"] = from_date
    url = f"{API_URL}/congressional-record"
    items: List[Dict] = []
    while url:
        data = get_json(url, params=params, headers=headers)
        items.extend(data.get("congressionalRecord", {}).get("record", []))
        url = data.get("pagination", {}).get("next")
        params = None
    return items
