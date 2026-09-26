from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING, Final, cast

import pyarrow.parquet as pq

from dtypeflow import profile as profile_dataset
from dtypeflow.core.dtype import (
    ALL_TYPES,
    BooleanDtype,
    DictionaryDtype,
    Dtype,
    Float16Dtype,
    Float32Dtype,
    Float64Dtype,
    FloatDtype,
    Int8Dtype,
    Int16Dtype,
    Int32Dtype,
    Int64Dtype,
    IntegerDtype,
    StringDtype,
    UInt8Dtype,
    UInt16Dtype,
    UInt32Dtype,
    UInt64Dtype,
)
from dtypeflow.core.override import (
    BooleanOverride,
    DictionaryOverride,
    Float16Override,
    Float32Override,
    Float64Override,
    Int8Override,
    Int16Override,
    Int32Override,
    Int64Override,
    Override,
    StringOverride,
    UInt8Override,
    UInt16Override,
    UInt32Override,
    UInt64Override,
)
from dtypeflow.core.schema import Schema

from .compatibility import GROUP_SAFE, group_of, is_selectable
from .dto import (
    ColumnReport,
    ColumnSelection,
    DatasetReport,
    DtypeOption,
    LoadedDataset,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from dtypeflow.core.dataset import Dataset
    from dtypeflow.core.profile import Profile
_DTYPE_BY_NAME: Final[dict[str, type[Dtype]]] = {
    dtype.__name__: dtype for dtype in ALL_TYPES
}
_OVERRIDE_BY_DTYPE: Final[dict[type[Dtype], type[Override]]] = {
    BooleanDtype: BooleanOverride,
    UInt8Dtype: UInt8Override,
    UInt16Dtype: UInt16Override,
    UInt32Dtype: UInt32Override,
    UInt64Dtype: UInt64Override,
    Int8Dtype: Int8Override,
    Int16Dtype: Int16Override,
    Int32Dtype: Int32Override,
    Int64Dtype: Int64Override,
    Float16Dtype: Float16Override,
    Float32Dtype: Float32Override,
    Float64Dtype: Float64Override,
    StringDtype: StringOverride,
    DictionaryDtype: DictionaryOverride,
}
DESCRIPTIONS: Final[dict[type[Dtype], str]] = {
    BooleanDtype: f"{BooleanDtype.TRUE} or {BooleanDtype.FALSE}",
    UInt8Dtype: f"Whole non-negative number, {UInt8Dtype.LOWER_BOUND:,} to {UInt8Dtype.HIGHER_BOUND:,}",
    UInt16Dtype: f"Whole non-negative number, {UInt16Dtype.LOWER_BOUND:,} to {UInt16Dtype.HIGHER_BOUND:,}",
    UInt32Dtype: f"Whole non-negative number, {UInt32Dtype.LOWER_BOUND:,} to {float(UInt32Dtype.HIGHER_BOUND):.1E}",
    UInt64Dtype: f"Whole non-negative number, {UInt64Dtype.LOWER_BOUND:,} to {float(UInt64Dtype.HIGHER_BOUND):.1E}",
    Int8Dtype: f"Whole number, {Int8Dtype.LOWER_BOUND:,} to {Int8Dtype.HIGHER_BOUND:,}",
    Int16Dtype: f"Whole number, {Int16Dtype.LOWER_BOUND:,} to {Int16Dtype.HIGHER_BOUND:,}",
    Int32Dtype: f"Whole number, {float(Int32Dtype.LOWER_BOUND):.1E} to {float(Int32Dtype.HIGHER_BOUND):.1E}",
    Int64Dtype: f"Whole number, {float(Int64Dtype.LOWER_BOUND):.1E} to {float(Int64Dtype.HIGHER_BOUND):.1E}",
    Float16Dtype: f"Decimal number, about {Float16Dtype.MAX_SIGNIFICANT_DIGITS} digits of precision, up to {Float16Dtype.MAX_ABSOLUTE_VALUE:.1E}",
    Float32Dtype: f"Decimal number, about {Float32Dtype.MAX_SIGNIFICANT_DIGITS} digits of precision, up to {Float32Dtype.MAX_ABSOLUTE_VALUE:.1E}",
    Float64Dtype: f"Decimal number, about {Float64Dtype.MAX_SIGNIFICANT_DIGITS} digits of precision, up to {Float64Dtype.MAX_ABSOLUTE_VALUE:.1E}",
    StringDtype: "Text",
    DictionaryDtype: "Category, a fixed set of repeating values",
}


def _label(dtype: type[Dtype], /) -> str:
    return dtype.__name__.removesuffix("Dtype")


def _dtype_option(dtype: type[Dtype], group: str, /) -> DtypeOption:
    return DtypeOption(
        name=dtype.__name__,
        label=_label(dtype),
        description=DESCRIPTIONS[dtype],
        group=group,
    )


def _format_sample(dtype: type[Dtype], value: str, /) -> str:
    if issubclass(dtype, IntegerDtype):
        return f"{int(value):,}"
    if issubclass(dtype, FloatDtype):
        return f"{Decimal(value):,}"
    return value


def _stats(dtype: type[Dtype], profile: Profile, /) -> tuple[tuple[str, str], ...]:
    samples = ", ".join(
        _format_sample(dtype, value) for value in profile.uniques(n=5)
    )
    stats: list[tuple[str, str]] = [
        ("Unique values", f"{profile.num_unique:,}"),
        ("Samples", samples),
    ]
    if issubclass(dtype, (FloatDtype, IntegerDtype)):
        stats.append(("Range", f"{profile.min:,} – {profile.max:,}"))
        if issubclass(dtype, FloatDtype):
            stats.append(("Precision", str(profile.precision)))
            stats.append(("Scale", str(profile.scale)))
    elif issubclass(dtype, StringDtype):
        stats.append(
            ("Length range", f"{profile.min_length:,} – {profile.max_length:,}"),
        )
    return tuple(stats)


def _column_report(column: str, profile: Profile, /) -> ColumnReport:
    dtype: type[Dtype] = type(profile).DTYPE
    options: list[DtypeOption] = [_dtype_option(dtype, GROUP_SAFE)]
    options.extend(

            _dtype_option(candidate.DTYPE, group_of(candidate.compatibility))
            for candidate in profile.candidates
            if is_selectable(candidate.compatibility)

    )
    return ColumnReport(
        name=column,
        inferred_dtype=dtype.__name__,
        description=DESCRIPTIONS[dtype],
        num_unique=profile.num_unique,
        total=profile.total,
        samples=profile.uniques(n=5),
        stats=_stats(dtype, profile),
        options=tuple(options),
    )


def _build_override(column: str, selection: ColumnSelection, /) -> Override:
    dtype: type[Dtype] = _DTYPE_BY_NAME[selection.dtype_name]
    override_cls: type[Override] = _OVERRIDE_BY_DTYPE[dtype]
    if dtype is BooleanDtype:
        if selection.true_value is None or selection.false_value is None:
            msg = f"Column {column!r} needs both a true and a false value to become Boolean."
            raise ValueError(msg)
        return BooleanOverride(
            column, true_value=selection.true_value, false_value=selection.false_value,
        )
    if dtype is DictionaryDtype:
        if selection.categories is None:
            msg = f"Column {column!r} needs a category list to become Dictionary."
            raise ValueError(msg)
        return DictionaryOverride(
            column, *selection.categories, ordered=selection.ordered,
        )
    return override_cls(column)


class DtypeflowService:
    def load_dataset(self, path: str | Path, /) -> LoadedDataset:
        dataset: Dataset = profile_dataset(path)
        columns = tuple(
            _column_report(column, dataset[column]) for column in dataset.columns
        )
        report = DatasetReport(source=str(dataset.source), columns=columns)
        return LoadedDataset(report=report, dataset_ref=dataset)

    def unique_values(self, loaded: LoadedDataset, column: str, /) -> tuple[str, ...]:
        dataset = cast("Dataset", loaded.dataset_ref)
        return dataset[column].uniques()

    def export(
        self,
        loaded: LoadedDataset,
        destination: str | Path,
        selections: Mapping[str, ColumnSelection],
        /,
    ) -> tuple[tuple[str, str], ...]:
        dataset = cast("Dataset", loaded.dataset_ref)
        overrides = tuple(

                _build_override(column, selection)
                for (column, selection) in selections.items()

        )
        destination = Path(destination)
        Schema(*overrides).apply(dataset, destination=destination)
        written = pq.read_table(destination).schema
        return tuple((field.name, str(field.type)) for field in written)
