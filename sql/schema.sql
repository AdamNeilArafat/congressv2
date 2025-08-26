-- Schema for campaign finance pipeline

CREATE TABLE members (
    member_id TEXT PRIMARY KEY,
    bioguide_id TEXT,
    first TEXT,
    last TEXT,
    chamber TEXT,
    party TEXT,
    state TEXT,
    district TEXT,
    fec_candidate_ids TEXT[]
);

CREATE TABLE committees (
    committee_id TEXT PRIMARY KEY,
    name TEXT,
    type TEXT,
    fec_type TEXT,
    party_affiliation TEXT
);

CREATE TABLE contributions (
    id INTEGER PRIMARY KEY,
    committee_id TEXT REFERENCES committees(committee_id),
    recipient_fec_id TEXT,
    contributor_name TEXT,
    contributor_employer TEXT,
    contributor_occupation TEXT,
    contributor_type TEXT,
    industry TEXT,
    amount NUMERIC,
    date DATE,
    cycle INTEGER
);

CREATE INDEX idx_contributions_recipient_date ON contributions(recipient_fec_id, date);

CREATE TABLE bills (
    bill_id TEXT PRIMARY KEY,
    congress INTEGER,
    chamber TEXT,
    number TEXT,
    title TEXT,
    sponsor_bioguide TEXT,
    subjects TEXT,
    introduced_date DATE
);

CREATE TABLE rollcalls (
    vote_id TEXT PRIMARY KEY,
    bill_id TEXT REFERENCES bills(bill_id),
    question TEXT,
    result TEXT,
    date DATE,
    chamber TEXT,
    source_url TEXT
);

CREATE TABLE member_votes (
    vote_id TEXT REFERENCES rollcalls(vote_id),
    member_id TEXT REFERENCES members(member_id),
    position TEXT,
    PRIMARY KEY (vote_id, member_id)
);

CREATE INDEX idx_member_votes_member_vote ON member_votes(member_id, vote_id);

CREATE TABLE member_finance (
    member_id TEXT REFERENCES members(member_id),
    cycle INTEGER,
    total_pac NUMERIC,
    total_indiv NUMERIC,
    top_industries JSON,
    top_pacs JSON,
    PRIMARY KEY (member_id, cycle)
);

CREATE TABLE alignment_events (
    id INTEGER PRIMARY KEY,
    member_id TEXT REFERENCES members(member_id),
    vote_id TEXT REFERENCES rollcalls(vote_id),
    alignment_score REAL,
    rationale TEXT,
    drivers JSON
);

CREATE INDEX idx_alignment_events_member ON alignment_events(member_id);

CREATE TABLE badges (
    member_id TEXT REFERENCES members(member_id),
    badge_code TEXT,
    label TEXT,
    reason TEXT,
    computed_at TIMESTAMP,
    PRIMARY KEY (member_id, badge_code)
);
