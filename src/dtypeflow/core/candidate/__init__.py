from __future__ import annotations

from .base import Candidate, Compatibility
from .factory import candidate_factory
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

__all__: list[str] = [
    "BooleanCandidate",
    "Candidate",
    "Compatibility",
    "DictionaryCandidate",
    "Float16Candidate",
    "Float32Candidate",
    "Float64Candidate",
    "Int8Candidate",
    "Int16Candidate",
    "Int32Candidate",
    "Int64Candidate",
    "StringCandidate",
    "UInt8Candidate",
    "UInt16Candidate",
    "UInt32Candidate",
    "UInt64Candidate",
    "candidate_factory",
]
