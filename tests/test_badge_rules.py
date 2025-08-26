from src.badges import assign_badges


def test_badge_rules():
    summary = {
        "member_id": "A000360",
        "finance_conflicts": 3,
        "finance_alignment_index": 0.3,
        "top_industries": ["Finance"],
        "pharma_conflicts": 0,
        "defense_alignment_index": 0.0,
        "pac_share": 0.1,
        "small_donor_share": 0.5,
    }
    badges = assign_badges(summary, [])
    codes = {b.badge_code for b in badges}
    assert "WALL_STREET_WONT_LIKE_IT" in codes
    assert "SMALL_DOLLARS_HEAVY" in codes

