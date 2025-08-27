from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Iterable

import requests
try:  # pragma: no cover - optional dependency
    from tqdm import tqdm
except Exception:  # pragma: no cover
    class tqdm:  # type: ignore
        def __init__(self, iterable=None, total=None, unit=None, unit_scale=None, desc=None):
            self.iterable = iterable
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
        def update(self, n):
            pass

from . import paths

GIT_LEGISLATORS = "https://github.com/unitedstates/congress-legislators.git"
GIT_CONGRESS = "https://github.com/unitedstates/congress.git"


def _clone(url: str, dest: Path) -> None:
    if dest.exists():
        return
    subprocess.run(["git", "clone", "--depth", "1", url, str(dest)], check=True)


def clone_legislators() -> Path:
    dest = paths.RAW_DIR / "congress-legislators"
    _clone(GIT_LEGISLATORS, dest)
    return dest


def clone_congress_tools() -> Path:
    dest = paths.RAW_DIR / "congress"
    _clone(GIT_CONGRESS, dest)
    return dest


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        with open(dest, "wb") as f, tqdm(total=total, unit="B", unit_scale=True, desc=dest.name) as pbar:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))


def fetch_govinfo_rollcalls(congresses: Iterable[int]) -> None:
    base = "https://www.govinfo.gov/bulkdata/rollcallvote"
    for congress in congresses:
        for chamber in ("house", "senate"):
            url = f"{base}/{congress}/{chamber}/rollcallvotes.zip"
            dest = paths.RAW_DIR / "rollcalls" / str(congress) / f"{chamber}_rollcallvotes.zip"
            _download(url, dest)


def fetch_fec_bulk(cycles: Iterable[int]) -> None:
    base = "https://www.fec.gov/files/bulk-downloads"
    files = {
        "candidates": "cn.csv.zip",
        "committees": "cm.csv.zip",
        "candidate_totals": "ccl.csv.zip",
        "committee_totals": "webk.csv.zip",
        "indiv_contrib": "itcont.zip",
        "disbursements": "oppexp.zip",
    }
    for cycle in cycles:
        for key, fname in files.items():
            url = f"{base}/{cycle}/{fname}"
            dest = paths.RAW_DIR / "fec" / str(cycle) / f"{key}.zip"
            _download(url, dest)
