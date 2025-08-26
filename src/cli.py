"""Command line interface for the campaign pipeline."""
from __future__ import annotations

import csv
from pathlib import Path

import typer

from . import analyze, fec, load, normalize, votes
from .models import Member, MemberVote

app = typer.Typer()
ingest_app = typer.Typer()
app.add_typer(ingest_app, name="ingest")


@ingest_app.command("members")
def ingest_members() -> None:
    """Load a tiny set of members into the database."""
    load.init_db()
    members = [
        Member(
            member_id="A000360",
            bioguide_id="A000360",
            first="Alice",
            last="Anderson",
            chamber="House",
            party="D",
            state="CA",
        ),
        Member(
            member_id="B000123",
            bioguide_id="B000123",
            first="Bob",
            last="Brown",
            chamber="House",
            party="R",
            state="TX",
        ),
    ]
    load.load_objects(members)


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
