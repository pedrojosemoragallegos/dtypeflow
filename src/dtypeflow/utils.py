from __future__ import annotations

from csv import DictReader, Error, Sniffer
from pathlib import Path

from dtypeflow.core.table import Table


def read_csv(path: str | Path, /, *, delimiter: str | None = None) -> Table:
    if delimiter is not None and len(delimiter) != 1:
        msg = "The delimiter must be exactly one character."
        raise ValueError(msg)
    if isinstance(path, str):
        if not path:
            msg = "The path to the file cannot be empty."
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
    with path.open(newline="") as file:
        if delimiter is None:
            sample = file.read(64 * 1024).replace("\r\n", "\n")
            try:
                delimiter = Sniffer().sniff(sample, delimiters=",;\t|").delimiter
            except Error as exc:
                msg = "Could not detect the delimiter; specify one explicitly."
                raise ValueError(msg) from exc
            file.seek(0)
        reader: DictReader[str] = DictReader(file, delimiter=delimiter)
        rows: list[dict[str, str]] = list(reader)
        return Table(
            **{
                name: tuple(row[name] for row in rows)
                for name in reader.fieldnames or ()
            },
        )
