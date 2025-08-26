"""Badge assignment rules."""
from __future__ import annotations

from typing import Iterable, List

from .models import Badge


def assign_badges(member_summary: dict, alignment_events: Iterable[dict]) -> List[Badge]:
    """Assign badges to a member based on summary stats and events."""
    badges: List[Badge] = []
    mid = member_summary["member_id"]

    if (
        member_summary.get("finance_conflicts", 0) >= 3
        and member_summary.get("finance_alignment_index", 1.0) <= 0.35
    ):
        badges.append(Badge(member_id=mid, badge_code="WALL_STREET_WONT_LIKE_IT", label="Wall Street Won't Like It"))

    if (
        "Healthcare" in member_summary.get("top_industries", [])
        and member_summary.get("pharma_conflicts", 0) >= 2
    ):
        badges.append(Badge(member_id=mid, badge_code="HEALTHCARE_INDEPENDENT", label="Healthcare Independent"))

    if (
        "Defense" in member_summary.get("top_industries", [])
        and member_summary.get("defense_alignment_index", 0.0) >= 0.65
    ):
        badges.append(Badge(member_id=mid, badge_code="DEFENSE_ALIGNED", label="Defense Aligned"))

    if (
        member_summary.get("pac_share", 1.0) <= 0.2
        and member_summary.get("small_donor_share", 0.0) >= 0.4
    ):
        badges.append(Badge(member_id=mid, badge_code="SMALL_DOLLARS_HEAVY", label="Small Dollars Heavy"))

    if member_summary.get("top_industries", [None])[0] == "Unknown":
        badges.append(Badge(member_id=mid, badge_code="INDUSTRY_LEAN_UNKNOWN", label="Industry Lean Unknown"))

    return badges

