from src.fec import link_members_to_candidates


def test_link_member_candidates(sample_members, candidate_mapping):
    result = link_members_to_candidates(sample_members, candidate_mapping)
    assert result["A000360"] == ["H0XX00001"]
    assert result["C000456"] == []

