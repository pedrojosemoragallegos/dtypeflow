from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DtypeOption:
    name: str
    label: str
    description: str
    group: str


@dataclass(frozen=True)
class ColumnReport:
    name: str
    inferred_dtype: str
    description: str
    num_unique: int
    total: int
    samples: tuple[str, ...]
    stats: tuple[tuple[str, str], ...]
    options: tuple[DtypeOption, ...]


@dataclass(frozen=True)
class DatasetReport:
    source: str
    columns: tuple[ColumnReport, ...]


@dataclass(frozen=True)
class ColumnSelection:
    dtype_name: str
    true_value: str | None = None
    false_value: str | None = None
    ordered: bool = False
    categories: tuple[str, ...] | None = None


@dataclass
class LoadedDataset:
    report: DatasetReport
    dataset_ref: object = field(repr=False)
