# Campaign Finance and Vote Alignment Pipeline

This repo provides a reproducible Python pipeline to fetch FEC data, roll call votes, analyze alignment between money and votes, and assign badges to members of Congress.

## Setup

```bash
make dev
```

## Run End-to-End

```bash
poetry run campaign-cli ingest members && \
poetry run campaign-cli ingest fec --cycles 2024,2026 && \
poetry run campaign-cli ingest votes --from 2023-01-01 && \
poetry run campaign-cli normalize all && \
poetry run campaign-cli analyze alignment --window 24m && \
poetry run campaign-cli export csv --out outputs/
```

## Schema (ASCII)

```
members(member_id PK, bioguide_id, first, last, chamber, party, state, district, fec_candidate_ids[])
committees(committee_id PK, name, type, fec_type, party_affiliation NULL)
contributions(id PK, committee_id FK, recipient_fec_id, contributor_name, contributor_employer,
              contributor_occupation, contributor_type, industry, amount, date, cycle)
bills(bill_id PK, congress, chamber, number, title, sponsor_bioguide, subjects[], introduced_date)
rollcalls(vote_id PK, bill_id FK NULL, question, result, date, chamber, source_url)
member_votes(vote_id FK, member_id FK, position)
member_finance(member_id FK, cycle, total_pac, total_indiv, top_industries JSONB, top_pacs JSONB)
alignment_events(id PK, member_id FK, vote_id FK, alignment_score FLOAT, rationale TEXT, drivers JSONB)
badges(member_id FK, badge_code, label, reason, computed_at)
```

## Example Badge Output

`outputs/member_badges.csv`

```
member_id,badge_code,label
A000360,WALL_STREET_WON'T_LIKE_IT,Wall Street Won't Like It
```

 codex/create-reproducible-pipeline-for-fec-data-analysis-erh252

## Publish data for Accountability Wall

After generating CSV outputs, convert them to JSON for the accountability cards:

```bash
poetry run python scripts/build_accountability_data.py
```

This populates `data/` and `accountability/data/` with donors, alignment, and badge JSON used by the web page.

