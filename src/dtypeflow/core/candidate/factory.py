from __future__ import annotations

from decimal import Decimal
from typing import Final, overload

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

from .base import Candidate, Compatibility
from .primitive import (
    Boolean as BooleanCandidate,
    Dictionary as DictionaryCandidate,
    Float16 as Float16Candidate,
    Float32 as Float32Candidate,
    Float64 as Float64Candidate,
    Int8 as Int8Candidate,
    Int16 as Int16Candidate,
    Int32 as Int32Candidate,
    Int64 as Int64Candidate,
    String as StringCandidate,
    UInt8 as UInt8Candidate,
    UInt16 as UInt16Candidate,
    UInt32 as UInt32Candidate,
    UInt64 as UInt64Candidate,
)

_MAX_BOOLEAN_UNIQUE: Final[int] = 2
_MAX_DICTIONARY_ABSOLUTE: Final[int] = 20
_MAX_DICTIONARY_RATIO: Final[float] = 0.05
_CANDIDATE_MAPPER: Final[dict[type[Dtype], type[Candidate]]] = {
    BooleanDtype: BooleanCandidate,
    UInt8Dtype: UInt8Candidate,
    UInt16Dtype: UInt16Candidate,
    UInt32Dtype: UInt32Candidate,
    UInt64Dtype: UInt64Candidate,
    Int8Dtype: Int8Candidate,
    Int16Dtype: Int16Candidate,
    Int32Dtype: Int32Candidate,
    Int64Dtype: Int64Candidate,
    Float16Dtype: Float16Candidate,
    Float32Dtype: Float32Candidate,
    Float64Dtype: Float64Candidate,
    StringDtype: StringCandidate,
    DictionaryDtype: DictionaryCandidate,
}


def _full_bounds(dtype: type[Dtype], /) -> tuple[Decimal, Decimal] | None:
    if issubclass(dtype, BooleanDtype):
        return (Decimal(0), Decimal(1))
    if issubclass(dtype, IntegerDtype):
        return (Decimal(dtype.LOWER_BOUND), Decimal(dtype.HIGHER_BOUND))
    if issubclass(dtype, FloatDtype):
        return (-dtype.MAX_ABSOLUTE_VALUE, dtype.MAX_ABSOLUTE_VALUE)
    return None


def _full_precision(dtype: type[Dtype], /) -> int:
    if issubclass(dtype, FloatDtype):
        return dtype.MAX_SIGNIFICANT_DIGITS
    bounds: tuple[Decimal, Decimal] | None = _full_bounds(dtype)
    if bounds is None:
        return 0
    return len(str(int(max(abs(bounds[0]), abs(bounds[1])))))


def _boolean_compatibility(num_unique: int | None, /) -> Compatibility:
    if num_unique is not None and num_unique <= _MAX_BOOLEAN_UNIQUE:
        return Compatibility.BOOLEAN_MAPPING
    return Compatibility.VALUES_NO_FIT


def _dictionary_compatibility(
    num_unique: int | None, total: int | None, /,
) -> Compatibility:
    eligible: bool = num_unique is not None and (
        num_unique <= _MAX_DICTIONARY_ABSOLUTE
        or (
            total is not None
            and total > 0
            and (num_unique / total <= _MAX_DICTIONARY_RATIO)
        )
    )
    if not eligible:
        return Compatibility.DICTIONARY_INEFFICIENT
    return Compatibility.DICTIONARY_ENCODING


def _fits_full_range(source: type[Dtype], target: type[Dtype], /) -> bool:
    source_bounds: tuple[Decimal, Decimal] | None = _full_bounds(source)
    target_bounds: tuple[Decimal, Decimal] | None = _full_bounds(target)
    return (
        source_bounds is not None
        and target_bounds is not None
        and (target_bounds[0] <= source_bounds[0])
        and (source_bounds[1] <= target_bounds[1])
        and (
            not issubclass(target, FloatDtype)
            or _full_precision(source) <= target.MAX_SIGNIFICANT_DIGITS
        )
    )


def _exceeds_precision(
    target: type[FloatDtype],
    min_value: int | Decimal,
    max_value: int | Decimal,
    precision: int | None,
    /,
) -> bool:
    if precision is not None:
        observed_precision: int = precision
    else:
        bound: Decimal | int = max(abs(min_value), abs(max_value))
        observed_precision = len(str(int(bound)))
    return observed_precision > target.MAX_SIGNIFICANT_DIGITS


def _unevaluated_compatibility(*, full_range_fits: bool) -> Compatibility:
    if full_range_fits:
        return Compatibility.FULL_RANGE_FIT
    return Compatibility.UNEVALUATED_NO_FIT


def _observed_compatibility(*, full_range_fits: bool) -> Compatibility:
    if full_range_fits:
        return Compatibility.FULL_RANGE_FIT
    return Compatibility.OBSERVED_ONLY_FIT


def _range_compatibility(
    source: type[Dtype],
    target: type[Dtype],
    /,
    *,
    min_value: int | Decimal | None,
    max_value: int | Decimal | None,
    precision: int | None,
    scale: int | None,
) -> Compatibility:
    full_range_fits: bool = _fits_full_range(source, target)
    target_bounds: tuple[Decimal, Decimal] | None = _full_bounds(target)
    if min_value is None or max_value is None or target_bounds is None:
        if issubclass(source, StringDtype):
            return Compatibility.NOT_NUMERIC
        return _unevaluated_compatibility(full_range_fits=full_range_fits)
    if issubclass(target, IntegerDtype) and (scale or 0) > 0:
        return Compatibility.DECIMAL_TRUNCATION
    if not (target_bounds[0] <= min_value and max_value <= target_bounds[1]):
        return Compatibility.RANGE_NO_FIT
    if issubclass(target, FloatDtype) and _exceeds_precision(
        target, min_value, max_value, precision,
    ):
        return Compatibility.PRECISION_REDUCTION
    return _observed_compatibility(full_range_fits=full_range_fits)


def _compatibility(
    source: type[Dtype],
    target: type[Dtype],
    /,
    *,
    num_unique: int | None,
    total: int | None,
    min_value: int | Decimal | None,
    max_value: int | Decimal | None,
    precision: int | None,
    scale: int | None,
) -> Compatibility:
    if issubclass(target, StringDtype):
        return Compatibility.VALUES_PRESERVED
    if issubclass(target, BooleanDtype):
        return _boolean_compatibility(num_unique)
    if issubclass(target, DictionaryDtype):
        return _dictionary_compatibility(num_unique, total)
    return _range_compatibility(
        source,
        target,
        min_value=min_value,
        max_value=max_value,
        precision=precision,
        scale=scale,
    )


@overload
def candidate_factory(dtype: type[Dtype], /) -> tuple[Candidate, ...]: ...


@overload
def candidate_factory(
    dtype: type[Dtype], /, *, num_unique: int, total: int | None = None,
) -> tuple[Candidate, ...]: ...


@overload
def candidate_factory(
    dtype: type[Dtype],
    /,
    *,
    num_unique: int,
    total: int | None = None,
    min_value: int | Decimal,
    max_value: int | Decimal,
    precision: int | None = None,
    scale: int | None = None,
) -> tuple[Candidate, ...]: ...


def candidate_factory(
    dtype: type[Dtype],
    /,
    *,
    num_unique: int | None = None,
    total: int | None = None,
    min_value: int | Decimal | None = None,
    max_value: int | Decimal | None = None,
    precision: int | None = None,
    scale: int | None = None,
) -> tuple[Candidate, ...]:
    if dtype not in ALL_TYPES:
        msg = f"Unsupported dtype: {dtype}"
        raise ValueError(msg)
    candidate_dtypes: tuple[type[Dtype], ...] = tuple(
        target for target in ALL_TYPES if target is not dtype
    )
    candidates: list[Candidate] = []
    for target in candidate_dtypes:
        compatibility: Compatibility = _compatibility(
            dtype,
            target,
            num_unique=num_unique,
            total=total,
            min_value=min_value,
            max_value=max_value,
            precision=precision,
            scale=scale,
        )
        candidates.append(_CANDIDATE_MAPPER[target](compatibility))
    return tuple(candidates)
