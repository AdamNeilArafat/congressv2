"""Command line interface for the campaign pipeline."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional

import typer

from . import (
    analyze,
    bills,
    committees,
    fec,
    load,
    members,
    normalize,
    records,
    votes,
    voter_history,
)
from .models import Bill, Committee, CongressionalRecord, Member, MemberVote

app = typer.Typer()
ingest_app = typer.Typer()
app.add_typer(ingest_app, name="ingest")


@ingest_app.command("members")
def ingest_members(from_date: Optional[str] = typer.Option(None, "--from")) -> None:
    """Fetch members from Congress.gov and store them."""
    load.init_db()
    records = members.fetch_members(from_date=from_date)
    objs = [
        Member(
            member_id=r.get("bioguideId") or r.get("memberId"),
            bioguide_id=r.get("bioguideId"),
            first=r.get("firstName", ""),
            last=r.get("lastName", ""),
            chamber=r.get("chamber", ""),
            party=r.get("party", ""),
            state=r.get("state", ""),
        )
        for r in records
        if r.get("bioguideId") or r.get("memberId")
    ]
    load.load_objects(objs)


@ingest_app.command("bills")
def ingest_bills(from_date: Optional[str] = typer.Option(None, "--from")) -> None:
    """Fetch bills from Congress.gov and store them."""
    load.init_db()
    records = bills.fetch_bills(from_date=from_date)
    objs = [
        Bill(
            bill_id=r.get("billId")
            or f"{r.get('type', '')}{r.get('number', '')}-{r.get('congress', '')}",
            congress=int(r.get("congress", 0)),
            chamber=r.get("type", ""),
            number=str(r.get("number", "")),
            title=r.get("title", ""),
        )
        for r in records
    ]
    load.load_objects(objs)


@ingest_app.command("committees")
def ingest_committees(from_date: Optional[str] = typer.Option(None, "--from")) -> None:
    """Fetch committees from Congress.gov and store them."""
    load.init_db()
    records = committees.fetch_committees(from_date=from_date)
    objs = [
        Committee(
            committee_id=r.get("committeeId") or r.get("code"),
            name=r.get("name", ""),
            type=r.get("type"),
        )
        for r in records
        if r.get("committeeId") or r.get("code")
    ]
    load.load_objects(objs)


@ingest_app.command("records")
def ingest_records(from_date: Optional[str] = typer.Option(None, "--from")) -> None:
    """Fetch Congressional Record entries and store them."""
    load.init_db()
    records_data = records.fetch_records(from_date=from_date)
    objs = [
        CongressionalRecord(
            record_id=r.get("recordId"),
            title=r.get("title", ""),
            date=r.get("date"),
            chamber=r.get("chamber"),
        )
        for r in records_data
        if r.get("recordId")
    ]
    load.load_objects(objs)


@ingest_app.command("fec")
def ingest_fec(cycles: str = typer.Option(..., "--cycles")) -> None:
    """Normalize and store a sample FEC contribution record."""
    members = [{"member_id": "A000360", "bioguide_id": "A000360"}]
    mapping = {"A000360": ["H0XX00001"]}
    fec.link_members_to_candidates(members, mapping)
    raw = [
        {
            "committee_id": "C1",
            "recipient_id": "H0XX00001",
            "name": "John Doe",
            "employer": "Corp",
            "occupation": "CEO",
            "type": "PAC",
            "industry": "Finance",
            "amount": 1000,
            "date": "2024-01-01",
            "cycle": int(cycles),
        }
    ]
    contribs = normalize.normalize_contributions(raw)
    load.load_objects(contribs)


@ingest_app.command("votes")
def ingest_votes(from_date: str = typer.Option(..., "--from")) -> None:
    """Parse and store a minimal vote record."""
    vote = {
        "vote_id": "1",
        "question": "On Passage",
        "result": "Passed",
        "date": from_date,
        "chamber": "House",
        "positions": [
            {"member_id": "A000360", "vote_position": "Yes"},
            {"member_id": "B000123", "vote_position": "No"},
        ],
    }
    positions = votes.parse_member_positions(vote)
    member_votes = [
        MemberVote(vote_id=vote["vote_id"], member_id=mid, position=pos)
        for mid, pos in positions.items()
    ]
    load.load_objects(member_votes)


@ingest_app.command("voter-history")
def ingest_voter_history(path: str = typer.Option("data/voter_history_sample.csv", "--path")) -> None:
    """Parse and store voter history records from a CSV file."""
    load.init_db()
    records = voter_history.parse_voter_history(path)
    load.load_objects(records)


@app.command("normalize")
def normalize_all(kind: str = typer.Argument("all")) -> None:  # pragma: no cover
    """Normalize a sample contribution record and store it."""
    raw = [
        {
            "committee_id": "C1",
            "recipient_id": "H0XX00001",
            "name": "John Doe",
            "employer": "Corp",
            "occupation": "CEO",
            "type": "PAC",
            "industry": "Finance",
            "amount": 1000,
            "date": "2024-01-01",
            "cycle": 2024,
        }
    ]
    contribs = normalize.normalize_contributions(raw)
    load.load_objects(contribs)


@app.command("analyze")
def analyze_alignment(window: str = "24m") -> None:  # pragma: no cover
    """Run a simple alignment analysis and store the event."""
    records = [
        {
            "member_id": "A000360",
            "vote_id": "1",
            "net_industry": 5000.0,
            "matches_interest": True,
        }
    ]
    events = analyze.analyze_events(records)
    load.load_objects(events)


@app.command("export")
def export_csv(out: str = "outputs/") -> None:  # pragma: no cover
    """Export alignment events to a CSV file."""
    Path(out).mkdir(parents=True, exist_ok=True)
    records = [
        {
            "member_id": "A000360",
            "vote_id": "1",
            "net_industry": 5000.0,
            "matches_interest": True,
        }
    ]
    events = analyze.analyze_events(records)
    path = Path(out) / "alignment.csv"
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["member_id", "vote_id", "alignment_score"])
        for ev in events:
            writer.writerow([ev.member_id, ev.vote_id, ev.alignment_score])


@app.command("report")
def report_member(id: str = typer.Option(..., "--id")) -> None:  # pragma: no cover
    """Emit a tiny alignment report for a member."""
    records = [
        {
            "member_id": id,
            "vote_id": "1",
            "net_industry": 5000.0,
            "matches_interest": True,
        }
    ]
    events = analyze.analyze_events(records)
    for ev in events:
        typer.echo(
            f"member {ev.member_id} aligned on vote {ev.vote_id} score={ev.alignment_score:.2f}"
        )


if __name__ == "__main__":  # pragma: no cover
    app()
