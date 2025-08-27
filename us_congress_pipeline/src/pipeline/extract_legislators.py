from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import yaml

from . import paths


def _load_people(repo: Path) -> List[Dict[str, Any]]:
    files = ["legislators-current.yaml", "legislators-historical.yaml"]
    people: List[Dict[str, Any]] = []
    for fname in files:
        fpath = repo / fname
        if fpath.exists():
            with open(fpath) as f:
                people.extend(yaml.safe_load(f))
    return people


def extract(repo: Path | None = None) -> None:
    repo = repo or (paths.RAW_DIR / "congress-legislators")
    people = _load_people(repo)
    rows = []
    xwalk = []
    for p in people:
        bioguide = p.get("id", {}).get("bioguide")
        name = p.get("name", {})
        first = name.get("first")
        last = name.get("last")
        party = None
        terms = p.get("terms", [])
        if terms:
            party = terms[-1].get("party")
        rows.append({
            "bioguide_id": bioguide,
            "first_name": first,
            "last_name": last,
            "party": party,
        })
        ids = p.get("id", {})
        fec_ids = ids.get("fec", [])
        xwalk.append({
            "bioguide_id": bioguide,
            "govtrack_id": ids.get("govtrack"),
            "icpsr_id": ids.get("icpsr"),
            "fec_candidate_ids": ";".join(fec_ids) if isinstance(fec_ids, list) else fec_ids,
        })
    pd.DataFrame(rows).to_csv(paths.INTERIM_DIR / "legislators.csv", index=False)
    pd.DataFrame(xwalk).to_csv(paths.INTERIM_DIR / "xwalk_ids.csv", index=False)
