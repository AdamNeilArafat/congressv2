"""Database models using SQLModel."""
from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from sqlmodel import JSON, Column, Field, SQLModel


class Member(SQLModel, table=True):
    member_id: str = Field(primary_key=True)
    bioguide_id: Optional[str] = None
    first: str
    last: str
    chamber: str
    party: str
    state: str
    district: Optional[str] = None
    fec_candidate_ids: List[str] = Field(default_factory=list, sa_column=Column(JSON))


class Committee(SQLModel, table=True):
    committee_id: str = Field(primary_key=True)
    name: str
    type: Optional[str] = None
    fec_type: Optional[str] = None
    party_affiliation: Optional[str] = None


class Contribution(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    committee_id: Optional[str] = Field(default=None, foreign_key="committee.committee_id")
    recipient_fec_id: Optional[str] = None
    contributor_name: Optional[str] = None
    contributor_employer: Optional[str] = None
    contributor_occupation: Optional[str] = None
    contributor_type: Optional[str] = None
    industry: Optional[str] = None
    amount: float
    date: date
    cycle: int


class IndependentExpenditure(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    committee_id: Optional[str] = Field(
        default=None, foreign_key="committee.committee_id"
    )
    candidate_id: Optional[str] = None
    payee: Optional[str] = None
    purpose: Optional[str] = None
    amount: float
    date: date
    support_oppose: Optional[str] = None
    cycle: int


class Bill(SQLModel, table=True):
    bill_id: str = Field(primary_key=True)
    congress: int
    chamber: str
    number: str
    title: str
    sponsor_bioguide: Optional[str] = None
    subjects: Optional[str] = None
    introduced_date: Optional[date] = None


class RollCall(SQLModel, table=True):
    vote_id: str = Field(primary_key=True)
    bill_id: Optional[str] = Field(default=None, foreign_key="bill.bill_id")
    question: str
    result: str
    date: date
    chamber: str
    source_url: Optional[str] = None


class MemberVote(SQLModel, table=True):
    vote_id: str = Field(foreign_key="rollcall.vote_id", primary_key=True)
    member_id: str = Field(foreign_key="member.member_id", primary_key=True)
    position: str


class VoterHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    voter_id: str
    election_date: date
    participated: bool
    method: Optional[str] = None


class MemberFinance(SQLModel, table=True):
    member_id: str = Field(foreign_key="member.member_id", primary_key=True)
    cycle: int = Field(primary_key=True)
    total_pac: float
    total_indiv: float
    top_industries: dict | None = Field(default=None, sa_column=Column(JSON))
    top_pacs: dict | None = Field(default=None, sa_column=Column(JSON))


class AlignmentEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    member_id: str = Field(foreign_key="member.member_id")
    vote_id: str = Field(foreign_key="rollcall.vote_id")
    alignment_score: float
    rationale: Optional[str] = None
    drivers: dict | None = Field(default=None, sa_column=Column(JSON))


class Badge(SQLModel, table=True):
    member_id: str = Field(foreign_key="member.member_id", primary_key=True)
    badge_code: str = Field(primary_key=True)
    label: str
    reason: Optional[str] = None
    computed_at: datetime = Field(default_factory=datetime.utcnow)



class CongressionalRecord(SQLModel, table=True):
    record_id: str = Field(primary_key=True)
    title: str
    date: date
    chamber: Optional[str] = None
