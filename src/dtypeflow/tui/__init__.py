from __future__ import annotations

import argparse

__all__: list[str] = ["run"]


def run() -> None:
    from dtypeflow.tui.app import DtypeflowApp

    parser = argparse.ArgumentParser(
        prog="dtypeflow",
        description="Interactive terminal UI to convert a CSV file to Parquet.",
    )
    parser.add_argument("path", nargs="?", help="Path to a CSV file to load on startup")
    args = parser.parse_args()
    DtypeflowApp(initial_path=args.path).run()
