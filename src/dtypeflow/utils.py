from __future__ import annotations

from csv import DictReader
from pathlib import Path

from dtypeflow.core.table import Table


def read_csv(path: str | Path, /, *, delimiter: str = ",", newline: str = "") -> Table:
    if isinstance(path, str):
        if not path:
            msg = "The path to the CSV file cannot be empty."
            raise ValueError(msg)
        path: Path = Path(path)
    if not path.exists():
        msg = f"The CSV file at path '{path}' does not exist."
        raise FileNotFoundError(msg)
    if not path.is_file():
        msg = f"The path '{path}' is not a valid file."
        raise ValueError(msg)
    if path.suffix.lower() != ".csv":
        msg = f"The file '{path}' is not a CSV file."
        raise ValueError(msg)
    with path.open(newline=newline) as file:
        reader: DictReader[str] = DictReader(file, delimiter=delimiter)
        rows: list[dict[str, str]] = list(reader)
        return Table(
            **{
                name: tuple(row[name] for row in rows)
                for name in reader.fieldnames or ()
            },
        )
