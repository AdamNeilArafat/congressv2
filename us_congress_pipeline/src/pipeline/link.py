from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd

from . import paths


def link_legislators_candidates(cycles: list[int]) -> None:
    leg = pd.read_csv(paths.INTERIM_DIR / "legislators.csv")
    xwalk = pd.read_csv(paths.INTERIM_DIR / "xwalk_ids.csv")
    links = []
    for cycle in cycles:
        fec = pd.read_csv(paths.INTERIM_DIR / f"fec_candidates_{cycle}.csv")
        for _, row in leg.iterrows():
            bioguide = row["bioguide_id"]
            fec_ids = xwalk.loc[xwalk["bioguide_id"] == bioguide, "fec_candidate_ids"].fillna("").iloc[0]
            fec_ids_list = [fid for fid in fec_ids.split(";") if fid]
            matched = fec[fec["CAND_ID"].isin(fec_ids_list)]
            if not matched.empty:
                for fid in matched["CAND_ID"]:
                    links.append({
                        "cycle": cycle,
                        "bioguide_id": bioguide,
                        "cand_id": fid,
                        "method": "yaml_direct",
                        "score": 1.0,
                    })
    pd.DataFrame(links).to_csv(paths.INTERIM_DIR / "legislator_candidate_link.csv", index=False)
