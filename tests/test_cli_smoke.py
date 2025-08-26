from pathlib import Path

from typer.testing import CliRunner

from src.cli import app


def test_cli_smoke(tmp_path):
    runner = CliRunner()

    # ingest members should create a database file
    db_path = Path("campaign.db")
    if db_path.exists():
        db_path.unlink()
    result = runner.invoke(app, ["ingest", "members"])
    assert result.exit_code == 0
    assert db_path.exists()

    # run remaining commands to ensure CLI wiring works
    result = runner.invoke(app, ["ingest", "fec", "--cycles", "2024"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["ingest", "votes", "--from", "2023-01-01"])
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
