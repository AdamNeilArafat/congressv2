"""Utility helpers for API access and caching."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


def cache_key(url: str, params: Optional[Dict[str, Any]] = None) -> Path:
    """Return path for cached response."""
    params = params or {}
    key = hashlib.sha256((url + json.dumps(params, sort_keys=True)).encode()).hexdigest()
    return RAW_DIR / f"{key}.json"


def get_json(url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Any:
    """GET a URL with basic retry and caching."""
    params = params or {}
    path = cache_key(url, params)
    if path.exists():
        with path.open() as fh:
            return json.load(fh)

    for attempt in range(3):
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            with path.open("w") as fh:
                json.dump(data, fh)
            return data
        time.sleep(2 ** attempt)
    raise RuntimeError(f"Request failed: {url}")

