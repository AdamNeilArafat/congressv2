from datetime import date

from src.normalize import normalize_independent_expenditures


def test_independent_expenditure_normalization(raw_independent_expenditures):
    normalized = normalize_independent_expenditures(raw_independent_expenditures)
    assert len(normalized) == 1
    ie = normalized[0]
    assert ie.committee_id == "C1"
    assert ie.candidate_id == "H0XX00001"
    assert ie.payee == "Media Co"
    assert ie.amount == 5000
    assert ie.cycle == 2024
    assert isinstance(ie.date, date)
    assert ie.date == date(2024, 2, 1)

