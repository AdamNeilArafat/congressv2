from pathlib import Path

from sqlmodel import Session, select
from typer.testing import CliRunner

from src.cli import app
from src.models import IndependentExpenditure
import src.fec as fec
from src.load import get_engine


def test_cli_ingest_schedule_e(monkeypatch):
    runner = CliRunner()
    db_path = Path("campaign.db")
    if db_path.exists():
        db_path.unlink()
    result = runner.invoke(app, ["ingest", "members"])
    assert result.exit_code == 0

    sample = [
        {
            "committee_id": "C1",
            "candidate_id": "H0XX00001",
            "payee": "Media Co",
            "purpose": "Ads",
            "amount": 5000,
            "date": "2024-02-01",
            "support_oppose": "S",
            "cycle": 2024,
        }
    ]

    monkeypatch.setattr(fec, "fetch_independent_expenditures", lambda cid, cyc: sample)

    result = runner.invoke(app, ["ingest", "fec", "--cycles", "2024", "--schedule-e"])
    assert result.exit_code == 0

    engine = get_engine()
    with Session(engine) as session:
        rows = session.exec(select(IndependentExpenditure)).all()
        assert len(rows) == 1
        assert rows[0].candidate_id == "H0XX00001"

