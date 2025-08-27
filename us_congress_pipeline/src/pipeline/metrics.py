from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from . import paths


def _finance_summary(cycle: int) -> Path:
    totals = pd.read_csv(paths.INTERIM_DIR / f"fec_candidate_totals_{cycle}.csv")
    receipts = pd.read_csv(paths.INTERIM_DIR / f"fec_indiv_contrib_{cycle}.csv")
    receipts["TRANSACTION_AMT"] = receipts["TRANSACTION_AMT"].astype(float)
    small = receipts[receipts["TRANSACTION_AMT"] <= 200].groupby("CAND_ID")["TRANSACTION_AMT"].sum()
    out = totals[["CAND_ID", "TOTAL_RECEIPTS"]].merge(
        small, left_on="CAND_ID", right_index=True, how="left"
    )
    out.rename(
        columns={
            "CAND_ID": "cand_id",
            "TOTAL_RECEIPTS": "total_receipts",
            "TRANSACTION_AMT": "small_dollar",
        },
        inplace=True,
    )
    out["small_dollar"] = out["small_dollar"].fillna(0)
    out_path = paths.OUTPUT_DIR / f"candidate_finance_summary_{cycle}.csv"
    out.to_csv(out_path, index=False)
    return out_path


def _vote_summary(congress: int) -> Path:
    votes = pd.read_csv(paths.INTERIM_DIR / "votes.csv")
    records = pd.read_csv(paths.INTERIM_DIR / "vote_records.csv")
    leg = pd.read_csv(paths.INTERIM_DIR / "legislators.csv")
    total_votes = votes.shape[0]
    records = records.merge(leg[["bioguide_id", "party"]], on="bioguide_id", how="left")
    party_majority = records.groupby(["vote_id", "party"])["position"].agg(lambda x: x.value_counts().idxmax()).reset_index()
    records = records.merge(party_majority, on=["vote_id", "party"], suffixes=("", "_party"))
    records["unity"] = records["position"] == records["position_party"]
    summary = records.groupby("bioguide_id").agg(
        participated=("vote_id", "count"),
        unity=("unity", "mean"),
    )
    summary["participation_rate"] = summary["participated"] / total_votes
    out = summary.reset_index()[["bioguide_id", "participation_rate", "unity"]]
    out_path = paths.OUTPUT_DIR / f"incumbent_vote_summary_{congress}.csv"
    out.to_csv(out_path, index=False)
    return out_path


def _alignment(cycle: int, congress: int) -> Path:
    finance = pd.read_csv(paths.OUTPUT_DIR / f"candidate_finance_summary_{cycle}.csv")
    votes = pd.read_csv(paths.OUTPUT_DIR / f"incumbent_vote_summary_{congress}.csv")
    links = pd.read_csv(paths.INTERIM_DIR / "legislator_candidate_link.csv")
    df = links.merge(finance, on="cand_id", how="left").merge(votes, on="bioguide_id", how="left")
    df["flag"] = (df["total_receipts"] > 100000) & (df["unity"] < 0.5)
    out_path = paths.OUTPUT_DIR / f"alignment_flags_{cycle}_{congress}.csv"
    df.to_csv(out_path, index=False)
    return out_path


def build_metrics(cycles: Iterable[int], congresses: Iterable[int]) -> None:
    paths.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for cycle in cycles:
        _finance_summary(cycle)
    for congress in congresses:
        _vote_summary(congress)
    for cycle in cycles:
        for congress in congresses:
            _alignment(cycle, congress)
