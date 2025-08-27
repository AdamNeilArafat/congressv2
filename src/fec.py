"""Access FEC API for contributions and campaign finance data."""
from __future__ import annotations

import csv
import io
import tempfile
import urllib.request
import zipfile
from pathlib import Path
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


def _fetch_all_pages(url: str, params: Dict) -> List[Dict]:
    """Fetch all pages for a given endpoint."""
    results: List[Dict] = []
    page = 1
    while True:
        params["page"] = page
        data = get_json(url, params=params)
        results.extend(data.get("results", []))
        pagination = data.get("pagination", {})
        pages = pagination.get("pages", page)
        if page >= pages:
            break
        page += 1
    return results


def _download_bulk_candidate_totals(cycle: int, candidate_id: str) -> List[Dict]:
    """Download candidate totals in bulk CSV format."""
    base = f"https://www.fec.gov/files/bulk-downloads/{cycle}"
    url = f"{base}/ccl.csv.zip"
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / "ccl.zip"
        urllib.request.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path) as zf:
            name = zf.namelist()[0]
            with zf.open(name) as fh:
                reader = csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1"))
                cid = candidate_id.upper()
                return [row for row in reader if row.get("CAND_ID") == cid]


def fetch_candidate_totals(candidate_id: str, cycle: int, bulk: bool = False) -> List[Dict]:
    """Fetch candidate totals for a given cycle.

    Parameters
    ----------
    candidate_id: str
        FEC candidate identifier.
    cycle: int
        Two-year election cycle.
    bulk: bool, optional
        If ``True``, download bulk CSV data instead of calling the API.
    """
    if bulk:
        return _download_bulk_candidate_totals(cycle, candidate_id)

    settings = get_settings()
    if settings.fec_data_dir:
        path = Path(settings.fec_data_dir) / "candidate_totals.csv"
        if path.exists():
            with path.open() as fh:
                reader = csv.DictReader(fh)
                return [
                    r
                    for r in reader
                    if r.get("candidate_id") == candidate_id
                    and str(r.get("cycle")) == str(cycle)
                ]

    url = f"{API_URL}/candidate/totals/"
    params = {
        "api_key": settings.fec_api_key,
        "candidate_id": candidate_id,
        "cycle": cycle,
        "per_page": 100,
    }
    return _fetch_all_pages(url, params)


def _download_bulk_schedule_e(cycle: int, candidate_id: str) -> List[Dict]:
    """Download Schedule E independent expenditures in bulk CSV format."""
    base = f"https://www.fec.gov/files/bulk-downloads/{cycle}"
    url = f"{base}/independent-expenditure-{cycle}.zip"
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / "ie.zip"
        urllib.request.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path) as zf:
            name = zf.namelist()[0]
            with zf.open(name) as fh:
                reader = csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1"))
                return [row for row in reader if row.get("cand_id") == candidate_id]


def fetch_independent_expenditures(
    candidate_id: str, cycle: int, bulk: bool = False
) -> List[Dict]:
    """Fetch Schedule E independent expenditures for a candidate.

    Parameters
    ----------
    candidate_id: str
        FEC candidate identifier.
    cycle: int
        Two-year election cycle.
    bulk: bool, optional
        If ``True``, download bulk CSV data instead of calling the API.
    """
    if bulk:
        return _download_bulk_schedule_e(cycle, candidate_id)

    settings = get_settings()
    url = f"{API_URL}/schedules/schedule_e/"
    params = {
        "api_key": settings.fec_api_key,
        "candidate_id": candidate_id,
        "two_year_transaction_period": cycle,
        "per_page": 100,
    }
    return _fetch_all_pages(url, params)


