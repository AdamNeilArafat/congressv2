from typer.testing import CliRunner

from src.cli import app


def test_cli_smoke():
    runner = CliRunner()
    result = runner.invoke(app, ["ingest", "members"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["ingest", "fec", "--cycles", "2024"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["ingest", "votes", "--from", "2023-01-01"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["normalize", "all"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["analyze", "--window", "24m"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["export", "--out", "outputs/"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["report", "--id", "A000360"])
    assert result.exit_code == 0

