from __future__ import annotations

from pathlib import Path


ROOT: Path = Path(__file__).resolve().parents[2]
DATA_DIR: Path = ROOT / "data"
RAW_DIR: Path = DATA_DIR / "raw"
INTERIM_DIR: Path = DATA_DIR / "interim"
WAREHOUSE_DIR: Path = DATA_DIR / "warehouse"
OUTPUT_DIR: Path = DATA_DIR / "outputs"


def init_dirs() -> None:
    """Create project directories."""
    for p in [RAW_DIR, INTERIM_DIR, WAREHOUSE_DIR, OUTPUT_DIR]:
        p.mkdir(parents=True, exist_ok=True)
