from __future__ import annotations

from sqlalchemy import Column, Float, Integer, String, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Legislator(Base):
    __tablename__ = "legislators"
    bioguide_id = Column(String, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    party = Column(String)
    terms = relationship("LegislatorTerm", back_populates="legislator")


class LegislatorTerm(Base):
    __tablename__ = "legislator_terms"
    id = Column(Integer, primary_key=True)
    bioguide_id = Column(String, ForeignKey("legislators.bioguide_id"))
    start = Column(Date)
    end = Column(Date)
    state = Column(String)
    district = Column(String)
    legislator = relationship("Legislator", back_populates="terms")


class Vote(Base):
    __tablename__ = "votes"
    vote_id = Column(String, primary_key=True)
    chamber = Column(String)
    congress = Column(Integer)
    session = Column(String)
    rollnumber = Column(Integer)
    date = Column(String)
    question = Column(String)
    result = Column(String)
    bill_id = Column(String)
    records = relationship("VoteRecord", back_populates="vote")


class VoteRecord(Base):
    __tablename__ = "vote_records"
    id = Column(Integer, primary_key=True)
    vote_id = Column(String, ForeignKey("votes.vote_id"))
    bioguide_id = Column(String)
    position = Column(String)
    vote = relationship("Vote", back_populates="records")


class FECCandidate(Base):
    __tablename__ = "fec_candidates"
    cand_id = Column(String, primary_key=True)
    name = Column(String)
    party = Column(String)
    state = Column(String)
    district = Column(String)


class FECCandidateTotals(Base):
    __tablename__ = "fec_candidate_totals"
    id = Column(Integer, primary_key=True)
    cand_id = Column(String)
    receipts = Column(Float)
    disbursements = Column(Float)


class FECReceipt(Base):
    __tablename__ = "fec_receipts"
    id = Column(Integer, primary_key=True)
    cand_id = Column(String)
    amount = Column(Float)
    contributor_state = Column(String)


class LinkLegislatorCandidate(Base):
    __tablename__ = "link_leg_cand"
    id = Column(Integer, primary_key=True)
    cycle = Column(Integer)
    bioguide_id = Column(String)
    cand_id = Column(String)
    method = Column(String)
    score = Column(Float)
