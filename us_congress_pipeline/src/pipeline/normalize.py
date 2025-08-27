from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

from . import paths
from .sql_models import Base


def load_sqlite(db_path: Path | None = None) -> None:
    db_path = db_path or (paths.WAREHOUSE_DIR / "congress.db")
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    # load CSVs if present
    csv_map = {
        "legislators.csv": "legislators",
        "votes.csv": "votes",
        "vote_records.csv": "vote_records",
        # FEC
    }
    for name, table in csv_map.items():
        fpath = paths.INTERIM_DIR / name
        if fpath.exists():
            df = pd.read_csv(fpath)
            df.to_sql(table, engine, if_exists="append", index=False)
    for fpath in paths.INTERIM_DIR.glob("fec_*_*.csv"):
        table = fpath.stem
        df = pd.read_csv(fpath)
        df.to_sql(table, engine, if_exists="append", index=False)
    link_path = paths.INTERIM_DIR / "legislator_candidate_link.csv"
    if link_path.exists():
        pd.read_csv(link_path).to_sql("link_leg_cand", engine, if_exists="append", index=False)
