from src.votes import parse_member_positions


def test_vote_parser(vote_record):
    positions = parse_member_positions(vote_record)
    assert positions["A000360"] == "Yes"
    assert positions["B000123"] == "No"


def test_house_rollcall_vote_parser():
    """Ensure votes from the Congress.gov API are normalised."""
    vote_record = {
        "results": {
            "item": [
                {"bioguideId": "A000360", "voteCast": "Aye"},
                {"bioguideId": "B000123", "voteCast": "Nay"},
            ]
        }
    }
    positions = parse_member_positions(vote_record)
    assert positions["A000360"] == "Yes"
    assert positions["B000123"] == "No"

