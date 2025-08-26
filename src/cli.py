"""Command line interface for the campaign pipeline."""
from __future__ import annotations

 codex/create-reproducible-pipeline-for-fec-data-analysis-erh252

 codex/create-reproducible-pipeline-for-fec-data-analysis-bn84jr
 main
import typer

from . import analyze, fec, load, normalize, votes

 codex/create-reproducible-pipeline-for-fec-data-analysis-erh252

import csv
from pathlib import Path

import typer

from . import analyze, fec, load, normalize, votes
from .models import AlignmentEvent, Member, MemberVote
 main

 main
app = typer.Typer()
ingest_app = typer.Typer()
app.add_typer(ingest_app, name="ingest")


@ingest_app.command("members")
def ingest_members() -> None:
 codex/create-reproducible-pipeline-for-fec-data-analysis-erh252
    """Placeholder for member ingestion."""
    typer.echo("ingest members")


@ingest_app.command("fec")
def ingest_fec(cycles: str = typer.Option(..., "--cycles")) -> None:
    """Placeholder for FEC ingestion."""
    typer.echo(f"ingest fec cycles={cycles}")


@ingest_app.command("votes")
def ingest_votes(from_date: str = typer.Option(..., "--from")) -> None:
    """Placeholder for vote ingestion."""
    typer.echo(f"ingest votes from {from_date}")


@app.command("normalize")
def normalize_all(kind: str = typer.Argument("all")) -> None:  # pragma: no cover - CLI only
    typer.echo(f"normalize {kind}")


@app.command("analyze")
def analyze_alignment(window: str = "24m") -> None:  # pragma: no cover - CLI only
    typer.echo(f"analyze alignment window={window}")


@app.command("export")
def export_csv(out: str = "outputs/") -> None:  # pragma: no cover - CLI only
    typer.echo(f"exporting to {out}")


@app.command("report")
def report_member(id: str = typer.Option(..., "--id")) -> None:  # pragma: no cover - CLI only
    typer.echo(f"report for {id}")


 codex/create-reproducible-pipeline-for-fec-data-analysis-bn84jr
    """Placeholder for member ingestion."""
    typer.echo("ingest members")

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
 main


@ingest_app.command("fec")
def ingest_fec(cycles: str = typer.Option(..., "--cycles")) -> None:
 codex/create-reproducible-pipeline-for-fec-data-analysis-bn84jr
    """Placeholder for FEC ingestion."""
    typer.echo(f"ingest fec cycles={cycles}")

    """Normalize and store a sample FEC contribution record."""
    members = [{"member_id": "A000360", "bioguide_id": "A000360"}]
    mapping = {"A000360": ["H0XX00001"]}
    # Link members to candidate IDs using the fec module
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
 main


@ingest_app.command("votes")
def ingest_votes(from_date: str = typer.Option(..., "--from")) -> None:
 codex/create-reproducible-pipeline-for-fec-data-analysis-bn84jr
    """Placeholder for vote ingestion."""
    typer.echo(f"ingest votes from {from_date}")

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
 main


@app.command("normalize")
def normalize_all(kind: str = typer.Argument("all")) -> None:  # pragma: no cover - CLI only
 codex/create-reproducible-pipeline-for-fec-data-analysis-bn84jr
    typer.echo(f"normalize {kind}")

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
 main


@app.command("analyze")
def analyze_alignment(window: str = "24m") -> None:  # pragma: no cover - CLI only
 codex/create-reproducible-pipeline-for-fec-data-analysis-bn84jr
    typer.echo(f"analyze alignment window={window}")

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
 main


@app.command("export")
def export_csv(out: str = "outputs/") -> None:  # pragma: no cover - CLI only
 codex/create-reproducible-pipeline-for-fec-data-analysis-bn84jr
    typer.echo(f"exporting to {out}")

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
    rows = [(ev.member_id, ev.vote_id, ev.alignment_score) for ev in events]
    load.load_objects(events)
    path = Path(out) / "alignment.csv"
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["member_id", "vote_id", "alignment_score"])
        writer.writerows(rows)
 main


@app.command("report")
def report_member(id: str = typer.Option(..., "--id")) -> None:  # pragma: no cover - CLI only
 codex/create-reproducible-pipeline-for-fec-data-analysis-bn84jr
    typer.echo(f"report for {id}")

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
 main

 main

if __name__ == "__main__":  # pragma: no cover - manual execution
    app()

