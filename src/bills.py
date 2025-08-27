from __future__ import annotations

from typing import Dict, List, Optional

from .config import get_settings
from .utils import get_json

API_URL = "https://api.congress.gov/v3"


def fetch_bills(from_date: Optional[str] = None, limit: int = 250) -> List[Dict]:
    """Fetch bill summaries from Congress.gov.

    Parameters
    ----------
    from_date:
        Optional ISO ``fromDateTime`` filter for incremental updates.
    limit:
        Number of records per page (max 250).
    """

    settings = get_settings()
    headers = {"X-Api-Key": settings.congress_api_key}
    params: Dict[str, Optional[str | int]] = {"format": "json", "limit": limit}
    if from_date:
        params["fromDateTime"] = from_date
    url = f"{API_URL}/bill"
    items: List[Dict] = []
    while url:
        data = get_json(url, params=params, headers=headers)
        items.extend(data.get("bills", {}).get("bill", []))
        url = data.get("pagination", {}).get("next")
        params = None  # next URLs already contain query parameters
    return items
