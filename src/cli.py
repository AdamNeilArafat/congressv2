"""Command line interface for the campaign pipeline."""
from __future__ import annotations

import typer

from . import analyze, fec, load, normalize, votes

app = typer.Typer()
ingest_app = typer.Typer()
app.add_typer(ingest_app, name="ingest")


@ingest_app.command("members")
def ingest_members() -> None:
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


if __name__ == "__main__":  # pragma: no cover - manual execution
    app()

