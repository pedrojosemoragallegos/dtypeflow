from __future__ import annotations

from typing import Final

from dtypeflow.core.dtype import (
    BooleanDtype,
    DictionaryDtype,
    Dtype,
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

from .base import Candidate


class Boolean(Candidate):
    DTYPE: Final[type[Dtype]] = BooleanDtype


class UInt8(Candidate):
    DTYPE: Final[type[Dtype]] = UInt8Dtype


class UInt16(Candidate):
    DTYPE: Final[type[Dtype]] = UInt16Dtype


class UInt32(Candidate):
    DTYPE: Final[type[Dtype]] = UInt32Dtype


class UInt64(Candidate):
    DTYPE: Final[type[Dtype]] = UInt64Dtype


class Int8(Candidate):
    DTYPE: Final[type[Dtype]] = Int8Dtype


class Int16(Candidate):
    DTYPE: Final[type[Dtype]] = Int16Dtype


class Int32(Candidate):
    DTYPE: Final[type[Dtype]] = Int32Dtype


class Int64(Candidate):
    DTYPE: Final[type[Dtype]] = Int64Dtype


class Float16(Candidate):
    DTYPE: Final[type[Dtype]] = Float16Dtype


class Float32(Candidate):
    DTYPE: Final[type[Dtype]] = Float32Dtype


class Float64(Candidate):
    DTYPE: Final[type[Dtype]] = Float64Dtype


class String(Candidate):
    DTYPE: Final[type[Dtype]] = StringDtype


class Dictionary(Candidate):
    DTYPE: Final[type[Dtype]] = DictionaryDtype
