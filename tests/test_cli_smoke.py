 codex/create-reproducible-pipeline-for-fec-data-analysis-bn84jr

from pathlib import Path

 main
from typer.testing import CliRunner

from src.cli import app


 codex/create-reproducible-pipeline-for-fec-data-analysis-bn84jr
def test_cli_smoke():
    runner = CliRunner()
    result = runner.invoke(app, ["ingest", "members"])
    assert result.exit_code == 0

def test_cli_smoke(tmp_path):
    runner = CliRunner()
    db_path = Path("campaign.db")
    if db_path.exists():
        db_path.unlink()
    result = runner.invoke(app, ["ingest", "members"])
    assert result.exit_code == 0
    # database should be created by ingest_members
    assert db_path.exists()

 main
    result = runner.invoke(app, ["ingest", "fec", "--cycles", "2024"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["ingest", "votes", "--from", "2023-01-01"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["normalize", "all"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["analyze", "--window", "24m"])
    assert result.exit_code == 0
 codex/create-reproducible-pipeline-for-fec-data-analysis-bn84jr
    result = runner.invoke(app, ["export", "--out", "outputs/"])
    assert result.exit_code == 0


    outdir = tmp_path / "out"
    result = runner.invoke(app, ["export", "--out", str(outdir)])
    assert result.exit_code == 0
    assert (outdir / "alignment.csv").exists()

 main
    result = runner.invoke(app, ["report", "--id", "A000360"])
    assert result.exit_code == 0

