#!/usr/bin/env python3
"""Clone or update data sources from GitHub."""
from pathlib import Path
import subprocess

REPOS = {
    "unitedstates-congress": "https://github.com/unitedstates/congress",
    "openFEC": "https://github.com/fecgov/openFEC",
}

def main() -> None:
    base = Path("data") / "sources"
    base.mkdir(parents=True, exist_ok=True)
    for name, url in REPOS.items():
        dest = base / name
        if dest.exists():
            subprocess.run(["git", "-C", str(dest), "pull", "--ff-only"], check=True)
        else:
            subprocess.run(["git", "clone", url, str(dest)], check=True)

if __name__ == "__main__":
    main()
