from src.normalize import normalize_contributions


def test_contribution_normalization(raw_contribs):
    normalized = normalize_contributions(raw_contribs)
    assert len(normalized) == 1
    c = normalized[0]
    assert c.committee_id == "C1"
    assert c.amount == 1000
    assert c.cycle == 2024

