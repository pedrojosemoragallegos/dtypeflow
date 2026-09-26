from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pyarrow as pa
import pyarrow.parquet as pq

from dtypeflow.utils import read_csv

if TYPE_CHECKING:
    from dtypeflow.core.dataset import Dataset
    from dtypeflow.core.override import Override


class Schema:
    def __init__(self, *overrides: Override) -> None:
        self._overrides: tuple[Override, ...] = overrides

    def apply(self, dataset: Dataset, /, *, destination: str | Path) -> None:
        if isinstance(destination, str):
            destination: Path = Path(destination)
        columns: dict[str, Override] = {}
        for override in self._overrides:
            if override.column not in dataset:
                msg = f"{override!r} is not valid for {dataset!r}."
                raise ValueError(msg)
            columns[override.column] = override
        raw: dict[str, tuple[str, ...]] = dict(read_csv(dataset.source))
        arrays = []
        for column, override in columns.items():
            arrays.append(override.transform(*raw.pop(column)))
        pq.write_table(pa.Table.from_arrays(arrays, names=list(columns)), destination)
