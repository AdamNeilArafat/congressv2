from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from . import paths
from . import download
from . import extract_legislators, extract_votes, extract_fec
from . import normalize
from . import link
from . import metrics


def cmd_init(args: argparse.Namespace) -> None:
    paths.init_dirs()


def cmd_download(args: argparse.Namespace) -> None:
    if args.clone:
        download.clone_legislators()
        download.clone_congress_tools()
    if args.congresses:
        download.fetch_govinfo_rollcalls(args.congresses)
    if args.cycles:
        download.fetch_fec_bulk(args.cycles)


def cmd_extract(args: argparse.Namespace) -> None:
    extract_legislators.extract()
    extract_votes.extract()
    cycles = [int(p.name) for p in (paths.RAW_DIR / "fec").glob("*/")]
    extract_fec.extract(cycles)


def cmd_load(args: argparse.Namespace) -> None:
    normalize.load_sqlite()


def cmd_link(args: argparse.Namespace) -> None:
    cycles = [int(f.stem.split("_")[-1]) for f in paths.INTERIM_DIR.glob("fec_candidates_*.csv")]
    link.link_legislators_candidates(sorted(set(cycles)))


def cmd_metrics(args: argparse.Namespace) -> None:
    metrics.build_metrics(args.cycles, args.congresses)


def cmd_export(args: argparse.Namespace) -> None:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for f in paths.OUTPUT_DIR.glob("*.csv"):
        shutil.copy(f, out / f.name)
    with open(out / "DATADICT.md", "w") as f:
        f.write("See README for column descriptions.")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init")
    p_init.set_defaults(func=cmd_init)

    p_dl = sub.add_parser("download")
    p_dl.add_argument("--congresses", nargs="*", type=int, default=[])
    p_dl.add_argument("--cycles", nargs="*", type=int, default=[])
    p_dl.add_argument("--clone", action="store_true", help="clone Git repos")
    p_dl.set_defaults(func=cmd_download)

    p_ex = sub.add_parser("extract")
    p_ex.set_defaults(func=cmd_extract)

    p_load = sub.add_parser("load")
    p_load.set_defaults(func=cmd_load)

    p_link = sub.add_parser("link")
    p_link.set_defaults(func=cmd_link)

    p_met = sub.add_parser("metrics")
    p_met.add_argument("--cycles", nargs="*", type=int, required=True)
    p_met.add_argument("--congresses", nargs="*", type=int, required=True)
    p_met.set_defaults(func=cmd_metrics)

    p_export = sub.add_parser("export")
    p_export.add_argument("--out", required=True)
    p_export.set_defaults(func=cmd_export)

    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
