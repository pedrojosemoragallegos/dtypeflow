from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING, Final

from dtypeflow.core.dataset import Dataset
from dtypeflow.core.dtype import (
    FLOAT_TYPES,
    SIGNED_INTEGER_TYPES,
    UNSIGNED_INTEGER_TYPES,
    BooleanDtype,
    Float16Dtype,
    Float32Dtype,
    Float64Dtype,
    Int8Dtype,
    Int16Dtype,
    Int32Dtype,
    Int64Dtype,
    StringDtype,
    UInt8Dtype,
    UInt16Dtype,
    UInt32Dtype,
    UInt64Dtype,
)
from dtypeflow.core.profile import (
    BooleanProfile,
    Float16Profile,
    Float32Profile,
    Float64Profile,
    Int8Profile,
    Int16Profile,
    Int32Profile,
    Int64Profile,
    Profile,
    StringProfile,
    UInt8Profile,
    UInt16Profile,
    UInt32Profile,
    UInt64Profile,
)
from dtypeflow.utils import read_csv

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from dtypeflow.core.dtype import Dtype
PROFILE_MAPPER: Final[dict[type[Dtype], type[Profile]]] = {
    BooleanDtype: BooleanProfile,
    UInt8Dtype: UInt8Profile,
    UInt16Dtype: UInt16Profile,
    UInt32Dtype: UInt32Profile,
    UInt64Dtype: UInt64Profile,
    Int8Dtype: Int8Profile,
    Int16Dtype: Int16Profile,
    Int32Dtype: Int32Profile,
    Int64Dtype: Int64Profile,
    Float16Dtype: Float16Profile,
    Float32Dtype: Float32Profile,
    Float64Dtype: Float64Profile,
    StringDtype: StringProfile,
}
_BOOLEAN_UNIQUE_COUNT: Final[int] = 2


def _try_int(value: str, /) -> int | None:
    try:
        return int(value)
    except ValueError:
        return None


def _try_decimal(value: str, /) -> Decimal | None:
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def _pick_integer_type(min_value: int, max_value: int, /) -> type[Dtype] | None:
    integer_types = SIGNED_INTEGER_TYPES if min_value < 0 else UNSIGNED_INTEGER_TYPES
    for integer_type in integer_types:
        if (
            min_value >= integer_type.LOWER_BOUND
            and max_value <= integer_type.HIGHER_BOUND
        ):
            return integer_type
    return None


def _pick_float_type(max_abs: Decimal, max_digits: int, /) -> type[Dtype] | None:
    for float_type in FLOAT_TYPES:
        if (
            max_abs <= float_type.MAX_ABSOLUTE_VALUE
            and max_digits <= float_type.MAX_SIGNIFICANT_DIGITS
        ):
            return float_type
    return None


def classify(*values: str) -> tuple[type[Dtype], Mapping[str, int | Decimal] | None]:
    if len(values) == _BOOLEAN_UNIQUE_COUNT:
        return (BooleanDtype, None)
    is_integer = True
    min_int: int | None = None
    max_int: int | None = None
    int_by_value: dict[str, int] = {}
    is_decimal = True
    max_abs: Decimal | None = None
    max_digits = 0
    decimal_by_value: dict[str, Decimal] = {}
    for value in values:
        if is_integer:
            as_int = _try_int(value)
            if as_int is None:
                is_integer = False
            else:
                int_by_value[value] = as_int
                min_int = as_int if min_int is None else min(min_int, as_int)
                max_int = as_int if max_int is None else max(max_int, as_int)
        if is_decimal:
            as_decimal = _try_decimal(value)
            if as_decimal is None:
                is_decimal = False
            else:
                decimal_by_value[value] = as_decimal
                abs_value = abs(as_decimal)
                max_abs = abs_value if max_abs is None else max(max_abs, abs_value)
                max_digits = max(max_digits, len(as_decimal.as_tuple().digits))
    if is_integer and min_int is not None and (max_int is not None):
        integer_type = _pick_integer_type(min_int, max_int)
        if integer_type is not None:
            return (integer_type, int_by_value)
    if is_decimal and max_abs is not None:
        float_type = _pick_float_type(max_abs, max_digits)
        if float_type is not None:
            return (float_type, decimal_by_value)
    return (StringDtype, None)


def profile_column(*values: str | None) -> Profile:
    stripped: tuple[str | None, ...] = tuple(
        value.strip() if value is not None else None for value in values
    )
    non_nan: tuple[int, ...] = tuple(
        index for (index, value) in enumerate(stripped) if value
    )
    nan: tuple[int, ...] = tuple(
        index for (index, value) in enumerate(stripped) if not value
    )
    value_to_index: dict[str, int] = {stripped[index]: index for index in non_nan}
    (dtype, parsed) = classify(*value_to_index)
    sort_key = (
        (lambda item: parsed[item[0]]) if parsed is not None else lambda item: item[0]
    )
    uniques: tuple[int, ...] = tuple(
        index for (_, index) in sorted(value_to_index.items(), key=sort_key)
    )
    return PROFILE_MAPPER[dtype](*stripped, uniques=uniques, non_nan=non_nan, nan=nan)


def profile(source: str | Path, /) -> Dataset:
    return Dataset(
        source,
        **{
            column: profile_column(*values)
            for (column, values) in read_csv(source).items()
        },
    )
