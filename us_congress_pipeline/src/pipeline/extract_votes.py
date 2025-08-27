from __future__ import annotations

import json
from pathlib import Path
from typing import List

import pandas as pd
from lxml import etree

from . import paths


class VoteParser:
    """Parse GovInfo roll-call vote XML or JSON."""

    def parse_file(self, fpath: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
        if fpath.suffix == ".json":
            with open(fpath) as f:
                data = json.load(f)
            return self._from_json(data)
        else:
            tree = etree.parse(str(fpath))
            return self._from_xml(tree)

    def _from_json(self, data: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
        vote_id = data["vote_id"]
        vote_row = {
            "vote_id": vote_id,
            "chamber": data.get("chamber"),
            "congress": data.get("congress"),
            "session": data.get("session"),
            "rollnumber": data.get("rollnumber"),
            "date": data.get("date"),
            "question": data.get("question"),
            "result": data.get("result"),
            "bill_id": data.get("bill")
        }
        records = [
            {"vote_id": vote_id, "bioguide_id": r["id"], "position": r["vote"]}
            for r in data.get("records", [])
        ]
        return pd.DataFrame([vote_row]), pd.DataFrame(records)

    def _from_xml(self, tree: etree._ElementTree) -> tuple[pd.DataFrame, pd.DataFrame]:
        root = tree.getroot()
        vote_id = root.findtext("vote_id") or "unknown"
        vote_row = {
            "vote_id": vote_id,
            "chamber": root.findtext("chamber"),
            "congress": root.findtext("congress"),
            "session": root.findtext("session"),
            "rollnumber": root.findtext("rollnumber"),
            "date": root.findtext("date"),
            "question": root.findtext("question"),
            "result": root.findtext("result"),
            "bill_id": root.findtext("bill"),
        }
        records = []
        for rec in root.findall("records/record"):
            records.append({
                "vote_id": vote_id,
                "bioguide_id": rec.findtext("id"),
                "position": rec.findtext("vote"),
            })
        return pd.DataFrame([vote_row]), pd.DataFrame(records)


def extract(rollcall_dir: Path | None = None) -> None:
    rollcall_dir = rollcall_dir or (paths.RAW_DIR / "rollcalls")
    parser = VoteParser()
    votes: List[pd.DataFrame] = []
    records: List[pd.DataFrame] = []
    for fpath in rollcall_dir.rglob("*.xml"):
        v, r = parser.parse_file(fpath)
        votes.append(v)
        records.append(r)
    for fpath in rollcall_dir.rglob("*.json"):
        v, r = parser.parse_file(fpath)
        votes.append(v)
        records.append(r)
    if votes:
        pd.concat(votes, ignore_index=True).to_csv(paths.INTERIM_DIR / "votes.csv", index=False)
    if records:
        pd.concat(records, ignore_index=True).to_csv(paths.INTERIM_DIR / "vote_records.csv", index=False)
