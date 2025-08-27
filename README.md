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
## Publish data for Accountability Wall

After generating CSV outputs, convert them to JSON for the accountability cards:

```bash
poetry run python scripts/build_accountability_data.py
```

This populates `data/` and `accountability/data/` with donors, alignment, and badge JSON used by the web page.

### FEC data without an API key

If the OpenFEC API is unavailable, set the `FEC_FALLBACK_CSV` environment
variable to a CSV file containing `candidate_id,total_receipts,individual_contributions,
pac_contributions,transfers_from_other_authorized_committee` columns. The
`scripts/pull-donors.mjs` script reads this file instead of calling the API.

## GitHub Pages Deployment

The project deploys its static site with GitHub Pages via `.github/workflows/pages.yml`. The default
`GITHUB_TOKEN` cannot create or enable a Pages site, so generate a personal access token with `repo`
and `pages:write` scopes and add it as a repository secret named `PAGES_TOKEN`. The workflow uses
this token to configure and deploy the site automatically.

## Congress.gov API curl examples

All Congress.gov endpoints share a rate limit of **5,000 requests per hour**. List endpoints are
paginated with a `limit` parameter (default 20, maximum 250) and an `offset` parameter for the start
record.

### Amendments
Rate limit: 5,000 requests per hour. Pagination: `limit` and `offset`.
```bash
curl -H "X-Api-Key: YOUR_API_KEY" "https://api.congress.gov/v3/bill/118/hr/1234/amendments?format=json&limit=20&offset=0"
```

### Related bills
Rate limit: 5,000 requests per hour. Pagination: `limit` and `offset`.
```bash
curl -H "X-Api-Key: YOUR_API_KEY" "https://api.congress.gov/v3/bill/118/hr/1234/relatedBills?format=json&limit=20&offset=0"
```

### Titles
Rate limit: 5,000 requests per hour. Pagination: `limit` and `offset`.
```bash
curl -H "X-Api-Key: YOUR_API_KEY" "https://api.congress.gov/v3/bill/118/hr/1234/titles?format=json&limit=20&offset=0"
```

### Policy area
Rate limit: 5,000 requests per hour. This endpoint returns at most one record and is not paginated.
```bash
curl -H "X-Api-Key: YOUR_API_KEY" "https://api.congress.gov/v3/bill/118/hr/1234/policy-area?format=json"
```

### Bill text
Rate limit: 5,000 requests per hour. Pagination: `limit` and `offset` across text versions.
```bash
curl -H "X-Api-Key: YOUR_API_KEY" "https://api.congress.gov/v3/bill/118/hr/1234/text?format=json&limit=20&offset=0"
```

### Incremental window queries
Rate limit: 5,000 requests per hour. Pagination: `limit` and `offset`.
```bash
curl -H "X-Api-Key: YOUR_API_KEY" "https://api.congress.gov/v3/bill?fromDateTime=2024-01-01T00:00:00Z&toDateTime=2024-01-31T23:59:59Z&format=json&limit=20&offset=0"
```

### Member details
Rate limit: 5,000 requests per hour. This endpoint returns a single record and is not paginated.
```bash
curl -H "X-Api-Key: YOUR_API_KEY" "https://api.congress.gov/v3/member/B000575?format=json"
```

### Member cosponsored legislation
Rate limit: 5,000 requests per hour. Pagination: `limit` and `offset`.
```bash
curl -H "X-Api-Key: YOUR_API_KEY" "https://api.congress.gov/v3/member/B000575/cosponsoredLegislation?format=json&limit=20&offset=0"
```

### Vote item/member levels
Rate limit: 5,000 requests per hour. Pagination: `limit` and `offset` for member vote lists.
```bash
curl -H "X-Api-Key: YOUR_API_KEY" "https://api.congress.gov/v3/house-vote/118/1/45?format=json&limit=20&offset=0"
```

### Committees
Rate limit: 5,000 requests per hour. Pagination: `limit` and `offset`.
```bash
curl -H "X-Api-Key: YOUR_API_KEY" "https://api.congress.gov/v3/committee?format=json&limit=20&offset=0"
```

### Committee reports
Rate limit: 5,000 requests per hour. Single report retrieval is not paginated.
```bash
curl -H "X-Api-Key: YOUR_API_KEY" "https://api.congress.gov/v3/committee-report/118/hrpt/1?format=json"
```

### Nominations
Rate limit: 5,000 requests per hour. Pagination: `limit` and `offset`.
```bash
curl -H "X-Api-Key: YOUR_API_KEY" "https://api.congress.gov/v3/nomination?format=json&limit=20&offset=0"
```

### Treaties
Rate limit: 5,000 requests per hour. Pagination: `limit` and `offset`.
```bash
curl -H "X-Api-Key: YOUR_API_KEY" "https://api.congress.gov/v3/treaty?format=json&limit=20&offset=0"
```

### Congressional Record
Rate limit: 5,000 requests per hour. Pagination: `limit` and `offset`.
```bash
curl -H "X-Api-Key: YOUR_API_KEY" "https://api.congress.gov/v3/congressional-record/118/house?format=json&limit=20&offset=0"
```

### Amendment collections
Rate limit: 5,000 requests per hour. Pagination: `limit` and `offset`.
```bash
curl -H "X-Api-Key: YOUR_API_KEY" "https://api.congress.gov/v3/amendment?format=json&limit=20&offset=0"
```


