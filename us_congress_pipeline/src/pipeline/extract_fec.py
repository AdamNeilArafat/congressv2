from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Iterable

import pandas as pd

from . import paths


FEC_FILES = {
    "candidates": "fec_candidates_{cycle}.csv",
    "committees": "fec_committees_{cycle}.csv",
    "candidate_totals": "fec_candidate_totals_{cycle}.csv",
    "committee_totals": "fec_committee_totals_{cycle}.csv",
    "indiv_contrib": "fec_indiv_contrib_{cycle}.csv",
    "disbursements": "fec_disbursements_{cycle}.csv",
}


def _unzip_to_csv(zip_path: Path, out_csv: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        name = z.namelist()[0]
        with z.open(name) as f:
            df = pd.read_csv(f, dtype=str)
        df.to_csv(out_csv, index=False)


def extract(cycles: Iterable[int]) -> None:
    for cycle in cycles:
        cycle_dir = paths.RAW_DIR / "fec" / str(cycle)
        for key, out_template in FEC_FILES.items():
            zip_path = cycle_dir / f"{key}.zip"
            if not zip_path.exists():
                continue
            out_csv = paths.INTERIM_DIR / out_template.format(cycle=cycle)
            _unzip_to_csv(zip_path, out_csv)
