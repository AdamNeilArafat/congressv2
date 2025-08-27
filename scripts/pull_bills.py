#!/usr/bin/env python3
"""Fetch legislation metadata from Congress.gov.

This script requests bill summaries from the Congress.gov API using
pagination and stores a compact JSON file under ``data/``.  It reads the
API key from ``.env`` via the ``congress_api_key`` setting defined in
:mod:`src.config`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, Generator

import requests

# Ensure ``src`` can be imported when running as a script
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import get_settings  # noqa: E402  (import after path setup)

BASE = "https://api.congress.gov/v3/bill"


def fetch_all(limit: int = 50) -> Generator[Dict, None, None]:
    """Yield bill records from Congress.gov.

    Parameters
    ----------
    limit:
        Number of bills to request per API call (max 250).
    """

    settings = get_settings()
    url = f"{BASE}?format=json&limit={limit}&api_key={settings.congress_api_key}"
    while url:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        for b in data.get("bills", []):
            yield {
                "congress": b.get("congress"),
                "number": b.get("number"),
                "title": b.get("title"),
                "action": (b.get("latestAction") or {}).get("text"),
                "date": (b.get("latestAction") or {}).get("actionDate"),
            }
        url = data.get("pagination", {}).get("next")
        if url:
            url += f"&api_key={settings.congress_api_key}"


def main() -> None:
    bills = list(fetch_all(limit=20))  # small sample for exploration
    out_dir = ROOT / "data"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "bills.json"
    with out_path.open("w") as fh:
        json.dump(bills, fh, indent=2)
    print(f"Saved {len(bills)} bills to {out_path}")


if __name__ == "__main__":
    main()
