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

### Sample API calls

The pipeline primarily relies on two public data sources:

* **OpenFEC** for campaign finance data via the [OpenFEC API](https://api.open.fec.gov/developers/) and the [fecgov/openFEC](https://github.com/fecgov/openFEC) bulk downloads as a fallback.
* **Congress.gov** for legislative data via the [Congress.gov API](https://api.congress.gov) and the [LibraryOfCongress/api.congress.gov](https://github.com/LibraryOfCongress/api.congress.gov) project or [GovInfo BILLSTATUS XML](https://www.govinfo.gov/bulkdata/BILLSTATUS) as a fallback.

Either service can be queried directly when experimenting or building new ingestion steps.

#### OpenFEC examples

```bash
# Candidates (basic)
curl "https://api.open.fec.gov/v1/candidates/?page=1&per_page=100&api_key=nlaFzcVKa7YQrbCJvkZFRDNcZD5rAdA0stgXSNp5"

# Candidate totals (money in/out by cycle)
curl "https://api.open.fec.gov/v1/candidate/H0WA10149/totals/?cycle=2024&api_key=nlaFzcVKa7YQrbCJvkZFRDNcZD5rAdA0stgXSNp5"

# Itemized contributions (Schedule A) to a committee
curl "https://api.open.fec.gov/v1/schedules/schedule_a/?committee_id=C00XXXXXX&two_year_transaction_period=2024&per_page=100&api_key=nlaFzcVKa7YQrbCJvkZFRDNcZD5rAdA0stgXSNp5"

# Independent expenditures (Schedule E)
curl "https://api.open.fec.gov/v1/schedules/schedule_e/?per_page=100&api_key=nlaFzcVKa7YQrbCJvkZFRDNcZD5rAdA0stgXSNp5"
```

Bulk CSVs for full backfills are available from <https://www.fec.gov/data/browse-data/>.

#### Congress.gov examples

```bash
# Latest bills (follow pagination.next)
curl "https://api.congress.gov/v3/bill?format=json&limit=250&api_key=FhFEPhUSuCNrTbbxyOngBBqedbfTA9SeTCtTy6Vz"

# Bill details (item)
curl "https://api.congress.gov/v3/bill/119/hr/2808?format=json&api_key=FhFEPhUSuCNrTbbxyOngBBqedbfTA9SeTCtTy6Vz"

# Sub-resources you'll likely use:
curl "https://api.congress.gov/v3/bill/119/hr/2808/actions?format=json&api_key=FhFEPhUSuCNrTbbxyOngBBqedbfTA9SeTCtTy6Vz"
curl "https://api.congress.gov/v3/bill/119/hr/2808/cosponsors?format=json&api_key=FhFEPhUSuCNrTbbxyOngBBqedbfTA9SeTCtTy6Vz"
curl "https://api.congress.gov/v3/bill/119/hr/2808/committees?format=json&api_key=FhFEPhUSuCNrTbbxyOngBBqedbfTA9SeTCtTy6Vz"
curl "https://api.congress.gov/v3/bill/119/hr/2808/summary?format=json&api_key=FhFEPhUSuCNrTbbxyOngBBqedbfTA9SeTCtTy6Vz"
curl "https://api.congress.gov/v3/bill/119/hr/2808/subjects?format=json&api_key=FhFEPhUSuCNrTbbxyOngBBqedbfTA9SeTCtTy6Vz"

# Members + their bill relationships
curl "https://api.congress.gov/v3/member?format=json&limit=250&api_key=FhFEPhUSuCNrTbbxyOngBBqedbfTA9SeTCtTy6Vz"
curl "https://api.congress.gov/v3/member/B001135/sponsored-legislation?format=json&limit=250&api_key=FhFEPhUSuCNrTbbxyOngBBqedbfTA9SeTCtTy6Vz"

# House roll call votes
curl "https://api.congress.gov/v3/house-vote?format=json&limit=100&api_key=FhFEPhUSuCNrTbbxyOngBBqedbfTA9SeTCtTy6Vz"
```

Rate limits are roughly 5,000 requests per hour; use `pagination.next` and
`fromDateTime`/`toDateTime` parameters for incremental loads. Bulk bill status
XML files can be downloaded from <https://www.govinfo.gov/bulkdata/BILLSTATUS>
to backfill the dataset if the API is unavailable.

## GitHub Pages Deployment

The project deploys its static site with GitHub Pages via `.github/workflows/pages.yml`. The workflow
uses the default `GITHUB_TOKEN`, but will also accept a personal access token supplied as the
`PAGES_TOKEN` secret. Provide a token with `repo` and `pages:write` scopes if you need to create or
enable the Pages site; otherwise the built-in token is sufficient for routine deployments.

