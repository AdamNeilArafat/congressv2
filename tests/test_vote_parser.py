from src.votes import parse_member_positions


def test_vote_parser(vote_record):
    positions = parse_member_positions(vote_record)
    assert positions["A000360"] == "Yes"
    assert positions["B000123"] == "No"

