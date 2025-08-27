from pathlib import Path

from typer.testing import CliRunner

from src import bills, committees, members, records
from src.cli import app


def test_cli_smoke(tmp_path, monkeypatch):
    runner = CliRunner()

    # stub API wrappers
    monkeypatch.setattr(
        members,
        "fetch_members",
        lambda from_date=None: [
            {
                "bioguideId": "A000360",
                "firstName": "Alice",
                "lastName": "Anderson",
                "chamber": "House",
                "party": "D",
                "state": "CA",
            }
        ],
    )
    monkeypatch.setattr(
        bills,
        "fetch_bills",
        lambda from_date=None: [
            {
                "billId": "hr1-118",
                "congress": 118,
                "type": "hr",
                "number": "1",
                "title": "Test",
            }
        ],
    )
    monkeypatch.setattr(
        committees,
        "fetch_committees",
        lambda from_date=None: [
            {"committeeId": "HSED", "name": "Education", "type": "House"}
        ],
    )
    monkeypatch.setattr(
        records,
        "fetch_records",
        lambda from_date=None: [
            {
                "recordId": "R1",
                "title": "Record",
                "date": "2024-01-01",
                "chamber": "House",
            }
        ],
    )

    # ingest members should create a database file
    db_path = Path("campaign.db")
    if db_path.exists():
        db_path.unlink()
    result = runner.invoke(app, ["ingest", "members"])
    assert result.exit_code == 0
    assert db_path.exists()

    # run remaining commands to ensure CLI wiring works
    result = runner.invoke(app, ["ingest", "bills", "--from", "2024-01-01"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["ingest", "committees"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["ingest", "records"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["ingest", "fec", "--cycles", "2024"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["ingest", "votes", "--from", "2023-01-01"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["ingest", "voter-history", "--path", "data/voter_history_sample.csv"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["normalize", "all"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["analyze", "--window", "24m"])
    assert result.exit_code == 0

    outdir = tmp_path / "out"
    result = runner.invoke(app, ["export", "--out", str(outdir)])
    assert result.exit_code == 0
    assert (outdir / "alignment.csv").exists()

    result = runner.invoke(app, ["report", "--id", "A000360"])
    assert result.exit_code == 0
