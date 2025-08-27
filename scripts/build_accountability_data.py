import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
outputs_dir = ROOT / "outputs"
data_dir = ROOT / "data"
acct_dir = ROOT / "accountability" / "data"

def build_donor_records():
    """Create donor records per member from summary CSV."""
    donors = {}
    align = {}
    summary_csv = outputs_dir / "member_summary.csv"
    if not summary_csv.exists():
        raise FileNotFoundError(summary_csv)
    with summary_csv.open() as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            mid = row["member_id"]
            total_pac = float(row.get("total_pac", 0) or 0)
            total_indiv = float(row.get("total_indiv", 0) or 0)
            total = total_pac + total_indiv
            pac_pct = (total_pac / total) if total else 0.0
            donors[mid] = {
                "pac_pct": pac_pct,
                "in_state_dollars": 0,
                "out_state_dollars": total,
                "industries": {"Unknown": total_pac},
            }
            align[mid] = {"donor_alignment_index": float(row.get("alignment_index", 0) or 0)}
    return donors, align

def build_awards_records():
    """Create award records per member from badge CSV."""
    awards = {}
    badges_csv = outputs_dir / "member_badges.csv"
    if not badges_csv.exists():
        return awards
    with badges_csv.open() as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            mid = row["member_id"]
            awards.setdefault(mid, {"badges": []})["badges"].append(
                {"key": row["badge_code"], "label": row["label"]}
            )
    return awards

def main() -> None:
    donors, align = build_donor_records()
    awards = build_awards_records()

    data_dir.mkdir(exist_ok=True)
    with (data_dir / "donors-by-member.json").open("w") as fh:
        json.dump(donors, fh, indent=2, sort_keys=True)
    with (data_dir / "vote-alignments.json").open("w") as fh:
        json.dump(align, fh, indent=2, sort_keys=True)
    with (data_dir / "member-awards.json").open("w") as fh:
        json.dump(awards, fh, indent=2, sort_keys=True)

    acct_dir.mkdir(parents=True, exist_ok=True)
    for name in [
        "donors-by-member.json",
        "vote-alignments.json",
        "member-awards.json",
        "members.json",
    ]:
        shutil.copy(data_dir / name, acct_dir / name)

if __name__ == "__main__":
    main()
