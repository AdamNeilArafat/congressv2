# US Congress Pipeline

This project provides a no-API, reproducible data pipeline that assembles per-candidate Congressional voting history and campaign finance metrics from publicly available bulk sources and GitHub repositories.

## Sources
- [unitedstates/congress-legislators](https://github.com/unitedstates/congress-legislators)
- [unitedstates/congress](https://github.com/unitedstates/congress)
- [GovInfo roll-call votes](https://www.govinfo.gov/)
- [FEC bulk data](https://www.fec.gov/data/browse-data/?tab=bulk-data)

## Setup

```bash
python -m pip install -e .
```

## Usage

```bash
# initialize folders
python -m pipeline.cli init

# download data
python -m pipeline.cli download --congresses 118 --cycles 2024

# extract, load, link, metrics
python -m pipeline.cli extract
python -m pipeline.cli load
python -m pipeline.cli link
python -m pipeline.cli metrics --cycles 2024 --congresses 118
python -m pipeline.cli export --out data/outputs/
```

## Data Dictionary
A `DATADICT.md` file will be generated describing output columns.

