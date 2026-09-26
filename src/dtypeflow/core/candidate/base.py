from __future__ import annotations

from abc import ABC
from enum import Enum, auto
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from dtypeflow.core.dtype import Dtype


class Compatibility(Enum):
    FULL_RANGE_FIT = auto()
    VALUES_PRESERVED = auto()
    VALUES_NO_FIT = auto()
    RANGE_NO_FIT = auto()
    UNEVALUATED_NO_FIT = auto()
    NOT_NUMERIC = auto()
    OBSERVED_ONLY_FIT = auto()
    DECIMAL_TRUNCATION = auto()
    PRECISION_REDUCTION = auto()
    BOOLEAN_MAPPING = auto()
    DICTIONARY_ENCODING = auto()
    DICTIONARY_INEFFICIENT = auto()


class Candidate(ABC):
    DTYPE: ClassVar[type[Dtype]]

    def __init__(self, compatibility: Compatibility, /) -> None:
        self._compatibility: Compatibility = compatibility

    @property
    def compatibility(self) -> Compatibility:
        return self._compatibility

    def __repr__(self) -> str:
        return f"{type(self).__name__}(compatibility={self._compatibility.name})"
