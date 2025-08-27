from src.voter_history import parse_voter_history


def test_parse_voter_history():
    records = parse_voter_history("data/voter_history_sample.csv")
    assert len(records) == 2
    assert records[0].voter_id == "V001"
    assert records[0].participated is True
    assert records[1].participated is False
