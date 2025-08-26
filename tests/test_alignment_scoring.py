from src.analyze import compute_alignment_score


def test_alignment_scoring():
    assert compute_alignment_score(1000, True) > 0
    assert compute_alignment_score(1000, False) == 0

