from __future__ import annotations

from typing import Final

from .base import Dtype
from .nested import DictionaryDtype
from .primitive import (
    BooleanDtype,
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
from .primitive.integer import SignedDtype, UnsignedDtype

__all__: list[str] = [
    "ALL_TYPES",
    "BOOLEAN_TYPES",
    "FLOAT_TYPES",
    "INTEGER_TYPES",
    "SIGNED_INTEGER_TYPES",
    "STRING_TYPES",
    "UNSIGNED_INTEGER_TYPES",
    "BooleanDtype",
    "DictionaryDtype",
    "Dtype",
    "Float16Dtype",
    "Float32Dtype",
    "Float64Dtype",
    "FloatDtype",
    "Int8Dtype",
    "Int16Dtype",
    "Int32Dtype",
    "Int64Dtype",
    "IntegerDtype",
    "StringDtype",
    "UInt8Dtype",
    "UInt16Dtype",
    "UInt32Dtype",
    "UInt64Dtype",
]
BOOLEAN_TYPES: Final[tuple[type[Dtype], ...]] = (BooleanDtype,)
UNSIGNED_INTEGER_TYPES: Final[tuple[type[IntegerDtype], ...]] = tuple(
    UnsignedDtype.__subclasses__(),
)
SIGNED_INTEGER_TYPES: Final[tuple[type[IntegerDtype], ...]] = tuple(
    SignedDtype.__subclasses__(),
)
INTEGER_TYPES: Final[tuple[type[IntegerDtype], ...]] = (
    UNSIGNED_INTEGER_TYPES + SIGNED_INTEGER_TYPES
)
FLOAT_TYPES: Final[tuple[type[FloatDtype], ...]] = tuple(FloatDtype.__subclasses__())
STRING_TYPES: Final[tuple[type[Dtype], ...]] = (StringDtype,)
ALL_TYPES: Final[tuple[type[Dtype], ...]] = (
    *BOOLEAN_TYPES,
    DictionaryDtype,
    *INTEGER_TYPES,
    *FLOAT_TYPES,
    *STRING_TYPES,
)
