"""Test fixtures for the campaign pipeline."""
from __future__ import annotations

import pathlib
import sys

import pytest

# Ensure src package is importable
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))


@pytest.fixture
def sample_members() -> list[dict]:
    return [
        {"member_id": "A000360", "bioguide_id": "A000360"},
        {"member_id": "B000123", "bioguide_id": "B000123"},
        {"member_id": "C000456", "bioguide_id": "C000456"},
    ]


@pytest.fixture
def candidate_mapping() -> dict:
    return {"A000360": ["H0XX00001"], "B000123": ["S0XX00002"]}


@pytest.fixture
def raw_contribs() -> list[dict]:
    return [
        {
            "committee_id": "C1",
            "recipient_id": "H0XX00001",
            "name": "John Doe",
            "employer": "Corp",
            "occupation": "CEO",
            "type": "PAC",
            "industry": "Finance",
            "amount": 1000,
            "date": "2024-01-01",
            "cycle": 2024,
        }
    ]


@pytest.fixture
def raw_independent_expenditures() -> list[dict]:
    return [
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


@pytest.fixture
def vote_record() -> dict:
    return {
        "positions": [
            {"member_id": "A000360", "vote_position": "Yes"},
            {"member_id": "B000123", "vote_position": "No"},
        ]
    }


@pytest.fixture
def alignment_records() -> list[dict]:
    return [
        {
            "member_id": "A000360",
            "vote_id": "1",
            "net_industry": 5000.0,
            "matches_interest": True,
        }
    ]

